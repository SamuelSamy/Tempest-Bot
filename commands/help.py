import discord

from discord.ext import commands

import service.help as functions
from domain.exceptions import CustomException


class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def help(self, ctx, *, command = ""):

        if command == "":
            _embed, _view = functions.handle_help(self.bot)
            await ctx.reply(embed = _embed, view = _view)
        else:
            try:
                _embed = functions.handle_command_help(self.bot, ctx.author, command)
                await ctx.reply(embed = _embed)
            except CustomException as error:
                await ctx.reply(error)
