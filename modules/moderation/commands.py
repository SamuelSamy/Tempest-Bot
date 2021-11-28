import discord
from discord.ext import commands

from modules.moderation.package.exceptions import *
import modules.moderation.package.functions as functions


class Moderation(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def modlogs(self, ctx, user : discord.User, page = 1):

        try:
            await ctx.send(embed = functions.generate_modlogs(ctx.guild, user, page))
        except:
            await ctx.send("Something went wrong...")


    @commands.command()
    async def warn(self, ctx, user : discord.User, *, reason = ""):

        if functions.user_in_guild(ctx.guild, user):

            try:
                await functions.handle_case(self.bot, ctx, user, 'warn', reason, 0)
            except DMException:
                pass
            except MmeberNotFoundException as error:
                await ctx.send(error)
            except:
                await ctx.send("Something went wrong...")

        else:
            await ctx.send("The user is not in this server!")


    @commands.command()
    async def kick(self, ctx, user : discord.User, *, reason = ""):
        
        if functions.user_in_guild(ctx.guild, user):

            try:
                
                await functions.handle_case(self.bot, ctx, user, 'kick', reason, 0)
            except DMException:
                pass
            except MmeberNotFoundException as error:
                await ctx.send(error)
            except:
                await ctx.send("Something went wrong...")

            try:
                member = ctx.guild.get_member(user.id)
                await member.kick(reason = reason)
            except:
                await ctx.send("Something went wrong...")
        else:
            await ctx.send("The user is not in this server!")

       
    @commands.command()
    async def ban(self, ctx, user : discord.User, *, reason = ""):
        
        if functions.user_in_guild(ctx.guild, user):

            try:
                await functions.handle_case(self.bot, ctx, user, 'ban', reason, 0)
            except DMException:
                pass
            except:
                await ctx.send("Something went wrong...")

            try:
                member = ctx.guild.get_member(user.id)
                await member.ban(reason = reason)
            except:
                await ctx.send("Something went wrong...")

        else:
            await ctx.send("The user is not in this server!")


    @commands.command()
    async def tempban(self, ctx, user : discord.User, duration, *, reason = ""):
        
        if functions.user_in_guild(ctx.guild, user):

            try:
                await functions.handle_case(self.bot, ctx, user, 'ban', reason, duration)
            except DMException:
                pass
            except:
                await ctx.send("Something went wrong...")

            try:
                member = ctx.guild.get_member(user.id)
                await member.ban(reason = reason)
            except:
                await ctx.send("Something went wrong...")   

        else:
            await ctx.send("The user is not in this server!")


    @commands.command()
    async def unban(self, ctx, user : discord.User, *, reason = ""):
        
        try:
            await functions.handle_unban(ctx, user, reason)
            await functions.handle_case(self.bot, ctx, user, 'unban', reason, 0)
        except DMException:
            pass
        except MemberNotAffectedByModeration as error:
            await ctx.send(error)
        except:
            await ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(Moderation(bot))