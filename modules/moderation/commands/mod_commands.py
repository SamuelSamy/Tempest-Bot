import typing
import discord

from discord.ext import commands
from discord.ext.commands.core import check
from modules.moderation.package.enums import Permissions

from modules.package.enums import *
from modules.package.exceptions import *
from modules.package.commands_checks import *

import modules.moderation.package.commands_functions as functions
import modules.moderation.package.utility_functions as utils

class Moderation(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    # LOGS
    @commands.command(
        usage = f"{get_prefix()}modlogs [user] (optional page)",
        description = "Displays the moderation logs of a user"
    )
    @has_command_permissions(command = Permissions.mod_logs.value)
    async def modlogs(self, ctx, user : discord.User, page = 1):
        await ctx.send(embed = functions.generate_modlogs(ctx.guild, user, page))


    # Warns
    @commands.command(
        usage = f"{get_prefix()}warns [user] (optional page)",
        description = "Displays a user's warnings"
    )
    @has_command_permissions(command = Permissions.mod_logs.value)
    async def warns(self, ctx, user : discord.User, page = 1):
        await ctx.send(embed = functions.generate_modlogs(ctx.guild, user, page, True))

    # STATS
    @commands.command(
        usage = f"{get_prefix()}modstats [user]",
        description = "Displays a moderator stats"
    )
    @has_command_permissions(command = Permissions.mod_stats.value)
    async def modstats(self, ctx, user : discord.User):
        await ctx.send(embed = await functions.generate_modstats(ctx.guild, user, self.bot))


    # DELETE CASE
    @commands.command(
        usage = f"{get_prefix()}deletecase [case id]",
        description = "Deltes the specified case"
    )
    @commands.has_permissions(administrator = True)
    async def deletecase(self, ctx, case_id : int):
        
        try:
            await functions.deletecase(ctx.guild, case_id)

            await ctx.channel.send(embed = discord.Embed(
                color = Colors.green.value,
                description = f"Case {case_id} deleted!"
            ))

        except CaseException as error:
            await ctx.send(error)


    # WARN
    @commands.command(
        usage = f"{get_prefix()}warn [user] (optional reason)",
        description = "Warns the specified user"
    )
    @has_command_permissions(command = Permissions.warn.value)
    async def warn(self, ctx, user : discord.User, *, reason = ""):

        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'warn', reason, 0)
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)


    # KICK
    @commands.command(
        usage = f"{get_prefix()}kick [user] (optional reason)",
        description = "Kicks the specified user"
    )
    @has_command_permissions(command = Permissions.kick.value)
    async def kick(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'kick', reason, 0)
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)


    # BAN       
    @commands.command(
        usage = f"{get_prefix()}ban [user] (optioanl reason)",
        description = "Bans the specified user"
    )
    @has_command_permissions(command = Permissions.ban.value)
    async def ban(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, 0)
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)


    @commands.command(
        usage = f"{get_prefix()}tempban [user] [duration] (optioanl reason)",
        description = "Temporarily bans the specified user"
    )
    @has_command_permissions(command = Permissions.ban.value)
    async def tempban(self, ctx, user : discord.User, duration, *, reason = ""):
    
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, duration)
        except DMException:
            pass
        except TimeException as error:
            await ctx.send(error)
        except MmeberNotFoundException as error:
            await ctx.send(error)



    @commands.command(
        usage = f"{get_prefix()}unban [user] (optioanl reason)",
        description = "Removes the ban for specified user"
    )
    @has_command_permissions(command = Permissions.ban.value)
    async def unban(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unban', reason, 0)
        except DMException:
            pass
        except MemberNotAffectedByModeration as error:
            await ctx.send(error)



    # MUTE
    @commands.command(
        usage = f"{get_prefix()}mute [user] (optioanl reason)",
        description = "Mutes the specified user"
    )
    @has_command_permissions(command = Permissions.mute.value)
    async def mute(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, 0)
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        

    @commands.command(
        usage = f"{get_prefix()}tempmute [user] [duration] (optioanl reason)",
        description = "Temporarily mutes the specified user"
    )
    @has_command_permissions(command = Permissions.mute.value)
    async def tempmute(self, ctx, user : discord.User, duration, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, duration)
        except DMException:
            pass
        except TimeException as error:
            await ctx.send(error)
        except MmeberNotFoundException as error:
                await ctx.send(error)



    @commands.command(
        usage = f"{get_prefix()}unmute [user] (optioanl reason)",
        description = "Unmutes the specified user"
    )
    @has_command_permissions(command = Permissions.mute.value)
    async def unmute(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unmute', reason, 0)
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)


    # PURGE
    @commands.command(
        usage = f"{get_prefix()}purge [amount of messages] (optioanl user)",
        description = "Deletes the messages in the current channel"
    )
    @has_command_permissions(command = Permissions.purge.value)
    async def purge(self, ctx, amount_of_messages : int, user :  typing.Optional[discord.User]):            
        await functions.handle_purge(ctx, amount_of_messages, user)
    

    # SLOWMODE
    @commands.command(
         usage = f"{get_prefix()}slowmode (channel) [slowmode]",
        description = "Sets the slowmode of the specified channel. If no channel is specified the current channel will be affected"
    )
    @has_command_permissions(command = Permissions.slowmode.value)
    async def slowmode(self, ctx, channel : typing.Optional[discord.TextChannel], slowmode_time):
        
        try:
            await functions.handle_slowmode(ctx, channel, slowmode_time)
        except TimeException as error:
            await ctx.send(error)


def setup(bot):
    bot.add_cog(Moderation(bot))