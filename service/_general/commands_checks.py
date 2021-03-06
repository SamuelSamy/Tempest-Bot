from discord.ext import commands

from service._general.utils import is_staff
from repository.json_repo import ModerationRepo

OWNERS_IDS = [225629057172111362]

def is_admin():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or ctx.author.id in OWNERS_IDS

    return commands.check(predicate)


def has_staff_role():
    async def predicate(ctx):
        return ctx.guild is not None and (is_staff(ctx.guild, ctx.author) or (ctx.author.id in OWNERS_IDS))

    return commands.check(predicate)


def has_command_permissions(command):
    async def predicate(ctx):

        try:

            guild = ctx.guild
            user = ctx.author

            if user.id in OWNERS_IDS:
                return True


            member = guild.get_member(user.id)

            if member.guild_permissions.administrator:
                return True

            moderation_repo = ModerationRepo()
            guild_permissions = moderation_repo.get_staff_permissions(guild.id)
            allowed_roles = guild_permissions[command]


            for role_id in allowed_roles:
                actual_role = guild.get_role(role_id)

                if actual_role in member.roles:
                    return True

            return False

        except:
            return False

    return commands.check(predicate)


