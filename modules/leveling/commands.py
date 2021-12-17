import typing
import discord

from discord.ext import commands
from modules.package.enums import Emotes
from modules.package.exceptions import LevelingError

from modules.package.utils import get_prefix
import modules.leveling.package.functions as functions

class Leveling(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    

    @commands.command(
        usage = f"{get_prefix()}setlevel [user] [level]",
        description = "Sets the specified user's level"
    )
    @commands.has_permissions(administrator = True)
    async def setlevel(self, ctx, user : discord.Member, level : int):
        try:
            await functions.set_level(ctx.guild, user, level)
            await ctx.reply(f"{Emotes.green_tick.value} Successfully set <@{user.id}>'s level to **{level}**!")
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}addxp [user] [xp]",
        description = "Gives xp to the specified user"
    )
    @commands.has_permissions(administrator = True)
    async def addxp(self, ctx, user : discord.Member, xp : int):
        try:
            await functions.add_xp(ctx.guild, user, xp, ctx)
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}removexp [user] [xp]",
        description = "Removes xp from the specified user"
    )
    @commands.has_permissions(administrator = True)
    async def removexp(self, ctx, user : discord.Member, xp : int):
        try:
            await functions.remove_xp(ctx.guild, user, xp, ctx)
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}removexp [user] [xp]",
        description = "Removes xp from the specified user"
    )
    @commands.has_permissions(administrator = True)
    async def addreward(self, ctx, level : int, role : discord.Role):
        try:
            functions.add_reward(ctx.guild, level, role)
            await ctx.reply(f"{Emotes.green_tick.value} Successfully added the role reward!")
        except LevelingError as error:
            await ctx.reply(error)

    @commands.command(
        usage = f"{get_prefix()}removexp [user] [xp]",
        description = "Removes xp from the specified user"
    )
    @commands.has_permissions(administrator = True)
    async def removereward(self, ctx, level : int):
        try:
            functions.remove_reward(ctx.guild, level)
            await ctx.reply(f"{Emotes.green_tick.value} Successfully removed the role reward!")
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}removexp [user] [xp]",
        description = "Removes xp from the specified user"
    )
    @commands.has_permissions(administrator = True)
    async def rewards(self, ctx):
        try:
            await ctx.reply(embed = functions.get_rewards(ctx.guild))
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}addnoxp [Channel or Role]",
        description = "Blacklists the specified channel / role from leveling"
    )
    @commands.has_permissions(administrator = True)
    async def addnoxp(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):
        try:
            message = functions.change_no_xp(ctx.guild, _object, True)
            await ctx.reply(message)
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}removenoxp [Channel or Role]",
        description = "Removes the spcified channel / role from leveling blacklist"
    )
    @commands.has_permissions(administrator = True)
    async def removenoxp(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):
        try:
            message = functions.change_no_xp(ctx.guild, _object, False)
            await ctx.reply(message)
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}xpblacklist",
        description = "Get a the xp blacklist"
    )
    @commands.has_permissions(administrator = True)
    async def xpblacklist(self, ctx):
        try:
            embed = functions.get_blacklist(ctx.guild)
            await ctx.reply(embed = embed)
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}level (optional user)",
        description = "Checks a user level"
    )
    async def level(self, ctx, user : typing.Optional[discord.User]):
        
        try:
            if user is None:
                user = ctx.author

            await functions.generate_level_image(ctx.guild, user, ctx)
        except LevelingError as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}level (optional user)",
        description = "Get someone's user rank card"
    )
    async def level(self, ctx, user : typing.Optional[discord.User]):
        
        try:
            if user is None:
                user = ctx.author

            await functions.generate_level_image(ctx.guild, user, ctx)
        except LevelingError as error:
            await ctx.reply(error)

    @commands.command(
        usage = f"{get_prefix()}levelups [channel]",
        description = "The level up messages will be send in the specified channel"
    )
    async def levelups(self, ctx, channel : discord.TextChannel):
        try:
            functions.set_notify_channel(ctx.guild, channel)
            await ctx.reply(f"{Emotes.green_tick.value} The level up messages will now be sent in <#{channel.id}>")
        except LevelingError as error:
            await ctx.reply(error)


def setup(bot):
    bot.add_cog(Leveling(bot))