import json
import discord
import time
import math

from modules.package.enums import *
from modules.moderation.package.enums import *
from modules.moderation.package.exceptions import *


def open_json(file_path):

    with open(file_path) as file:
        json_file = json.load(file)
        file.close()

    return json_file


def save_json(json_file, file_path):

    with open(file_path, "w") as f:
        json.dump(json_file, f)


def user_in_guild(guild, user):
    return (guild.get_member(user.id) is not None)


def create_message(guild, case_type, reason, duration, user = None):

    _color = Colors.red.value
    message = f"You have been **"
    
    if user is not None:
        message = f"{user.mention} has been **"


    if case_type == "warn":
        message += f"warned"
        _color = Colors.yellow.value
    elif case_type == "ban":
        message += f"banned"
    elif case_type == "mute":
        message += f"muted"
    elif case_type == "kick":
        message += f"kicked"
    elif case_type == "unmute":
        message += f"unmuted"
        _color = Colors.green.value
    elif case_type == "unban":
        message += f"unbanned"
        _color = Colors.green.value
    
    message += "**"

    if user is None:

        if case_type in ["kick", "banned", "unbanned"]:
            message += f" from `{guild.name}`"
        else:
            message += f" in `{guild.name}`"


    if reason != "":
        message += f"\n**Reason:** {reason}"

    if duration != 0:

        if case_type == "ban":
            if user is None:
                message += f"\nYour ban "
            else:
                message += f"\nThe ban "
        elif case_type == "mute":
            if user is None:
                message += f"\nYour mute "
            else:
                message += f"\nThe mute "

        message += f"will expire at <t:{round(time.time() + duration)}>"

    
    embed = discord.Embed(
        color = _color,
        description = message
    )

    return embed


def fetch_logs(guild, user, page):

    logs_per_page = 5

    json_file = open_json("data/moderation.json")
    
    guild_id = str(guild.id)

    if str(user.id) in json_file[guild_id][ModFormat.logs.value].keys():
        logs = json_file[guild_id][ModFormat.logs.value][str(user.id)]
        logs.reverse()


        start_page = (page -1) * logs_per_page
        stop_page = min(start_page + logs_per_page, len(logs))

        to_return_logs = []

        for i in range(start_page, stop_page):
            to_return_logs.append(logs[i])


        return math.ceil(len(logs) / logs_per_page), len(logs), to_return_logs
    else:
        return 0, 0, []


def fetch_warns(guild, user, page):

    logs_per_page = 5

    json_file = open_json("data/moderation.json")
    
    guild_id = str(guild.id)

    if str(user.id) in json_file[guild_id][ModFormat.logs.value].keys():
        
        logs = json_file[guild_id][ModFormat.logs.value][str(user.id)]

        i = 0
        
        while i < len(logs):
            
            if logs[i][CaseFormat._type.value] != 'warn':
                del logs[i]
                i -= 1
            
            i += 1
        
        logs.reverse()

        start_page = (page -1) * logs_per_page
        stop_page = min(start_page + logs_per_page, len(logs))

        to_return_logs = []

        for i in range(start_page, stop_page):
            to_return_logs.append(logs[i])


        return math.ceil(len(logs) / logs_per_page), len(logs), to_return_logs
    else:
        return 0, 0, []


def generate_modlogs(guild, user, page, warns_only = False):
    
    total_pages = 0
    total_logs = 0
    modlogs = []

    if warns_only:
        total_pages, total_logs, modlogs = fetch_warns(guild, user, page)
    else:
        total_pages, total_logs, modlogs = fetch_logs(guild, user, page)


    embed = discord.Embed()

    if len(modlogs) == 0:
        embed.color = Colors.red.value
        embed.description = "No logs found for this user!"

        embed.set_author(
            name = f"{user}",
            icon_url = user.avatar_url
        )

    else:
        embed.color = Colors.blue.value

        embed.set_author(
            name = f"{user}",
            icon_url = user.avatar_url
        )

        for log in modlogs:
            details = compute_case_details(log)
            

            embed.add_field(
                name = f"**Case {log[CaseFormat.case_id.value]}**",
                value = details,
                inline = False
            )
        
        embed.set_footer(
            text = f"Total logs: {total_logs}  |  Page {page} / {total_pages} "
        )

    return embed


async def get_case_and_user_by_id(guild, case_id, bot):
    json_file = open_json("data/moderation.json")
    
    users = json_file[str(guild.id)][ModFormat.logs.value]

    for user_id in users:
        user_cases = json_file[str(guild.id)][ModFormat.logs.value][user_id]
        for case in user_cases:
            if case[CaseFormat.case_id.value] == case_id:
                return case, await bot.fetch_user(int(user_id))

    return None
 

async def generate_modstats(guild, user, bot):

    json_file = open_json("data/moderation.json")

    seven_days  =  7 * 24 * 60 * 60
    thirty_days = 30 * 24 * 60 * 60

    last_7_days = {
        "ban": 0,
        "kick": 0,
        "mute": 0,
        "warn": 0
    }

    last_30_days = {
        "ban": 0,
        "kick": 0,
        "mute": 0,
        "warn": 0
    }

    all_time = {
        "ban": 0,
        "kick": 0,
        "mute": 0,
        "warn": 0
    }
    
    if str(user.id) in json_file[str(guild.id)][ModFormat.mod_logs.value].keys():
        
        for case_id in json_file[str(guild.id)][ModFormat.mod_logs.value][str(user.id)]:
            case, _ = await get_case_and_user_by_id(guild, case_id, bot)
            
            if case is not None and case[CaseFormat._type.value] in all_time.keys():

                if case[CaseFormat.time.value] < round(time.time()) + seven_days:
                    last_7_days[case[CaseFormat._type.value]] += 1
                
                if case[CaseFormat.time.value] < round(time.time()) + thirty_days:
                    last_30_days[case[CaseFormat._type.value]] += 1

                all_time[case[CaseFormat._type.value]] += 1


        embed = discord.Embed(
            color = Colors.blue.value,
            description = "**Moderation Stats**"
        )

        embed.set_author(
            name = user,
            icon_url = user.avatar_url
        )

        total = "Total:"
        bans = "Bans:"
        kicks = "Kicks:"
        mutes = "Mutes:"
        warns = "Warns:"

        embed.add_field(
            name = "**__Last 7 days__**",
            value = f"**{total:7s}** {str(count_total(last_7_days)):8s}\n**{bans:7s}** {str(last_7_days['ban']):8s}\n**{kicks:7s}** {str(last_7_days['kick']):8s}\n**{mutes:7s}** {str(last_7_days['mute']):8s}\n**{warns:7s}** {str(last_7_days['warn']):8s}"
        )

        embed.add_field(
            name = "**__Last 30 days__**",
            value = f"**{total:7s}** {str(count_total(last_30_days)):8s}\n**{bans:7s}** {str(last_30_days['ban']):8s}\n**{kicks:7s}** {str(last_30_days['kick']):8s}\n**{mutes:7s}** {str(last_30_days['mute']):8s}\n**{warns:7s}** {str(last_30_days['warn']):8s}"
        )

        embed.add_field(
            name = "**__All time__**",
            value = f"**{total:7s}** {str(count_total(all_time)):8s}\n**{bans:7s}** {str(all_time['ban']):8s}\n**{kicks:7s}** {str(all_time['kick']):8s}\n**{mutes:7s}** {str(all_time['mute']):8s}\n**{warns:7s}** {str(all_time['warn']):8s}"
        )


    else:
        embed = discord.Embed(
            color = Colors.red.value,
            description = f"<@{user.id}> is not a moderator or has no stats to show!"
        )

    return embed


def count_total(dict):
    total = 0
    for value in dict.values():
        total += value
    return total


def compute_case_details(case):
    message = ""

    _type = case[CaseFormat._type.value]
    _type = str(_type[0].upper()) + _type[1:]

    message += f"**Type:** {_type}"

    if case[CaseFormat.reason.value] != "":
        message += f"\n**Reason:** {case[CaseFormat.reason.value]}"

    if case[CaseFormat.duration.value] != 0:
        message += f"\n**Duration:** {get_string_from_seconds(case[CaseFormat.duration.value])}"

    message += f"\n**Moderator:** <@{(case[CaseFormat.moderator.value])}>"
    message += f"\n**Time:** <t:{(case[CaseFormat.time.value])}> (<t:{(case[CaseFormat.time.value])}:R>)"

    return message


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