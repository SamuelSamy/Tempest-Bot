import discord
import time

from modules.package.enums import Colors
from modules.package.utils import open_json, save_json


async def notify(notify_channel, bot, guild, join):

    guild_owner = await bot.fetch_user(guild.owner.id)
    _color = Colors.green.value
    _message = f"Joined `{guild}`\nGuild ID: `{guild.id}`\nGuild Owner: <@{guild_owner.id}>\nTime: <t:{round(time.time())}>"

    if join is False:
        _color = Colors.red.value
        _message = f"Left `{guild}`\nGuild ID: `{guild.id}`\nGuild Owner: <@{guild_owner.id}>\nTime: <t:{round(time.time())}>"

    embed = discord.Embed(
        color = _color,
        description = _message
    )


    embed.set_author(
        name = f"{bot.user}",
        icon_url = bot.user.avatar_url
    )

    notify_channel = bot.get_channel(notify_channel)
    await notify_channel.send(embed = embed)


def create_setup(guild, restart = False):

    settings = open_json("data/settings.json")
    guild_id = str(guild.id)

    if guild_id not in settings.keys() or restart:
        
        settings[guild_id] = {
            "muted-role": 0,
            "staff-roles": []
        }
        

        leveling = open_json("data/leveling.json")

        leveling[guild_id] = {
            "notify_channel": 0,
            "min_xp": 15,
            "max_xp": 40,
            "time": 60,
            "no_xp_roles": [],
            "no_xp_channels": [],
            "rewards": {}
        }

        moderation = open_json("data/moderation.json")
        moderation[guild_id] = {
            "next-case-id": 0,
            "next-bannedowrd-id": 0,
            "next-auto-punishment-id": 0,
            "logs-channel": 0,
            "permissions": {
                "warn": [],
                "ban": [],
                "kick": [],
                "mute": [],
                "purge": [],
                "slowmode": [],
                "delete-case": [],
                "mod-logs": [],
                "mod-stats": []
            },
            "auto-punishments": {},
            "banned_words": {},
            "external_links": {
                "protected_roles": [],
                "protected_channels": []
            }
        }

        save_json(settings, "data/settings.json")
        save_json(moderation, "data/moderation.json")
        save_json(leveling, "data/leveling.json")
