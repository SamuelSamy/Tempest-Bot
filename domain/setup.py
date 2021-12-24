from commands.guild_setup import Configure
from commands.leveling import Leveling
from commands.moderation.mod_commands import Moderation
from commands.owner import Owner
from commands.welcome import Welcome
from commands.moderation.auto_moderator import AutoModerator
from commands.moderation.auto_punish import AutoPunishments

from listeners.info import Info
from listeners.command_errors import CommandErrorHandler
from listeners.guild_setup import AutoSetup
from listeners.leveling import LevelingListeners
from listeners.moderation import AutoModeratorListeners
from listeners.welcome import WelcomeListener


def setup(bot):
    # Owner 
    bot.add_cog(Owner(bot))


    # Error handler
    bot.add_cog(CommandErrorHandler(bot))


    # Info
    bot.add_cog(Info(bot))
    

    # Moderation
    bot.add_cog(AutoModerator(bot))
    bot.add_cog(AutoPunishments(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(AutoModeratorListeners(bot))


    # Guild Setup
    bot.add_cog(Configure(bot))
    bot.add_cog(AutoSetup(bot))

    # Leveling
    bot.add_cog(Leveling(bot))
    bot.add_cog(LevelingListeners(bot))


    # Welcome
    bot.add_cog(Welcome(bot))
    bot.add_cog(WelcomeListener(bot))


