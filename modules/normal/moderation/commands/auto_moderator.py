import discord
import io
import typing

import modules.normal.moderation.package.auto_mod_command_utils as functions

from discord.ext import commands
from discord.commands import slash_command


from modules.normal.package.enums import *
from modules.normal.package.exceptions import *
from modules.normal.package.utils import get_prefix


class AutoModerator(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        usage = f"{get_prefix()}banword [word] [warn/kick/ban] (optional time)",
        description = "Bans the specified word and sets a punishment when members use the word. *The time must be a number ending in 's'/'m'/'h'/'d'*"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def banword(self, ctx, word,  punishment, duration = ""):
        
        try:
            functions.add_banned_word(ctx.guild, word, punishment, duration)
            await ctx.reply(f"Successfully banned the specified word!")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}unbanword [word_id]",
        description = "Removes the ban word entry with the specified ID"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def unbanword(self, ctx, id):

        try:
            functions.remove_banned_word(ctx.guild, id)
            await ctx.reply(f"Successfully removed the word!")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}bannedwords",
        description = "Displays a list of banned words and their punishments"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def bannedwords(self, ctx):

        try:
            json_content = functions.list_banned_words(ctx.guild)
            _fp = io.StringIO(json_content)
            _filename = f"{ctx.guild.id}.banned_words.json"
            await ctx.reply(content = "**Banned Words**", file = discord.File(fp = _fp, filename =_filename ))
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}notifychannel [word_id] [channel]",
        description = "When members use the specified banned word a message will be sent in the mentioned channel"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def notifychannel(self, ctx, word_id, channel : discord.TextChannel = None):

        try:
            functions.notify_channel(ctx.guild, word_id, channel)
            if channel is not None:
                await ctx.reply("Channel successfully set as a notify channel for the specified word!")
            else:
                await ctx.reply("Successfully removed the notify channel for the specified word!")
        except CustomException as error:
            await ctx.reply(error)



    @commands.command(
        usage = f"{get_prefix()}linkblock [channel / role]",
        description = "Removes the specified role / channel from the blacklist"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def linkblock(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):

        try:
            message = functions.change_link_perms(ctx.guild, _object, False)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}linkallow [channel / role]",
        description = "Allows the specified role / channel to send external links"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def linkallow(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):

        try:
            message = functions.change_link_perms(ctx.guild, _object, True)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


def setup(bot):
    bot.add_cog(AutoModerator(bot))