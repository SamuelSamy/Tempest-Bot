from modules.package.enums import *
from modules.package.utils import *

def modifiy_staff(guild, role, append = True):
    
    json_file = open_json("data/settings.json")
    guild_id = str(guild.id)


    if append:
        if role.id not in json_file[guild_id][Settings.staff_roles.value]:
            json_file[guild_id][Settings.staff_roles.value].append(role.id)
            answer = f"{Emotes.green_tick.value} Successfully added the specifed role to the staff roles!"
        else:
            answer = f"{Emotes.red_tick.value} This role already is already a staff role!"
    else:
        if role.id in json_file[guild_id][Settings.staff_roles.value]:
            json_file[guild_id][Settings.staff_roles.value].remove(role.id)
            answer = f"{Emotes.green_tick.value} Successfully removed the specifed role from the staff roles!"
        else:
            answer = f"{Emotes.red_tick.value} This role is not a staff role!"


    save_json(json_file, "data/settings.json")

    return answer


async def list_staff(guild, channel):
    
    roles_string = "**Current Staff Roles**\n```"

    guild_id = str(guild.id)

    json_file = open_json("data/settings.json")

    roles = json_file[guild_id][Settings.staff_roles.value]

    for role in roles:
        actual_role = guild.get_role(role)
        roles_string += f"{actual_role.name}, "


    roles_string = roles_string[:-2]
    roles_string += "```*Note: Administrators are staff members, regradless of their roles!*"
    
    if len(roles) == 0:
        roles_string = "No staff roles found!\n*Note: Administrators are staff members, regradless of their roles!*"

    await channel.send(roles_string)
    