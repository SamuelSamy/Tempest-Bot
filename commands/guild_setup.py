import discord

from discord.ext import commands
from discord.ext.commands.core import has_permissions

import service.moderation.setup_commands as setup_functions
import service.guild_setup as guild_functions

from domain.enums.general import Emotes
from service._general.utils import get_prefix


class Configure(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.group(
        invoke_without_command = True
    )
    @commands.guild_only()
    async def staff(self, ctx):
        pass

    
    @staff.command(
        name = "remove",
        usage = f"{get_prefix()}staff remove [role]",
        description = "Removes the specified role from the staff roles",
        brief = "2"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def removestaff(self, ctx, role : discord.Role):
        answer = guild_functions.modifiy_staff(ctx.guild, role, False)
        await ctx.reply(answer)

    
    @staff.command(
        name = "add",
        usage = f"{get_prefix()}staff add [role]",
        description = "Adds the specified role as a staff role",
        brief = "1"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def addstaff(self, ctx, role : discord.Role):
        answer = guild_functions.modifiy_staff(ctx.guild, role, True)
        await ctx.reply(answer)     


    @staff.command(
        name = "list",
        usage = f"{get_prefix()}staff list",
        description = "Displays a list with the current staff roles",
        brief = "0"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def _liststaff(self, ctx):
        await guild_functions.list_staff(ctx.guild, ctx)


    # Permissions
    @staff.command(
        name = "permissions",
        usage = f"{get_prefix()}staff permissions",
        description = "Displays a list with the current permissions configuration",
        aliases = ["perms"],
        brief = "3"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def listpermissions(self, ctx):
        await guild_functions.list_permissions(ctx.guild, ctx)


    @staff.command(
        name = "allow",
        usage = f"{get_prefix()}staff allow [command] [role]",
        description = "Allows a role to use the specified command",
        brief = "4"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def modallow(self, ctx, _type, role : discord.Role):
        answer = guild_functions.change_permissions(ctx.guild, _type, role, True)
        await ctx.reply(answer)


    @staff.command(
        name = "block",
        usage = f"{get_prefix()}staff block [command] [role]",
        description = "Blocks the role from using the specified command",
        brief = "5"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def modblock(self, ctx, _type, role : discord.Role):
        answer = guild_functions.change_permissions(ctx.guild, _type, role, False)
        await ctx.reply(answer)


    @staff.command(
        name = "logs",
        usage = f"{get_prefix()}staff logs [channel]",
        description = "Sets the moderator log channel",
        brief = "6"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def logs(self, ctx, channel : discord.TextChannel):
        setup_functions.set_mod_channel(ctx.guild, channel)
        await ctx.reply(f"{Emotes.green_tick} Successfully set the specified channel as the moderation log channel!")


    @commands.command(
        usage = f"{get_prefix()}muterole [role]",
        description = "Sets the muted role",
        brief = "7"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def muterole(self, ctx, role : discord.Role):
        setup_functions.set_mute_role(ctx.guild, role)
        await ctx.reply(f"{Emotes.green_tick} Successfully set the `Muted` role!")



    