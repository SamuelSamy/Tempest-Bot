import discord
import io

from discord.ext import commands

from modules.package.enums import *
from modules.package.exceptions import *
import modules.moderation.package.auto_mod_utils as functions


class AutoPunishmentsModule(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def banword(self, ctx, word,  punishment, duration = ""):
        
        try:
            functions.add_banned_word(ctx.guild, word, punishment, duration)
            await ctx.reply(f"Successfully banned the specified word!")
        except ValueError as error:
            await ctx.reply(error)
        except TimeException as error:
            await ctx.reply(error)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def unbanword(self, ctx, id):

        try:
            functions.remove_banned_word(ctx.guild, id)
            await ctx.reply(f"Successfully removed the word!")
        except ValueError as error:
            await ctx.reply(error)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def bannedwords(self, ctx):
        
        json_content = functions.list_banned_words(ctx.guild)
        _fp = io.StringIO(json_content)
        _filename = f"{ctx.guild.id}.banned_words.json"
        await ctx.send(content = "**Banned Words**", file = discord.File(fp = _fp, filename =_filename ))


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def protectrole(self, ctx, word_id, role : discord.Role):
        
        # try:
        functions.protect_role(ctx.guild, word_id, role)
        await ctx.reply("The role was successfully protected")
        # except Exception as error:
            # print(error)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def unprotectrole(self, ctx, word_id, role : discord.Role):
        
        # try:
        functions.unprotect_role(ctx.guild, word_id, role)
        await ctx.reply("The role was successfully protected")
        # except Exception as error:
            # print(error)


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def protectchannel(self, ctx, word_id, channel : discord.TextChannel):
        
        # try:
        functions.protect_channel(ctx.guild, word_id, channel)
        await ctx.reply("The role was successfully protected")
        # except Exception as error:
            # print(error)

    
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def unprotectchannel(self, ctx, word_id, channel : discord.TextChannel):
        
        # try:
        functions.unprotect_channel(ctx.guild, word_id, channel)
        await ctx.reply("The role was successfully protected")
        # except Exception as error:
            # print(error)



def setup(bot):
    bot.add_cog(AutoPunishmentsModule(bot))