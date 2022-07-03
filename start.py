from domain.bot import Bot
from domain.config import Config

config = Config()
bot = Bot(config.token, config.prefix)
bot.run_bot()
