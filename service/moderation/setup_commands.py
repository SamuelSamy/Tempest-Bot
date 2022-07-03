from domain.bot import Bot
from repository.json_repo import ModerationRepo, SettingsRepo
from service.moderation.utility_functions import *
from domain.enums.general import Emotes, Colors
from domain.enums.moderation import ExternalLinks, ModFormat, Permissions


def change_permissions(guild, _type, role, append = True):
    
    moderation_repo = ModerationRepo()
   
    if append:
        answer = moderation_repo.allow_role(guild.id, role.id, _type)
    else:
        answer = moderation_repo.remove_role(guild.id, role.id, _type)

    return answer


async def list_permissions(guild, ctx):
    
    embed = discord.Embed(
        color = Colors.blue,
        title = "Current Moderator Permissions"
    )
    
    moderation_repo = ModerationRepo()
    permissions = moderation_repo.get_staff_permissions(guild.id)

    for permission in permissions.keys():
        
        roles = permissions[permission]

        allowed_roles = ""

        for role in roles:
            actual_role = guild.get_role(role)
            if actual_role is not None:
                allowed_roles += f"<@&{actual_role.id}> "
        
        if allowed_roles == "":
            allowed_roles = None

        perm = permission[0].upper() + permission[1:]

        embed.add_field(
            name = f"{perm}",
            value = allowed_roles,
            inline = True
        )

    embed.set_footer(
        text = "Administrators can use any of the above commands, regradless of their roles!"
    )

    await ctx.reply(embed = embed)
    


def set_mod_channel(guild, channel):
    moderation_repo = ModerationRepo()
    moderation_repo.set_mod_logs_channel(guild.id, channel.id)


def set_mute_role(guild, role):
    settings_repo = SettingsRepo()
    settings_repo.set_muted_role(guild.id, role.id)


def set_chat_logs(guild, channel_id):
    settings_repo = SettingsRepo()
    settings_repo.set_logs_channel(guild.id, channel_id)


def block_logs(guild, _object):
    
    if type(_object) is discord.Role:
        _type = "roles"

    else:  # type(_object) is discord.TextChannel:
        _type = "channels"

    settings_repo = SettingsRepo()
    settings_repo.chatlogs_ignore(guild.id, _type, _object)


def unblock_logs(guild, _object):

    if type(_object) is discord.Role:
        _type = "roles"

    else:  # type(_object) is discord.TextChannel:
        _type = "channels"

    settings_repo = SettingsRepo()
    settings_repo.chatlogs_unignore(guild.id, _type, _object)


def chatlogs_is_ignored_channel(guild, _id):
    settings_repo = SettingsRepo()
    return settings_repo.chatlogs_is_ignored(guild, _id)


def chatlogs_is_ignored_user(guild, user: discord.Member):
    settings_repo = SettingsRepo()

    for role in user.roles:
        if settings_repo.chatlogs_is_ignored(guild, role.id):
            return True
    
    return False


def get_ignored_list(bot: Bot, guild: discord.Guild):

    embed = discord.Embed(
        color = Colors.green,
        description = f"**Chatlogs Configuration**"
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

    settings_repo = SettingsRepo()
    ignored_roles = settings_repo.get_ignored_roles(guild.id)
    ignored_channels = settings_repo.get_ignored_channels(guild.id)

    _value = None

    if len(ignored_roles) != 0:
        _value = ""

        index = 0

        for role in ignored_roles:
            _value += f"<@&{role}> "
            index += 1
            if index % 3 == 0:
                _value += "\n"
        

    
    embed.add_field(
        name = "Ignored roles",
        value = _value
    )

    _value = None  

    if len(ignored_channels) != 0:
        _value = ""
        
        index = 0

        for channel in ignored_channels:
            _value += f"<#{channel}> "
            index += 1
            if index % 3 == 0:
                _value += "\n"

          

    embed.add_field(
        name = "Ignored channels",
        value = _value
    )

    return embed
