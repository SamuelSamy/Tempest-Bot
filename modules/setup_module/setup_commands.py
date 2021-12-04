import discord

from discord.ext import commands
from discord.ext.commands.core import has_permissions

from modules.package.enums import *
import modules.setup_module.package.setup_utils as setup_utils


class SetUpCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @has_permissions(administrator = True)
    async def liststaff(self, ctx):
        await setup_utils.list_staff(ctx.guild, ctx.channel)


    @commands.command()
    @has_permissions(administrator = True)
    async def addstaff(self, ctx, role : discord.Role):
        answer = setup_utils.modifiy_staff(ctx.guild, role, True)
        await ctx.send(answer)


    @commands.command()
    @has_permissions(administrator = True)
    async def removestaff(self, ctx, role : discord.Role):
        answer = setup_utils.modifiy_staff(ctx.guild, role, False)
        await ctx.send(answer)


def setup(bot):
    bot.add_cog(SetUpCommands(bot))