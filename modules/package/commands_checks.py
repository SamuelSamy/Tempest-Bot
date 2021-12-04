from discord.ext import commands

from modules.package.utils import *
from modules.moderation.package.enums import *


def has_staff_role():

    async def predicate(ctx):
        return ctx.guild is not None and is_staff(ctx.guild, ctx.author)

    return commands.check(predicate)


def has_command_permissions(command):

    async def predicate(ctx):

        try:
            guild = ctx.guild
            user = ctx.author

            member = guild.get_member(user.id)

            if member.guild_permissions.administrator:
                return True

            guild_id = str(guild.id)

            mod_json = open_json("data/moderation.json")

            allowed_roles = mod_json[guild_id][ModFormat.permissions.value][command]

            for role_id in allowed_roles:
                actual_role = guild.get_role(role_id)

                if actual_role in member.roles:
                    return True

            return False

        except:
            return False

    return commands.check(predicate)