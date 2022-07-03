import discord
from discord.ext import commands
from domain.enums.general import Emotes

import service.starboard as functions

class StarboardListeners(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener("on_message")
    async def add_reactions(self, message):
        if message.guild is not None and not message.author.bot:
            await functions.add_reactions(message)


    @commands.Cog.listener("on_raw_reaction_add")
    async def checker_increase(self, ctx: discord.RawReactionActionEvent):
        if f"{ctx.emoji}" == f"{Emotes.star}":
            await functions.check_for_spotlight_add(self.bot, ctx)
    

    @commands.Cog.listener("on_raw_reaction_add")
    async def checker_increase_edit(self, ctx: discord.RawReactionActionEvent):
        if f"{ctx.emoji}" == f"{Emotes.star}":
            await functions.check_for_spotlight_edit(self.bot, ctx)


    @commands.Cog.listener("on_raw_reaction_remove")
    async def checker_decrease_edit(self, ctx: discord.RawReactionActionEvent):
        if f"{ctx.emoji}" == f"{Emotes.star}":
            await functions.check_for_spotlight_edit(self.bot, ctx)


    @commands.Cog.listener("on_raw_reaction_remove")
    async def checker_decrease(self, ctx: discord.RawReactionActionEvent):
        if f"{ctx.emoji}" == f"{Emotes.star}":
            await functions.check_for_spotlight_remove(self.bot, ctx)
    

    @commands.Cog.listener("on_raw_message_delete")
    async def checker_deleted(self, ctx: discord.RawMessageDeleteEvent):
        if ctx.guild_id is not None:
            await functions.remove_from_spotlight_on_delete(self.bot, ctx)


def setup(bot):
    bot.add_cog(StarboardListeners(bot))