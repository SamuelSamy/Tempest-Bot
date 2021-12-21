from modules.normal.moderation.package.utility_functions import *
from modules.normal.moderation.package.enums import *
from modules.normal.moderation.package.enums import *

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

async def list_permissions(guild, ctx):
    
    embed = discord.Embed(
        color = Colors.blue.value,
        title = "Current Moderator Permissions"
    )
    

    guild_id = str(guild.id)

    json_file = open_json("data/moderation.json")

    permissions = json_file[guild_id][ModFormat.permissions.value]

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
    
    moderation = open_json("data/moderation.json")
    guild_settings = moderation[str(guild.id)]
    guild_settings[ModFormat.mod_channel.value] = channel.id
    save_json(moderation, "data/moderation.json")
    return f"{Emotes.green_tick.value} Successfully set the specified channel as the moderation log channel!"


def set_mute_role(guild, role):
    settings = open_json("data/settings.json")
    guild_settings = settings[str(guild.id)]
    guild_settings[Settings.muted_role.value] = role.id
    save_json(settings, "data/settings.json")
    return f"{Emotes.green_tick.value} Successfully set the `Muted` role!"