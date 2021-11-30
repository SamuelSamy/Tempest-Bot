import typing
import discord

from discord.ext import commands
from modules.moderation.package.enums import Permissions

from modules.package.enums import *
from modules.package.exceptions import *
import modules.moderation.package.commands_functions as functions
import modules.moderation.package.utility_functions as utils

class ModerationGeneralCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    # LOGS
    @commands.command()
    async def modlogs(self, ctx, user : discord.User, page = 1):

        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.mod_logs.value):
                await ctx.send(embed = functions.generate_modlogs(ctx.guild, user, page))
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except:
            await ctx.send("Something went wrong...")

    # Warns
    @commands.command()
    async def warns(self, ctx, user : discord.User, page = 1):

        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.mod_logs.value):
                await ctx.send(embed = functions.generate_modlogs(ctx.guild, user, page, True))
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")       
        except:
            await ctx.send("Something went wrong...")


    # STATS
    @commands.command()
    async def modstats(self, ctx, user : discord.User):

        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.mod_stats.value):
                await ctx.send(embed = await functions.generate_modstats(ctx.guild, user, self.bot))
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")   
        except:
            await ctx.send("Something went wrong...")


    # DELETE CASE
    @commands.command()
    async def deletecase(self, ctx, case_id : int):
        
        try:

            if ctx.author.guild_permissions.administrator:
                await functions.deletecase(ctx.guild, case_id)

                await ctx.channel.send(embed = discord.Embed(
                    color = Colors.green.value,
                    description = f"Case {case_id} deleted!"
                ))
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")

        except CaseException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    # WARN
    @commands.command()
    async def warn(self, ctx, user : discord.User, *, reason = ""):

        try:

            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.warn.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'warn', reason, 0)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")

        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    # KICK
    @commands.command()
    async def kick(self, ctx, user : discord.User, *, reason = ""):
        
        try:

            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.kick.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'kick', reason, 0)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")

        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    # BAN       
    @commands.command()
    async def ban(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.ban.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, 0)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    @commands.command()
    async def tempban(self, ctx, user : discord.User, duration, *, reason = ""):
    
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.ban.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, duration)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except DMException:
            pass
        except TimeException as error:
            await ctx.send(error)
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    @commands.command()
    async def unban(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.ban.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unban', reason, 0)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except DMException:
            pass
        except MemberNotAffectedByModeration as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    # MUTE
    @commands.command()
    async def mute(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.mute.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, 0)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")
        

    @commands.command()
    async def tempmute(self, ctx, user : discord.User, duration, *, reason = ""):
        
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.mute.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, duration)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except DMException:
            pass
        except TimeException as error:
            await ctx.send(error)
        except MmeberNotFoundException as error:
                await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")



    @commands.command()
    async def unmute(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.mute.value):
                await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unmute', reason, 0)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    # PURGE
    @commands.command()
    async def purge(self, ctx, amount_of_messages : int, user :  typing.Optional[discord.User]):
            
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.purge.value):
                await functions.handle_purge(ctx, amount_of_messages, user)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except:
            await ctx.send("Something went wrong...")
    

    # SLOWMODE
    @commands.command()
    async def slowmode(self, ctx, channel : typing.Optional[discord.TextChannel], slowmode_time):
            
        try:
            if utils.has_permissions_to_use_command(ctx.guild, ctx.author, Permissions.slowmode.value):
                await functions.handle_slowmode(ctx, channel, slowmode_time)
            else:
                await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")
        except TimeException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(ModerationGeneralCommands(bot))