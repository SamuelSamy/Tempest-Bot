import discord

from discord.ext import commands

import service.welcome as welcome

from domain.enums.general import Emotes
from domain.exceptions import CustomException
from service._general.utils import get_prefix


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
            welcome.set_welcome_message(ctx.guild, message)
            await ctx.reply(f"{Emotes.green_tick} Successfully set the default welcome message!")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}welcomechannel [channel]",
        description = "Sets the welcome channael"
    )
    @commands.has_permissions(administrator = True)
    async def welcomechannel(self, ctx, channel : discord.TextChannel):
        try:
            welcome.set_welcome_channel(ctx.guild, channel)
            await ctx.reply(f"{Emotes.green_tick} Successfully set the welcome channel!")
        except CustomException as error:
            await ctx.reply(error)
    
