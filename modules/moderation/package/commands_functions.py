import discord
import time
import asyncio

import modules.moderation.package.punish_functions as punish_funcs

from modules.moderation.package.exceptions import *
from modules.moderation.package.enums import CaseFormat, ModFormat
from modules.package.enums import *
from modules.moderation.package.utility_functions import *


# General

async def handle_case(bot, guild, channel, moderator, user, case_type, reason, duration):

    if user_in_guild(guild, user) or case_type == 'unban':
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
            
            if case_type != 'unban':
                try:
                    await user.send(embed = create_message(guild, case_type, reason, duration))
                except:
                    raise DMException("DMs closed")

        except:
            raise UnexpectedError("UnexpectedError occured when logging case")

        if case_type == 'warn':
            await punish_funcs.apply_punishments(bot, channel, guild, user)
        elif case_type == 'ban':
            await handle_ban(guild, user, reason)
        elif case_type == 'unban':
            await handle_unban(guild, user, reason)
        elif case_type == 'kick':
            await handle_kick(guild, user, reason)
        elif case_type == 'mute':
            await handle_mute(guild, user, reason)
        elif case_type == 'unmute':
            await handle_unmute(guild, user, reason)
    else:
        raise MmeberNotFoundException("The specified user is not in this guild")


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


async def handle_mute(guild, user, reason):

    member = guild.get_member(user.id)

    settings = open_json("data/settings.json")
    muted_role = guild.get_role(settings[str(guild.id)][Settings.muted_role.value])

    await fix_mute_permissions(guild, muted_role)
    await member.add_roles(muted_role, reason = reason)


async def handle_unmute(guild, user, resaon):
    
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


async def handle_kick(guild, user, reason):

    try:
        memeber = guild.get_member(user.id)
        await memeber.kick(reason = reason)
    except:
        raise ValueError("")


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


async def handle_ban(guild, user, reason):
    member = guild.get_member(user.id)
    await member.ban(reason = reason)


async def fix_mute_permissions(guild, muted_role):
    channels = guild.text_channels
    for channel in channels:
        await channel.set_permissions(muted_role, send_messages = False)