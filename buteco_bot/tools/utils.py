import discord
import aiohttp
from typing import Optional
from tools.constants import CLIENT_API_URL
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def make_api_request(session: aiohttp.ClientSession, method: str, url: str, json_data: dict = None):
    """Make an API request with error handling."""
    try:
        async with session.request(method, url, json=json_data) as response:
            if response.content_type == 'application/json':
                data = await response.json()
            else:
                data = await response.text()
            return response.status, data
    except aiohttp.ClientError as e:
        logger.error(f"API request failed: {e}")
        return None, str(e)

async def get_or_create_user(discord_id: str, username: str) -> Optional[dict]:
    """Get existing user or create new one."""
    async with aiohttp.ClientSession() as session:
        status, data = await make_api_request(
            session, 'GET', f"{CLIENT_API_URL}/client/discordId/{discord_id}"
        )
        
        if status == 200:
            return data
        elif status == 404:
            user_data = {
                "discordId": discord_id,
                "name": username
            }
            status, data = await make_api_request(
                session, 'POST', f"{CLIENT_API_URL}/client/", user_data
            )
            if status == 200:
                return data
    return None

def is_admin(user: discord.Member) -> bool:
    """Check if user has admin permissions."""
    return user.guild_permissions.administrator or user.guild_permissions.manage_guild
