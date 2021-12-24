from datetime import datetime
import time
from discord.ext import commands

class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def ready(self):
        global startTime
        startTime = round(time.time())
        _time = datetime.now().strftime("%H:%M:%S")
        print(f"{_time} -- Bot is ready!")