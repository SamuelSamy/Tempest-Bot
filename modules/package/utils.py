import json
import re

from modules.package.enums import Settings
from modules.package.exceptions import *


def open_json(file_path):

    with open(file_path) as file:
        json_file = json.load(file)

    return json_file


def save_json(json_file, file_path):

    with open(file_path, "w") as f:
        json.dump(json_file, f)


def user_in_guild(guild, user):
    return (guild.get_member(user.id) is not None)


def get_string_from_seconds(seconds):

    format = ""

    hours = seconds // 3600
    seconds = seconds % 3600

    minutes = seconds // 60
    seconds = seconds % 60

    if hours > 0:
        if hours == 1:
            format += f"{hours} hour "
        else:
            format += f"{hours} hours "


    if minutes > 0:
        if minutes == 1:
            format += f"{minutes} minute "
        else:
            format += f"{minutes} minutes "

    if seconds > 0:
        if seconds == 1:
            format += f"{seconds} second "
        else:
            format += f"{seconds} second "

    return format


def compute_seconds(time):
    
    time_units = ['s', 'm', 'h', 'd']

    time_dict = {
        's' : 1,
        'm' : 60,
        'h' : 60 * 60,
        'd' : 60 * 60 * 24
    }

    time_unit = time[-1]

    if time_unit not in time_units:
        raise TimeException("Time must be either: `s`, `m`, `h` or `d`")

    try:
        actual_time = int(time[:-1])
    except:
        raise TimeException("Time must be an integer")

    return actual_time * time_dict[time_unit]


def is_staff(guild, user):
    
    try:

        member = guild.get_member(user.id) 
        
        if member.guild_permissions.administrator:
            return True
        
        settings_file = open_json("data/settings.json")
        
        guild_id = str(guild.id)

        staff_roles = settings_file[guild_id][Settings.staff_roles.value]

        for role_id in staff_roles:
            role = guild.get_role(role_id)

            if role in member.roles:
                return True

    except:
        return False

    return False

def get_prefix():
    json_file = open_json("data/config.json")
    return json_file["prefix"]


def get_urls(message):
    urls = re.findall("https?:\/\/\S+", message)
    return urls