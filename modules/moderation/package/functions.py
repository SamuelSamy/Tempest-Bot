import discord
import json
import time
import math
import asyncio

from discord import message

from modules.moderation.package.exceptions import *
from modules.moderation.package.enums import CaseFormat, ModFormat
from modules.package.enums import *

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


async def handle_case(bot, guild, channel, moderator, user, case_type, reason, duration):

    case_type = case_type.lower()
    reason = reason.strip()


    if not isinstance(duration, int):
        duration = compute_seconds(duration)

    if case_type not in ['warn', 'ban', 'kick', 'mute', 'unban', 'unmute']:
        raise TypeException("Invalid case type")
    
    json_file = open_json("data/moderation.json")

    try:
        guild_id = str(guild.id)
        user_id = str(user.id)
        moderator_id = str(moderator.id)
        case_id = int(json_file[guild_id][ModFormat.next_id.value])
        case = {
            CaseFormat.case_id.value: case_id,
            CaseFormat._type.value: case_type,
            CaseFormat.reason.value: reason,
            CaseFormat.time.value: round(time.time()),
            CaseFormat.duration.value: duration,
            CaseFormat.moderator.value: moderator_id
        }

        if user_id not in json_file[guild_id][ModFormat.logs.value].keys():
            json_file[guild_id][ModFormat.logs.value][user_id] = []

        json_file[guild_id][ModFormat.logs.value][user_id].append(case)
        

        if moderator_id not in json_file[guild_id][ModFormat.mod_logs.value].keys():
            json_file[guild_id][ModFormat.mod_logs.value][moderator_id] = []

        json_file[guild_id][ModFormat.mod_logs.value][moderator_id].append(case_id)

        json_file[guild_id][ModFormat.next_id.value] += 1


        if duration != 0:

            if case_type == 'ban':
                json_file[guild_id][ModFormat.temp_ban.value].append(case_id)
            elif case_type == 'mute':
                json_file[guild_id][ModFormat.temp_mute.value].append(case_id)


        save_json(json_file, "data/moderation.json")

        if channel is not None:
            await channel.send(embed = create_message(guild, case_type, reason, duration, user))
            
        await send_to_logs(bot, json_file, guild, case, user)
        
        try:
            await user.send(embed = create_message(guild, case_type, reason, duration))
        except:
            raise DMException("DMs closed")

    except:
        raise UnexpectedError("UnexpectedError occured when logging case")


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


async def handle_unban(guild, user, reason):

    member_was_unbanned = False
    banned_users = await guild.bans()

    for ban_entry in banned_users:
        banned_user = ban_entry.user

        if banned_user.id == user.id:
            await guild.unban(user, reason = reason)
            member_was_unbanned = True

    if not member_was_unbanned:
        raise MemberNotAffectedByModeration("This user is not banned from this server!")
    else:
        moderation_logs = open_json("data/moderation.json")

        guild_id = str(guild.id)
        user_id = str(user.id)

        if user_id in moderation_logs[guild_id].keys():
            for case in moderation_logs[guild_id][user_id]:
                if case[CaseFormat._type.value] == "ban" and case[CaseFormat.handled.value] == False and case[CaseFormat.duration.value] != 0:
                    case[CaseFormat.handled.value] = True
                    break
        
        save_json(moderation_logs, "data/moderation.json")


async def handle_purge(ctx, amount_of_messages, user):

    if user is None:
        deleted = await ctx.channel.purge(limit = amount_of_messages + 1)
    else:
        if user == ctx.author:
            amount_of_messages += 1

        deleted = await ctx.channel.purge(limit = amount_of_messages, check = lambda message: message.author == user)

    deleted = len(deleted) - 1 if (user is None or user == ctx.author) else 0
    message = ""

    if deleted > 0:
        message = f"Purged {deleted} message"

        if deleted > 1:
            message += "s"

        if user is not None:
            message += f" by {user.mention}"
    else:
        message = "No messages found to delete"

    embed = discord.Embed(
        color = Colors.green.value,
        description = message
    )

    embed.set_author(
        name = f"{ctx.author}",
        icon_url = ctx.author.avatar_url
    )
    
    purge_message = await ctx.channel.send(embed = embed)
    await asyncio.sleep(5)
    await purge_message.delete()



async def handle_slowmode(ctx, channel, slowmode_time):

    if channel is None:
        channel = ctx.channel

    seconds = compute_seconds(slowmode_time)
    seconds = min(seconds, 6 * 60 * 60)

    await channel.edit(slowmode_delay = seconds)
    
    if seconds != 0:
        message = f"Slowmode activated in <#{channel.id}>\nTime: {get_string_from_seconds(seconds)}"
    else:
        message = f"Slowmode disabled in <#{channel.id}>"

    await ctx.send(embed = discord.Embed(
        color = Colors.green.value,
        description = message
    ))



async def deletecase(guild, case_id):

    case_found = False

    json_file = open_json("data/moderation.json")

    users = json_file[str(guild.id)][ModFormat.logs.value]

    for user in users:

        if case_found: 
            break

        user_cases = json_file[str(guild.id)][ModFormat.logs.value][user]
        for case in user_cases:
            if case[CaseFormat.case_id.value] == case_id:
                case_found = True
                json_file[str(guild.id)][ModFormat.logs.value][user].remove(case)
                break

    if case_found:

        for moderator in json_file[str(guild.id)][ModFormat.mod_logs.value]:
            if case_id in json_file[str(guild.id)][ModFormat.mod_logs.value][moderator]:
                json_file[str(guild.id)][ModFormat.mod_logs.value][moderator].remove(case_id)
                break
            
        save_json(json_file, "data/moderation.json")
    else:
        raise CaseException("Case with the specified ID not found!")


async def mute(guild, user, reason):

    member = guild.get_member(user.id)

    settings = open_json("data/settings.json")
    muted_role = guild.get_role(settings[str(guild.id)][Settings.muted_role.value])

    await fix_mute_permissions(guild, muted_role)
    await member.add_roles(muted_role, reason = reason)



async def unmute(guild, user, resaon):
    
    member = guild.get_member(user.id)

    settings = open_json("data/settings.json")
    muted_role = guild.get_role(settings[str(guild.id)][Settings.muted_role.value])

    await member.remove_roles(muted_role, reason = resaon)

    moderation_logs = open_json("data/moderation.json")

    guild_id = str(guild.id)
    user_id = str(user.id)

    if user_id in moderation_logs[guild_id].keys():
        for case in moderation_logs[guild_id][user_id]:
            if case[CaseFormat._type.value] == "mute" and case[CaseFormat.handled.value] == False and case[CaseFormat.duration.value] != 0:
                case[CaseFormat.handled.value] = True
                break
    
    save_json(moderation_logs, "data/moderation.json")


async def fix_mute_permissions(guild, muted_role):
    channels = guild.text_channels
    for channel in channels:
        await channel.set_permissions(muted_role, send_messages = False)