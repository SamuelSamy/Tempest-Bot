import discord

from datetime import datetime
from domain.bot import Bot
from domain.enums.general import Colors
from repository.json_repo import SettingsRepo
from service.moderation.setup_commands import chatlogs_is_ignored_channel, chatlogs_is_ignored_user

async def send_delete_log(bot: Bot, args: discord.RawMessageDeleteEvent):

    message = args.cached_message
    guild_id = args.guild_id
    channel_id = args.channel_id

    if message is None or message.author.bot or chatlogs_is_ignored_channel(guild_id, channel_id) or chatlogs_is_ignored_user(guild_id, message.author):
        return

    repo = SettingsRepo()
    logs_channel_id = repo.get_logs_channel(guild_id)

    if logs_channel_id == 0:
        return
   
    guild = bot.get_guild(guild_id)
    logs_channel: discord.TextChannel = guild.get_channel(logs_channel_id)
    channel = guild.get_channel(channel_id)

    author = message.author

    embed: discord.Embed = discord.Embed(
        color = Colors.red,
        description = f"Message from {author.mention} deleted in {channel.mention}\n<t:{round(message.created_at.timestamp())}>",
        timestamp = datetime.utcnow()
    )

    embed.set_author(
        name = f"{author}",
        icon_url = author.avatar
    )

    stripped_message = message.content

    if len(message.content) > 1000:
        stripped_message = message.content[:1000] + "..."


    if message.content:
        embed.add_field(
            name = "Message Content",
            value = stripped_message,
            inline = False
        )    


    links = ""
    for attachment in message.attachments:
        links += f"{attachment.proxy_url}\n"

    if len(links) > 1000:
        links = links[:1000] + "..."

    embed.set_footer(
        text = f"User ID: {author.id}"
    )

    await logs_channel.send(
        embed = embed,
        content = f"**Deleted Attachments:**\n{links}"
    )


async def send_edit_log(bot: Bot, args: discord.RawMessageUpdateEvent):

    old_message = args.cached_message
    guild_id = args.guild_id
    channel_id = args.channel_id

    if old_message is None or old_message.author.bot or chatlogs_is_ignored_channel(guild_id, channel_id) or chatlogs_is_ignored_user(guild_id, old_message.author):
        return

    repo = SettingsRepo()
    logs_channel_id = repo.get_logs_channel(guild_id)

    if logs_channel_id == 0:
        return
   
    guild = bot.get_guild(guild_id)
    logs_channel: discord.TextChannel = guild.get_channel(logs_channel_id)
    channel = guild.get_channel(channel_id)

    author = old_message.author

    embed: discord.Embed = discord.Embed(
        color = Colors.yellow,
        description = f"Message from {author.mention} edited in {channel.mention}",
        timestamp = datetime.utcnow()
    )

    embed.set_author(
        name = f"{author}",
        icon_url = author.avatar
    )

    stripped_message = old_message.content

    if len(old_message.content) > 500:
        stripped_message = old_message.content[:1000] + "..."

    if old_message.content:
        embed.add_field(
            name = "Before",
            value = stripped_message,
            inline = False
        )    

    new_message = await channel.fetch_message(old_message.id)

    stripped_message = new_message.content

    if len(new_message.content) > 500:
        stripped_message = new_message.content[:1000] + "..."

    if old_message.content:
        embed.add_field(
            name = "After",
            value = stripped_message,
            inline = False
        )    

    embed.set_footer(
        text = f"User ID: {author.id}"
    )

    await logs_channel.send(
        embed = embed
    )