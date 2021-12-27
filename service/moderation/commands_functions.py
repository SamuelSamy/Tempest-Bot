import discord
import time
import asyncio

from datetime import datetime
from discord import channel

from discord.channel import CategoryChannel

from repository.database_repo import DatabaseRepository
from repository.json_repo import ModerationRepo

import service.moderation.punish_functions as punish_funcs

from service._general.utils import *
from domain.exceptions import CustomException
from domain.enums.general import Emotes
from service.moderation.utility_functions import *
from domain.case import Case

# General

async def handle_case(bot, guild, channel, moderator, user, case_type, reason, duration = 0, message = None, ctx = None):

    if user_in_guild(guild, user) or case_type == 'unban':

        if user.id == moderator.id:
            if ctx is not None:
                await ctx.reply(f"{Emotes.red_tick} You can not use that command on yourself!")
            else:
                await channel.send(f"{Emotes.red_tick} You can not use that command on yourself!")
        elif not is_staff(guild, moderator):
            if ctx is not None:
                await ctx.reply(f"{Emotes.red_tick} You can not use that command on a staff member!")
            else:
                await channel.send(f"{Emotes.red_tick} You can not use that command on a staff member!")

        else:
            case_type = case_type.lower()
            reason = reason.strip()

            if not isinstance(duration, int):
                duration = compute_seconds(duration)

            if case_type not in ['warn', 'ban', 'kick', 'mute', 'unban', 'unmute']:
                raise CustomException(f"{Emotes.wrong} Invalid case type")

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
        raise CustomException(f"{Emotes.wrong} The specified user is not in this guild")


async def send_to_logs(bot, case, message = None):
    
    moderation_repo = ModerationRepo()
    channel_id = moderation_repo.get_mod_logs_channel(case.guild)
    channel = bot.get_channel(int(channel_id))
    
    if channel is not None:

        user =  await bot.fetch_user(case.user)
    
        _color = Colors.red

        if case._type == "warn":
            _color = Colors.yellow
        elif case._type.startswith("un"):
            _color = Colors.green
    
        embed = discord.Embed(
            color = _color     
        )

        _type = case._type[0].upper() + case._type[1:]

        embed.set_author(
            name = f"[{_type}]  {user}",
            icon_url = user.display_avatar
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
            message += f" sent by {user.mention}"
    else:
        message = "No messages found to delete"

    purge_message = await ctx.send(f"{Emotes.green_tick} {message}")
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
        color = Colors.green,
        description = message
    ))



def deletecase(guild, case_id):
    
    database_repo = DatabaseRepository()
    deleted = database_repo.delete(
        sql_statement = "delete from moderation_cases where ID = ? and guild = ?", 
        args = (case_id, guild.id)
    )

    if deleted == 0:
        raise CustomException(f"{Emotes.wrong} Case with the specified ID not found!")


async def handle_mute(guild, user, reason):

    member = guild.get_member(user.id)

    if has_muted_role(guild, user):
        raise CustomException(f"{Emotes.no_entry} <@{user.id}> is already muted!")


    settings_repo = SettingsRepo()
    muted_role = guild.get_role(int(settings_repo.get_muted_role(guild.id)))
    await fix_mute_permissions(guild, muted_role)
    await member.add_roles(muted_role, reason = reason)


async def handle_unmute(guild, user, resaon):

    member = guild.get_member(user.id)
  
    if not has_muted_role(guild, user):
        raise CustomException(f"{Emotes.no_entry} <@{user.id}> is not muted!")

    settings_repo = SettingsRepo()
    muted_role = guild.get_role(int(settings_repo.get_muted_role(guild.id)))

    await member.remove_roles(muted_role, reason = resaon)

    database_repo = DatabaseRepository()
    database_repo.general_statement(
        sql_statement = "update moderation_cases set expired = 1 where guild = ? and user = ? and type = 'mute'", 
        args = (guild.id, user.id)
    )


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
        raise CustomException(f"{Emotes.wrong} <@{user.id}> is not banned from this server!")
    else:
        
        database_repo = DatabaseRepository()
        database_repo.general_statement(
            sql_statement = "update moderation_cases set expired = 1 where guild = ? and user = ? and type = 'ban'", 
            args = (guild.id, user.id)
        )


async def handle_ban(guild, user, reason):
    member = guild.get_member(user.id)
    await member.ban(reason = reason)


async def fix_mute_permissions(guild, muted_role):
    channels = guild.text_channels
    for channel in channels:
        await channel.set_permissions(muted_role, send_messages = False)



def insert_case(case):
    
    database_repo = DatabaseRepository()
    database_repo.general_statement(
        sql_statement = "insert into moderation_cases values (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        args = (None, case.guild, case.user, case._type, case.reason, case.time, case.moderator, case.duration, 0)
    )


def get_last_id():
    
    database_repo = DatabaseRepository()
    data = database_repo.select(
        sql_statement = "select ID, max(ID) from moderation_cases"
    )

    return data[0]["ID"] # last_id



def has_muted_role(guild, user):
    
    member = guild.get_member(user.id)

    settings_repo = SettingsRepo()
    muted_role = guild.get_role(int(settings_repo.get_muted_role(guild.id)))
    
    if muted_role is None:
        raise CustomException(f"{Emotes.wrong} Mute role not found")

    return muted_role.id in [role.id for role in member.roles] 


async def generate_whois(ctx, user):
    
    
    if user is None:
        user = ctx.author

    guild = ctx.guild
    member = guild.get_member(user.id)

    if member is None:
        raise CustomException(f"{Emotes.not_found} The user is not in this server!")

    joined = round((member.joined_at.replace(tzinfo = None) - datetime(1970, 1, 1)).total_seconds()) 
    created = round((user.created_at.replace(tzinfo = None) - datetime(1970, 1, 1)).total_seconds())

    embed = discord.Embed(
        color = Colors.blue,
        description = f"<@{user.id}>"
    )

    embed.set_author(
        name = f"{member}", 
        icon_url = member.display_avatar
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


async def lock_channel(guild, ctx, channel, reason, send_system_message = True):
    
    everyone_role = guild.roles[0]

    permissions = channel.overwrites_for(everyone_role)

    if permissions.pair()[1].value & (1 << 11):  # the @everyone role does not have permissions to send messages in this channel
        if send_system_message:
            if ctx.channel != channel:
                await ctx.reply(f"{Emotes.wrong} <#{channel.id}> is already locked!")
            else:
                await ctx.reply(f"{Emotes.wrong} This channel is already locked!")

    else:  # @everyone has permissions to send messages in this channel
        permissions.update(send_messages = False)
        await channel.set_permissions(everyone_role, overwrite = permissions)

        embed = discord.Embed(
            title = f"{Emotes.closed_lock} Channel Locked", 
            color = Colors.red
        )

        if reason != "":
            embed.description = reason

        await channel.send(embed = embed)

        if channel != ctx.channel and send_system_message:
            await ctx.reply(f"{Emotes.green_tick} <#{channel.id}> is now locked!")


async def unlock_channel(guild, ctx, channel, reason, send_system_message = True):

    everyone_role = guild.roles[0]

    permissions = channel.overwrites_for(everyone_role)

    if permissions.pair()[1].value & (1 << 11):  # the @everyone role does not have permissions to send messages in this channel
        permissions.update(send_messages = True)
        await channel.set_permissions(everyone_role, overwrite = permissions)

        embed = discord.Embed(
            title = f"{Emotes.open_lock} Channel Unlocked", 
            color = Colors.green
        )

        if reason != "":
            embed.description = reason

        await channel.send(embed = embed)

        if channel != ctx.channel and send_system_message:
            await ctx.reply(f"{Emotes.green_tick} <#{channel.id}> is no longer locked!")
        
           
    else:  # @everyone has permissions to send messages in this channel
        if send_system_message:
            if channel != ctx.channel:
                await ctx.reply(f"{Emotes.wrong} <#{channel.id}> is not locked!")
            else:
                await ctx.reply(f"{Emotes.wrong} This channel is not locked!")


async def start_lockdown(guild, ctx, reason):

    settings_repo = SettingsRepo()
    channels = settings_repo.get_lockdown_channels(guild.id)

    if len(channels):
        channels_count = 0
        initial_message = await ctx.reply(f"{Emotes.loading} Locking channels ({channels_count}/{len(channels)})")
        
        for channel_id in channels:
            channel = guild.get_channel(channel_id)
            await lock_channel(guild, ctx, channel, reason, send_system_message = False)
            channels_count += 1
            await initial_message.edit(f"{Emotes.loading} Locking channels ({channels_count}/{len(channels)})")
        
        await initial_message.edit(f"{Emotes.green_tick} {channels_count} channels locked!")
    else:
        await ctx.reply(f"{Emotes.no_entry} There are no lockdown channels!\nUse `{get_prefix()}lockdown add [channel]` in order to add a channel")


async def end_lockdown(guild, ctx, reason):
    settings_repo = SettingsRepo()
    channels = settings_repo.get_lockdown_channels(guild.id)

    if len(channels) != 0:
        channels_count = 0
        initial_message = await ctx.reply(f"{Emotes.loading} Unlocking channels ({channels_count}/{len(channels)})")
        
        for channel_id in channels:
            channel = guild.get_channel(channel_id)

            await unlock_channel(guild, ctx, channel, reason, send_system_message = False)
            channels_count += 1
            await initial_message.edit(f"{Emotes.loading} Unlocking channels ({channels_count}/{len(channels)})")
        
        await initial_message.edit(f"{Emotes.green_tick} {channels_count} channels unlocked!")
    else:
        await ctx.reply(f"{Emotes.no_entry} There are no lockdown channels!\nUse `{get_prefix()}lockdown add [channel]` in order to add a channel")


def add_lockdown_channel(guild, channel):
    settings_repo = SettingsRepo()
    settings_repo.add_lockdown_channel(guild.id, channel.id)


def remove_lockdown_channel(guild, channel):
    settings_repo = SettingsRepo()
    settings_repo.remove_lockdown_channel(guild.id, channel.id)



def lockdown_list(guild):
    settings_repo = SettingsRepo()
    channels = settings_repo.get_lockdown_channels(guild.id)

    embed = discord.Embed(
        title = "Lockdown channels",
        color = Colors.blue
    )

    if len(channels) != 0:
        description = ""
        
        channels_per_line = 3
        channels_count = 0


        for channel_id in channels:
            description += f"<#{channel_id}> "
            channels_count += 1

            if channels_count % channels_per_line == 0:
                description += "\n"
        
        embed.description = description
    else:
        embed.description = "There are no lockdown channels!\nUse `{get_prefix()}lockdown add [channel]` in order to add a channel"

    return embed