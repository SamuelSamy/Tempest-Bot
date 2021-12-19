import time
import sqlite3

from discord.ext import commands, tasks
from modules.moderation.package.enums import ModFormat
from modules.moderation.package.classes import Case
from modules.moderation.package.utility_functions import get_case_by_entry

from modules.package.enums import *
from modules.package.exceptions import *
import modules.moderation.package.commands_functions as functions
import modules.moderation.package.utility_functions as utils


class ModerationGeneralCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def open_listeners(self):
        self.remove_mute.start()
        self.remove_bans.start()


    @tasks.loop(seconds = 5) # TODO: 30 sec
    async def remove_mute(self):
        
        path = "data/database.db"
        table = "moderation_cases"

        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(f"select * from {table} where time + duration <= ? and duration != 0 and type = 'mute' and expired = 0", (int(round(time.time())),))
        data = cursor.fetchall()
        connection.close()

        for entry in data:
            case = get_case_by_entry(entry)
            guild = self.bot.get_guild(case.guild)
            user = guild.get_member(case.user)

            
            await functions.handle_case(self.bot, guild, None, self.bot.user, user, 'unmute', "Mute was temporary", 0)
            utils.mark_as_expired(case)
            

    @tasks.loop(seconds = 10) # TODO: 15 min
    async def remove_bans(self):
        
        path = "data/database.db"
        table = "moderation_cases"

        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(f"select * from {table} where time + duration <= ? and duration != 0 and type = 'ban' and expired = 0", (int(round(time.time())),))
        data = cursor.fetchall()
        connection.close()

        for entry in data:
            case = get_case_by_entry(entry)
            guild = self.bot.get_guild(case.guild)
            user = await self.bot.fetch_user(case.user)

           
            await functions.handle_case(self.bot, guild, None, self.bot.user, user, 'unban', "Ban was temporary", 0)
            utils.mark_as_expired(case)
            
def setup(bot):
    bot.add_cog(ModerationGeneralCommands(bot))