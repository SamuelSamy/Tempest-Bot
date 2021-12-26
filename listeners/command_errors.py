import time
import discord
import traceback
import sys

from discord.ext import commands

from domain.enums.general import Emotes

# https://gist.github.com/EvieePy/7822af90858ef65012ea500bcecf1612

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

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.reply(f"{Emotes.not_found} Missing required arguments!")

        elif isinstance(error, commands.BadUnionArgument):
            await ctx.reply(f"{Emotes.not_found} Invalid arguments!")
        
        elif isinstance(error, commands.UserNotFound) or isinstance(error, commands.MemberNotFound):
            await ctx.reply(f"{Emotes.not_found} The specified user is not in this server or does not exist!")


        elif isinstance(error, commands.BadArgument):
            await ctx.reply(f"{Emotes.not_found} Incorect arguments!")

        else:
            # All other Errors not returned come here. And we can just print the default TraceBack.
            error_id = f"{round(time.time())}{ctx.message.id}"

            await ctx.reply(f'{Emotes.wrong} Something went wrong.\n*Error ID: {error_id}*')
            

            error_channel = self.bot.get_channel(921429366007816212)

            message  = f"Guild ID: {ctx.guild.id}\n"
            message += f"Error ID: {error_id}\n"
            message += f'The command: `{ctx.command}` raised an error\n'
            message += f"Error type: {type(error)}\n"
            message += f"Short description: {error}\n"
            message += f"Error message:\n"

            lines = traceback.format_exception(type(error), error, error.__traceback__)
            for line in lines:
                message += line

            message = [message[i: i + 1536] for i in range(0, len(message), 1536)]

            for _message in message:
                await error_channel.send(f"```\n{_message}\n```")


            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)



def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))