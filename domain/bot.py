import discord
from discord.ext import commands

class Bot:

    def __init__(self, token, prefix):
        
        self.__token = token
        self.__prefix = prefix

        self.__bot = commands.Bot(
            intents = discord.Intents.all(), 
            command_prefix = commands.when_mentioned_or(self.__prefix),
            case_insensitive = True,
            help_command = None
        )

        self.__bot.load_extension("domain.setup")


    def run(self):
        self.__bot.run(self.__token)


