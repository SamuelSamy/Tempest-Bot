import time
import discord
import traceback
import sys
import io

from discord.ext import commands

from domain.enums.general import Emotes
from service._general.utils import get_prefix


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
    
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)
        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.reply(f'{Emotes.no_entry} {ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):

            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure):
            
            if str(error) != "You do not own this bot.":
                await ctx.reply(f'{Emotes.no_entry}You can not use that command!')
        
        elif isinstance(error, commands.RoleNotFound):
            await ctx.reply(f"{Emotes.not_found } The specified role does not exist!")

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.reply(f"{Emotes.not_found } The specified channel does not exist!")

        elif isinstance(error, commands.BadUnionArgument) or isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"{Emotes.not_found} Invalid command usage\n{Emotes.invisible} Use `{get_prefix()}help {ctx.command}` for aditional help")
        
        elif isinstance(error, commands.UserNotFound) or isinstance(error, commands.MemberNotFound):
            await ctx.reply(f"{Emotes.not_found} The specified user is not in this server or does not exist!")


        else:
            
            error_id = f"{round(time.time())}{ctx.message.id}"

            await ctx.reply(f'{Emotes.wrong} Something went wrong.\n*Error ID: {error_id}*')
            

            error_channel = self.bot.get_channel(921429366007816212)

            message  = f"Guild ID: {ctx.guild.id}\n"
            message += f"Error ID: {error_id}\n"
            message += f'Command: `{ctx.command}` raised an error\n'
            message += f"Error type: {type(error)}\n"
            message += f"Short description: {error}\n"

            error_text =  ""
            lines = traceback.format_exception(type(error), error, error.__traceback__)
            for line in lines:
                error_text += f"{line}\n"
            error_text = io.StringIO(error_text)
            
            await error_channel.send(f"```\n{message}\n```", file = discord.File(fp = error_text, filename = f"{error_id}.txt"))


            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))