import sqlite3
import random
import math
import time

from modules.leveling.package.enums import Leveling
from modules.package.utils import open_json

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


