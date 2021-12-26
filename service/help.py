import discord

from discord.ext import commands
from discord.ui import View, Button

from domain.enums.general import Colors, Emotes
from domain.exceptions import CustomException
from service._general.utils import get_prefix


bounds = {
    "Configure": "Configuration",
    "Moderation": "Moderator",
    "Leveling": "Leveling",
    "Welcome": "Welcome"
}


class HelpDropDown(discord.ui.Select):

    def __init__(self, bot, default_key):
        
        self.bot = bot

        options = [
            discord.SelectOption(
                label = bounds["Configure"],
                value = "Configure",
                default = default_key == "Configure"
            ),
            discord.SelectOption(
                label = bounds["Moderation"],
                value = "Moderation",
                default = default_key == "Moderation"
            ),
            discord.SelectOption(
                label = bounds["Leveling"],
                value = "Leveling",
                default = default_key == "Leveling"
            ),
            discord.SelectOption(
                label = bounds["Welcome"],
                value = "Welcome",
                default = default_key == "Welcome"
            )
        ]

        super().__init__(
            custom_id = "help-dropdown",
            options = options
        )
    
    async def callback(self, interaction: discord.Interaction):
        key = self.values[0]
        await interaction.message.edit(
            content = interaction.message.content,
            embed = generate_embed(self.bot, key),
            view = generate_view(self.bot, key)
        )


class HelpButton(discord.ui.Button):

    def __init__(self, page_index, max_index_page, custom_id, label, bot, style = discord.ButtonStyle.blurple, disabled = True):

        self.bot = bot
        self.max_index_page = max_index_page
        self.page_index = page_index

        if custom_id.endswith("left"):
            if page_index != 0:  
                disabled = False
            
        if custom_id.endswith("right") and page_index != max_index_page:
            disabled = False

        super().__init__(
            custom_id = custom_id,
            label = label,
            style = style,
            disabled = disabled
        )

    async def callback(self, interaction: discord.Interaction):

        args = self.custom_id.split("-")
        key = args[0]

        if "left" in args[1]:
            if "d" in args[1]:
                page_index = 0
            else:
                page_index = self.page_index - 1
        
        elif "right" in args[1]:
            if "d" in args[1]:
                page_index = self.max_index_page
            else:
                page_index = self.page_index + 1

        await interaction.message.edit(
            content = interaction.message.content,
            embed = generate_embed(self.bot, key, page_index),
            view = generate_view(self.bot, key, page_index)
        )



MAX_COMMANDS = 8

def handle_help(bot):
    return generate_embed(bot, "Configure"), generate_view(bot, "Configure")


def generate_view(bot, key, page_index = 0):
    view = View(timeout = None)    
    generate_buttons(bot, view, page_index, get_max_index_page(bot, key), key)
    view.add_item(HelpDropDown(bot, key))
    return view


def generate_buttons(bot, view, page_index, max_page, key):

    view.add_item(HelpButton(page_index, max_page, f"{key}-dleft", "<<", bot = bot))
    view.add_item(HelpButton(page_index, max_page, f"{key}-left", "<", bot = bot))
    view.add_item(HelpButton(page_index, max_page, f"{key}-right", ">", bot = bot))
    view.add_item(HelpButton(page_index, max_page, f"{key}-dright", ">>", bot = bot))


def get_max_index_page(bot, key):
    cogs = bot.cogs
    current_cog = cogs[key]
    cmds = current_cog.get_commands()
    total_commands = len(cmds)
    return total_commands // MAX_COMMANDS - (total_commands % MAX_COMMANDS == 0)


def generate_embed(bot, key, page_index = 0):

    cogs = bot.cogs
    current_cog = cogs[key]
    cmds = current_cog.get_commands()

    _description = ""


    for i in range(page_index * MAX_COMMANDS, min(len(cmds), (page_index + 1) * MAX_COMMANDS)):
        command = cmds[i]

        if isinstance(command, commands.Group):
            
            if command.usage is not None:
                _description += f"`{command.usage}`\n{Emotes.reply}{command.description}\n\n"
            
            for subcommand in command.walk_commands():
                if subcommand.parents[0] == command and subcommand.usage is not None:
                    _description += f"`{subcommand.usage}`\n{Emotes.reply}{subcommand.description}\n\n"
        
        elif command.usage is not None:
            _description += f"`{command.usage}`\n{Emotes.reply}{command.description}\n\n"


    embed = discord.Embed(
        color = Colors.blue,
        description = _description
    )

    embed.set_footer(
        text = f"Page {page_index + 1} / {get_max_index_page(bot, key) + 1}"
    )

    return embed


def handle_command_help(bot, invoker, command):  

    command = bot.get_command(command)

    if command is None or (command.cog_name == "Owner" and invoker.id != bot.owner_id):
        raise CustomException(f"{Emotes.not_found} This command does not exist! Please use `{get_prefix()}help` to view a full list of commands.")

    embed = discord.Embed(
        color = Colors.blue
    )
    
    embed.set_author(
        name = bot.user.name,
        icon_url = bot.user.display_avatar   
    )

    embed.add_field(
        name = f"{get_prefix()}{command}",
        value = command.description,
        inline = False
    )

    embed.add_field(
        name = f"Category",
        value = bounds[command.cog_name]
    )

    if command.usage is not None:
        embed.add_field(
            name = "Usage",
            value = f"`{command.usage}`",
            inline = True
        )

    if command.aliases is not None and len(command.aliases) != 0:
        embed.add_field(
            name = "Aliases",
            value = f"{str(command.aliases)[1:-1]}",
            inline = True
        )

    return embed