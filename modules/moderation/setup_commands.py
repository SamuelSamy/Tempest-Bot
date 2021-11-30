import discord
from discord.ext import commands

import modules.moderation.package.setup_commands as setup_commands
from modules.package.enums import *


class ModerationSetUp(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def listpermissions(self, ctx):
        
        if ctx.author.guild_permissions.administrator:
            await setup_commands.list_permissions(ctx.guild, ctx.channel)
        else:
            await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")


    @commands.command()
    async def modallow(self, ctx, _type, role : discord.Role):
        
        if ctx.author.guild_permissions.administrator:
            answer = setup_commands.change_permissions(ctx.guild, _type, role, True)
            await ctx.send(answer)
        else:
            await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")


    @commands.command()
    async def modremove(self, ctx, _type, role : discord.Role):
        
        if ctx.author.guild_permissions.administrator:
            answer = setup_commands.change_permissions(ctx.guild, _type, role, False)
            await ctx.send(answer)
        else:
            await ctx.send(f"{Emotes.red_tick.value} <@{ctx.author.id}> you do not have permissions to use that command!")


def setup(bot):
    bot.add_cog(ModerationSetUp(bot))