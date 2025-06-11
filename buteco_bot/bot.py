import logging
from models.ChorumeBot import ChorumeBot
from tools.constants import DISCORD_TOKEN
from commands.client import client_commands
from commands.coins import coins_commands
from commands.balance import balance_commands
from commands.bet import bet_commands
from commands.help import help_commands
from commands.genai import genai_commands


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
bot = ChorumeBot()

client_commands(bot)
coins_commands(bot)
balance_commands(bot)
bet_commands(bot)
help_commands(bot)
genai_commands(bot)

if not DISCORD_TOKEN:
    logger.error("DISCORD_TOKEN not found in environment variables!")
    exit(1)

logger.info("Starting Bot...")
bot.run(DISCORD_TOKEN)
