import discord
from modules.normal.leveling.package.enums import Leveling

from modules.normal.moderation.package.enums import BannedWord, ExternalLinks, ModFormat
from modules.normal.package.exceptions import CustomException
from modules.normal.package.enums import *
from modules.normal.package.utils import *


def add_banned_word(guild, word, _type, duration):
    
    if _type not in ['ban', 'kick', 'warn']:
        raise CustomException(f"{Emotes.wrong.value} Auto-punishment type must be `ban`, `kick` or `warn`")

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
        raise CustomException(f"{Emotes.wrong.value} No word entry found with the specified ID")


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
        raise CustomException(f"{Emotes.wrong.value} Unable to unprotect the specified channel")

    
def change_link_perms(guild, _object, allow):
    
    message = ""
    json_file = open_json("data/moderation.json")
    moderation = json_file[str(guild.id)][ModFormat.links.value]
    
    _type = ""
    _value = None

    if type(_object) is discord.Role:
        _type = f"from <@&{_object.id}>"
        _value = ExternalLinks.protected_roles.value

    else:  # type(_object) is discord.TextChannel:
        _type = f"in <#{_object.id}>"
        _value = ExternalLinks.protected_channels.value

    
    if allow == True:
            
        if _object.id not in moderation[_value]:
            moderation[_value].append(_object.id)
        
        message = f"{Emotes.green_tick.value} Links {_type} will no longer be deleted!"
    
    else:  # allow == False
        
        if _object.id in moderation[_value]:
            moderation[_value].remove(_object.id)
        
        message = f"{Emotes.not_found.value} This {_type.lower()} is not blacklisted!"

    save_json(json_file, "data/moderation.json")

    return message