import discord

from discord.ext import commands
from service._general.commands_checks import is_admin

from discord.ext.commands.errors import BadArgument

from domain.exceptions import CustomException
from service._general.utils import get_prefix

import service.starboard as service_starboard


class Starboard(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.group(
        invoke_without_command = True,
        usage = f"{get_prefix()}starboards",
        description = "View a list with all the starboards",
        brief = "0"
    )
    @is_admin()
    async def starboards(self, ctx, message = ""):
        
        if message != "":
            raise BadArgument()

        try:
            embed = service_starboard.get_starboards(ctx.guild)
            await ctx.reply(embed = embed)
        except CustomException as error:
            await ctx.reply(error)

        
    @starboards.command(
        name = "create",
        usage = f"{get_prefix()}starboards create [suggestions channel] [spotlight channel] [required stars]",
        description = "Create a new starboard",
        brief = "10"
    )
    @is_admin()
    async def starboard_create(self, ctx, suggestions: discord.TextChannel, spotlight: discord.TextChannel, stars: int):
        try:
            answer = service_starboard.create_starboard(ctx.guild, suggestions, spotlight, stars)
            await ctx.reply(answer)
        except CustomException as error:
            await ctx.reply(error)


    @starboards.command(
        name = "remove",
        usage = f"{get_prefix()}starboards remove [starboard id]",
        description = "Remove a starboard",
        brief = "20"
    )
    @is_admin()
    async def starboard_remove(self, ctx, starboard_id):
        try:
            answer = service_starboard.remove_starboard(ctx.guild, starboard_id)
            await ctx.reply(answer)
        except CustomException as error:
            await ctx.reply(error)
