from io import BytesIO
from re import A
import sqlite3
import random
import math
import time
import discord

from PIL import Image, ImageDraw, ImageFont, ImageChops

from modules.leveling.package.enums import Leveling
from modules.package.enums import Colors, Emotes
from modules.package.exceptions import LevelingError
from modules.package.utils import get_prefix, open_json, save_json

MAX_LEVEL = 1e3
TESTING_XP = 50
IS_TESTING = True

def get_level_from_xp(xp):
    return int((-1 + math.floor(math.floor(math.sqrt(1 + 8 * xp / 25)))) / 4)

def get_xp_from_level(level):
    return 25 * (2 * level ** 2 + level)


async def increase_xp(guild, user, message):

    channel = message.channel

    leveling_settings = open_json("data/leveling.json")
    leveling_settings = leveling_settings[str(guild.id)]

    if (not user_is_blacklisted(guild, user, leveling_settings[Leveling.no_xp_roles.value]) \
        and not channel_is_blacklisted(channel, leveling_settings[Leveling.no_xp_channels.value])):

        current_xp, last_message = get_leveling_data(guild, user)

        if current_xp == -1:
            create_leveling_entry(guild, user)

        current_time = round(time.time())

        if last_message + leveling_settings[Leveling.time.value] < current_time \
            or IS_TESTING:

            xp_to_give = random.randint(leveling_settings[Leveling.min_xp.value], leveling_settings[Leveling.max_xp.value])
            xp_to_give += TESTING_XP
            
            await change_xp(guild, user, current_xp, xp_to_give, current_time, channel)
    

def get_leveling_data(guild, user):

    path = "data/database.db"
    table = "levels"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"select * from {table} where guild = ? and user = ?", (guild.id, user.id))
    data = cursor.fetchall()
    connection.close()

    if len(data) != 0:
        entry = data[0]
        return entry["total_xp"], entry["last_message_time"]
    else:
        return -1, -1


def create_leveling_entry(guild, user):
    
    path = "data/database.db"
    table = "levels"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"insert into {table} values (?, ?, ?, ?, ?)", (None, guild.id, user.id, 0, 0))
    connection.commit()
    connection.close()



def user_is_blacklisted(guild, user, roles):
    member = guild.get_member(user.id)

    for role in member.roles:
        if role.id in roles:
            return True

    return False


def channel_is_blacklisted(channel, channels):
    return channel.id in channels


async def change_xp(guild, user, current_xp, xp_to_give = 0, timestamp = None, last_channel = None):
    
    new_xp = current_xp + xp_to_give

    if new_xp < 0:
        new_xp = 0

    level = get_level_from_xp(new_xp)
    if level > MAX_LEVEL:
        new_xp = get_xp_from_level(MAX_LEVEL)
    

    path = "data/database.db"
    table = "levels"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    if timestamp is not None:
        cursor.execute(f"update {table} set total_xp = ?, last_message_time = ? where guild = ? and user = ?", (new_xp, timestamp, guild.id, user.id))
    else:
        cursor.execute(f"update {table} set total_xp = ? where guild = ? and user = ?", (new_xp, guild.id, user.id))

    connection.commit()
    connection.close()

    await check_for_level_up(guild, user, current_xp, new_xp, last_channel)



async def check_for_level_up(guild, user, old_xp, new_xp, last_channel):
    
    if new_xp > old_xp:
        old_level = get_level_from_xp(old_xp)
        new_level = get_level_from_xp(new_xp)
        
        if new_level > old_level:
            await send_level_up_message(guild, user, new_level, last_channel)



async def send_level_up_message(guild, user, level, last_channel):

    leveling_settings = open_json("data/leveling.json")
    leveling_settings = leveling_settings[str(guild.id)]

    channel_id = leveling_settings[Leveling.notify_channel.value]

    if channel_id == 0:
        channel_id = last_channel.id

    channel = guild.get_channel(int(channel_id))
    await channel.send(f"Congratulations <@{user.id}>! You just advanced to **level {level}**")


async def set_level(guild, user, level):

    if level < 0:
        raise LevelingError(f"{Emotes.not_found.value} The level can not be a negative number!")

    if level > MAX_LEVEL:
        raise LevelingError(f"{Emotes.not_found.value} The maximum level is **{MAX_LEVEL}**")

    new_xp = get_xp_from_level(level)
    old_xp, last_message_timestamp = get_leveling_data(guild, user)
    
    if old_xp == -1:
        create_leveling_entry(guild, user)

    await change_xp(guild, user, old_xp, new_xp - old_xp, timestamp = last_message_timestamp)


async def add_xp(guild, user, xp_to_add, ctx):

    if xp_to_add < 0:
        raise LevelingError(f"{Emotes.not_found.value} The amount of xp can not be a negative number!")
    
    old_xp, last_message_timestamp = get_leveling_data(guild, user)
    new_xp = min(old_xp + xp_to_add, get_xp_from_level(MAX_LEVEL))

    if old_xp == -1:
        create_leveling_entry(guild, user)

    await change_xp(guild, user, old_xp, new_xp - old_xp, timestamp = last_message_timestamp)
    await ctx.reply(f"{Emotes.green_tick.value} Successfully added {xp_to_add} to <@{user.id}>!\nTheir new level is **{get_level_from_xp(new_xp)}**!")


async def remove_xp(guild, user, xp_to_remove, ctx):

    if xp_to_remove < 0:
        raise LevelingError(f"{Emotes.not_found.value} The amount of xp can not be a negative number!")
    
    old_xp, last_message_timestamp = get_leveling_data(guild, user)
    new_xp = min(old_xp - xp_to_remove, 0)

    if old_xp == -1:
        create_leveling_entry(guild, user)

    await change_xp(guild, user, old_xp, new_xp - old_xp, timestamp = last_message_timestamp)
    await ctx.reply(f"{Emotes.green_tick.value} Successfully removed {xp_to_remove} from <@{user.id}>!\nTheir new level is **{get_level_from_xp(new_xp)}**!")



    
def add_reward(guild, level, role):

    leveling = open_json("data/leveling.json")
    rewards = leveling[str(guild.id)][Leveling.rewards.value]

    if str(level) in rewards.keys():
        raise LevelingError("This level already has a reward set!")

    rewards[str(level)] = role.id
    save_json(leveling, "data/leveling.json")


def remove_reward(guild, level):

    leveling = open_json("data/leveling.json")
    rewards = leveling[str(guild.id)][Leveling.rewards.value]

    if str(level) not in rewards.keys():
        raise LevelingError("This level does not have a reward!")

    del rewards[str(level)]
    save_json(leveling, "data/leveling.json")


def get_rewards(guild):

    leveling = open_json("data/leveling.json")
    rewards = leveling[str(guild.id)][Leveling.rewards.value]

    if len(rewards) == 0:
        _title = "There are no role rewards!"
        _desc  = f"{Emotes.reply.value} Use `{get_prefix()} addreward` in order to add rewards!"
        _color = Colors.red.value
    else:
        _title = "Role Rewards\n"
        _desc = ""
        _color = Colors.green.value

        data = []

        for reward_key in rewards.keys():
            role = rewards[reward_key]
            data.append((int(reward_key), role))

        data.sort(key = lambda entry: entry[0])

        for reward in data:
            _desc += f"Level **{reward[0]}**\n{Emotes.reply.value}<@&{reward[1]}>\n"


    embed = discord.Embed(
        color = _color,
        description = _desc,
        title = _title
    )

    return embed


def change_no_xp(guild, _object, allow):

    message = ""
    leveling = open_json("data/leveling.json")
    guild_settings = leveling[str(guild.id)]

    _type = ""
    _value = None

    if type(_object) is discord.Role:
        _type = "Role"
        _value = Leveling.no_xp_roles.value

    else:  # type(_object) is discord.TextChannel:
        _type = "Channel"
        _value = Leveling.no_xp_channels.value

    
    if allow == True:
            
        if _object.id in guild_settings[_value]:
            message = f"{Emotes.not_found.value} This {_type.lower()} is already blacklisted!"
        else:
            guild_settings[_value].append(_object.id)
            message = f"{Emotes.green_tick.value} {_type} successfully blacklisted!"
    
    else:  # allow == False
        
        if _object.id not in guild_settings[_value]:
            message = f"{Emotes.not_found.value} This {_type.lower()} is not blacklisted!"
        else:
            guild_settings[_value].remove(_object.id)
            message = f"{Emotes.green_tick.value} The {_type.lower()} was successfully removed from the blacklist!"

    save_json(leveling, "data/leveling.json")

    return message



def get_blacklist(guild):
    
    leveling = open_json("data/leveling.json")
    no_xp_channels = leveling[str(guild.id)][Leveling.no_xp_channels.value]
    no_xp_roles = leveling[str(guild.id)][Leveling.no_xp_roles.value]

    if len(no_xp_channels) == 0 and len(no_xp_roles):
        _title = "There are no blacklisted roles or channels!"
        _desc  = f"{Emotes.reply.value} Use `{get_prefix()} addreward` in order to add rewards!"
        _color = Colors.red.value
    else:
        _title = "Leveling Blacklist\n"
        _desc = ""
        _color = Colors.green.value

        if len(no_xp_roles) != 0:
            _desc += f"**Roles**\n{Emotes.reply.value}"

            for role in no_xp_roles:
                _desc += f"<@&{role}> "

            _desc += "\n\n"

        if len(no_xp_channels) != 0:
            _desc += f"**Channels**\n{Emotes.reply.value}"
            for channel in no_xp_channels:
                _desc += f"<#{channel}> "
        
    embed = discord.Embed(
        color = _color,
        description = _desc,
        title = _title
    )

    return embed


async def generate_level_image(guild, user, ctx):
    
    template = Image.open("Images/rank_card.png").convert("RGBA")

    profile_picture = user.avatar_url_as(size = 256)
    data = BytesIO(await profile_picture.read())
    profile_picture = Image.open(data).convert("RGBA")

    name = str(user)
    level, rank = get_user_level_and_rank(guild, user, ctx)

    image = ImageDraw.draw(template)
    pfp_circle = create_circle_picture(profile_picture, (100, 100)) 

    name_font = None

    
def get_user_level_and_rank(guild, user, author):
    
    path = "data/database.db"
    table = "levels"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"select * from {table} where guild = ? order by total_xp desc", (guild.id,))
    data = cursor.fetchall()

    cursor.execute(f"select * from {table} where guild = ? and user = ?", (guild.id, user.id))
    user_data = cursor.fetchall()
    connection.close()

    if len(user_data) != 0:
        entry = user_data[0]
        return get_level_from_xp(entry["total_xp"]), data.index(entry) + 1
    else:

        if user == author:
            raise LevelingError(f"{Emotes.no_entry.value} You have no level! Keep chatting to earn a rank!")
        else:
            raise LevelingError(f"{Emotes.no_entry.value} That user has no level!")
            

def create_circle_picture(image, size):

    image = image.resize(size, Image.ANTIALIAS).convert("RGBA")

    bigsize = (size[0] * 3, size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.elipse((0, 0) + bigsize, fill = 255)
    mask = mask.resize(size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, image.split()[-1])
    image.putalpha(mask)

    return image