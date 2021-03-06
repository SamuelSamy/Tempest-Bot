import typing
import discord

from discord.ext import commands

import service.moderation.commands_functions as functions

from service._general.utils import get_prefix
from service._general.commands_checks import has_command_permissions, has_staff_role, is_admin
from domain.enums.moderation import Permissions
from domain.exceptions import CustomException
from domain.enums.general import Colors, Emotes


class Moderation(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    # LOGS
    @commands.command(
        usage = f"{get_prefix()}modlogs [user] (optional page)",
        description = "Displays the moderation logs of a user",
        brief = "0"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.mod_logs)
    async def modlogs(self, ctx, user : discord.User, page = 1):
        try:
            await ctx.reply(embed = functions.generate_modlogs(ctx.guild, user, page, False, False))
        except CustomException as error:
            await ctx.reply(error)


    # Warns
    @commands.command(
        usage = f"{get_prefix()}warns [user] (optional page)",
        description = "Displays a user's warnings",
        brief = "10"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.mod_logs)
    async def warns(self, ctx, user : discord.User, page = 1):
        try:
            await ctx.reply(embed = functions.generate_modlogs(ctx.guild, user, page, True, True))
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}mywarns (optional page)",
        description = "Get a DM with your warns. **You must have your DMs on!**",
        brief = "11"
    )
    @commands.guild_only()
    async def mywarns(self, ctx, page = 1):
        try:
            await ctx.author.send(embed = functions.generate_modlogs(ctx.guild, ctx.author, page, True, False))
            await ctx.message.delete()
        except CustomException as error:
            await ctx.author.send(error)


    # STATS
    @commands.command(
        usage = f"{get_prefix()}modstats [user]",
        description = "Displays a moderator stats",
        brief = "20"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.mod_stats)
    async def modstats(self, ctx, user : discord.User):
        try:
            await ctx.reply(embed = await functions.generate_modstats(ctx.guild, user, self.bot))
        except CustomException as error:
            await ctx.reply(error)


    # DELETE CASE
    @commands.command(
        usage = f"{get_prefix()}deletecase [case id]",
        description = "Deltes the specified case",
        brief = "30"
    )
    @commands.guild_only()
    @is_admin()
    async def deletecase(self, ctx, case_id : int):
        
        try:
            functions.deletecase(ctx.guild, case_id)

            await ctx.reply(embed = discord.Embed(
                color = Colors.green,
                description = f"Case {case_id} deleted!"
            ))

        except CustomException as error:
            await ctx.reply(error)


    # WARN
    @commands.command(
        usage = f"{get_prefix()}warn (times) [user] (optional reason)",
        description = "Warns the specified user\n> (times) must be a positive number or 0 (verbal warn).\n> If not specified times will be 1*",
        brief = "40"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.warn)
    async def warn(self, ctx, times: typing.Optional[int], user : discord.User, *, reason = ""):

        if times is None:
            times = 1

        if times < 0:
            raise commands.BadArgument
        
        else:
            try:
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'warn', reason, 0, ctx = ctx, weight = times)
            except CustomException as error:
                await ctx.reply(error)
        
    # KICK
    @commands.command(
        usage = f"{get_prefix()}kick [user] (optional reason)",
        description = "Kicks the specified user",
        brief = "60"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.kick)
    async def kick(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'kick', reason, 0, ctx = ctx)
        except CustomException as error:
            await ctx.reply(error)


    # BAN       
    @commands.command(
        usage = f"{get_prefix()}ban [user] (optioanl reason)",
        description = "Bans the specified user",
        brief = "70"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.ban)
    async def ban(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, 0, ctx = ctx)
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}tempban [user] [duration] (optioanl reason)",
        description = "Temporarily bans the specified user",
        brief = "80"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.ban)
    async def tempban(self, ctx, user : discord.User, duration, *, reason = ""):
    
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, duration, ctx = ctx)
        except CustomException as error:
            await ctx.reply(error)



    @commands.command(
        usage = f"{get_prefix()}unban [user] (optioanl reason)",
        description = "Removes the ban for specified user",
        brief = "90"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.ban)
    async def unban(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unban', reason, 0, ctx = ctx)
        except CustomException as error:
            await ctx.reply(error)

 
    # MUTE
    @commands.command(
        usage = f"{get_prefix()}mute [user] (optioanl reason)",
        description = "Mutes the specified user",
        brief = "100"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.mute)
    async def mute(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, 0, ctx = ctx)
        except CustomException as error:
            await ctx.reply(error)

        

    @commands.command(
        usage = f"{get_prefix()}tempmute [user] [duration] (optioanl reason)",
        description = "Temporarily mutes the specified user",
        brief = "110"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.mute)
    async def tempmute(self, ctx, user : discord.User, duration, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, duration, ctx = ctx)
        except CustomException as error:
            await ctx.reply(error)



    @commands.command(
        usage = f"{get_prefix()}unmute [user] (optioanl reason)",
        description = "Unmutes the specified user",
        brief = "120"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.mute)
    async def unmute(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unmute', reason, 0, ctx = ctx)
        except CustomException as error:
            await ctx.reply(error)


    # WHOIS
    @commands.command(
        usage = f"{get_prefix()}whois (user)",
        description = "Get information about a user",
        brief = "130"
    )
    @commands.guild_only()
    @has_staff_role()
    async def whois(self, ctx, user : typing.Optional[discord.User]):
        
        try:
            await functions.generate_whois(ctx, user)
        except CustomException as error:
            await ctx.reply(error)


    # SLOWMODE
    @commands.command(
         usage = f"{get_prefix()}slowmode (channel) [slowmode]",
        description = "Sets the slowmode of the specified channel. If no channel is specified the current channel will be affected",
        brief = "140"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.slowmode)
    async def slowmode(self, ctx, channel : typing.Optional[discord.TextChannel], slowmode_time):
        
        try:
            await functions.handle_slowmode(ctx, channel, slowmode_time)
        except CustomException as error:
            await ctx.reply(error)


    # PURGE
    @commands.command(
        usage = f"{get_prefix()}purge [amount of messages] (optioanl user)",
        description = "Deletes the messages in the current channel",
        brief = "150"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.purge)
    async def purge(self, ctx, amount_of_messages : int, user :  typing.Optional[discord.User]):   

        try:       
            await functions.handle_purge(ctx, amount_of_messages, user)
        except CustomException as error:
            await ctx.reply(error)


    # LOCK

    @commands.command(
        name = f"lock",
        usage = f"{get_prefix()}lock (optional channel) (optional reason)",
        description = "Prevents the `@everyone` role to send messages in a channel",
        brief = "160"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def lock(self, ctx, channel : typing.Optional[discord.TextChannel], *, reason = ""):   
        try:       
            await functions.lock_channel(ctx.guild, ctx, channel or ctx.channel, reason)
        except CustomException as error:
            await ctx.reply(error)

    @commands.command(
        name = f"unlock",
        usage = f"{get_prefix()}unlock (optional channel) (optional reason)",
        description = "Allows the `@everyone` role to send messages in a channel",
        brief = "170"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def unlock(self, ctx, channel : typing.Optional[discord.TextChannel], *, reason = ""):   
        try:       
            await functions.unlock_channel(ctx.guild, ctx, channel or ctx.channel, reason)
        except CustomException as error:
            await ctx.reply(error)


    # LCOKDOWN
    @commands.group(
        invoke_without_command = True
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def lockdown(self, ctx):
        pass


    @lockdown.command(
        name = f"enable",
        usage = f"{get_prefix()}lockdown enable (optional reason)",
        description = "Enable the lockdown",
        brief = "180"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def lockdown_enable(self, ctx, *, reason = ""):   
        try:       
            await functions.start_lockdown(ctx.guild, ctx, reason)
        except CustomException as error:
            await ctx.reply(error)



    @lockdown.command(
        name = f"disable",
        usage = f"{get_prefix()}lockdown disable (optional reason)",
        description = "Disable the lockdown",
        brief = "190"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def lockdown_disable(self, ctx, *, reason = ""):   
        try:       
            await functions.end_lockdown(ctx.guild, ctx, reason)
        except CustomException as error:
            await ctx.reply(error)


    @lockdown.command(
        name = f"add",
        usage = f"{get_prefix()}lockdown add [channel]",
        description = "Adds a channel to the lockdown list",
        brief = "200"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def lockdown_add(self, ctx, channel : discord.TextChannel):   
        try:       
            functions.add_lockdown_channel(ctx.guild, channel)
            await ctx.reply(f"{Emotes.green_tick} Successfully added <#{channel.id}> to the lockdown list")
        except CustomException as error:
            await ctx.reply(error)


    @lockdown.command(
        name = f"remove",
        usage = f"{get_prefix()}lockdown remove [channel]",
        description = "Removes a channel from the lockdown list",
        brief = "210"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def lockdown_remove(self, ctx, channel : discord.TextChannel):   
        try:       
            functions.remove_lockdown_channel(ctx.guild, channel or ctx.channel)
            await ctx.reply(f"{Emotes.green_tick} Successfully removed <#{channel.id}> from the lockdown list")
        except CustomException as error:
            await ctx.reply(error)


    @lockdown.command(
        name = f"list",
        usage = f"{get_prefix()}lockdown list",
        description = "Displays the lockdown channels",
        brief = "220"
    )
    @commands.guild_only()
    @has_command_permissions(command = Permissions.lock)
    async def lockdown_list(self, ctx):   
        try:       
            embed = functions.lockdown_list(ctx.guild)
            await ctx.reply(embed = embed)
        except CustomException as error:
            await ctx.reply(error)
    