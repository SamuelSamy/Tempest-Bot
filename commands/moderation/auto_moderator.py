import discord
import io
import typing

from discord.ext import commands
from discord.ext.commands.errors import BadArgument

import service.moderation.auto_mod_command_utils as functions

from service._general.utils import get_prefix
from domain.exceptions import CustomException

class AutoModerator(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        usage = f"{get_prefix()}banword [word] [warn/kick/ban] (optional time)",
        description = "Bans the specified word and sets a punishment when members use the word. *The time must be a number ending in 's'/'m'/'h'/'d'*",
        brief = "1"
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
        description = "Removes the ban word entry with the specified ID",
        brief = "2"
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
        description = "Displays a list of banned words and their punishments",
        brief = "0"
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
        description = "When members use the specified banned word a message will be sent in the mentioned channel",
        brief = "3"
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


    @commands.group(
        invoke_without_command = False,
        usage = f"{get_prefix()}links",
        description = "Displays the roles and channels that will be ignored when sending links",
        brief = "4"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def links(self, ctx, message = ""):

        if message != "":
            raise BadArgument()

        try:
            embed = functions.list_links_permissions(ctx.guild)
            await ctx.reply(embed = embed)
        except CustomException as error:
            await ctx.reply(error)


    @links.command(
        name = "block",
        usage = f"{get_prefix()}links block [channel / role]",
        description = "Removes the specified role / channel from the allowed list",
        brief = "5"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def link_block(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):

        try:
            message = functions.change_link_perms(ctx.guild, _object, False)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


    @links.command(
        name = "allow",
        usage = f"{get_prefix()}links allow [channel / role]",
        description = "Allows the specified role / channel to send external links",
        brief = "6"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def link_allow(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):

        try:
            message = functions.change_link_perms(ctx.guild, _object, True)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


