import discord

from discord.ext import commands
from discord.ext.commands.core import has_permissions

from modules.package.enums import *
from modules.package.utils import get_prefix
import modules.setup_module.package.setup_utils as setup_utils
import modules.moderation.package.setup_commands as setup_commands


class Configure(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        usage = f"{get_prefix()}liststaff",
        description = "Displays a list with the current staff roles"
    )
    @has_permissions(administrator = True)
    async def liststaff(self, ctx):
        await setup_utils.list_staff(ctx.guild, ctx.channel)


    @commands.command(
        usage = f"{get_prefix()}addstaff [role]",
        description = "Adds the specified role as a staff role"
    )
    @has_permissions(administrator = True)
    async def addstaff(self, ctx, role : discord.Role):
        answer = setup_utils.modifiy_staff(ctx.guild, role, True)
        await ctx.send(answer)


    @commands.command(
        usage = f"{get_prefix()}removestaff [role]",
        description = "Removes the specified role from the staff roles"
    )
    @has_permissions(administrator = True)
    async def removestaff(self, ctx, role : discord.Role):
        answer = setup_utils.modifiy_staff(ctx.guild, role, False)
        await ctx.send(answer)


    # Permissions
    @commands.command(
        usage = f"{get_prefix()}listpermissions",
        description = "Displays a list with the current permissions configuration"
    )
    @has_permissions(administrator = True)
    async def listpermissions(self, ctx):
        await setup_commands.list_permissions(ctx.guild, ctx.channel)


    @commands.command(
        usage = f"{get_prefix()}modallow [command] [role]",
        description = "Allows a role to use the specified command"
    )
    @has_permissions(administrator = True)
    async def modallow(self, ctx, _type, role : discord.Role):
        answer = setup_commands.change_permissions(ctx.guild, _type, role, True)
        await ctx.send(answer)


    @commands.command(
        usage = f"{get_prefix()}modblock [command] [role]",
        description = "Blcoks the role from using the specified command"
    )
    @has_permissions(administrator = True)
    async def modblock(self, ctx, _type, role : discord.Role):
        answer = setup_commands.change_permissions(ctx.guild, _type, role, False)
        await ctx.send(answer)


def setup(bot):
    bot.add_cog(Configure(bot))