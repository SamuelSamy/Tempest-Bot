import discord

from discord.ext import commands
from discord.ext.commands.core import has_permissions
from discord.commands import slash_command

import modules.normal.moderation.package.setup_commands as setup_commands
import modules.normal.setup_module.package.setup_utils as setup_utils

from modules.normal.package.enums import *
from modules.normal.package.utils import get_prefix


class Configure(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        usage = f"{get_prefix()}liststaff",
        description = "Displays a list with the current staff roles"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def liststaff(self, ctx):
        await setup_utils.list_staff(ctx.guild, ctx)


    @commands.command(
        usage = f"{get_prefix()}addstaff [role]",
        description = "Adds the specified role as a staff role"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def addstaff(self, ctx, role : discord.Role):
        answer = setup_utils.modifiy_staff(ctx.guild, role, True)
        await ctx.reply(answer)


    @commands.command(
        usage = f"{get_prefix()}removestaff [role]",
        description = "Removes the specified role from the staff roles"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def removestaff(self, ctx, role : discord.Role):
        answer = setup_utils.modifiy_staff(ctx.guild, role, False)
        await ctx.reply(answer)


    # Permissions
    @commands.command(
        usage = f"{get_prefix()}listpermissions",
        description = "Displays a list with the current permissions configuration"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def listpermissions(self, ctx):
        await setup_commands.list_permissions(ctx.guild, ctx)


    @commands.command(
        usage = f"{get_prefix()}modallow [command] [role]",
        description = "Allows a role to use the specified command"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def modallow(self, ctx, _type, role : discord.Role):
        answer = setup_commands.change_permissions(ctx.guild, _type, role, True)
        await ctx.reply(answer)


    @commands.command(
        usage = f"{get_prefix()}modblock [command] [role]",
        description = "Blocks the role from using the specified command"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def modblock(self, ctx, _type, role : discord.Role):
        answer = setup_commands.change_permissions(ctx.guild, _type, role, False)
        await ctx.reply(answer)


    @commands.command(
        usage = f"{get_prefix()}muterole [role]",
        description = "Sets the muted role"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def muterole(self, ctx, role : discord.Role):
        answer = setup_commands.set_mute_role(ctx.guild, role)
        await ctx.reply(answer)


    @commands.command(
        usage = f"{get_prefix()}modlogchannel [channel]",
        description = "Sets the moderator log channel"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def modlogchannel(self, ctx, channel : discord.TextChannel):
        answer = setup_commands.set_mod_channel(ctx.guild, channel)
        await ctx.reply(answer)


def setup(bot):
    bot.add_cog(Configure(bot))
