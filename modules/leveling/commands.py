import discord

from discord.ext import commands

from modules.package.utils import get_prefix


class Leveling(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    

    @commands.command(
        usage = f"{get_prefix()}banword [word] [warn/kick/ban] (optional time)",
        description = "Bans the specified word and sets a punishment when members use the word. *The time must be a number ending in 's'/'m'/'h'/'d'*"
    )
    @commands.has_permissions(administrator = True)
    async def test(self, ctx, word,  punishment, duration = ""):
        
        pass



def setup(bot):
    bot.add_cog(Leveling(bot))