import discord
import io

from discord.ext import commands

from modules.package.enums import *
import modules.setup_module.package.setup_utils as setup_utils


class SetUpCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def liststaff(self, ctx):
        
        if ctx.author.guild_permissions.administrator:
            await setup_utils.list_staff(ctx.guild, ctx.channel)
        else:
            await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")


    @commands.command()
    async def addstaff(self, ctx, role : discord.Role):
        
        if ctx.author.guild_permissions.administrator:
            answer = setup_utils.modifiy_staff(ctx.guild, role, True)
            await ctx.send(answer)
        else:
            await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")


    @commands.command()
    async def removestaff(self, ctx, role : discord.Role):
        
        if ctx.author.guild_permissions.administrator:
            answer = setup_utils.modifiy_staff(ctx.guild, role, False)
            await ctx.send(answer)
        else:
            await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")


def setup(bot):
    bot.add_cog(SetUpCommands(bot))