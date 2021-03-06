from discord.ext import commands

import service.guild_setup as functions

class AutoSetup(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self._main_channel = 921151734049562694

    
    @commands.Cog.listener("on_guild_join")
    async def giuld_join(self, guild):
        await functions.notify(self._main_channel, self.bot, guild, True)
        functions.create_setup(guild)


    @commands.Cog.listener("on_guild_remove")
    async def giuld_leave(self, guild):
        await functions.notify(self._main_channel, self.bot, guild, False)
        