import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
from dotenv import load_dotenv
import logging
from typing import Optional

load_dotenv()

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

@bot.tree.command(name="register", description="Registre-se no sistema de economia")
async def register(interaction: discord.Interaction):
    """Register a user in the system."""
    await interaction.response.defer()
    
    user = await get_or_create_user(str(interaction.user.id), interaction.user.display_name)
    
    if user:
        embed = discord.Embed(
            title="✅ Registro Realizado com Sucesso!",
            description=f"Bem-vindo à Economia Chorume, {interaction.user.mention}!",
            color=discord.Color.green()
        )
        embed.add_field(name="ID do Usuário", value=user.get('id', 'Desconhecido'), inline=False)
        embed.add_field(name="Discord ID", value=user.get('discordId', 'Desconhecido'), inline=True)
        embed.add_field(name="Nome", value=user.get('name', 'Desconhecido'), inline=True)
    else:
        embed = discord.Embed(
            title="❌ Falha no Registro",
            description="Falha ao registrar. Tente novamente mais tarde.",
            color=discord.Color.red()
        )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="balance", description="Verifique seu saldo atual")
async def balance(interaction: discord.Interaction, user: Optional[discord.Member] = None):
    """Check balance for yourself or another user."""
    await interaction.response.defer()
    
    target_user = user if user else interaction.user
    discord_id = str(target_user.id)
    
    user_data = await get_or_create_user(discord_id, target_user.display_name)
    if not user_data:
        embed = discord.Embed(
            title="❌ Usuário Não Encontrado",
            description="Usuário não está registrado no sistema.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        status, balance_data = await make_api_request(
            session, 'GET', f"{BALANCE_API_URL}/balance/{user_data['id']}"
        )
        
        if status == 200:
            balance_amount = balance_data.get('balance', 0)
            embed = discord.Embed(
                title="💰 Informações do Saldo",
                color=discord.Color.blue()
            )
            embed.add_field(
                name=f"Saldo de {target_user.display_name}",
                value=f"**{balance_amount:,} moedas** 🪙",
                inline=False
            )
            embed.set_thumbnail(url=target_user.display_avatar.url)
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao obter informações do saldo.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="daily", description="Colete suas moedas diárias")
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
    
    async with aiohttp.ClientSession() as session:
        claim_data = {"clientId": user_data['id']}
        status, response = await make_api_request(
            session, 'POST', f"{COIN_API_URL}/daily-coins", claim_data
        )
        
        if status == 200:
            amount = response.get('amount', 0)
            embed = discord.Embed(
                title="🎉 Moedas Diárias Coletadas!",
                description=f"Você recebeu **{amount:,} moedas**! 🪙",
                color=discord.Color.gold()
            )
            embed.add_field(
                name="Próxima Coleta",
                value="Volte amanhã para mais moedas!",
                inline=False
            )
        elif status == 400:
            embed = discord.Embed(
                title="⏰ Já Coletado",
                description="Você já coletou suas moedas diárias hoje!\nVolte amanhã! ⏰",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao coletar moedas diárias. Tente novamente mais tarde.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="transfer", description="Transfira moedas para outro usuário")
@app_commands.describe(
    recipient="O usuário para quem transferir moedas",
    amount="Quantidade de moedas para transferir",
    description="Descrição opcional para a transferência"
)
async def transfer(interaction: discord.Interaction, recipient: discord.Member, amount: int, description: str = "Transfer"):
    """Transfer coins between users."""
    await interaction.response.defer()
    
    if amount <= 0:
        embed = discord.Embed(
            title="❌ Valor Inválido",
            description="O valor da transferência deve ser positivo!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    if recipient.id == interaction.user.id:
        embed = discord.Embed(
            title="❌ Transferência Inválida",
            description="Você não pode transferir moedas para si mesmo!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    sender = await get_or_create_user(str(interaction.user.id), interaction.user.display_name)
    receiver = await get_or_create_user(str(recipient.id), recipient.display_name)
    
    if not sender or not receiver:
        embed = discord.Embed(
            title="❌ Usuário Não Encontrado",
            description="Um ou ambos os usuários não estão registrados.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        status, balance_data = await make_api_request(
            session, 'GET', f"{BALANCE_API_URL}/balance/{sender['id']}"
        )
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao verificar saldo.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        current_balance = balance_data.get('balance', 0)
        if current_balance < amount:
            embed = discord.Embed(
                title="❌ Saldo Insuficiente",
                description=f"Você tem {current_balance:,} moedas, mas precisa de {amount:,} moedas.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
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
                title="✅ Transferência Realizada com Sucesso!",
                description=f"Transferiu **{amount:,} moedas** para {recipient.mention}",
                color=discord.Color.green()
            )
            embed.add_field(name="Descrição", value=description, inline=False)
            embed.add_field(name="Saldo Restante", value=f"{current_balance - amount:,} moedas", inline=True)
        else:
            embed = discord.Embed(
                title="❌ Falha na Transferência",
                description="Falha ao completar a transferência. Tente novamente.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="leaderboard", description="Mostre os melhores usuários por saldo")
@app_commands.describe(limit="Número de usuários para mostrar (máximo 20)")
async def leaderboard(interaction: discord.Interaction, limit: int = 10):
    """Show leaderboard of users by balance."""
    await interaction.response.defer()
    
    if limit > 20:
        limit = 20
    if limit < 1:
        limit = 10
    
    async with aiohttp.ClientSession() as session:
        status, users = await make_api_request(session, 'GET', f"{CLIENT_API_URL}/client/")
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao obter dados dos usuários.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        user_balances = []
        for user in users:
            status, balance_data = await make_api_request(
                session, 'GET', f"{BALANCE_API_URL}/balance/{user['id']}"
            )
            if status == 200:
                balance = balance_data.get('balance', 0)
                user_balances.append((user, balance))
        
        user_balances.sort(key=lambda x: x[1], reverse=True)
        
        embed = discord.Embed(
            title="🏆 Ranking - Melhores Usuários",
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
                value=f"{balance:,} moedas 🪙",
                inline=True
            )
        
        if not user_balances:
            embed.description = "Nenhum usuário encontrado no ranking."
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="history", description="Veja seu histórico de transações")
@app_commands.describe(limit="Número de transações para mostrar (máximo 50)")
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
            title="❌ Registro Necessário",
            description="Use `/register` primeiro!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        status, operations = await make_api_request(
            session, 'GET', f"{BALANCE_API_URL}/balance/operations/{user_data['id']}"
        )
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao obter histórico de transações.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📊 Histórico de Transações",
            description=f"Últimas {min(len(operations), limit)} transações",
            color=discord.Color.blue()
        )
        
        operations.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
        
        for operation in operations[:limit]:
            amount = operation.get('amount', 0)
            description = operation.get('description', 'Sem descrição')
            created_at = operation.get('createdAt', '')
            
            if amount > 0:
                amount_str = f"+{amount:,} moedas 📈"
                color_emoji = "🟢"
            else:
                amount_str = f"{amount:,} moedas 📉"
                color_emoji = "🔴"
            
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_str = dt.strftime('%d/%m %H:%M')
            except:
                date_str = "Desconhecido"
            
            embed.add_field(
                name=f"{color_emoji} {amount_str}",
                value=f"{description}\n`{date_str}`",
                inline=True
            )
        
        if not operations:
            embed.description = "Nenhuma transação encontrada."
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="daily_history", description="Veja seu histórico de coletas diárias")
@app_commands.describe(limit="Número de coletas para mostrar (máximo 30)")
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
            title="❌ Registro Necessário",
            description="Use `/register` primeiro!",
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
                title="❌ Erro",
                description="Falha ao obter histórico de coletas diárias.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        total_claims = history_data.get('totalClaims', 0)
        total_earned = history_data.get('totalCoinsEarned', 0)
        history = history_data.get('history', [])
        
        embed = discord.Embed(
            title="📅 Histórico de Coletas Diárias",
            description=f"Total de Coletas: **{total_claims}** | Total Ganho: **{total_earned:,} moedas**",
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
                value=f"+{amount:,} moedas 🪙",
                inline=True
            )
        
        if not history:
            embed.description = "Nenhuma coleta diária encontrada. Use `/daily` para começar a coletar!"
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="status", description="Verifique o status de todos os microserviços")
async def status(interaction: discord.Interaction):
    """Check the health status of all microservices."""
    await interaction.response.defer()
    
    services = [
        ("Balance API", f"{BALANCE_API_URL}/health"),
        ("Client API", f"{CLIENT_API_URL}/health"),
        ("Coin API", f"{COIN_API_URL}/health")
    ]
    
    embed = discord.Embed(
        title="🔧 Status do Sistema",
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
        name="🤖 Status do Bot",
        value="🟢 Online",
        inline=True
    )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="help", description="Mostre todos os comandos disponíveis")
async def help_command(interaction: discord.Interaction):
    """Show help information."""
    logger.info(f"Help command requested by {interaction.user.display_name} ({interaction.user.id})")
    await interaction.response.defer()
    
    embed = discord.Embed(
        title="🤖 Chorume Bot - Comandos",
        description="Aqui estão todos os comandos slash disponíveis:",
        color=discord.Color.blue()
    )
    
    commands_info = [
        ("👤 **Comandos de Usuário**", ""),
        ("/register", "Registre-se no sistema de economia"),
        ("/balance [usuário]", "Verifique seu saldo ou de outro usuário"),
        ("", ""),
        ("💰 **Comandos de Economia**", ""),
        ("/daily", "Colete suas moedas diárias (uma vez por dia)"),
        ("/transfer <usuário> <valor> [descrição]", "Transfira moedas para outro usuário"),
        ("", ""),
        ("📊 **Comandos de Informação**", ""),
        ("/leaderboard [limite]", "Mostre os melhores usuários por saldo"),
        ("/history [limite]", "Veja seu histórico de transações"),
        ("/daily_history [limite]", "Veja seu histórico de coletas diárias"),
        ("", ""),
        ("🔧 **Comandos do Sistema**", ""),
        ("/status", "Verifique o status dos microserviços"),
        ("/help", "Mostre esta mensagem de ajuda"),
    ]
    
    description_lines = []
    for command, desc in commands_info:
        if command and desc:
            description_lines.append(f"**{command}**\n{desc}")
        elif command:
            description_lines.append(f"\n{command}")
    
    embed.description = "\n".join(description_lines)
    
    embed.add_field(
        name="💡 Dicas",
        value="• Use `/register` antes de usar comandos de economia\n• Moedas diárias resetam à meia-noite UTC\n• Verifique `/status` se algo não estiver funcionando",
        inline=False
    )
    
    try:
        await interaction.followup.send(embed=embed)
        logger.info(f"Successfully sent help command response to {interaction.user.display_name}")
    except Exception as e:
        logger.error(f"Failed to send help command response: {e}")
        try:
            await interaction.followup.send("Comando de ajuda temporariamente indisponível. Tente novamente mais tarde.")
        except:
            pass

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle application command errors."""
    command_name = interaction.command.name if interaction.command else "unknown"
    user_info = f"{interaction.user.display_name} ({interaction.user.id})"
    logger.error(f"Command '{command_name}' raised an exception: {error} (User: {user_info})")
    
    embed = discord.Embed(
        title="❌ Erro no Comando",
        description="Ocorreu um erro ao processar seu comando.",
        color=discord.Color.red()
    )
    
    if isinstance(error, app_commands.CommandOnCooldown):
        embed.description = f"Comando em cooldown. Tente novamente em {error.retry_after:.2f} segundos."
    elif isinstance(error, app_commands.MissingPermissions):
        embed.description = "Você não tem permissão para usar este comando."
    else:
        embed.description = "Ocorreu um erro inesperado. Tente novamente mais tarde."
    
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
