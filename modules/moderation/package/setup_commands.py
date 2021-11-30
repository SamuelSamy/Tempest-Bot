from modules.moderation.package.utility_functions import *
from modules.moderation.package.enums import *
from modules.moderation.package.enums import *

def change_permissions(guild, _type, role, append = True):
    
    json_file = open_json("data/moderation.json")
    guild_id = str(guild.id)

    _type = _type.lower()

    if _type  in json_file[guild_id][ModFormat.permissions.value].keys():

        if append:
            if role.id not in json_file[guild_id][ModFormat.permissions.value][_type]:
                json_file[guild_id][ModFormat.permissions.value][_type].append(role.id)
                answer = f"{Emotes.green_tick.value} Successfully added permission!"
            else:
                answer = f"{Emotes.red_tick.value} This role already has the specified permission!"
        else:
            if role.id in json_file[guild_id][ModFormat.permissions.value][_type]:
                json_file[guild_id][ModFormat.permissions.value][_type].remove(role.id)
                answer = f"{Emotes.green_tick.value} Successfully removed permission!"
            else:
                answer = f"{Emotes.red_tick.value} This role does not have the specified permission!"


        save_json(json_file, "data/moderation.json")
    else:
        answer = f"{Emotes.red_tick.value} That permission does not exist!"

    return answer

async def list_permissions(guild, channel):
    
    permission_string = "**Current Moderator Permissions**\n```"

    guild_id = str(guild.id)

    json_file = open_json("data/moderation.json")

    permissions = json_file[guild_id][ModFormat.permissions.value]

    for permission in permissions.keys():
        permission_string += f"{permission}: ["

        roles = permissions[permission]

        for role in roles:
            actual_role = guild.get_role(role)
            permission_string += f"{actual_role.name}, "

        if permission_string[-1] == ' ':
            permission_string = permission_string[:-2]

        permission_string += "]\n"

    permission_string += "```*Note: Administrators can use any of the above commands, regradless of their roles!*"
    await channel.send(permission_string)
    