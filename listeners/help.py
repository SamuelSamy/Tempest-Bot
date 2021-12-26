from discord.ext import commands

import service.guild_setup as functions

class HelpListeners(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener("on_guild_join")
    async def giuld_join(self, guild):
        await functions.notify(self._main_channel, self.bot, guild, True)
        functions.create_setup(guild)


    @commands.Cog.listener("on_guild_remove")
    async def giuld_leave(self, guild):
        await functions.notify(self._main_channel, self.bot, guild, False)
    