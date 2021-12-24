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


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def leave(self, ctx, guild : discord.Guild):
        await guild.leave()
        await ctx.respond(f"{Emotes.green_tick} Succsefully left `{guild.name}`")


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def guilds(self, ctx):
        await ctx.respond(f"I am currently in **{len(self.bot.guilds)}** guilds!")


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def reconfigure(self, ctx, guild : discord.Guild):
        create_setup(guild, True)
        await ctx.respond(f"{Emotes.green_tick} Reconfigured data for the specified guild!")
    
    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def invite(self, ctx, guild : discord.Guild):
        invite = await guild.text_channels[0].create_invite(max_uses = 1, reason = "Invite requested by the bot owner")
        await ctx.respond(invite.url)
    

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def status(self, ctx):
        await ctx.reply("I am alive!")

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def user(self, ctx, user : typing.Optional[discord.User]):
        await ctx.respond(embed = get_user_data(ctx, user))

        
