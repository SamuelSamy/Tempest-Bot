from PIL.Image import init
import discord

from discord.ext import commands

from modules.package.enums import Emotes
from modules.setup_module.package.auto_functions import create_setup


class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def leave(self, ctx, guild : discord.Guild):
        await guild.leave()
        await ctx.reply(f"{Emotes.green_tick.value} Succsefully left `{guild.name}`")


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def guilds(self, ctx):
        await ctx.reply(f"I am currently in **{len(self.bot.guilds)}** guilds!")


    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def reconfigure(self, ctx, guild : discord.Guild):
        create_setup(guild, True)
        await ctx.reply(f"{Emotes.green_tick.value} Reconfigured data for the specified guild!")
    
    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def invite(self, ctx, guild : discord.Guild):
        invite = await guild.text_channels[0].create_invite(max_uses = 1, reason = "Invite requested by the bot owner")
        await ctx.reply(invite.url)
    

    @commands.command()
    @commands.is_owner()
    @commands.guild_only()
    async def test(self, ctx):
        raise ValueError()


def setup(bot):
    bot.add_cog(Owner(bot))