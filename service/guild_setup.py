import discord
import time

from domain.enums.general import *
from repository.json_repo import *

async def notify(notify_channel, bot, guild, join):

    guild_owner = await bot.fetch_user(guild.owner.id)
    _color = Colors.green
    _message = f"Joined `{guild}`\nGuild ID: `{guild.id}`\nGuild Owner: <@{guild_owner.id}>\nTime: <t:{round(time.time())}>"

    if join is False:
        _color = Colors.red
        _message = f"Left `{guild}`\nGuild ID: `{guild.id}`\nGuild Owner: <@{guild_owner.id}>\nTime: <t:{round(time.time())}>"

    embed = discord.Embed(
        color = _color,
        description = _message
    )


    embed.set_author(
        name = f"{bot.user}",
        icon_url = bot.user.display_avatar
    )

    notify_channel = bot.get_channel(notify_channel)
    await notify_channel.send(embed = embed)


def create_setup(guild, restart = False):

    settings_repo = SettingsRepo()
    leveling_repo = LevelingRepo()
    moderation_repo = ModerationRepo()

    settings_repo.init_data(guild.id, restart)
    leveling_repo.init_data(guild.id, restart)
    moderation_repo.init_data(guild.id, restart)


def modifiy_staff(guild, role, append = True):

    settings_repo = SettingsRepo()

    if append:
       answer = settings_repo.add_staff(guild.id, role.id)
    else:
        answer = settings_repo.remove_staff(guild.id, role.id)

    return answer


async def list_staff(guild, ctx):
    
    settings_repo = SettingsRepo()    
    roles = settings_repo.get_staff_roles()

    staff_roles = ""

    for role in roles:
        actual_role = guild.get_role(role)

        if actual_role is not None:
            staff_roles += f"<@&{actual_role.id}> "

    if staff_roles == "":
        staff_roles = None

    embed = discord.Embed(
        color = Colors.blue,
        title = "Staff Roles",
        description = staff_roles
    )

    embed.set_footer(text = "Administrators are staff members, regradless of their roles!")
    
    await ctx.reply(embed = embed)
    