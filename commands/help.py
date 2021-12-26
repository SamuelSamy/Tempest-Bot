import discord

from discord.ext import commands

import service.help as functions



class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def help(self, ctx):
        embed, view = functions.handle_help(self.bot)
        await ctx.reply(embed = embed, view = view)
        self.bot.add_view(view)
