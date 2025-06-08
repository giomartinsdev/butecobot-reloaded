import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import os
from dotenv import load_dotenv
import logging
from typing import Optional

# Load environment variables
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BALANCE_API_URL = os.getenv('BALANCE_API_URL', 'http://balance-api:5000')
CLIENT_API_URL = os.getenv('CLIENT_API_URL', 'http://client-api:5000')
COIN_API_URL = os.getenv('COIN_API_URL', 'http://coin-api:5000')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class ChorumeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Chorume Bot - Economy and Management System"
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
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="the economy 💰"
        )
        await self.change_presence(activity=activity)

bot = ChorumeBot()

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
        # Try to get existing user
        status, data = await make_api_request(
            session, 'GET', f"{CLIENT_API_URL}/client/discordId/{discord_id}"
        )
        
        if status == 200:
            return data
        elif status == 404:
            # Create new user
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

@bot.tree.command(name="register", description="Register yourself in the economy system")
async def register(interaction: discord.Interaction):
    """Register a user in the system."""
    await interaction.response.defer()
    
    user = await get_or_create_user(str(interaction.user.id), interaction.user.display_name)
    
    if user:
        embed = discord.Embed(
            title="✅ Registration Successful!",
            description=f"Welcome to the Chorume Economy, {interaction.user.mention}!",
            color=discord.Color.green()
        )
        embed.add_field(name="User ID", value=user.get('id', 'Unknown'), inline=False)
        embed.add_field(name="Discord ID", value=user.get('discordId', 'Unknown'), inline=True)
        embed.add_field(name="Name", value=user.get('name', 'Unknown'), inline=True)
    else:
        embed = discord.Embed(
            title="❌ Registration Failed",
            description="Failed to register. Please try again later.",
            color=discord.Color.red()
        )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="balance", description="Check your current balance")
async def balance(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Check balance for yourself or another user."""
    await interaction.response.defer()
    
    target_user = user if user else interaction.user
    discord_id = str(target_user.id)
    
    # Get user info first
    user_data = await get_or_create_user(discord_id, target_user.display_name)
    if not user_data:
        embed = discord.Embed(
            title="❌ User Not Found",
            description="User is not registered in the system.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Get balance
    async with aiohttp.ClientSession() as session:
        status, balance_data = await make_api_request(
            session, 'GET', f"{BALANCE_API_URL}/balance/{user_data['id']}"
        )
        
        if status == 200:
            balance_amount = balance_data.get('balance', 0)
            embed = discord.Embed(
                title="💰 Balance Information",
                color=discord.Color.blue()
            )
            embed.add_field(
                name=f"{target_user.display_name}'s Balance",
                value=f"**{balance_amount:,} coins** 🪙",
                inline=False
            )
            embed.set_thumbnail(url=target_user.display_avatar.url)
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve balance information.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="daily", description="Claim your daily coins")
async def daily(interaction: discord.Interaction):
    """Claim daily coins."""
    await interaction.response.defer()
    
    discord_id = str(interaction.user.id)
    user_data = await get_or_create_user(discord_id, interaction.user.display_name)
    
    if not user_data:
        embed = discord.Embed(
            title="❌ Registration Required",
            description="Please use `/register` first!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Claim daily coins
    async with aiohttp.ClientSession() as session:
        claim_data = {"clientId": user_data['id']}
        status, response = await make_api_request(
            session, 'POST', f"{COIN_API_URL}/daily-coins", claim_data
        )
        
        if status == 200:
            amount = response.get('amount', 0)
            embed = discord.Embed(
                title="🎉 Daily Coins Claimed!",
                description=f"You've received **{amount:,} coins**! 🪙",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="Next Claim",
                value="Come back tomorrow for more coins!",
                inline=False
            )
        elif status == 400:
            embed = discord.Embed(
                title="⏰ Already Claimed",
                description="You've already claimed your daily coins today!\nCome back tomorrow! ⏰",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to claim daily coins. Please try again later.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="transfer", description="Transfer coins to another user")
@app_commands.describe(
    recipient="The user to transfer coins to",
    amount="Amount of coins to transfer",
    description="Optional description for the transfer"
)
async def transfer(interaction: discord.Interaction, recipient: discord.Member, amount: int, description: str = "Transfer"):
    """Transfer coins between users."""
    await interaction.response.defer()
    
    if amount <= 0:
        embed = discord.Embed(
            title="❌ Invalid Amount",
            description="Transfer amount must be positive!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    if recipient.id == interaction.user.id:
        embed = discord.Embed(
            title="❌ Invalid Transfer",
            description="You cannot transfer coins to yourself!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Get both users
    sender = await get_or_create_user(str(interaction.user.id), interaction.user.display_name)
    receiver = await get_or_create_user(str(recipient.id), recipient.display_name)
    
    if not sender or not receiver:
        embed = discord.Embed(
            title="❌ User Not Found",
            description="One or both users are not registered.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    # Check sender's balance first
    async with aiohttp.ClientSession() as session:
        status, balance_data = await make_api_request(
            session, 'GET', f"{BALANCE_API_URL}/balance/{sender['id']}"
        )
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to check balance.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        current_balance = balance_data.get('balance', 0)
        if current_balance < amount:
            embed = discord.Embed(
                title="❌ Insufficient Funds",
                description=f"You have {current_balance:,} coins, but need {amount:,} coins.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Perform transfer
        transfer_data = {
            "senderId": sender['id'],
            "receiverId": receiver['id'],
            "amount": amount,
            "description": description
        }
        
        status, response = await make_api_request(
            session, 'POST', f"{BALANCE_API_URL}/balance/transaction", transfer_data
        )
        
        if status == 200:
            embed = discord.Embed(
                title="✅ Transfer Successful!",
                description=f"Transferred **{amount:,} coins** to {recipient.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Description", value=description, inline=False)
            embed.add_field(name="Remaining Balance", value=f"{current_balance - amount:,} coins", inline=True)
        else:
            embed = discord.Embed(
                title="❌ Transfer Failed",
                description="Failed to complete the transfer. Please try again.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="leaderboard", description="Show the top users by balance")
@app_commands.describe(limit="Number of users to show (max 20)")
async def leaderboard(interaction: discord.Interaction, limit: int = 10):
    """Show leaderboard of users by balance."""
    await interaction.response.defer()
    
    if limit > 20:
        limit = 20
    if limit < 1:
        limit = 10
    
    async with aiohttp.ClientSession() as session:
        # Get all users
        status, users = await make_api_request(session, 'GET', f"{CLIENT_API_URL}/client/")
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve user data.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # Get balances for all users
        user_balances = []
        for user in users:
            status, balance_data = await make_api_request(
                session, 'GET', f"{BALANCE_API_URL}/balance/{user['id']}"
            )
            if status == 200:
                balance = balance_data.get('balance', 0)
                user_balances.append((user, balance))
        
        # Sort by balance descending
        user_balances.sort(key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(
            title="🏆 Leaderboard - Top Users",
            color=discord.Color.gold()
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user, balance) in enumerate(user_balances[:limit]):
            rank = i + 1
            medal = medals[i] if i < 3 else f"{rank}."
            
            try:
                discord_user = bot.get_user(int(user['discordId']))
                display_name = discord_user.display_name if discord_user else user['name']
            except:
                display_name = user['name']
            
            embed.add_field(
                name=f"{medal} {display_name}",
                value=f"{balance:,} coins 🪙",
                inline=True
            )
        
        if not user_balances:
            embed.description = "No users found in the leaderboard."
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="history", description="View your transaction history")
@app_commands.describe(limit="Number of transactions to show (max 50)")
async def history(interaction: discord.Interaction, limit: int = 10):
    """Show user's transaction history."""
    await interaction.response.defer()
    
    if limit > 50:
        limit = 50
    if limit < 1:
        limit = 10
    
    discord_id = str(interaction.user.id)
    user_data = await get_or_create_user(discord_id, interaction.user.display_name)
    
    if not user_data:
        embed = discord.Embed(
            title="❌ Registration Required",
            description="Please use `/register` first!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        # Get balance operations
        status, operations = await make_api_request(
            session, 'GET', f"{BALANCE_API_URL}/balance/operations/{user_data['id']}"
        )
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve transaction history.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📊 Transaction History",
            description=f"Last {min(len(operations), limit)} transactions",
            color=discord.Color.blue()
        )
        
        # Sort by creation date (most recent first)
        operations.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        for operation in operations[:limit]:
            amount = operation.get('amount', 0)
            description = operation.get('description', 'No description')
            created_at = operation.get('createdAt', '')
            
            if amount > 0:
                amount_str = f"+{amount:,} coins 📈"
                color_emoji = "🟢"
            else:
                amount_str = f"{amount:,} coins 📉"
                color_emoji = "🔴"
            
            # Format date
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = dt.strftime('%m/%d %H:%M')
            except:
                date_str = "Unknown"
            
            embed.add_field(
                name=f"{color_emoji} {amount_str}",
                value=f"{description}\n`{date_str}`",
                inline=True
            )
        
        if not operations:
            embed.description = "No transactions found."
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="daily_history", description="View your daily coin claim history")
@app_commands.describe(limit="Number of claims to show (max 30)")
async def daily_history(interaction: discord.Interaction, limit: int = 10):
    """Show user's daily claim history."""
    await interaction.response.defer()
    
    if limit > 30:
        limit = 30
    if limit < 1:
        limit = 10
    
    discord_id = str(interaction.user.id)
    user_data = await get_or_create_user(discord_id, interaction.user.display_name)
    
    if not user_data:
        embed = discord.Embed(
            title="❌ Registration Required",
            description="Please use `/register` first!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        status, history_data = await make_api_request(
            session, 'GET', f"{COIN_API_URL}/daily-coins/history/{user_data['id']}?limit={limit}"
        )
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve daily claim history.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        total_claims = history_data.get('totalClaims', 0)
        total_earned = history_data.get('totalCoinsEarned', 0)
        history = history_data.get('history', [])
        
        embed = discord.Embed(
            title="📅 Daily Claim History",
            description=f"Total Claims: **{total_claims}** | Total Earned: **{total_earned:,} coins**",
            color=discord.Color.blue()
        )
        
        for claim in history[:limit]:
            claim_date = claim.get('claimDate', 'Unknown')
            amount = claim.get('amount', 0)
            
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(claim_date)
                date_str = dt.strftime('%B %d, %Y')
            except:
                date_str = claim_date
            
            embed.add_field(
                name=f"🗓️ {date_str}",
                value=f"+{amount:,} coins 🪙",
                inline=True
            )
        
        if not history:
            embed.description = "No daily claims found. Use `/daily` to start claiming!"
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="status", description="Check the status of all microservices")
async def status(interaction: discord.Interaction):
    """Check the health status of all microservices."""
    await interaction.response.defer()
    
    services = [
        ("Balance API", f"{BALANCE_API_URL}/health"),
        ("Client API", f"{CLIENT_API_URL}/health"),
        ("Coin API", f"{COIN_API_URL}/health")
    ]
    
    embed = discord.Embed(
        title="🔧 System Status",
        color=discord.Color.blue()
    )
    
    async with aiohttp.ClientSession() as session:
        for service_name, health_url in services:
            try:
                async with session.get(health_url, timeout=5) as response:
                    if response.status == 200:
                        status_emoji = "🟢"
                        status_text = "Online"
                    else:
                        status_emoji = "🟡"
                        status_text = f"Status: {response.status}"
            except:
                status_emoji = "🔴"
                status_text = "Offline"
            
            embed.add_field(
                name=f"{status_emoji} {service_name}",
                value=status_text,
                inline=True
            )
    
    embed.add_field(
        name="🤖 Bot Status",
        value="🟢 Online",
        inline=True
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="help", description="Show all available commands")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    logger.info(f"Help command requested by {interaction.user.display_name} ({interaction.user.id})")
    await interaction.response.defer()
    
    embed = discord.Embed(
        title="🤖 Chorume Bot - Commands",
        description="Here are all the available slash commands:",
        color=discord.Color.blue()
    )
    
    commands_info = [
        ("👤 **User Commands**", ""),
        ("/register", "Register yourself in the economy system"),
        ("/balance [user]", "Check your or another user's balance"),
        ("", ""),
        ("💰 **Economy Commands**", ""),
        ("/daily", "Claim your daily coins (once per day)"),
        ("/transfer <user> <amount> [description]", "Transfer coins to another user"),
        ("", ""),
        ("📊 **Information Commands**", ""),
        ("/leaderboard [limit]", "Show top users by balance"),
        ("/history [limit]", "View your transaction history"),
        ("/daily_history [limit]", "View your daily claim history"),
        ("", ""),
        ("🔧 **System Commands**", ""),
        ("/status", "Check microservices status"),
        ("/help", "Show this help message"),
    ]
    
    description_lines = []
    for command, desc in commands_info:
        if command and desc:
            description_lines.append(f"**{command}**\n{desc}")
        elif command:
            description_lines.append(f"\n{command}")
    
    embed.description = "\n".join(description_lines)
    
    embed.add_field(
        name="💡 Tips",
        value="• Use `/register` before using economy commands\n• Daily coins reset at midnight UTC\n• Check `/status` if something isn't working",
        inline=False
    )
    
    try:
        await interaction.followup.send(embed=embed)
        logger.info(f"Successfully sent help command response to {interaction.user.display_name}")
    except Exception as e:
        logger.error(f"Failed to send help command response: {e}")
        # Fallback to basic response
        try:
            await interaction.followup.send("Help command is temporarily unavailable. Please try again later.")
        except:
            pass

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle application command errors."""
    command_name = interaction.command.name if interaction.command else "unknown"
    user_info = f"{interaction.user.display_name} ({interaction.user.id})"
    logger.error(f"Command '{command_name}' raised an exception: {error} (User: {user_info})")
    
    embed = discord.Embed(
        title="❌ Command Error",
        description="An error occurred while processing your command.",
        color=discord.Color.red()
    )
    
    if isinstance(error, app_commands.CommandOnCooldown):
        embed.description = f"Command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    elif isinstance(error, app_commands.MissingPermissions):
        embed.description = "You don't have permission to use this command."
    else:
        embed.description = "An unexpected error occurred. Please try again later."
    
    try:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    except:
        pass

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        exit(1)
    
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
