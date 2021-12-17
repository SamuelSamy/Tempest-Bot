from discord.ext import commands

import modules.setup_module.package.auto_functions as functions

class AutoModerator(commands.Cog):
    
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
        

    
    
def setup(bot):
    bot.add_cog(AutoModerator(bot))