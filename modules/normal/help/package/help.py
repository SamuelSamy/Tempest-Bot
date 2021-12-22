import discord
import re

from discord.ext import commands
from modules.normal.package.enums import Colors, Emotes
from modules.normal.package.utils import get_prefix


class CustomHelpCommand(commands.HelpCommand):
    

    def __init__(self):
        super().__init__()
        self.prefix = get_prefix()


    async def send_bot_help(self, mapping):

        embed = discord.Embed(
            color = Colors.blue.value
        )

        embed.set_author(
            name = "Bura's Modules",
            icon_url = "https://cdn.discordapp.com/avatars/914549816330170388/ccb4759c2a6ff6462869003c765a37b9.webp"
        )

        for cog in mapping:
            if cog is not None and len(cog.get_commands()) > 0:
                _name = re.sub(r"(\w)([A-Z])", r"\1 \2", cog.qualified_name)
                
                if _name.lower() != "owner":
                    embed.add_field(
                        name = f"{_name}",
                        value = f"`{self.prefix}help {cog.qualified_name}`",
                        inline = False
                    )

        await self.get_destination().send(embed = embed)


    async def send_cog_help(self, cog):

        if len(cog.get_commands()) == 0:
            await self.get_destination().send(f"{Emotes.wrong.value} No module found with the specified name")
        else:

            _description = ""

            embed = discord.Embed(
                color = Colors.blue.value
            )

            embed.set_author(
                name = f"{cog.qualified_name} Module",
            )

            for command in cog.get_commands():
                
                if isinstance(command, commands.Group):

                    for subcommand in command.walk_commands():
                        if subcommand.parents[0] == command and subcommand.usage is not None:
                            _description += f"`{subcommand.usage}`\n{Emotes.reply.value}{subcommand.description}\n\n"
                
                elif command.usage is not None:
                    _description += f"`{command.usage}`\n{Emotes.reply.value}{command.description}\n\n"

            embed.description = _description

            await self.get_destination().send(embed = embed)
    


    async def send_group_help(self, group):
        await self.get_destination().send(f"{Emotes.wrong.value} No module found with the specified name")
        return


    async def send_command_help(self, command):
        await self.get_destination().send(f"{Emotes.wrong.value} No module found with the specified name")
        return