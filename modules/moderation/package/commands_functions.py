import discord
import time
import asyncio
import sqlite3

from datetime import datetime

import modules.moderation.package.punish_functions as punish_funcs

from modules.package.exceptions import *
from modules.moderation.package.enums import ModFormat
from modules.package.enums import *
from modules.moderation.package.utility_functions import *
from modules.moderation.package.classes import Case

# General

async def handle_case(bot, guild, channel, moderator, user, case_type, reason, duration = 0, message = None, ctx = None):

    if user_in_guild(guild, user) or case_type == 'unban':

        if user.id == moderator.id:
            if ctx is not None:
                await ctx.reply(f"{Emotes.red_tick.value} You can not use that command on yourself!")
            else:
                await channel.send(f"{Emotes.red_tick.value} You can not use that command on yourself!")
        elif is_staff(guild, user):
            if ctx is not None:
                await ctx.reply(f"{Emotes.red_tick.value} You can not use that command on a staff member!")
            else:
                await channel.send(f"{Emotes.red_tick.value} You can not use that command on a staff member!")

        else:
            case_type = case_type.lower()
            reason = reason.strip()

            if not isinstance(duration, int):
                duration = compute_seconds(duration)

            if case_type not in ['warn', 'ban', 'kick', 'mute', 'unban', 'unmute']:
                raise CustomException(f"{Emotes.wrong.value} Invalid case type")

            guild_id = guild.id
            user_id = user.id
            moderator_id = moderator.id
            
            case = Case(
                None,
                guild_id,
                user_id,
                case_type,
                reason,
                round(time.time()),
                moderator_id,
                duration
            )

            insert_case(case)
            case.case_id = get_last_id()
            
            if ctx is not None:
                await ctx.reply(embed = create_message(guild, case_type, reason, duration, user, message))
            else:
                if channel is not None:
                    await channel.send(embed = create_message(guild, case_type, reason, duration, user, message))

            await send_to_logs(bot, case, message)
            
            if case_type != 'unban':

                try:
                    await user.send(embed = create_message(guild, case_type, reason, duration, _message = message))
                except:
                    pass

            
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
        raise CustomException(f"{Emotes.wrong.value} The specified user is not in this guild")


async def send_to_logs(bot, case, message = None):
    
    json_file = open_json("data/moderation.json")
    channel = bot.get_channel(int(json_file[str(case.guild)][ModFormat.mod_channel.value]))
    
    if channel is not None:

        user =  await bot.fetch_user(case.user)
    
        _color = Colors.red.value

        if case._type == "warn":
            _color = Colors.yellow.value
        elif case._type.startswith("un"):
            _color = Colors.green.value
    
        embed = discord.Embed(
            color = _color     
        )

        _type = case._type[0].upper() + case._type[1:]

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
            value = f"<@{case.moderator}>"
        )

        if case.reason != "":

            embed.add_field(
                name = "Reason",
                value = case.reason
            )

        if case.duration != 0:
            embed.add_field(
                name = "Duration",
                value = get_string_from_seconds(case.duration)
            )     

        if message is not None:
            embed.add_field(
                name = "Message",
                value = message
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
    
    purge_message = await ctx.reply(embed = embed)
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

    await ctx.reply(embed = discord.Embed(
        color = Colors.green.value,
        description = message
    ))



async def deletecase(guild, case_id):
    
    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(f"delete from {table} where ID = ? and guild = ?", (case_id, guild.id))
    deleted = cursor.rowcount
    connection.commit()
    connection.close()

    if deleted == 0:
        raise CustomException(f"{Emotes.wrong.value} Case with the specified ID not found!")


async def handle_mute(guild, user, reason):

    member = guild.get_member(user.id)

    settings = open_json("data/settings.json")
    muted_role = guild.get_role(settings[str(guild.id)][Settings.muted_role.value])

    if muted_role is None:
        raise CustomException(f"{Emotes.wrong.value} Mute role not found")

    if muted_role is not None and muted_role not in member.roles:
        raise CustomException(f"{Emotes.no_entry.value} <@{user.id}> is already muted!")


    await fix_mute_permissions(guild, muted_role)
    await member.add_roles(muted_role, reason = reason)


async def handle_unmute(guild, user, resaon):

    member = guild.get_member(user.id)

    settings = open_json("data/settings.json")
    muted_role = guild.get_role(settings[str(guild.id)][Settings.muted_role.value])

    if muted_role is None:
        raise CustomException(f"{Emotes.wrong.value} Mute role not found")

    if muted_role is not None and muted_role not in member.roles:
        raise CustomException(f"{Emotes.no_entry.value} <@{user.id}> is not muted!")

    await member.remove_roles(muted_role, reason = resaon)

    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(f"update {table} set expired = 1 where guild = ? and user = ? and type = 'mute' and duration != 0", (guild.id, user.id))
    connection.commit()
    connection.close()


async def handle_kick(guild, user, reason):
    member = guild.get_member(user.id)

    if member is not None:
        await member.kick(reason = reason)
  

async def handle_unban(guild, user, reason):

    member_was_unbanned = False
    banned_users = await guild.bans()

    for ban_entry in banned_users:
        banned_user = ban_entry.user

        if banned_user.id == user.id:
            await guild.unban(user, reason = reason)
            member_was_unbanned = True

    if not member_was_unbanned:
        raise CustomException(f"{Emotes.wrong.value} This user is not banned from this server!")
    else:
        
        path = "data/database.db"
        table = "moderation_cases"

        connection = sqlite3.connect(path)
        cursor = connection.cursor()
        cursor.execute(f"update {table} set expired = 1 where guild = ? and user = ? and type = 'ban' and duration != 0", (guild.id, user.id))
        connection.commit()
        connection.close()


async def handle_ban(guild, user, reason):
    member = guild.get_member(user.id)
    await member.ban(reason = reason)


async def fix_mute_permissions(guild, muted_role):
    channels = guild.text_channels
    for channel in channels:
        await channel.set_permissions(muted_role, send_messages = False)



def insert_case(case):
    
    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(f"insert into {table} values (?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, case.guild, case.user, case._type, case.reason, case.time, case.moderator, case.duration, 0))
    connection.commit()
    connection.close()


def get_last_id():
    
    path = "data/database.db"
    table = "moderation_cases"

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(f"select ID, max(ID) from {table}")
    last_id = cursor.fetchall()[0][0]
    connection.close()

    return last_id


def has_muted_role(guild, user):
    
    member = guild.get_member(user.id)

    settings = open_json("data/settings.json")
    muted_role = guild.get_role(settings[str(guild.id)][Settings.muted_role.value])
    
    if muted_role is None:
        raise CustomException(f"{Emotes.wrong.value} Mute role not found")

    return muted_role.id in [role.id for role in member.roles] 


async def generate_whois(ctx, user):
    
    
    if user is None:
        user = ctx.author

    guild = ctx.guild
    member = guild.get_member(user.id)

    if member is None:
        raise CustomException(f"{Emotes.not_found.value} The user is not in this server!")

    joined = round((member.joined_at - datetime(1970, 1, 1)).total_seconds()) 
    created = round((user.created_at - datetime(1970, 1, 1)).total_seconds())

    embed = discord.Embed(
        color = Colors.blue.value,
        description = f"<@{user.id}>"
    )

    embed.set_author(
        name = f"{member}", 
        icon_url = member.avatar_url
    )
    
    embed.add_field(
        name = 'Joined', 
        value = f"<t:{joined}> (<t:{joined}:R>)",    
        inline = False    
    )

    embed.add_field(
        name = 'Registered',
        value = f"<t:{created}> (<t:{created}:R>)",
        inline = False
    )

    embed.set_footer(
        text = f"ID: {user.id}"
    )

    roles = ""

    for role in member.roles:
        if str(role) != "@everyone":
            role = guild.get_role(role.id)
            roles += f"{role.mention} "

    if roles != "":
        embed.add_field(
            name = f"Roles [{len(member.roles) - 1}]",
            value = roles,
            inline = False
        )
    

    if member.premium_since is not None:
        boosting = round((member.premium_since - datetime(1970, 1, 1)).total_seconds())

        embed.add_field(
            name = "Nitro Booster since", 
            value = f"<t:{boosting}>",
            inline = False
        )
    

    await ctx.reply(embed = embed)
        