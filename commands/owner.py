import typing
from PIL.Image import init
import discord

from discord.ext import commands

from domain.enums.general import Emotes
from service.guild_setup import *
from service.owner import *


class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def leave(self, ctx, guild : discord.Guild):
        await guild.leave()
        await ctx.reply(f"{Emotes.green_tick} Succsefully left `{guild.name}`")


    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def guilds(self, ctx):
        await ctx.reply(f"I am currently in **{len(self.bot.guilds)}** guilds!")


    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def reconfig(self, ctx, guild : discord.Guild):
        create_setup(guild, True)
        await ctx.reply(f"{Emotes.green_tick} Reconfigured data for the specified guild!")
    

    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def reconfigall(self, ctx):
        message = await ctx.reply(f"{Emotes.loading} Reconfiguring all guilds...")
        reconfig_all(self.bot)
        await message.edit(f"{Emotes.green_tick} All guilds ({len(self.bot.guilds)}) reconfigured!")


    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def invite(self, ctx, guild : discord.Guild):
        invite = await guild.text_channels[0].create_invite(max_uses = 1, reason = "Invite requested by the bot owner")
        await ctx.reply(invite.url)
    

    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def status(self, ctx):
        await ctx.reply("I am alive!")


    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def user(self, ctx, user : typing.Optional[discord.User]):
        await ctx.reply(embed = get_user_data(ctx, user))


    @commands.command(
        brief = "0"
    )
    @commands.is_owner()
    @commands.guild_only()
    async def test(self, ctx):
        raise ValueError("Hello, this is greater!")        
