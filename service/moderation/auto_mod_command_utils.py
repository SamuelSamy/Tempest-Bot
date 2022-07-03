import discord
from commands.moderation.mod_commands import Moderation
from domain.enums.general import Colors
from domain.enums.leveling import Leveling

from domain.enums.moderation import *
from domain.exceptions import CustomException
from domain.enums.moderation import *
from repository.json_repo import ModerationRepo
from service._general.utils import *


def add_banned_word(guild, word, _type, duration):
    
    if _type not in ['ban', 'kick', 'warn']:
        raise CustomException(f"{Emotes.wrong} Auto-punishment type must be `ban`, `kick` or `warn`")

    if _type != 'ban' or duration == "":
        duration = "0s"
    
    banned_word = {
        BannedWord.word: word,
        BannedWord.flags: {
            BannedWord.flag_type: _type,
            BannedWord.flag_duration: compute_seconds(duration),
            BannedWord.flag_notify_channel: 0
        }
    }

    moderation_repo = ModerationRepo()
    moderation_repo.add_banned_word(guild.id, banned_word)



def remove_banned_word(guild, word_id):
    
    moderation_repo = ModerationRepo()
    removed = moderation_repo.remove_banned_word(guild.id, word_id)
    if not removed:
        raise CustomException(f"{Emotes.wrong} No word entry found with the specified ID")


def list_banned_words(guild):
    
    moderation_repo = ModerationRepo()
    punishments_dict = moderation_repo.get_banned_words(guild.id)
    json_object = json.dumps(punishments_dict, indent = 4)
    return json_object


def notify_channel_add(guild, word_id, channel):

    moderation_repo = ModerationRepo()
    set = moderation_repo.set_notify_channel(guild.id, word_id, channel.id)
    if not set:
        raise CustomException(f"{Emotes.wrong} The specified word ID does not exist!")


def notify_channel_remove(guild, word_id):

    moderation_repo = ModerationRepo()
    set = moderation_repo.remove_notify_channel(guild.id, word_id)
    if not set:
        raise CustomException(f"{Emotes.wrong} The specified word ID does not exist!")

    
def change_link_perms(guild, _object, allow):
    
    message = ""

    if type(_object) is discord.Role:
        _value = f"from <@&{_object.id}>"
        _type = ExternalLinks.protected_roles

    else:  # type(_object) is discord.TextChannel:
        _value = f"in <#{_object.id}>"
        _type = ExternalLinks.protected_channels

    moderation_repo = ModerationRepo()
    
    if allow == True:
        moderation_repo.allow_link(guild.id, _type, _object)
        message = f"{Emotes.green_tick} Links {_value} will no longer be deleted!"
    else:  # allow == False
        moderation_repo.block_link(guild.id, _type, _object)
        message = f"{Emotes.green_tick} Links {_value} will now be deleted!"


    return message


def list_links_permissions(guild):

    embed = discord.Embed(
        color = Colors.green,
        description = f"**Links Configuration**"
    )

    if guild.icon is not None:
        embed.set_author(
            name = f"{guild}",
            icon_url = guild.icon.url
        )
    else:
        embed.set_author(
            name = f"{guild}"
        )

    moderation_repo = ModerationRepo()
    allowed_roles = moderation_repo.get_link_protected_roles(guild.id)
    allowed_channels = moderation_repo.get_link_protected_channels(guild.id)

    if len(allowed_roles) != 0:
        _value = ""

        index = 0

        for role in allowed_roles:

            _value += f"<@&{role}> "

            index += 1
            if index % 3 == 0:
                _value += "\n"

    else:
        _value = None

    
    embed.add_field(
        name = "Allowed roles",
        value = _value
    )

    if len(allowed_channels) != 0:
        _value = ""
        
        index = 0

        for channel in allowed_channels:
            _value += f"<#{channel}> "

            index += 1
            
            if index % 3 == 0:
                _value += "\n"

    else:
        _value = None    

    embed.add_field(
        name = "Allowed channels",
        value = _value
    )

    return embed