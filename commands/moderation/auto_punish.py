import discord
import io

from discord.ext import commands
from discord.ext.commands.core import has_permissions
from discord.ext.commands.errors import BadArgument

import service.moderation.punish_functions as functions

from service._general.utils import get_prefix
from domain.exceptions import CustomException


class AutoPunishments(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.group(
        invoke_without_command = False,
        usage = f"{get_prefix()}punishments",
        description = "Displays a list of auto-punishments",
        brief = "0"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def punishments(self, ctx, message = ""):
        
        if message != "":
            raise BadArgument()

        try:
            json_content = functions.list_punishments(ctx.guild)
            _fp = io.StringIO(json_content)
            _filename = f"{ctx.guild.id}.auto_punishments.json"
            await ctx.reply(content = "**Autho Punishments**", file = discord.File(fp = _fp, filename =_filename ))
        except CustomException as error:
            await ctx.reply(error)


    @punishments.command(
        name = "add",
        usage = f"{get_prefix()}punishments add [amount of warns] [time] [mute/kick/ban] (duration)",
        description = "Adds an auto-punishment",
        brief = "1"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def add_punishment(self, ctx, warns,  time, _type, duration = ""):
        
        try:
            if duration == "":
                duration = 0

            functions.add_punishment(ctx.guild, warns, time, _type, duration)
            await ctx.reply("Auto-Punishment added!")
        except CustomException as error:
            await ctx.reply(error)

    
    @punishments.command(
        name = "remove",
        usage = f"{get_prefix()}punishments remove [punishment id]",
        description = "Removes the punishment entry with the specified ID",
        brief = "2"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def remove_punishment(self, ctx, punishment_id):
        
        try:
            functions.remove_punishment(ctx.guild, punishment_id)
            await ctx.reply("Auto-Punishment removed!")
        except CustomException as error:
            await ctx.reply(error)


    

