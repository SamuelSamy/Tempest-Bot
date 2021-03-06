import time

from discord.ext import commands
from discord.ext import tasks
from repository.database_repo import DatabaseRepository


import service.moderation.utility_functions as utils
import service.moderation.auto_mod_utils as functions
import service.moderation.commands_functions as mod_funcs

from service._general.utils import is_staff
from service._general.config import MIN_BAN_TIME, MIN_MUTE_TIME


class AutoModeratorListeners(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    # Banned Words
    @commands.Cog.listener("on_message")
    async def check_ban_words(self, message):
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_banned_words(self.bot, message.guild,  message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_ban_words_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_banned_words(self.bot, message.guild,  message.author, message)


    # External Links
    @commands.Cog.listener("on_message")
    async def check_external_links(self, message):
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_external_links(message.guild,  message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_external_links_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_external_links(message.guild,  message.author, message)


    # Mass Mention
    @commands.Cog.listener("on_message")
    async def check_mass_mention(self, message):
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_mass_mention(self.bot, message.guild,  message.author, message)
            

    # Excesive Caps
    @commands.Cog.listener("on_message")
    async def check_excesive_caps(self, message):
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_excesive_caps(message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_excesive_caps_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_excesive_caps(message.author, message)


    # Discord Invites
    @commands.Cog.listener("on_message")
    async def check_discord_invites(self, message):
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_discord_invites(self.bot, message.guild,  message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_discord_invites_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not is_staff(message.guild,  message.author):
            await functions.check_for_discord_invites(self.bot, message.guild,  message.author, message)
    
    

    @commands.Cog.listener("on_ready")
    async def open_listeners(self):
        self.remove_mute.start()
        self.remove_bans.start()


    @tasks.loop(seconds = MIN_MUTE_TIME / 2)
    async def remove_mute(self):
        
        database_repo = DatabaseRepository()
        data = database_repo.select("select * from moderation_cases where time + duration <= ? and duration != 0 and type = 'mute' and expired = 0", (int(round(time.time())),))
        
        for entry in data:
            case = utils.get_case_by_entry(entry)
            guild = self.bot.get_guild(case.guild)
            user = guild.get_member(case.user)

            mark = True

            if user is not None:

                try:
                    await mod_funcs.handle_case(self.bot, guild, None, self.bot.user, user, 'unmute', "Mute was temporary", 0)
                except Exception as error:
                    if not str(error).endswith("is not muted!"):
                        mark = False
                        print(f"Error: Can not unmute {user.id} in {guild.id}\n{error}")
            
            if mark:
                utils.mark_as_expired(case)
            
            

    @tasks.loop(seconds = MIN_BAN_TIME)
    async def remove_bans(self):
        
        database_repo = DatabaseRepository()
        data = database_repo.select("select * from moderation_cases where time + duration <= ? and duration != 0 and type = 'ban' and expired = 0", (int(round(time.time())),))
        
        for entry in data:
            case = utils.get_case_by_entry(entry)
            guild = self.bot.get_guild(case.guild)
            user = await self.bot.fetch_user(case.user)

            try:

                await mod_funcs.handle_case(self.bot, guild, None, self.bot.user, user, 'unban', "Ban was temporary", 0)
                utils.mark_as_expired(case)

            except Exception as error:
                
                if not str(error).endswith("is not banned from this server!"):
                    print(f"Error: Can not unban {user.id} in {guild.id}\n{error}")
                else:
                    utils.mark_as_expired(case)


    @commands.Cog.listener("on_member_join")
    async def sync_mute(self, member):
        
        database_repo = DatabaseRepository()
        users = database_repo.select("select * from moderation_cases where type = 'mute' and expired = 0", row_type = lambda cursor, row: row[0])

        if member.id in users:
            await mod_funcs.handle_mute(member.guild, member, "")


def setup(bot):
    bot.add_cog(AutoModeratorListeners(bot))