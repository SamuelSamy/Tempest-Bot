import discord
import time
import math
import sqlite3

from modules.normal.package.enums import *
from modules.normal.moderation.package.enums import *
from modules.normal.package.exceptions import *
from modules.normal.package.utils import *
from modules.normal.moderation.package.classes import Case


def create_message(guild, case_type, reason, duration, user = None, _message = None):

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

    if _message is not None:
        message += f"\n**Message:** {_message}"

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

    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"select * from {table} where guild = ? and user = ? order by time desc", (guild.id, user.id))
    data = cursor.fetchall()
    connection.close()


    start_page = (page -1) * logs_per_page
    stop_page = min(start_page + logs_per_page, len(data))

    to_return_logs = []

    for i in range(start_page, stop_page):
        to_return_logs.append(
            Case(
                data[i]["ID"],
                data[i]["guild"],
                data[i]["user"],
                data[i]["type"],
                data[i]["reason"],
                data[i]["time"],
                data[i]["moderator"],
                data[i]["duration"]
            )
        )

    return (math.ceil(len(data) / logs_per_page), len(data), to_return_logs) if len(to_return_logs) != 0 else (0, 0, [])


def fetch_warns(guild, user, page):

    logs_per_page = 5

    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"select * from {table} where guild = ? and user = ? and type = 'warn' order by time desc", (guild.id, user.id))
    data = cursor.fetchall()
    connection.close()


    start_page = (page -1) * logs_per_page
    stop_page = min(start_page + logs_per_page, len(data))

    to_return_logs = []

    for i in range(start_page, stop_page):
        to_return_logs.append(
            Case(
                data[i]["ID"],
                data[i]["guild"],
                data[i]["user"],
                data[i]["type"],
                data[i]["reason"],
                data[i]["time"],
                data[i]["moderator"],
                data[i]["duration"]
            )
        )

    return (math.ceil(len(data) / logs_per_page), len(data), to_return_logs) if len(to_return_logs) != 0 else (0, 0, [])



def generate_modlogs(guild, user, page, warns_only = False):
    
    total_pages = 0
    total_logs = 0
    cases = []

    if warns_only:
        total_pages, total_logs, cases = fetch_warns(guild, user, page)
    else:
        total_pages, total_logs, cases = fetch_logs(guild, user, page)


    embed = discord.Embed()

    if len(cases) == 0:
        embed.color = Colors.red.value
        embed.description = "No logs found for this user!"

        embed.set_author(
            name = f"{user}",
            icon_url = user.display_avatar
        )

    else:
        embed.color = Colors.blue.value

        embed.set_author(
            name = f"{user}",
            icon_url = user.display_avatar
        )

        for case in cases:
            details = compute_case_details(case, display_mod = warns_only)
            

            embed.add_field(
                name = f"**Case {case.case_id}**",
                value = details,
                inline = False
            )
        
        embed.set_footer(
            text = f"Total logs: {total_logs}  |  Page {page} / {total_pages} "
        )

    return embed


def get_case_by_id(guild, case_id):
    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"select * from {table} where ID = ? and guild = ?", (case_id, guild.id))
    data = cursor.fetchall()[0]
    connection.close()

    return Case(
        data["ID"],
        data["guild"],
        data["user"],
        data["type"],
        data["reason"],
        data["time"],
        data["moderator"],
        data["duration"]
    )


async def generate_modstats(guild, user, bot):

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
    
    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute(f"select * from {table} where guild = ? and moderator = ?", (guild.id, user.id))
    data = cursor.fetchall()
    connection.close()

    if len(data) != 0:
        for entry in data:
            case = get_case_by_entry(entry)

            if not case._type.startswith('un'):

                if case.time < round(time.time()) + seven_days:
                    last_7_days[case._type] += 1
                
                if case.time < round(time.time()) + thirty_days:
                    last_30_days[case._type] += 1

                all_time[case._type] += 1
        
        
        
        embed = discord.Embed(
            color = Colors.blue.value,
            description = "**Moderation Stats**"
        )

        embed.set_author(
            name = user,
            icon_url = user.display_avatar
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


def compute_case_details(case, display_moderator):
    message = ""

    _type = case._type
    _type = str(_type[0].upper()) + _type[1:]

    message += f"**Type:** {_type}"

    if case.reason != "":
        message += f"\n**Reason:** {case.reason}"

    if case.duration != 0:
        message += f"\n**Duration:** {get_string_from_seconds(case.duration)}"

    if display_moderator:
        message += f"\n**Moderator:** <@{(case.moderator)}>"
    
    message += f"\n**Time:** <t:{(case.time)}> (<t:{(case.time)}:R>)"

    return message


def get_case_by_entry(entry):
    return Case(
        entry["ID"],
        entry["guild"],
        entry["user"],
        entry["type"],
        entry["reason"],
        entry["time"],
        entry["moderator"],
        entry["duration"]
    )


def mark_as_expired(case):
    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(f"update {table} set expired = 1 where ID = ?", (case.case_id,))
    connection.commit()
    connection.close()