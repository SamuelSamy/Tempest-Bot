import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions

from services import *


config = get_json_file('data/config.json')

files = []
init_files('./modules', files)

bot = commands.Bot(intents = discord.Intents.all(), command_prefix = config['prefix'])

load_packages(files, bot)

# Commands

@bot.command()
@has_permissions(administrator = True)
async def restart(ctx):

    if ctx.author.id == 225629057172111362:
        try:
            unload_packages(files, bot)
            load_packages(files, bot)
            await ctx.send("Modules restarted!")
        except:
            await ctx.send("Error while restarting")


@bot.event
async def on_ready():
    global startTime
    startTime = get_time()
    print("Bot is ready!")


@bot.command()
@has_permissions(administrator = True)
async def uptime(ctx):
    uptime = get_time() - startTime
    await ctx.send(f"Uptime: {uptime}")


class NewHelpName(commands.MinimalHelpCommand):
    
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)

bot.help_command = NewHelpName()


# Run

bot.run(config['token'])    

