import json
import re
from domain.config import Config

from domain.enums.general import Emotes
from domain.exceptions import CustomException
from repository.json_repo import SettingsRepo

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
        raise CustomException(f"{Emotes.wrong} Time must be either: `s`, `m`, `h` or `d`")

    try:
        actual_time = int(time[:-1])
    except:
        raise CustomException(f"{Emotes.wrong} Time must be an integer")

    return actual_time * time_dict[time_unit]


def is_staff(guild, user):
    
    try:

        member = guild.get_member(user.id) 

        if member.guild_permissions.administrator:
            return True
        
        settings_repo = SettingsRepo()
        staff_roles = settings_repo.get_staff_roles(guild.id)

        for role_id in staff_roles:
            role = guild.get_role(role_id)

            if role in member.roles:
                return True

        return False
    except:
        return False

   

def get_prefix():
    config = Config()
    return config.prefix


def get_urls(message):
    urls = re.findall("https?:\/\/\S+", message)
    return urls