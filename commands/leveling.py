import typing
import discord

import service.leveling as leveling

from discord.ext import commands
from discord.commands import slash_command

from service._general.utils import get_prefix
from domain.exceptions import CustomException
from domain.enums.general import Emotes


class Leveling(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        usage = f"{get_prefix()}setlevel [user] [level]",
        description = "Sets the specified user's level"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def setlevel(self, ctx, user : discord.Member, level : int):
        try:
            await leveling.set_level(ctx.guild, user, level)
            await ctx.reply(f"{Emotes.green_tick} Successfully set <@{user.id}>'s level to **{level}**!")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}addxp [user] [xp]",
        description = "Gives xp to the specified user"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def addxp(self, ctx, user : discord.Member, xp : int):
        try:
            await leveling.add_xp(ctx.guild, user, xp, ctx)
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}removexp [user] [xp]",
        description = "Removes xp from the specified user"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def removexp(self, ctx, user : discord.Member, xp : int):
        try:
            await leveling.remove_xp(ctx.guild, user, xp, ctx)
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}addreward [level] [role]",
        description = "Adds a new reward"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def addreward(self, ctx, level : int, role : discord.Role):
        try:
            leveling.add_reward(ctx.guild, level, role)
            await ctx.reply(f"{Emotes.green_tick} Successfully added the role reward!")
        except CustomException as error:
            await ctx.reply(error)

    @commands.command(
        usage = f"{get_prefix()}removereward [level]",
        description = "Removes a reward"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def removereward(self, ctx, level : int):
        try:
            leveling.remove_reward(ctx.guild, level)
            await ctx.reply(f"{Emotes.green_tick} Successfully removed the role reward!")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}rewards",
        description = "Displays all rewards"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def rewards(self, ctx):
        try:
            await ctx.reply(embed = leveling.get_rewards(ctx.guild))
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}addnoxp [Channel or Role]",
        description = "Blacklists the specified channel / role from leveling"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def addnoxp(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):
        try:
            message = leveling.change_no_xp(ctx.guild, _object, True)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}removenoxp [Channel or Role]",
        description = "Removes the specified channel / role from leveling blacklist"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def removenoxp(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):
        try:
            message = leveling.change_no_xp(ctx.guild, _object, False)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}xpblacklist",
        description = "Get the xp blacklist"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def xpblacklist(self, ctx):
        try:
            embed = leveling.get_blacklist(ctx.guild)
            await ctx.reply(embed = embed)
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}level (optional user)",
        description = "Get someone's user rank card"
    )
    @commands.guild_only()
    async def level(self, ctx, user : typing.Optional[discord.User]):
        
        try:
            if user is None:
                user = ctx.author

            await leveling.generate_level_image(ctx.guild, user, ctx)
        except CustomException as error:
            await ctx.reply(error)

    @commands.command(
        usage = f"{get_prefix()}levelups [channel]",
        description = "The level up messages will be send in the specified channel"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def levelups(self, ctx, channel : discord.TextChannel):
        try:
            leveling.set_notify_channel(ctx.guild, channel)
            await ctx.reply(f"{Emotes.green_tick} The level up messages will now be sent in <#{channel.id}>")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}defaultmultiplier [number]",
        description = "The server default multiplier"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def defaultmultiplier(self, ctx, value : float):
        try:
            value = leveling.set_multiplier(ctx.guild, 0, value)
            await ctx.reply(f"{Emotes.green_tick} Server's default multiplier is now **{value}x**")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}setmultiplier [role] [number]",
        description = "Sets a multiplier for the specified role"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def setmultiplier(self, ctx, role : discord.Role, value : float):
        try:
            value = leveling.set_multiplier(ctx.guild, role, value)
            await ctx.reply(f"{Emotes.green_tick} The specified role's multiplier is now **{value}x**")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}checkmultiplier [user]",
        description = "Check a user's multiplier"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def checkmultiplier(self, ctx, user : discord.Member):
        try:
            value = leveling.get_multiplier(ctx.guild, user)
            await ctx.reply(f"{user.mention}'s multipliers is **{value}x**")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}listmultipliers",
        description = "Get a list of all active multipliers"
    )
    @commands.guild_only()
    @commands.has_permissions(administrator = True)
    async def listmultipliers(self, ctx):
        try:
            multipliers_embed = leveling.list_multipliers(ctx.guild)
            await ctx.reply(embed = multipliers_embed)
        except CustomException as error:
            await ctx.reply(error)
