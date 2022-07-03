import discord
import time


from domain.enums.general import Colors
from repository.json_repo import SettingsRepo


def set_welcome_message(guild, message):
    settings_repo = SettingsRepo()
    settings_repo.set_welcome_message(guild.id, message)


def set_welcome_channel(guild, channel):
    settings_repo = SettingsRepo()
    settings_repo.set_welcome_channel(guild.id, channel.id)


async def welcome(bot, guild, member):
   
    settings_repo = SettingsRepo()
    message = settings_repo.get_welcome_message(guild.id)
    channel = settings_repo.get_welcome_channel(guild.id)

    if channel != 0 and message.strip() != "":
        channel = bot.get_channel(channel)

        embed = discord.Embed(
            color = Colors.blue,
            title = f"Welcome to `{guild}`",
            description = message + f"\n\nMember #{guild.member_count}\nJoined at: <t:{round(time.time())}>"
        )

        embed.set_author(
            name = member,
            icon_url = member.display_avatar
        )

        await channel.send(content = f"<@{member.id}> just joined the server", embed = embed)

        try:
            await member.send(embed = embed)
        except:
            pass

