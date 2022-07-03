import discord

from discord.ext import commands

from domain.enums.general import Colors, Emotes
from domain.exceptions import CustomException
from service._general.utils import get_prefix

MAX_COMMANDS = 8
TIMEOUT_TIME = 60 * 4

modules = {
    "Configure": "Configuration",
    "Moderation": "Moderator",
    "AutoModerator": "Auto Moderator",
    "AutoPunishments": "Auto Punishments",
    "Leveling": "Leveling",
    "Welcome": "Welcome",
    "Starboard": "Starboard"
}


class HelpDropDownView(discord.ui.View):

    def __init__(self, bot, key):
        super().__init__(
            timeout = TIMEOUT_TIME
        )
        self.add_item(HelpDropDown(bot, key))



class HelpDropDown(discord.ui.Select):

    def __init__(self, bot, default_key):
        
        self.bot = bot

        options = [ discord.SelectOption(label = modules[x], value = x, default = default_key == x) for x in modules.keys()]
            
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
        await interaction.response.defer()



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
            disabled = disabled,
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

        await interaction.response.defer()


def handle_help(bot):
    return generate_embed(bot, "Configure"), generate_view(bot, "Configure")


def generate_view(bot, key, page_index = 0):
    view = HelpDropDownView(bot, key)    
    generate_buttons(bot, view, page_index, get_max_index_page(bot, key), key)
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

    total_commands = 0
    for command in cmds:
        if command.usage is not None:
            total_commands += 1

        if isinstance(command, commands.Group):
            total_commands += len(list(command.walk_commands()))
    
    return total_commands // MAX_COMMANDS - (total_commands % MAX_COMMANDS == 0)


def generate_embed(bot, key, page_index = 0):
    cogs = bot.cogs
    current_cog = cogs[key]
    cmds = current_cog.get_commands()
    actual_commands = []

    for command in cmds:
        
        if command.usage is not None:
            actual_commands.append(command)

        if isinstance(command, commands.Group):
            actual_commands += list(command.walk_commands())
        
    _description = ""
    actual_commands.sort(key = lambda command: int(command.brief))

    for i in range(page_index * MAX_COMMANDS, min(len(actual_commands), (page_index + 1) * MAX_COMMANDS)):

        command = actual_commands[i]

        if command.usage is not None:
            _description += generate_help_command_string(command)

    embed = discord.Embed(
        color = Colors.blue,
        description = _description
    )

    embed.set_footer(
        text = f"Page {page_index + 1} / {get_max_index_page(bot, key) + 1}"
    )

    return embed


def generate_help_command_string(command):

    if command is None or command.usage is None:
        raise CustomException(f"{Emotes.not_found} The specified command does not exist!")

    text = f"`{command.usage}`\n{Emotes.reply}{command.description}"

    if command.aliases is not None and len(command.aliases) != 0:
        aliases = str(command.aliases)[1:-1].replace("'", "")
        text += f"\n{Emotes.invisible}Aliases: `{aliases}`"

    text += "\n\n"

    return text


def handle_command_help(bot, invoker, command):  

    command = bot.get_command(command)

    if command is None or command.usage is None or (command.cog_name == "Owner" and invoker.id != bot.owner_id):
        raise CustomException(f"{Emotes.not_found} This command does not exist!\n{Emotes.invisible} Use `{get_prefix()}help` to view a full list of commands.")

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
        value = modules[command.cog_name]
    )

    if command.usage is not None:
        embed.add_field(
            name = "Usage",
            value = f"`{command.usage}`",
            inline = True
        )

    if command.aliases is not None and len(command.aliases) != 0:
        _value = str(command.aliases)[1:-1].replace("'", "")
        embed.add_field(
            name = "Aliases",
            value = _value,
            inline = True
        )

    return embed