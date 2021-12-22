import time
import sqlite3

from discord.ext import commands, tasks

from modules.normal.package.enums import *
from modules.normal.package.exceptions import *
from modules.normal.package.config import *

import modules.normal.moderation.package.commands_functions as functions
import modules.normal.moderation.package.utility_functions as utils


class ModerationGeneralCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def open_listeners(self):
        self.remove_mute.start()
        self.remove_bans.start()


    @tasks.loop(seconds = MIN_MUTE_TIME / 2)
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
            case = utils.get_case_by_entry(entry)
            guild = self.bot.get_guild(case.guild)
            user = guild.get_member(case.user)

            mark = True

            if user is not None:

                try:
                    await functions.handle_case(self.bot, guild, None, self.bot.user, user, 'unmute', "Mute was temporary", 0)
                except Exception as error:
                    if not str(error).endswith("is not muted!"):
                        mark = False
                        print(f"Error: Can not unmute {user.id} in {guild.id}\n{error}")
            
            if mark:
                utils.mark_as_expired(case)
            
            

    @tasks.loop(seconds = MIN_BAN_TIME)
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
            case = utils.get_case_by_entry(entry)
            guild = self.bot.get_guild(case.guild)
            user = await self.bot.fetch_user(case.user)

            try:

                await functions.handle_case(self.bot, guild, None, self.bot.user, user, 'unban', "Ban was temporary", 0)
                utils.mark_as_expired(case)

            except Exception as error:
                
                if not str(error).endswith("is not banned from this server!"):
                    print(f"Error: Can not unban {user.id} in {guild.id}\n{error}")
                else:
                    utils.mark_as_expired(case)


    @commands.Cog.listener("on_member_join")
    async def sync_mute(self, member):
        
        path = "data/database.db"
        table = "moderation_cases"

        connection = sqlite3.connect(path)
        connection.row_factory = lambda cursor, row: row[0]
        cursor = connection.cursor()
        cursor.execute(f"select user from {table} where type = 'mute' and expired = 0")
        users = cursor.fetchall()
        connection.close()

        if member.id in users:
            await functions.handle_mute(member.guild, member, "")



def setup(bot):
    bot.add_cog(ModerationGeneralCommands(bot))