import discord
from datetime import datetime

from domain.enums.general import Colors


def get_user_data(ctx, user):
        
    if user is None:
        user = ctx.author

    created = round((user.created_at - datetime(1970, 1, 1)).total_seconds())

    embed = discord.Embed(
        color = Colors.blue,
        description = f"<@{user.id}>"
    )

    embed.set_author(
        name = f"{user}", 
        icon_url = user.display_avatar
    )
    
    embed.add_field(
        name = 'Registered',
        value = f"<t:{created}> (<t:{created}:R>)"
    )

    embed.set_footer(
        text = f"ID: {user.id}"
    )

    return embed