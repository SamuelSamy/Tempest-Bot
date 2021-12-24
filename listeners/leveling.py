from discord.ext import commands

import service.leveling as functions

class LevelingListeners(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    
    @commands.Cog.listener("on_message")
    async def increase_xp(self, message):
        if message.guild is not None and not message.author.bot:
            await functions.increase_xp(message.guild,  message.author, message)
    
    
def setup(bot):
    bot.add_cog(LevelingListeners(bot))