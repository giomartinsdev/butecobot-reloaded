from discord.ext import commands
import discord
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ChorumeBot(commands.Bot):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Chorume Bot - Sistema de Economia e Gerenciamento"
        )
        
    async def setup_hook(self):
        """Called when the bot is starting up."""
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info('------')
        
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="a economia 💰"
        )
        await self.change_presence(activity=activity)
