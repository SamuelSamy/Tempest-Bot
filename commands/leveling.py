import typing
import discord
from discord.ext.commands.errors import BadArgument
from service._general.commands_checks import is_admin

import service.leveling as leveling

from discord.ext import commands

from service._general.utils import get_prefix
from domain.exceptions import CustomException
from domain.enums.general import Emotes


class Leveling(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    # Set Level
    @commands.command(
        usage = f"{get_prefix()}setlevel [user] [level]",
        description = "Sets the specified user's level",
        brief = "6"
    )
    @commands.guild_only()
    @is_admin()
    async def setlevel(self, ctx, user : discord.Member, level : int):
        try:
            await leveling.set_level(ctx.guild, user, level)
            await ctx.reply(f"{Emotes.green_tick} Successfully set <@{user.id}>'s level to **{level}**!")
        except CustomException as error:
            await ctx.reply(error)


    # XP (add, remove)
    @commands.group(
        invoke_without_command = True
    )
    @commands.guild_only()
    @is_admin()
    async def xp(self, ctx):
        pass


    @xp.command(
        name = "add",
        usage = f"{get_prefix()}xp add [user] [xp]",
        description = "Adds xp to the specified user",
        brief = "7"
    )
    @commands.guild_only()
    @is_admin()
    async def add_xp(self, ctx, user : discord.Member, xp : int):
        try:
            await leveling.add_xp(ctx.guild, user, xp, ctx)
        except CustomException as error:
            await ctx.reply(error)


    @xp.command(
        name = "remove",
        usage = f"{get_prefix()}xp remove [user] [xp]",
        description = "Removes xp from the specified user",
        brief = "8"
    )
    @commands.guild_only()
    @is_admin()
    async def remove_xp(self, ctx, user : discord.Member, xp : int):
        try:
            await leveling.remove_xp(ctx.guild, user, xp, ctx)
        except CustomException as error:
            await ctx.reply(error)


    

    # Rewards (list, add, remove)
    @commands.group(
        invoke_without_command = True,
        usage = f"{get_prefix()}rewards",
        description = "Displays all rewards",
        brief = "3"
    )
    @commands.guild_only()
    @is_admin()
    async def rewards(self, ctx, message = ""):

        if message != "":
            raise BadArgument()

        try:
            await ctx.reply(embed = leveling.get_rewards(ctx.guild))
        except CustomException as error:
            await ctx.reply(error)

    @rewards.command(
        name = "add",
        usage = f"{get_prefix()}rewards add [level] [role]",
        description = "Adds a new reward",
        brief = "4"
    )
    @commands.guild_only()
    @is_admin()
    async def add_reward(self, ctx, level : int, role : discord.Role):
        try:
            leveling.add_reward(ctx.guild, level, role)
            await ctx.reply(f"{Emotes.green_tick} Successfully added the role reward!")
        except CustomException as error:
            await ctx.reply(error)


    @rewards.command(
        name = "remove",
        usage = f"{get_prefix()}rewards remove [level]",
        description = "Removes a reward",
        brief = "5"
    )
    @commands.guild_only()
    @is_admin()
    async def remove_reward(self, ctx, level : int):
        try:
            leveling.remove_reward(ctx.guild, level)
            await ctx.reply(f"{Emotes.green_tick} Successfully removed the role reward!")
        except CustomException as error:
            await ctx.reply(error)


    # noxp
    @commands.group(
        invoke_without_command = True,
        usage = f"{get_prefix()}noxp",
        description = "Displays a list containing the noxp roles and channels",
        brief = "9"
    )
    @commands.guild_only()
    @is_admin()
    async def noxp(self, ctx, message = ""):

        if message != "":
            raise BadArgument()

        try:
            embed = leveling.get_blacklist(ctx.guild)
            await ctx.reply(embed = embed)
        except CustomException as error:
            await ctx.reply(error)


    @noxp.command(
        name = "add",
        usage = f"{get_prefix()}noxp add [Channel or Role]",
        description = "Blacklists the specified channel / role from leveling",
        brief = "10"
    )
    @commands.guild_only()
    @is_admin()
    async def add_noxp(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):
        try:
            message = leveling.change_no_xp(ctx.guild, _object, True)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


    @noxp.command(
        name = "remove",
        usage = f"{get_prefix()}noxp remove [Channel or Role]",
        description = "Removes the specified channel / role from leveling blacklist",
        brief = "11"
    )
    @commands.guild_only()
    @is_admin()
    async def remove_noxp(self, ctx, _object : typing.Union[discord.TextChannel, discord.Role]):
        try:
            message = leveling.change_no_xp(ctx.guild, _object, False)
            await ctx.reply(message)
        except CustomException as error:
            await ctx.reply(error)


    # Level (rank)
    @commands.command(
        usage = f"{get_prefix()}rank (optional user)",
        description = "Get someone's user rank card",
        aliases = ["level"],
        brief = "0"
    )
    @commands.guild_only()
    async def rank(self, ctx, user : typing.Optional[discord.User]):
        
        try:
            if user is None:
                user = ctx.author
            message = await ctx.send(f"{Emotes.loading} Generating rank card...\n{Emotes.invisible} Please wait")
            await leveling.generate_level_image(ctx.guild, user, message, ctx.author)
        except CustomException as error:
            await ctx.reply(error)


    # Levelups
    @commands.command(
        usage = f"{get_prefix()}levelups [channel]",
        description = "The level up messages will be send in the specified channel",
        brief = "12"
    )
    @commands.guild_only()
    @is_admin()
    async def levelups(self, ctx, channel : discord.TextChannel):
        try:
            leveling.set_notify_channel(ctx.guild, channel)
            await ctx.reply(f"{Emotes.green_tick} The level up messages will now be sent in <#{channel.id}>")
        except CustomException as error:
            await ctx.reply(error)


    # Multipliers (list, default, set, remove, check)

    @commands.group(
        invoke_without_command = True,
        usage = f"{get_prefix()}multipliers",
        description = "Displays all active multipliers",
        brief = "13"
    )
    @commands.guild_only()
    @is_admin()
    async def multipliers(self, ctx, message = ""):

        if message != "":
            raise BadArgument()
        
        try:
            multipliers_embed = leveling.list_multipliers(ctx.guild)
            await ctx.reply(embed = multipliers_embed)
        except CustomException as error:
            await ctx.reply(error)


    @multipliers.command(
        name = "default",
        usage = f"{get_prefix()}multipliers default [number]",
        description = "Sets the server's default multiplier",
        brief = "14"
    )
    @commands.guild_only()
    @is_admin()
    async def default_multiplier(self, ctx, value : float):
        try:
            value = leveling.set_multiplier(ctx.guild, 0, value, can_be_1 = True)
            await ctx.reply(f"{Emotes.green_tick} Server's default multiplier is now **{value}x**")
        except CustomException as error:
            await ctx.reply(error)


    @multipliers.command(
        name = "set",
        usage = f"{get_prefix()}multipliers set [role] [number]",
        description = "Sets a multiplier for the specified role",
        brief = "15"
    )
    @commands.guild_only()
    @is_admin()
    async def set_multiplier(self, ctx, role : discord.Role, value : float):
        try:
            value = leveling.set_multiplier(ctx.guild, role, value)
            await ctx.reply(f"{Emotes.green_tick} The specified role's multiplier is now **{value}x**")
        except CustomException as error:
            await ctx.reply(error)


    @multipliers.command(
        name = "remove",
        usage = f"{get_prefix()}multipliers remove [role]",
        description = "Removes the specified role's multiplier",
        brief = "17"
    )
    @commands.guild_only()
    @is_admin()
    async def remove_multiplier(self, ctx, role : discord.Role):
        try:
            leveling.remove_multiplier(ctx.guild, role)
            await ctx.reply(f"{Emotes.green_tick} Succesfully removed the specified role's multiplier!")
        except CustomException as error:
            await ctx.reply(error)


    @multipliers.command(
        name = "check",
        usage = f"{get_prefix()}multipliers check [user]",
        description = "Check a user's multiplier",
        brief = "2"
    )
    @commands.guild_only()
    @is_admin()
    async def check_multiplier(self, ctx, user : discord.Member):
        try:
            value = leveling.get_multiplier(ctx.guild, user)
            await ctx.reply(f"{user.mention}'s multipliers is **{value}x**")
        except CustomException as error:
            await ctx.reply(error)


    @commands.command(
        usage = f"{get_prefix()}leaderboard (optional page)",
        description = "Displays the leveling leaderboard",
        aliases = ["lb"],
        brief = "1"
    )
    @commands.guild_only()
    async def leaderboard(self, ctx, page : int = 1):
        
        try:
            message = await ctx.send(f"{Emotes.loading} Generating leaderboard...\n{Emotes.invisible} Please wait")
            await leveling.generate_leaderboard(self.bot, ctx.guild, message, page)
        except CustomException as error:
            await ctx.reply(error)

   