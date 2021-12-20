from io import BytesIO
import sqlite3
import random
import math
import time
import discord
import math

from PIL import Image, ImageDraw, ImageFont, ImageChops

from modules.leveling.package.enums import CustomColors, Leveling
from modules.package.enums import Colors, Emotes
from modules.package.exceptions import CustomException
from modules.package.utils import get_prefix, open_json, save_json

MAX_LEVEL = 1e3
TESTING_XP = 100
IS_TESTING = True


# def get_level_from_xp(xp):
#     return int((-1 + math.floor(math.floor(math.sqrt(1 + 8 * xp / 25)))) / 4)

# def get_xp_from_level(level):
#     return 25 * (2 * level ** 2 + level)

def gaus(n):
    return n * (n + 1) / 2

def sum_of_squares(n):
    return n * (n + 1) * (2 * n + 1) / 6

def get_xp_from_level(x):
    return math.floor(5 * (sum_of_squares(x - 1)) + (40 * gaus(x - 1)) + x * 100)


def get_level_from_xp(xp):
    _xp, level = 0, 0

    while _xp < xp:
        level += 1
        _xp = get_xp_from_level(level)

    return level - 1


async def increase_xp(guild, user, message):
    
    if not user.bot:

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
                xp_to_give += TESTING_XP * IS_TESTING
                
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

    await check_for_level_change(guild, user, current_xp, new_xp, last_channel)



async def check_for_level_change(guild, user, old_xp, new_xp, last_channel):
    
   
    old_level = get_level_from_xp(old_xp)
    new_level = get_level_from_xp(new_xp)
    
    if new_level != old_level:
        await check_for_new_rewards(guild, user, new_level)

    if new_level > old_level:
        await send_level_up_message(guild, user, new_level, last_channel)



async def check_for_new_rewards(guild, user, level):
    
    leveling = open_json("data/leveling.json")
    guild_settings = leveling[str(guild.id)]
    rewards = guild_settings[Leveling.rewards.value]
    
    reward_roles = []
    new_reward_role = None
    last_index = None
    index = 0

    for reward_level in rewards:
        if level >= int(reward_level):
            new_reward_role = int(rewards[reward_level])
            last_index = index

        index += 1
        reward_roles.append(int(rewards[reward_level]))
  
    if last_index is None:
        last_index = len(reward_roles)

    index = 0

    while index < last_index: 
        role = reward_roles[index]
        role = guild.get_role(role)
        if role in user.roles:
            await user.remove_roles(role, reason = f"Removed old level reward")
        index += 1

    new_reward_role = guild.get_role(new_reward_role)
    if new_reward_role is not None and new_reward_role not in user.roles:
        await user.add_roles(new_reward_role, reason = f"Reached level {level}")
    

async def send_level_up_message(guild, user, level, last_channel):

    leveling_settings = open_json("data/leveling.json")
    leveling_settings = leveling_settings[str(guild.id)]

    channel_id = leveling_settings[Leveling.notify_channel.value]

    if channel_id == 0:
        channel_id = last_channel.id

    channel = guild.get_channel(int(channel_id))
    await channel.send(f"Congratulations <@{user.id}>! You just advanced to **level {level}**!")


async def set_level(guild, user, level):

    if level < 0:
        raise CustomException(f"{Emotes.not_found.value} The level can not be a negative number!")

    if level > MAX_LEVEL:
        raise CustomException(f"{Emotes.not_found.value} The maximum level is **{MAX_LEVEL}**")

    new_xp = get_xp_from_level(level)
    old_xp, last_message_timestamp = get_leveling_data(guild, user)
    
    if old_xp == -1:
        create_leveling_entry(guild, user)

    await change_xp(guild, user, old_xp, new_xp - old_xp, timestamp = last_message_timestamp)


async def add_xp(guild, user, xp_to_add, ctx):

    if xp_to_add < 0:
        raise CustomException(f"{Emotes.not_found.value} The amount of xp can not be a negative number!")
    
    old_xp, last_message_timestamp = get_leveling_data(guild, user)
    new_xp = min(old_xp + xp_to_add, get_xp_from_level(MAX_LEVEL))

    if old_xp == -1:
        create_leveling_entry(guild, user)
    
    await change_xp(guild, user, old_xp, new_xp - old_xp, timestamp = last_message_timestamp)
    await ctx.reply(f"{Emotes.green_tick.value} Successfully added {xp_to_add} XP to <@{user.id}>!")


async def remove_xp(guild, user, xp_to_remove, ctx):

    if xp_to_remove < 0:
        raise CustomException(f"{Emotes.not_found.value} The amount of xp can not be a negative number!")
    
    old_xp, last_message_timestamp = get_leveling_data(guild, user)
    new_xp = old_xp - xp_to_remove

    if old_xp == -1:
        await ctx.reply(f"{Emotes.no_entry.value} This use has no XP yet!")        
    else:
        await change_xp(guild, user, old_xp, new_xp - old_xp, timestamp = last_message_timestamp)
        await ctx.reply(f"{Emotes.green_tick.value} Successfully removed {xp_to_remove} XP from <@{user.id}>!")



    
def add_reward(guild, level, role):

    leveling = open_json("data/leveling.json")
    rewards = leveling[str(guild.id)][Leveling.rewards.value]

    if str(level) in rewards.keys():
        raise CustomException(f"{Emotes.wrong.value} This level already has a reward set!")

    rewards[str(level)] = role.id
    save_json(leveling, "data/leveling.json")


def remove_reward(guild, level):

    leveling = open_json("data/leveling.json")
    rewards = leveling[str(guild.id)][Leveling.rewards.value]

    if str(level) not in rewards.keys():
        raise CustomException(f"{Emotes.wrong.value} This level does not have a reward!")

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


def get_user_level_rank_xp(guild, user, author):
    
    
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
        return get_level_from_xp(entry["total_xp"]), data.index(entry) + 1, entry["total_xp"]
    else:

        if user == author:
            raise CustomException(f"{Emotes.wrong.value} You have no level! Keep chatting to earn a rank!")
        else:
            raise CustomException(f"{Emotes.wrong.value} That user has no level!")
            


async def generate_level_image(guild, user, ctx):
    
    if not user.bot:

        max_y = 256   # image max y
        max_x = 1024  # image max x

        y_offset = 25  # the right, top offset
        x_offset = 525

        # profile picture data
        picture_size = 200
        picture_border_size = 8
        picture_location_x = y_offset + picture_border_size
        picture_location_y = int((max_y - picture_size - 2 * picture_border_size) / 2)

        after_image_offset = 16 + picture_location_x + picture_size + 2 * picture_border_size


        # name location 
        name_box_location = (after_image_offset, int(y_offset / 2))

        #rank location
        rank_location  = (after_image_offset, name_box_location[1] + 3 * y_offset + int(y_offset / 2))

        #level location
        level_location = (after_image_offset, name_box_location[1] + 6 * y_offset)

        # XP location
        xp_location = (after_image_offset + x_offset, name_box_location[1] + 6 * y_offset)

        # rounded rectangle
        rectangle = (after_image_offset, name_box_location[1] + 8 * y_offset, after_image_offset + x_offset, name_box_location[1] + 8 * y_offset + 35 )

        #open the required images
        template = Image.open("Images/rank_card.png").convert("RGBA")
        borded_image = Image.open("Images/border.png").convert("RGBA")


        # create a round profile picture image
        profile_picture = user.avatar_url_as(size = 256)
        data = BytesIO(await profile_picture.read())
        profile_picture = Image.open(data).convert("RGBA")


        # initialize the dispaly data
        name = str(user.display_name)
        discriminator = "#" + str(user.discriminator)
        level, rank, xp = get_user_level_rank_xp(guild, user, ctx)

        # initialize the draw object
        draw = ImageDraw.Draw(template)

        # creating a border
        border = create_circle_picture(borded_image, (picture_size + 2 * picture_border_size, picture_size + 2 * picture_border_size))
        template.paste(border, (picture_location_x, picture_location_y), border)


        # pasting the profile picture on the rank card
        pfp_circle = create_circle_picture(profile_picture, (picture_size, picture_size)) 
        template.paste(pfp_circle, (picture_location_x + picture_border_size, picture_location_y + picture_border_size), pfp_circle)


        # initializing the fonts
        if len(name) >= 16:
            name = name[:16]

        if len(name) >= 12:
            name_font = ImageFont.truetype("Images/Cambria.ttf", 28)
            discriminator_font = ImageFont.truetype("Images/Cambria.ttf", 14)
            
        elif len(name) >= 8:
            name_font = ImageFont.truetype("Images/Cambria.ttf", 36)
            discriminator_font = ImageFont.truetype("Images/Cambria.ttf", 18)

        else:
            name_font = ImageFont.truetype("Images/Cambria.ttf", 56)
            discriminator_font = ImageFont.truetype("Images/Cambria.ttf", 27)

        rank_font = ImageFont.truetype("Images/Cambria.ttf", 36)
        rank_number_font = ImageFont.truetype("Images/Cambria.ttf", 48)

        level_font = ImageFont.truetype("Images/Cambria.ttf", 32)
        level_number_font = ImageFont.truetype("Images/Cambria.ttf", 48)
        
        xp_font = ImageFont.truetype("Images/Cambria.ttf", 32)
        xp_number_font = ImageFont.truetype("Images/Cambria.ttf", 32)


        #  draw the name
        _w, _h = name_font.getsize(name)
        draw.text(name_box_location, name, font = name_font, fill = CustomColors.white.value)


        # draw the discriminator
        w, h = discriminator_font.getsize(discriminator)
    
        discriminator_location = (name_box_location[0] + _w + 8, name_box_location[1] + h)
        draw.text(discriminator_location, discriminator, font = discriminator_font, fill = CustomColors.almost_white.value)
        

        # draw RANK
        _w, _h = rank_font.getsize("Rank")
        draw.text(rank_location, "Rank", font = rank_font, fill = CustomColors.almost_white.value)

        # draw the rank number
        w, h, = rank_number_font.getsize(f"#{rank}")
        rank_nnumber_location = (rank_location[0] + _w + 12, rank_location[1] - int(_h / 3))
        draw.text(rank_nnumber_location, f"#{rank}", font = rank_number_font, fill = CustomColors.white.value)
        

        # draw Level
        _w, _h = level_font.getsize("Level")
        draw.text(level_location, "Level", font = level_font, fill = CustomColors.almost_white.value)

        # draw the level number
        w, h, = level_number_font.getsize(str(level))
        level_number_location = (level_location[0] + _w + 12, level_location[1] - int(_h / 2))
        draw.text(level_number_location, str(level), font = level_number_font, fill = CustomColors.white.value)
        

        #draw xp
        needed_xp = get_xp_from_level(level + 1) - get_xp_from_level(level)
        _w, _h = xp_font.getsize(f"/ {format_xp(needed_xp)}  XP")
        xp_location = (xp_location[0] - _w, xp_location[1])
        draw.text(xp_location, f"/ {format_xp(needed_xp)}  XP" , font = xp_font, fill = CustomColors.almost_white.value, align = "right")
        
        # current xp
        current_xp = xp - get_xp_from_level(level)
        w, h = xp_number_font.getsize(f"/ {format_xp(current_xp)} ")
        xp_number_location = (xp_location[0] - w + 16, xp_location[1])
        draw.text(xp_number_location, f"{format_xp(current_xp)} " , font = xp_number_font, fill = CustomColors.white.value, align = "right")

        # draw bar
        draw.rounded_rectangle(rectangle, fill = CustomColors.white.value, width = 0, radius = 28)

        precent = current_xp / needed_xp 

        pixels = get_original_pixels(rectangle, template)

        rectangle = (rectangle[0], rectangle[1], after_image_offset + x_offset * precent, rectangle[3])
        draw.rounded_rectangle(rectangle, fill = CustomColors.blue.value, width = 0, radius = 28)

        rectify_bar(pixels, template)

        # send the image
        with BytesIO() as rank_card:
            template.save(rank_card, "PNG")
            rank_card.seek(0)
            await ctx.reply(file = discord.File(rank_card, f"{guild.id}_{user.id}_level.png"))


def create_circle_picture(image, size):

    image = image.resize(size, Image.ANTIALIAS).convert("RGBA")

    bigsize = (size[0] * 3, size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill = 255)
    mask = mask.resize(size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, image.split()[-1])
    image.putalpha(mask)

    return image


def format_xp(xp):

    if xp < 1e3:
        return str(xp)
    
    if xp < 1e4:
        return str(round(xp / 1000, 2)) + "k"
    
    return str(round(xp / 1000, 1)) + "k"


def get_original_pixels(rectangle, temppalte):

    pixels = []

    for i in range(50):
        for j in range(rectangle[3] - rectangle[1] + 1):
            
            pi = rectangle[0] + i
            pj = rectangle[1] + j

            r, g, b, a = temppalte.getpixel((pi, pj))
  
            if (r, g, b, 255) == CustomColors.card_black.value:
                pixels.append((pi, pj))


            pi = rectangle[2] - i
            pj = rectangle[1] + j

            r, g, b, a = temppalte.getpixel((pi, pj))
  
            if (r, g, b, 255) == CustomColors.card_black.value:
                pixels.append((pi, pj))

    return pixels


def rectify_bar(pixels, template):
    for pixel in pixels:
        template.putpixel(pixel, CustomColors.card_black.value)
    

def set_notify_channel(guild, channel):

    leveling = open_json("data/leveling.json")
    guild_settings = leveling[str(guild.id)]
    guild_settings[Leveling.notify_channel.value] = channel.id
    save_json(leveling, "data/leveling.json")