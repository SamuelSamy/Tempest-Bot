from commands.guild_setup import Configure
from commands.help import Help
from commands.leveling import Leveling
from commands.moderation.mod_commands import Moderation
from commands.owner import Owner
from commands.starboard import Starboard
from commands.welcome import Welcome
from commands.moderation.auto_moderator import AutoModerator
from commands.moderation.auto_punish import AutoPunishments

from listeners.command_errors import CommandErrorHandler
from listeners.guild_setup import AutoSetup
from listeners.leveling import LevelingListeners
from listeners.moderation import AutoModeratorListeners
from listeners.welcome import WelcomeListener
from listeners.chat_logs import ChatLogs
from listeners.starboard import StarboardListeners


async def setup(bot):
    
    # Owner 
    await bot.add_cog(Owner(bot))

    # Error handler
    await bot.add_cog(CommandErrorHandler(bot))
    
    # Help
    await bot.add_cog(Help(bot))


    # Moderation
    await bot.add_cog(AutoModerator(bot))
    await bot.add_cog(AutoPunishments(bot))
    await bot.add_cog(Moderation(bot))
    await bot.add_cog(AutoModeratorListeners(bot))


    # Guild Setup
    await bot.add_cog(Configure(bot))
    await bot.add_cog(AutoSetup(bot))

    # Leveling
    await bot.add_cog(Leveling(bot))
    await bot.add_cog(LevelingListeners(bot))


    # Welcome
    await bot.add_cog(Welcome(bot))
    await bot.add_cog(WelcomeListener(bot))

    # Chat logs
    await bot.add_cog(ChatLogs(bot))

    # Starboard
    await bot.add_cog(Starboard(bot))
    await bot.add_cog(StarboardListeners(bot))

