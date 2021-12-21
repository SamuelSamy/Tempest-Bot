import time

from discord.ext import commands

from modules.normal.package.enums import *
from modules.normal.package.exceptions import *

import modules.normal.welcome.package.functions as functions

class WelcomeListener(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener("on_member_join")
    async def welcome(self, member):
        await functions.welcome(self.bot, member.guild, member)

    
def setup(bot):
    bot.add_cog(WelcomeListener(bot))