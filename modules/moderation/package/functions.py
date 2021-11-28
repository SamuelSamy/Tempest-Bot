import discord
import json
import time
import math

from modules.moderation.package.exceptions import *
from modules.moderation.package.enums import CaseFormat, ModFormat
from modules.package.colors import Colors

# General

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


async def handle_case(bot, ctx, user, case_type, reason, duration):

    case_type = case_type.lower()
    reason = reason.strip()

    guild = ctx.guild
    respond_channel = ctx.channel
    moderator = ctx.author

    if not isinstance(duration, int):
        duration = compute_seconds(duration)

    if case_type not in ['warn', 'ban', 'kick', 'mute', 'unban', 'unmute']:
        raise TypeException("Invalid case type")
    
    json_file = open_json("data/moderation.json")

    # try:
    guild_id = str(guild.id)
    user_id = str(user.id)
    moderator_id = str(moderator.id)

    case = {
        CaseFormat.case_id.value: int(json_file[guild_id][ModFormat.next_id.value]),
        CaseFormat._type.value: case_type,
        CaseFormat.reason.value: reason,
        CaseFormat.time.value: round(time.time()),
        CaseFormat.duration.value: duration,
        CaseFormat.moderator.value: moderator_id
    }

    if user_id not in json_file[guild_id][ModFormat.logs.value].keys():
        json_file[guild_id][ModFormat.logs.value][user_id] = []

    json_file[guild_id][ModFormat.logs.value][user_id].append(case)
    json_file[guild_id][ModFormat.next_id.value] += 1

    save_json(json_file, "data/moderation.json")

    await respond_channel.send(embed = create_message(guild, case_type, reason, duration, user))
    await send_to_logs(bot, json_file, guild, case, user)
    
    try:
        await user.send(embed = create_message(guild, case_type, reason, duration))
    except:
        raise DMException("DMs closed")
    # except:
    #     raise UnexpectedError("UnexpectedError occured when logging case")


async def send_to_logs(bot, json_file, guild, case, user):
    
    guild_id = str(guild.id)
    channel = bot.get_channel(int(json_file[guild_id][ModFormat.channel.value]))
    moderator_id = case[CaseFormat.moderator.value]

    _color = Colors.red.value

    if case[CaseFormat._type.value] == "warn":
        _color = Colors.yellow.value
    elif case[CaseFormat._type.value].startswith("un"):
        _color = Colors.green.value
   
    embed = discord.Embed(
        color = _color     
    )

    _type = case[CaseFormat._type.value][0].upper() + case[CaseFormat._type.value][1:]

    embed.set_author(
        name = f"[{_type}]  {user}",
        icon_url = user.avatar_url
    )

    embed.add_field(
        name = "User",
        value = f"<@{user.id}>"
    )

    embed.add_field(
        name = "Moderator",
        value = f"<@{moderator_id}>"
    )

    if case[CaseFormat.reason.value] != "":

        embed.add_field(
            name = "Reason",
            value = case[CaseFormat.reason.value]
        )

    if case[CaseFormat.duration.value] != 0:
        embed.add_field(
            name = "Duration",
            value = get_string_from_seconds(case[CaseFormat.duration.value])
        )          

    await channel.send(embed = embed)


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

    logs = json_file[guild_id][ModFormat.logs.value][str(user.id)]
    logs.reverse()


    start_page = (page -1) * logs_per_page
    stop_page = min(start_page + logs_per_page, len(logs))

    to_return_logs = []

    for i in range(start_page, stop_page):
        to_return_logs.append(logs[i])


    return math.ceil(len(logs) / logs_per_page), len(logs), to_return_logs


def generate_modlogs(guild, user, page):

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


async def handle_unban(ctx, user, reason):

    guild = ctx.guild
    member_was_unbanned = False
    banned_users = await guild.bans()

    for ban_entry in banned_users:
        banned_user = ban_entry.user

        if banned_user.id == user.id:
            await guild.unban(user, reason = reason)
            member_was_unbanned = True

    if not member_was_unbanned:
        raise MemberNotAffectedByModeration("This user is not banned from this server!")
