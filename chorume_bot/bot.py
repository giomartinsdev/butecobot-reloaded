import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
load_dotenv()
import os
import json
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

ECONOMY_API_URL = os.getenv("ECONOMY_API_URL")

class APIClient:
    """Client for making requests to other containers"""
    
    @staticmethod
    def make_request(url, method='GET', data=None):
        """Make HTTP request to API"""
        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, timeout=10)
            else:
                return None
            
            return response.json() if response.status_code < 400 else None
        except Exception as e:
            print(f"API request error: {e}")
            return None

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)

@bot.command(name='balance')
async def balance(ctx):
    """Check user's coin balance"""
    user_id = str(ctx.author.id)
    
    response = APIClient.make_request(f"{ECONOMY_API_URL}/coin/show?user_id={user_id}")
    
    if response:
        embed = discord.Embed(
            title="💰 Your Balance",
            color=0x00ff00
        )
        embed.add_field(name="Coins", value=f"{response['balance']}", inline=True)
        embed.add_field(name="Daily Available", value="✅ Yes" if response['can_claim_daily'] else "❌ No", inline=True)
        embed.set_footer(text=f"User ID: {user_id}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Error checking balance. Please try again.")

@bot.command(name='daily')
async def daily(ctx):
    """Claim daily coins"""
    user_id = str(ctx.author.id)
    
    data = {'user_id': user_id}
    response = APIClient.make_request(f"{ECONOMY_API_URL}/coin/get-daily", method='POST', data=data)
    
    if response:
        embed = discord.Embed(
            title="🎁 Daily Coins Claimed!",
            color=0x00ff00
        )
        embed.add_field(name="Amount", value=f"{response['amount']} coins", inline=True)
        embed.add_field(name="New Balance", value=f"{response['new_balance']} coins", inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ You have already claimed your daily coins today or there was an error.")

@bot.command(name='transfer')
async def transfer(ctx, member: discord.Member, amount: float):
    """Transfer coins to another user"""
    from_user = str(ctx.author.id)
    to_user = str(member.id)
    
    if amount <= 0:
        await ctx.send("❌ Amount must be positive.")
        return
    
    data = {
        'from_user': from_user,
        'to_user': to_user,
        'amount': amount
    }
    
    response = APIClient.make_request(f"{ECONOMY_API_URL}/coin/transfer", method='POST', data=data)
    
    if response:
        embed = discord.Embed(
            title="💸 Transfer Successful",
            color=0x00ff00
        )
        embed.add_field(name="From", value=ctx.author.mention, inline=True)
        embed.add_field(name="To", value=member.mention, inline=True)
        embed.add_field(name="Amount", value=f"{amount} coins", inline=True)
        embed.add_field(name="Your New Balance", value=f"{response['sender_new_balance']} coins", inline=False)
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Transfer failed. Check your balance and try again.")

@bot.command(name='airplane')
async def airplane(ctx, total_amount: float, *members: discord.Member):
    """Distribute coins among multiple users (Silvio Santos style)"""
    if total_amount <= 0:
        await ctx.send("❌ Amount must be positive.")
        return
    
    if len(members) < 2:
        await ctx.send("❌ Need at least 2 participants for airplane distribution.")
        return
    
    distributor = str(ctx.author.id)
    participants = [str(member.id) for member in members]
    
    data = {
        'total_amount': total_amount,
        'participants': participants,
        'distributor': distributor
    }
    
    response = APIClient.make_request(f"{ECONOMY_API_URL}/airplane/distribute", method='POST', data=data)
    
    if response:
        embed = discord.Embed(
            title="✈️ Airplane Distribution Complete!",
            description=f"Total distributed: {total_amount} coins",
            color=0xffd700
        )
        
        for dist in response['distributions']:
            user = bot.get_user(int(dist['user_id']))
            if user:
                embed.add_field(
                    name=f"{user.display_name}",
                    value=f"{dist['amount']} coins",
                    inline=True
                )
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Airplane distribution failed. Check your balance and try again.")

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """Show coin leaderboard"""
    response = APIClient.make_request(f"{ECONOMY_API_URL}/leaderboard")
    
    if response and response['leaderboard']:
        embed = discord.Embed(
            title="🏆 Coin Leaderboard",
            color=0xffd700
        )
        
        for entry in response['leaderboard'][:10]:
            user = bot.get_user(int(entry['user_id']))
            username = user.display_name if user else f"User {entry['user_id']}"
            
            embed.add_field(
                name=f"#{entry['rank']} {username}",
                value=f"{entry['balance']} coins",
                inline=False
            )
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Error fetching leaderboard.")
# Utility Commands
@bot.command(name='help_chorume')
async def help_chorume(ctx):
    """Show bot commands"""
    embed = discord.Embed(
        title="🤖 Chorume Bot Commands",
        description="Here are all available commands:",
        color=0x00ff00
    )
    
    embed.add_field(
        name="💰 Economy Commands",
        value="`!balance` - Check your coins\n"
              "`!daily` - Claim daily coins\n"
              "`!transfer @user amount` - Transfer coins\n"
              "`!airplane amount @user1 @user2...` - Distribute coins\n"
              "`!leaderboard` - Show top users",
        inline=False
    )
    
    embed.add_field(
        name="🎲 Betting Commands",
        value="`!bet type team1 team2 bet_team amount [odds]` - Create bet\n"
              "`!mybets [all/open/closed]` - Show your bets",
        inline=False
    )
    
    embed.add_field(
        name="🤖 AI Commands",
        value="`!ai prompt` - Generate text with AI\n"
              "`!aiimage prompt` - Generate image with AI",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='status')
async def status(ctx):
    """Check bot and API status"""
    embed = discord.Embed(
        title="📊 System Status",
        color=0x00ff00
    )
    
    # Check each API
    apis = [
        ("Bet API", BET_API_URL),
        ("Economy API", ECONOMY_API_URL),
        ("AI API", AI_API_URL)
    ]
    
    for name, url in apis:
        try:
            response = requests.get(f"{url}/health", timeout=5)
            status = "🟢 Online" if response.status_code == 200 else "🔴 Error"
        except:
            status = "🔴 Offline"
        
        embed.add_field(name=name, value=status, inline=True)
    
    embed.add_field(name="Bot", value="🟢 Online", inline=True)
    embed.set_footer(text=f"Checked at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    await ctx.send(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found. Use `!help_chorume` for available commands.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error: {error}")

if __name__ == '__main__':
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        exit(1)
    
    bot.run(token)

