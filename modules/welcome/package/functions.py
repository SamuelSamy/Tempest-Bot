import discord
import time

from modules.package.enums import Colors, Settings
from modules.package.utils import open_json, save_json


def set_welcome_message(guild, message):
    settings = open_json("data/settings.json")
    settings[str(guild.id)][Settings.welcome_message.value] = message
    save_json(settings, "data/settings.json")


def set_welcome_channel(guild, channel):
    settings = open_json("data/settings.json")
    settings[str(guild.id)][Settings.welcome_channel.value] = channel.id
    save_json(settings, "data/settings.json")


async def welcome(bot, guild, member):
    settings = open_json("data/settings.json")

    message = settings[str(guild.id)][Settings.welcome_message.value]
    channel = settings[str(guild.id)][Settings.welcome_channel.value]

    if channel != 0 and message.strip() != "":
        channel = bot.get_channel(channel)

        embed = discord.Embed(
            color = Colors.blue.value,
            title = f"Welcome to `{guild}`",
            description = message + f"\n\nMember #{guild.member_count}\nJoined at: <t:{round(time.time())}>"
        )

        embed.set_author(
            name = member,
            icon_url = member.avatar_url
        )

        await channel.send(content = f"<@{member.id}> just joined the server", embed = embed)

        try:
            await member.send(embed = embed)
        except:
            pass

