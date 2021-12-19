import discord
import io

from discord.ext import commands
from discord.ext.commands.core import has_permissions

import modules.moderation.package.punish_functions as functions
from modules.package.enums import *
from modules.package.exceptions import *
from modules.package.utils import get_prefix


class AutoPunishments(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        usage = f"{get_prefix()}addpunishment [amount of warns] [time] [mute/kick/ban] (duration)",
        description = "Adds an auto-punishment"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def addpunishment(self, ctx, warns,  time, _type, duration = ""):
        
        try:
            if duration == "":
                duration = 0

            functions.add_punishment(ctx.guild, warns, time, _type, duration)
            await ctx.reply("Auto-Punishment added!")
        except CustomException as error:
            await ctx.reply(error)

    
    @commands.command(
        usage = f"{get_prefix()}removepunishment [punishment id]",
        description = "Removes the punishment entry with the specified ID"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def removepunishment(self, ctx, punishment_id):
        
        try:
            functions.remove_punishment(ctx.guild, punishment_id)
            await ctx.reply("Auto-Punishment removed!")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}listpunishments",
        description = "Displays a list of auto-punishments"
    )
    @commands.guild_only()
    @has_permissions(administrator = True)
    async def listpunishments(self, ctx):
        
        try:
            json_content = functions.list_punishments(ctx.guild)
            _fp = io.StringIO(json_content)
            _filename = f"{ctx.guild.id}.auto_punishments.json"
            await ctx.reply(content = "**Autho Punishments**", file = discord.File(fp = _fp, filename =_filename ))
        except CustomException as error:
            await ctx.reply(error)

def setup(bot):
    bot.add_cog(AutoPunishments(bot))