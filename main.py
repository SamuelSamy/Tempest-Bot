import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions

from services import *
from modules.help.package.help import CustomHelpCommand

config = get_json_file('data/config.json')

files = []
init_files('./modules', files)

bot = commands.Bot(
    intents = discord.Intents.all(), 
    command_prefix = commands.when_mentioned_or(config['prefix']),
    case_insensitive = True,
    help_command = CustomHelpCommand()
)

load_packages(files, bot)

# Commands

@bot.command()
@has_permissions(administrator = True)
async def restart(ctx):

    if ctx.author.id == 225629057172111362:
        try:
            unload_packages(files, bot)
            load_packages(files, bot)
            await ctx.reply("Modules restarted!")
        except:
            await ctx.reply("Error while restarting")


@bot.event
async def on_ready():
    global startTime
    startTime = get_time()
    print("Bot is ready!")


@bot.command()
@has_permissions(administrator = True)
async def uptime(ctx):
    uptime = get_time() - startTime
    await ctx.reply(f"Uptime: {uptime}")


bot.run(config['token'])