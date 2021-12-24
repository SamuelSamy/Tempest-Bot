from repository.json_repo import ModerationRepo, SettingsRepo
from service.moderation.utility_functions import *
from domain.enums.general import Emotes, Colors
from domain.enums.moderation import ModFormat, Permissions


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