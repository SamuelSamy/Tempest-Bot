from os import remove
from modules.moderation.package.enums import BannedWord, ModFormat
from modules.package.exceptions import TypeException
from modules.package.enums import *
from modules.package.utils import *


def add_banned_word(guild, word, _type, duration):
    
    if _type not in ['mute', 'ban', 'kick']:
        raise TypeException("Auto-punishment type must be `mute`, `kick` or `ban`")

    if _type == 'kick' or duration == "":
        duration = "0s"
    
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)
    next_id = json_file[guild_id][ModFormat.next_bw_id.value]

    banned_word = {
        BannedWord.word.value: word,
        BannedWord.flags.value: {
            BannedWord.flag_type.value: _type,
            BannedWord.flag_duration.value: compute_seconds(duration),
            BannedWord.flag_p_roles.value: [],
            BannedWord.flag_p_channels.value: [],
            BannedWord.flag_notify_channel.value: 0
        } 
    }

    json_file[guild_id][ModFormat.next_bw_id.value] += 1
    json_file[guild_id][ModFormat.banned_words.value][str(next_id)] = banned_word

    save_json(json_file, "data/moderation.json")


def remove_banned_word(guild, word_id):
    removed = False
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    if word_id in json_file[guild_id][ModFormat.banned_words.value].keys():
        del json_file[guild_id][ModFormat.banned_words.value][str(word_id)]
        removed = True
    
    save_json(json_file, "data/moderation.json")
    
    if not removed:
        raise UnexpectedError("No word entry found with the specified ID")


def list_banned_words(guild):
    
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    punishments_dict = json_file[guild_id][ModFormat.banned_words.value]

    json_object = json.dumps(punishments_dict, indent = 4)

    return json_object


def protect_role(guild, word_id, role):

    protected = False

    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    if word_id in json_file[guild_id][ModFormat.banned_words.value].keys():
        
        if role.id not in json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_roles.value]:
            json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_roles.value].append(role.id)
            protected = True

    save_json(json_file, "data/moderation.json")
    if not protected:
        raise UnexpectedError("Unable to protect the specified role")


def unprotect_role(guild, word_id, role):

    unprotected = False

    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    if word_id in json_file[guild_id][ModFormat.banned_words.value].keys():
        
        if role.id in json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_roles.value]:
            json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_roles.value].remove(role.id)
            unprotected = True

    save_json(json_file, "data/moderation.json")
    if not unprotected:
        raise UnexpectedError("Unable to unprotect the specified role")


def protect_channel(guild, word_id, channel):

    protected = False

    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    if word_id in json_file[guild_id][ModFormat.banned_words.value].keys():
        
        if channel.id not in json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_channels.value]:
            json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_channels.value].append(channel.id)
            protected = True

    save_json(json_file, "data/moderation.json")
    if not protected:
        raise UnexpectedError("Unable to protect the specified channel")


def unprotect_channel(guild, word_id, channel):

    unprotected = False

    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    if word_id in json_file[guild_id][ModFormat.banned_words.value].keys():
        
        if channel.id in json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_channels.value]:
            json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_p_channels.value].remove(channel.id)
            unprotected = True

    save_json(json_file, "data/moderation.json")
    if not unprotected:
        raise UnexpectedError("Unable to unprotect the specified channel")