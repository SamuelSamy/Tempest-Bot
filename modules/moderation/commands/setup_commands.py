import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions

import modules.moderation.package.setup_commands as setup_commands
from modules.package.enums import *


class ModerationSetUp(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @has_permissions(administrator = True)
    async def listpermissions(self, ctx):
        await setup_commands.list_permissions(ctx.guild, ctx.channel)


    @commands.command()
    @has_permissions(administrator = True)
    async def modallow(self, ctx, _type, role : discord.Role):
        answer = setup_commands.change_permissions(ctx.guild, _type, role, True)
        await ctx.send(answer)


    @commands.command()
    @has_permissions(administrator = True)
    async def modremove(self, ctx, _type, role : discord.Role):
        answer = setup_commands.change_permissions(ctx.guild, _type, role, False)
        await ctx.send(answer)


def setup(bot):
    bot.add_cog(ModerationSetUp(bot))