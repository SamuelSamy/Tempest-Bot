import typing
import discord
import time

from discord.ext import commands, tasks
from modules.moderation.package.enums import CaseFormat, ModFormat

from modules.package.enums import *
from modules.moderation.package.exceptions import *
import modules.moderation.package.functions as functions


class ModerationGeneralCommands(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_ready")
    async def open_listeners(self):

        self.remove_mute.start()
        self.remove_bans.start()


    @tasks.loop(seconds = 5) # TODO: 1 min
    async def remove_mute(self):

        moderation_logs = functions.open_json("data/moderation.json")

        for guild_id in moderation_logs:
            guild = self.bot.get_guild(int(guild_id))

            ids = moderation_logs[guild_id][ModFormat.temp_mute.value]
            ids_to_be_removed = []

            for case_id in ids:
                print(self.bot)
                case, user = await functions.get_case_and_user_by_id(guild, case_id, self.bot)

                if case[CaseFormat.time.value] + case[CaseFormat.duration.value] < round(time.time()):
                    ids_to_be_removed.append(case_id)
                    
                    try:
                        await functions.handle_case(self.bot, guild, None, self.bot.user, user, 'unmute', "Mute was temporary", 0)
                        await functions.unmute(guild, user, "Mute was temporary")
                    except:
                        print(f"Error while unmutting {user.id}")

            for id in ids_to_be_removed:
                moderation_logs[guild_id][ModFormat.temp_mute.value].remove(id)

            functions.save_json(moderation_logs, "data/moderation.json")


    @tasks.loop(seconds = 10) # TODO: 30 min
    async def remove_bans(self):

        moderation_logs = functions.open_json("data/moderation.json")

        for guild_id in moderation_logs:
            guild = self.bot.get_guild(int(guild_id))

            ids = moderation_logs[guild_id][ModFormat.temp_ban.value]
            ids_to_be_removed = []

            for case_id in ids:

                case, user = await functions.get_case_and_user_by_id(guild, case_id, self.bot)

                if case[CaseFormat.time.value] + case[CaseFormat.duration.value] < round(time.time()):
                
                    ids_to_be_removed.append(case_id)

                    try:
                        await functions.handle_unban(guild, user, "Ban was temporary")
                        await functions.handle_case(self.bot, guild, None, self.bot.user, user, 'unban', "Ban was temporary", 0)
                    except:
                        print(f"Error while unbanning {user.id}")

            for id in ids_to_be_removed:
                moderation_logs[guild_id][ModFormat.temp_ban.value].remove(id)

            functions.save_json(moderation_logs, "data/moderation.json")
        

def setup(bot):
    bot.add_cog(ModerationGeneralCommands(bot))