from modules.moderation.package.enums import BannedWord, ModFormat
from modules.package.exceptions import TypeException
from modules.package.enums import *
from modules.package.utils import *


def add_banned_word(guild, word, _type, duration):
    
    if _type not in ['ban', 'kick', 'warn']:
        raise TypeException("Auto-punishment type must be `ban`, `kick` or `warn`")

    if _type != 'ban' or duration == "":
        duration = "0s"
    
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)
    next_id = json_file[guild_id][ModFormat.next_bw_id.value]

    banned_word = {
        BannedWord.word.value: word,
        BannedWord.flags.value: {
            BannedWord.flag_type.value: _type,
            BannedWord.flag_duration.value: compute_seconds(duration),
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


def notify_channel(guild, word_id, channel):

    set = False

    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)

    if word_id in json_file[guild_id][ModFormat.banned_words.value].keys():
        json_file[guild_id][ModFormat.banned_words.value][str(word_id)][BannedWord.flags.value][BannedWord.flag_notify_channel.value] = channel.id if channel is not None else 0
        set = True

    save_json(json_file, "data/moderation.json")

    if not set:
        raise UnexpectedError("Unable to unprotect the specified channel")