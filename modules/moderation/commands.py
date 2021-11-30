import typing
import discord

from discord.ext import commands

from modules.package.enums import *
from modules.moderation.package.exceptions import *
import modules.moderation.package.commands_functions as functions

class ModerationGeneralCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    # LOGS
    @commands.command()
    async def modlogs(self, ctx, user : discord.User, page = 1):

        try:
            await ctx.send(embed = functions.generate_modlogs(ctx.guild, user, page))
        except:
            await ctx.send("Something went wrong...")

    # Warns
    @commands.command()
    async def warns(self, ctx, user : discord.User, page = 1):

        try:
            await ctx.send(embed = functions.generate_modlogs(ctx.guild, user, page, True))
        except:
            await ctx.send("Something went wrong...")


    # STATS
    @commands.command()
    async def modstats(self, ctx, user : discord.User):

        try:
            await ctx.send(embed = await functions.generate_modstats(ctx.guild, user, self.bot))
        except:
            await ctx.send("Something went wrong...")


    # DELETE CASE
    @commands.command()
    async def deletecase(self, ctx, case_id : int):
            
        try:
            await functions.deletecase(ctx.guild, case_id)

            await ctx.channel.send(embed = discord.Embed(
                color = Colors.green.value,
                description = f"Case {case_id} deleted!"
            ))

        except CaseException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    # WARN
    @commands.command()
    async def warn(self, ctx, user : discord.User, *, reason = ""):

        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'warn', reason, 0)
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
            
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'kick', reason, 0)
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
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, 0)
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


    @commands.command()
    async def tempban(self, ctx, user : discord.User, duration, *, reason = ""):
    
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'ban', reason, duration)
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
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unban', reason, 0)
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
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, 0)
        except DMException:
            pass
        except MmeberNotFoundException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")
        

    @commands.command()
    async def tempmute(self, ctx, user : discord.User, duration, *, reason = ""):
        
        try:
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'mute', reason, duration)
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
            await functions.handle_case(self.bot, ctx.guild, ctx.channel, ctx.author, user, 'unmute', reason, 0)
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
            await functions.handle_purge(ctx, amount_of_messages, user)
        except:
            await ctx.send("Something went wrong...")
    

    # SLOWMODE
    @commands.command()
    async def slowmode(self, ctx, channel : typing.Optional[discord.TextChannel], slowmode_time):
            
        try:
            await functions.handle_slowmode(ctx, channel, slowmode_time)
        except TimeException as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(ModerationGeneralCommands(bot))