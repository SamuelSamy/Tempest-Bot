import discord

from discord.ext import commands
from discord.ui import View, Button

from domain.enums.general import Colors, Emotes


# TODO make this actually work lol


class HelpDropDown(discord.ui.Select):

    def __init__(self, bot, default_key = "Moderation"):
        
        self.bot = bot

        options = [
            discord.SelectOption(
                label = "Configuration",
                value = "Configure",
                default = default_key == "Configure"
            ),
            discord.SelectOption(
                label = "Moderator",
                value = "Moderation",
                default = default_key == "Moderation"
            ),
            discord.SelectOption(
                label = "Leveling",
                value = "Leveling",
                default = default_key == "Leveling"
            ),
            discord.SelectOption(
                label = "Welcome",
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

    def __init__(self, page_index, total_commands, custom_id, label, bot, style = discord.ButtonStyle.blurple, disabled = True):

        self.bot = bot

        if custom_id.endswith("left"):
            if page_index != 0:  
                disabled = False
            


        if custom_id.endswith("right") and page_index != (total_commands // MAX_COMMANDS - (total_commands % MAX_COMMANDS == 0)):
            disabled = False

        super().__init__(
            custom_id = custom_id,
            label = label,
            style = style,
            disabled = disabled
        )

    async def callback(self, interaction: discord.Interaction):
        print(self.custom_id)
        page_index = 0
        print(interaction.message.components[1].values[0])
        key = "Configure"
        await interaction.message.edit(
            content = interaction.message.content,
            embed = generate_embed(self.bot, key),
            view = generate_view(self.bot, key, page_index)
        )



MAX_COMMANDS = 8

def handle_help(bot):
    return generate_embed(bot, "Configure"), generate_view(bot, "Configure")


def generate_view(bot, key, page_index = 0):
    view = View(timeout = None)    
    generate_buttons(bot, view, page_index, get_cmds_len(bot, key))
    view.add_item(HelpDropDown(bot, key))
    return view


def generate_buttons(bot, view, page_index, total_commands):

    view.add_item(HelpButton(page_index, total_commands, f"{page_index}help-dleft", "<<", bot = bot))
    view.add_item(HelpButton(page_index, total_commands, f"{page_index}help-left", "<", bot = bot))
    view.add_item(HelpButton(page_index, total_commands, f"{page_index}help-right", ">", bot = bot))
    view.add_item(HelpButton(page_index, total_commands, f"{page_index}help-dright", ">>", bot = bot))


def get_cmds_len(bot, key):
    cogs = bot.cogs
    current_cog = cogs[key]
    cmds = current_cog.get_commands()
    return len(cmds)


def generate_embed(bot, key, page_index = 0):

    cogs = bot.cogs
    current_cog = cogs[key]
    cmds = current_cog.get_commands()

    _description = ""


    for i in range(page_index, min(len(cmds), page_index + 8)):
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

    return embed
