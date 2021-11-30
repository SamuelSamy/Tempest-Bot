import discord
import io

from discord.ext import commands

from modules.package.enums import *
from modules.moderation.package.exceptions import *
import modules.moderation.package.punish_functions as functions


class AutoPunishmentsModule(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def addpunishment(self, ctx, warns,  time, _type, duration = ""):
        
        try:
            if duration == "":
                duration = 0

            functions.add_punishment(ctx.guild, warns, time, _type, duration)
            await ctx.send("Auto-Punishment added!")
        except ValueError as error:
            await ctx.send(error)
        except TimeException as error:
            await ctx.send(error)
        # except:
        #     await ctx.send("Something went wrong...")

    
    @commands.command()
    async def removepunishment(self, ctx, punishment_id):
        
        try:
            functions.remove_punishment(ctx.guild, punishment_id)
            await ctx.send("Auto-Punishment removed!")
        except ValueError as error:
            await ctx.send(error)
        # except:
        #     await ctx.send("Something went wrong...")


    @commands.command()
    async def listpunishments(self, ctx):
        
        try:
            json_content = functions.list_punishments(ctx.guild)
            _fp = io.StringIO(json_content)
            _filename = f"{ctx.guild.id}.auto_punishments.json"
            await ctx.send(content = "**Autho Punishments**", file = discord.File(fp = _fp, filename =_filename ))
        except:
            await ctx.send("Something went wrong...")


def setup(bot):
    bot.add_cog(AutoPunishmentsModule(bot))