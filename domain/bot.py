import discord
import time

from datetime import datetime
from discord.ext import commands

class Bot(commands.Bot):

    def __init__(self, token, prefix):
        self.__token = token
        self.__prefix = prefix

        super().__init__(
            intents = discord.Intents.all(), 
            command_prefix = commands.when_mentioned_or(self.__prefix),
            case_insensitive = True,
            help_command = None
        )

    async def setup_hook(self) -> None:
        await self.load_extension("domain.setup")
        return await super().setup_hook()


    async def on_ready(self):
        global startTime
        startTime = round(time.time())
        _time = datetime.now().strftime("%H:%M:%S")
        print(f"{_time} -- Bot is ready! -- {self.user.name}")


    def run_bot(self):
        self.run(self.__token)


