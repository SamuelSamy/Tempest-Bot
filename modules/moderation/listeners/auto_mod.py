import time

from discord.ext import commands

from modules.package.enums import *
from modules.package.exceptions import *

import modules.package.utils as utils   
import modules.moderation.package.auto_mod_utils as functions

class AutoModerator(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    # Banned Words
    @commands.Cog.listener("on_message")
    async def check_ban_words(self, message):
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_banned_words(self.bot, message.guild,  message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_ban_words_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_banned_words(self.bot, message.guild,  message.author, message)


    # External Links
    @commands.Cog.listener("on_message")
    async def check_external_links(self, message):
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_external_links(message.guild,  message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_external_links_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_external_links(message.guild,  message.author, message)


    # Mass Mention
    @commands.Cog.listener("on_message")
    async def check_mass_mention(self, message):
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_mass_mention(self.bot, message.guild,  message.author, message)
            

    # Excesive Caps
    @commands.Cog.listener("on_message")
    async def check_excesive_caps(self, message):
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_excesive_caps(message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_excesive_caps_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_excesive_caps(message.author, message)


    # Discord Invites
    @commands.Cog.listener("on_message")
    async def check_discord_invites(self, message):
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_discord_invites(self.bot, message.guild,  message.author, message)
            

    @commands.Cog.listener("on_message_edit")
    async def check_discord_invites_edit(self, old_message, new_message):
        message = new_message
        if message.guild is not None and message.author != self.bot.user and not utils.is_staff(message.guild,  message.author):
            await functions.check_for_discord_invites(self.bot, message.guild,  message.author, message)
    
    
    
def setup(bot):
    bot.add_cog(AutoModerator(bot))