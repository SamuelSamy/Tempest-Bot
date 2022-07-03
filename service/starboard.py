from datetime import datetime
import discord

from domain.bot import Bot
from domain.enums.general import Colors, Emotes
from domain.enums.starboard import SubStarboard
from repository.database_repo import DatabaseRepository

from repository.json_repo import StarboardRepo


def create_starboard(guild: discord.Guild, suggestions: discord.TextChannel, spotlight: discord.TextChannel, stars: int):
    repo = StarboardRepo()
    return repo.add_starboard(guild.id, suggestions.id, spotlight.id, stars)


def remove_starboard(guild: discord.Guild, starboard_id):
    repo = StarboardRepo()
    return repo.remove_starboard(guild.id, int(starboard_id))


def get_starboards(guild: discord.Guild) -> discord.Embed:
    
    embed = discord.Embed(
        color = Colors.blue,
        title = f"{Emotes.sparkles} Starboards"
    )

    repo = StarboardRepo()
    
    starboards = repo.get_starboards(guild.id)

    for starboard in starboards:
        embed.add_field(
            name = f"ID: {starboards[starboard][SubStarboard.id]}",
            value = f"Suggestions Channel: <#{starboard}>\nSpotlight Channel: <#{starboards[starboard][SubStarboard.spotlight]}>\n{Emotes.star} Required: {starboards[starboard][SubStarboard.required]}",
            inline = False
        )

    if len(embed.fields) == 0:
        embed.description = f"None"

    return embed


async def add_reactions(message: discord.Message):
    channel = message.channel
    data = get_starboard_data(channel)
    if data is not None:
        await message.add_reaction(Emotes.star)


async def check_for_spotlight_add(bot: Bot, ctx: discord.RawReactionActionEvent):
    guild = bot.get_guild(ctx.guild_id)
    channel = guild.get_channel(ctx.channel_id)
    data = get_starboard_data(channel)

    if data is not None:
        message = await channel.fetch_message(ctx.message_id)

        if has_enough_stars(data, message) and not is_in_spotlight(guild, message):
            spotlight = guild.get_channel(int(data[1][SubStarboard.spotlight]))
            await send_message_to_spotlight(spotlight, message, data[1][SubStarboard.id])


async def check_for_spotlight_edit(bot: Bot, ctx: discord.RawReactionActionEvent):
    guild = bot.get_guild(ctx.guild_id)
    channel = guild.get_channel(ctx.channel_id)
    data = get_starboard_data(channel)

    if data is not None:
        message = await channel.fetch_message(ctx.message_id)

        if is_in_spotlight(guild, message):
            spotlight = guild.get_channel(int(data[1][SubStarboard.spotlight]))
            await edit_spotlight_message(spotlight, message, data[1][SubStarboard.id])



async def check_for_spotlight_remove(bot: Bot, ctx: discord.RawReactionActionEvent):

    guild = bot.get_guild(ctx.guild_id)
    channel = guild.get_channel(ctx.channel_id)
    data = get_starboard_data(channel)

    if data is not None:
        message = await channel.fetch_message(ctx.message_id)

        if is_in_spotlight(guild, message) and not has_enough_stars(data, message):
            spotlight = guild.get_channel(int(data[1][SubStarboard.spotlight]))
            await delete_message_from_spotlight(spotlight, ctx.message_id, int(data[1][SubStarboard.id]))


async def remove_from_spotlight_on_delete(bot: Bot, ctx: discord.RawMessageDeleteEvent):
    
    guild = bot.get_guild(ctx.guild_id)
    channel = guild.get_channel(ctx.channel_id)
    data = get_starboard_data(channel)

    if data is not None:
        spotlight = guild.get_channel(int(data[1][SubStarboard.spotlight]))
        await delete_message_from_spotlight(spotlight, ctx.message_id, data[1][SubStarboard.id])



def get_starboard_data(channel: discord.TextChannel):
    repo = StarboardRepo()
    starboards = repo.get_starboards(channel.guild.id)

    for suggestions_id in starboards:
        if suggestions_id == str(channel.id):
            return [suggestions_id, starboards[suggestions_id]]

    return None


def get_stars_amount(message: discord.Message):
    reactions = message.reactions
    for reaction in reactions:
        if str(reaction.emoji) == Emotes.star:
            return reaction.count


def has_enough_stars(data, message: discord.Message):
    stars = data[1][SubStarboard.required]
    reacts = get_stars_amount(message)
    return reacts > stars


def is_in_spotlight(guild: discord.Guild, message: discord.Message):
    repo = DatabaseRepository()
    data = repo.select(
        "select * from starboards where guild = ? and suggestion_id = ?",
        args = (guild.id, message.id)
    )
    return len(data) != 0


async def send_message_to_spotlight(spotlight: discord.TextChannel, message: discord.Message, starboard_id: int):
    
    author = message.author
    _content = message.content if len(message.content) < 1000 else message.content[:1000]
    _content += f"\n\n[**Jump to message!**]({message.jump_url})"

    embed = discord.Embed(
        color = Colors.blue,
        timestamp = datetime.utcnow(),
        description = _content
    )

    embed.set_author(
        name = f"{author}",
        icon_url = author.avatar
    )

    if len(message.attachments) > 0:
        embed.set_image(
            url = message.attachments[0].proxy_url
        )

    spotlight_message = await spotlight.send(
        content = f"{Emotes.sparkles} **{get_stars_amount(message) - 1}** | <#{spotlight.id}>",
        embed = embed
    )

    repo = DatabaseRepository()
    repo.general_statement(
        sql_statement = "insert into starboards values (?, ?, ?, ?)",
        args = (message.guild.id, starboard_id, message.id, spotlight_message.id)
    )
    
   

async def delete_message_from_spotlight(spotlight: discord.TextChannel, message_id: int, starboard_id: int):
    
    repo = DatabaseRepository()
    data = repo.select(
        "select * from starboards where guild = ? and suggestion_id = ?",
        args = (spotlight.guild.id, message_id)
    )

    for entry in data:
        spotlight_message_id = int(entry["spotlight_id"])
        spotlight_message = await spotlight.fetch_message(spotlight_message_id)
        await spotlight_message.delete()


    repo = DatabaseRepository()
    repo.delete(
        sql_statement = "delete from starboards where guild = ? and starboard_id = ? and suggestion_id = ?",
        args = (spotlight.guild.id, starboard_id, message_id)
    )


async def edit_spotlight_message(spotlight: discord.TextChannel, message: discord.Message, starboard_id: int):
    
    repo = DatabaseRepository()
    data = repo.select(
        "select * from starboards where guild = ? and suggestion_id = ?",
        args = (message.guild.id, message.id)
    )

    for entry in data:
        spotlight_message_id = int(entry["spotlight_id"])
        spotlight_message = await spotlight.fetch_message(spotlight_message_id)
        await spotlight_message.edit(
            embed = spotlight_message.embeds[0],
            content = f"{Emotes.sparkles} **{get_stars_amount(message) - 1}** | <#{spotlight.id}>"
        )
