import discord

from discord.ext import commands
from modules.package.enums import Emotes
from modules.package.exceptions import LevelingError

from modules.package.utils import get_prefix
import modules.welcome.package.functions as functions

class Welcome(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    

    @commands.command(
        usage = f"{get_prefix()}welcomemessage [message]",
        description = "Sets the default welcome message"
    )
    @commands.has_permissions(administrator = True)
    async def welcomemessage(self, ctx, *, message):
        try:
            functions.set_welcome_message(ctx.guild, message)
            await ctx.reply(f"{Emotes.green_tick.value} Successfully set the default welcome message!")
        except LevelingError as error:
            await ctx.reply(error)

    @commands.command(
        usage = f"{get_prefix()}welcomechannel [channel]",
        description = "Sets the welcome channael"
    )
    @commands.has_permissions(administrator = True)
    async def welcomechannel(self, ctx, channel : discord.TextChannel):
        try:
            functions.set_welcome_channel(ctx.guild, channel)
            await ctx.reply(f"{Emotes.green_tick.value} Successfully set the welcome channel!")
        except LevelingError as error:
            await ctx.reply(error)
    


def setup(bot):
    bot.add_cog(Welcome(bot))