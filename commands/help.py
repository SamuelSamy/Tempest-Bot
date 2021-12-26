from discord.ext import commands

import service.help as functions
from domain.exceptions import CustomException


class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def help(self, ctx, command = ""):

        if command == "":
            embed, view = functions.handle_help(self.bot)
            await ctx.reply(embed = embed, view = view)
            self.bot.add_view(view)
        else:
            try:
                embed = functions.handle_command_help(self.bot, ctx.author, command)
                await ctx.reply(embed = embed)
            except CustomException as error:
                await ctx.reply(error)
