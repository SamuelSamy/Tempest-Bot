from typing import no_type_check
from modules.moderation.package.enums import BannedWord, ModFormat
from modules.package.enums import *
from modules.package.utils import *
from modules.moderation.package.commands_functions import handle_case

async def check_for_banned_words(bot, guild, member, message):
    
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)
    member = guild.get_member(member.id)

    punishments = []


    for entry in json_file[guild_id][ModFormat.banned_words.value].values():
        word = entry[BannedWord.word.value]

        if word in message.content.lower():
            punishments.append(entry)


    if len(punishments) != 0:

        await message.delete()

        punishments.sort(key = lambda punishment: punishment[BannedWord.flags.value][BannedWord.flag_type.value])
        
        highest_punishments = [punishments[0]]
        highest_punishment = punishments[0]

        index = 1
        while index < len(punishments) \
            and highest_punishment[BannedWord.flags.value][BannedWord.flag_type.value] == punishments[index][BannedWord.flags.value][BannedWord.flag_type.value]:
            highest_punishments.append(punishments[index])
            index += 1

        highest_punishments.sort(
            key = lambda punishment: punishment[BannedWord.flags.value][BannedWord.flag_duration.value], 
            reverse = highest_punishment[BannedWord.flags.value][BannedWord.flag_type.value] == 'mute'
        )
        
        punishment_to_apply = highest_punishments[0]
        notify_channel = None

        if punishment_to_apply[BannedWord.flags.value][BannedWord.flag_notify_channel.value] != 0:
            notify_channel = bot.get_channel(punishment_to_apply[BannedWord.flags.value][BannedWord.flag_notify_channel.value])


        await handle_case(
            bot = bot,
            guild = guild, 
            channel = notify_channel,
            moderator = bot.user,
            user = member,
            case_type = punishment_to_apply[BannedWord.flags.value][BannedWord.flag_type.value],
            reason = f"Usage of banned word **({punishment_to_apply[BannedWord.word.value]})**",
            duration = punishment_to_apply[BannedWord.flags.value][BannedWord.flag_duration.value],
            message = message.content
        )