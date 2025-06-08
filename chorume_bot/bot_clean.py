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
BET_API_URL = os.getenv('BET_API_URL', 'http://bet-api:5000')

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

# ===== HELPER FUNCTIONS =====

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

async def check_admin_permission(interaction: discord.Interaction) -> bool:
    """Check admin permission and send error if not admin."""
    if not is_admin(interaction.user):
        embed = discord.Embed(
            title="❌ Permissão Negada",
            description="Apenas administradores podem usar este comando.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return False
    return True

async def check_user_registration(interaction: discord.Interaction) -> Optional[dict]:
    """Check if user is registered and return user data."""
    discord_id = str(interaction.user.id)
    user_data = await get_or_create_user(discord_id, interaction.user.display_name)
    
    if not user_data:
        embed = discord.Embed(
            title="❌ Registro Necessário",
            description="Use `/register` primeiro!",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return None
    return user_data

async def find_bet_by_partial_id(session: aiohttp.ClientSession, partial_id: str) -> Optional[str]:
    """Find full bet ID from partial ID."""
    if len(partial_id) >= 36:  # Already full ID
        return partial_id
    
    status, response = await make_api_request(
        session, 'GET', f"{BET_API_URL}/bet/active"
    )
    
    if status == 200:
        active_bets = response.get('active_bets', [])
        for bet in active_bets:
            if bet.get('bet_id', '').startswith(partial_id):
                return bet.get('bet_id')
    return None

async def send_bet_not_found_error(interaction: discord.Interaction, bet_id: str):
    """Send standard bet not found error message."""
    embed = discord.Embed(
        title="❌ Aposta Não Encontrada",
        description=f"Não foi possível encontrar a aposta com ID `{bet_id}`.",
        color=discord.Color.red()
    )
    await interaction.followup.send(embed=embed)

# ===== USER COMMANDS =====

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

# ===== ECONOMY COMMANDS =====

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
                description="Você já coletou suas moedas diárias hoje. Volte amanhã!",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao coletar moedas diárias. Tente novamente.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

# ===== BETTING COMMANDS =====

@bot.tree.command(name="bet_create", description="Criar uma nova aposta")
@app_commands.describe(
    title="Título da aposta",
    description="Descrição da aposta",
    option1="Primeira opção",
    option2="Segunda opção"
)
async def bet_create(interaction: discord.Interaction, title: str, description: str, option1: str, option2: str):
    """Create a new bet (Admin only)."""
    await interaction.response.defer()
    
    if not await check_admin_permission(interaction):
        return
    
    # Validate inputs
    if len(title) > 100:
        embed = discord.Embed(
            title="❌ Título Muito Longo",
            description="O título deve ter no máximo 100 caracteres.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    if len(description) > 500:
        embed = discord.Embed(
            title="❌ Descrição Muito Longa",
            description="A descrição deve ter no máximo 500 caracteres.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        bet_data = {
            "title": title,
            "description": description,
            "choices": [
                {"name": option1},
                {"name": option2}
            ],
            "created_by": str(interaction.user.id)
        }
        
        status, response = await make_api_request(
            session, 'POST', f"{BET_API_URL}/bet/create", bet_data
        )
        
        if status == 200:
            bet_id = response.get('bet_id', 'N/A')
            embed = discord.Embed(
                title="🎰 Aposta Criada com Sucesso!",
                description=f"**{title}**\n{description}",
                color=discord.Color.green()
            )
            embed.add_field(name="🅰️ Opção 1", value=option1, inline=True)
            embed.add_field(name="🅱️ Opção 2", value=option2, inline=True)
            embed.add_field(name="📋 ID da Aposta", value=f"`{bet_id}`", inline=False)
        else:
            error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
            embed = discord.Embed(
                title="❌ Erro ao Criar Aposta",
                description=error_msg,
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="bet_list", description="Listar todas as apostas ativas")
async def bet_list(interaction: discord.Interaction):
    """List all active bets."""
    await interaction.response.defer()
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_api_request(
            session, 'GET', f"{BET_API_URL}/bet/active"
        )
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao obter lista de apostas ativas.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        active_bets = response.get('active_bets', [])
        
        if not active_bets:
            embed = discord.Embed(
                title="🎰 Apostas Ativas",
                description="Nenhuma aposta ativa no momento.",
                color=discord.Color.blue()
            )
        else:
            embed = discord.Embed(
                title="🎰 Apostas Ativas",
                description=f"Encontradas {len(active_bets)} apostas ativas:",
                color=discord.Color.blue()
            )
            
            for bet in active_bets[:10]:  # Limit to 10 bets
                choices_text = " vs ".join([choice['name'] for choice in bet.get('choices', [])])
                embed.add_field(
                    name=f"🎯 {bet['title']}",
                    value=f"**ID:** `{bet['bet_id']}`\n**Opções:** {choices_text}\n**Pool:** {bet.get('total_pool', 0):,} moedas",
                    inline=False
                )
            
            if len(active_bets) > 10:
                embed.set_footer(text=f"Mostrando 10 de {len(active_bets)} apostas ativas")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="bet_info", description="Ver detalhes de uma aposta específica")
@app_commands.describe(bet_id="ID da aposta para ver detalhes")
async def bet_info(interaction: discord.Interaction, bet_id: str):
    """Get detailed information about a specific bet."""
    await interaction.response.defer()
    
    async with aiohttp.ClientSession() as session:
        # Try to find full ID if partial ID provided
        full_id = await find_bet_by_partial_id(session, bet_id)
        if not full_id:
            await send_bet_not_found_error(interaction, bet_id)
            return
        
        status, response = await make_api_request(
            session, 'GET', f"{BET_API_URL}/bet/{full_id}"
        )
        
        if status == 404:
            await send_bet_not_found_error(interaction, bet_id)
            return
        elif status != 200:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao obter informações da aposta.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        bet = response.get('bet', {})
        choice_stats = response.get('choice_stats', {})
        total_bets = response.get('total_bets', 0)
        
        status_emojis = {
            "active": "🟢 Ativa",
            "finished": "🏁 Finalizada",
            "cancelled": "❌ Cancelada"
        }
        
        embed = discord.Embed(
            title=f"🎰 {bet['title']}",
            description=bet['description'],
            color=discord.Color.blue()
        )
        
        embed.add_field(name="ID", value=f"`{bet['bet_id']}`", inline=True)
        embed.add_field(name="Status", value=status_emojis.get(bet['status'], bet['status']), inline=True)
        embed.add_field(name="Pool Total", value=f"{bet.get('total_pool', 0):,} moedas", inline=True)
        embed.add_field(name="Total de Apostas", value=str(total_bets), inline=True)
        
        # Show choice statistics
        for choice_id, stats in choice_stats.items():
            choice_name = stats['name']
            total_amount = stats['total_amount']
            bet_count = stats['bet_count']
            
            percentage = (total_amount / bet.get('total_pool', 1)) * 100 if bet.get('total_pool', 0) > 0 else 0
            
            embed.add_field(
                name=f"{'🅰️' if choice_id == '1' else '🅱️'} {choice_name}",
                value=f"{total_amount:,} moedas ({percentage:.1f}%)\n{bet_count} apostadores",
                inline=True
            )
        
        if bet['status'] == 'finished' and bet.get('winning_choice'):
            winning_choice_name = next(
                (choice['name'] for choice in bet.get('choices', []) 
                 if choice['choice_id'] == bet['winning_choice']), 
                "Desconhecida"
            )
            embed.add_field(
                name="🏆 Opção Vencedora",
                value=winning_choice_name,
                inline=False
            )
        
        try:
            creator = bot.get_user(int(bet['created_by']))
            creator_name = creator.display_name if creator else "Administrador"
        except:
            creator_name = "Administrador"
        
        embed.set_footer(text=f"Criado por {creator_name}")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="bet_place", description="Fazer uma aposta")
@app_commands.describe(
    bet_id="ID da aposta",
    choice="Opção para apostar (1 ou 2)",
    amount="Quantidade de moedas para apostar"
)
async def bet_place(interaction: discord.Interaction, bet_id: str, choice: int, amount: int):
    """Place a bet on a specific choice."""
    await interaction.response.defer()
    
    user_data = await check_user_registration(interaction)
    if not user_data:
        return
    
    if choice not in [1, 2]:
        embed = discord.Embed(
            title="❌ Opção Inválida",
            description="A opção deve ser 1 ou 2.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    if amount <= 0:
        embed = discord.Embed(
            title="❌ Valor Inválido",
            description="O valor da aposta deve ser positivo.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        # Try to find full ID if partial ID provided
        full_id = await find_bet_by_partial_id(session, bet_id)
        if not full_id:
            await send_bet_not_found_error(interaction, bet_id)
            return
        
        bet_data = {
            "user_id": user_data['id'],
            "choice_id": str(choice),
            "amount": amount
        }
        
        status, response = await make_api_request(
            session, 'POST', f"{BET_API_URL}/bet/{full_id}/place", bet_data
        )
        
        if status == 200:
            embed = discord.Embed(
                title="🎰 Aposta Realizada com Sucesso!",
                description=f"Você apostou **{amount:,} moedas** na opção {choice}",
                color=discord.Color.green()
            )
        elif status == 400:
            error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
            embed = discord.Embed(
                title="❌ Erro na Aposta",
                description=error_msg,
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="❌ Erro na Aposta",
                description="Falha ao realizar a aposta. Tente novamente.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="bet_finalize", description="Finalizar uma aposta e distribuir prêmios (Admin)")
@app_commands.describe(
    bet_id="ID da aposta para finalizar",
    winning_choice="Opção vencedora (1 ou 2)"
)
async def bet_finalize(interaction: discord.Interaction, bet_id: str, winning_choice: int):
    """Finalize a bet and distribute prizes (Admin only)."""
    await interaction.response.defer()
    
    if not await check_admin_permission(interaction):
        return
    
    if winning_choice not in [1, 2]:
        embed = discord.Embed(
            title="❌ Opção Inválida",
            description="A opção vencedora deve ser 1 ou 2.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)
        return
    
    async with aiohttp.ClientSession() as session:
        # Try to find full ID if partial ID provided
        full_id = await find_bet_by_partial_id(session, bet_id)
        if not full_id:
            await send_bet_not_found_error(interaction, bet_id)
            return
        
        # Get bet info first
        status, bet_response = await make_api_request(
            session, 'GET', f"{BET_API_URL}/bet/{full_id}"
        )
        
        if status == 404:
            await send_bet_not_found_error(interaction, bet_id)
            return
        
        finalize_data = {
            "winning_choice": str(winning_choice),
            "admin_id": str(interaction.user.id)
        }
        
        status, response = await make_api_request(
            session, 'POST', f"{BET_API_URL}/bet/{full_id}/finalize", finalize_data
        )
        
        if status == 200:
            bet_info = bet_response.get('bet', {})
            choice_name = next(
                (c['name'] for c in bet_info.get('choices', []) if c['choice_id'] == str(winning_choice)),
                f"Opção {winning_choice}"
            )
            
            total_pool = response.get('total_pool', 0)
            winners_count = response.get('winners_count', 0)
            distributions = response.get('distributions', [])
            
            embed = discord.Embed(
                title="🏁 Aposta Finalizada!",
                description=f"**{bet_info.get('title', 'Aposta')}** foi finalizada.",
                color=discord.Color.gold()
            )
            embed.add_field(name="Opção Vencedora", value=f"{'🅰️' if winning_choice == 1 else '🅱️'} {choice_name}", inline=True)
            embed.add_field(name="Pool Total", value=f"{total_pool:,} moedas", inline=True)
            embed.add_field(name="Vencedores", value=str(winners_count), inline=True)
            
            if winners_count > 0:
                embed.add_field(
                    name="💰 Prêmios Distribuídos",
                    value=f"Os prêmios foram distribuídos proporcionalmente entre {winners_count} vencedores!",
                    inline=False
                )
            else:
                embed.add_field(
                    name="😞 Sem Vencedores",
                    value="Ninguém apostou na opção vencedora. O pool foi perdido.",
                    inline=False
                )
                
        elif status == 400:
            error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
            embed = discord.Embed(
                title="❌ Erro ao Finalizar",
                description=error_msg,
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="❌ Falha ao Finalizar",
                description="Falha ao finalizar a aposta. Tente novamente mais tarde.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="bet_cancel", description="Cancelar uma aposta e reembolsar apostadores (Admin)")
@app_commands.describe(bet_id="ID da aposta para cancelar")
async def bet_cancel(interaction: discord.Interaction, bet_id: str):
    """Cancel a bet and refund all bettors (Admin only)."""
    await interaction.response.defer()
    
    if not await check_admin_permission(interaction):
        return
    
    async with aiohttp.ClientSession() as session:
        # Try to find full ID if partial ID provided
        full_id = await find_bet_by_partial_id(session, bet_id)
        if not full_id:
            await send_bet_not_found_error(interaction, bet_id)
            return
        
        # Get bet info first
        status, bet_response = await make_api_request(
            session, 'GET', f"{BET_API_URL}/bet/{full_id}"
        )
        
        if status == 404:
            await send_bet_not_found_error(interaction, bet_id)
            return
        
        status, response = await make_api_request(
            session, 'DELETE', f"{BET_API_URL}/bet/{full_id}/cancel?admin_id={interaction.user.id}"
        )
        
        if status == 200:
            bet_info = bet_response.get('bet', {})
            refunds_count = response.get('refunds_count', 0)
            refunds = response.get('refunds', [])
            
            embed = discord.Embed(
                title="❌ Aposta Cancelada",
                description=f"**{bet_info.get('title', 'Aposta')}** foi cancelada e todos os valores foram reembolsados.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="📊 Reembolsos",
                value=f"**Apostas Reembolsadas:** {refunds_count}\n**Total Reembolsado:** {sum(r['amount'] for r in refunds):,} moedas",
                inline=False
            )
        else:
            error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
            embed = discord.Embed(
                title="❌ Erro ao Cancelar",
                description=error_msg,
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="my_bets", description="Ver suas apostas atuais e históricas")
async def my_bets(interaction: discord.Interaction):
    """View user's current and historical bets."""
    await interaction.response.defer()
    
    user_data = await check_user_registration(interaction)
    if not user_data:
        return
    
    async with aiohttp.ClientSession() as session:
        status, response = await make_api_request(
            session, 'GET', f"{BET_API_URL}/bet/user/{user_data['id']}"
        )
        
        if status == 200:
            bets = response.get('bets', [])
            
            if not bets:
                embed = discord.Embed(
                    title="🎰 Suas Apostas",
                    description="Você ainda não fez nenhuma aposta.",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="🎰 Suas Apostas",
                    description=f"**{len(bets)} apostas encontradas:**",
                    color=discord.Color.blue()
                )
                
                for bet in bets[:10]:  # Limit to 10 bets
                    status_emoji = "🟡"  # Active
                    status_text = "Em andamento"
                    
                    if bet.get('bet_status') == 'finished':
                        if bet.get('is_winner'):
                            status_emoji = "🏆"
                            status_text = "Venceu!"
                        else:
                            status_emoji = "❌"
                            status_text = "Perdeu"
                    elif bet.get('bet_status') == 'cancelled':
                        status_emoji = "♻️"
                        status_text = "Cancelada (Reembolsado)"
                    
                    embed.add_field(
                        name=f"{status_emoji} {bet.get('bet_title', 'N/A')}",
                        value=(
                            f"**Escolha:** {bet.get('choice_name', f\"Opção {bet.get('choice_id', 'N/A')}\")}\n"
                            f"**Valor:** {bet.get('amount', 0):,} moedas\n"
                            f"**Status:** {status_text}"
                        ),
                        inline=True
                    )
        else:
            embed = discord.Embed(
                title="❌ Erro",
                description="Falha ao obter suas apostas.",
                color=discord.Color.red()
            )
    
    await interaction.followup.send(embed=embed)

# ===== SYSTEM COMMANDS =====

@bot.tree.command(name="status", description="Verifique o status de todos os microserviços")
async def status(interaction: discord.Interaction):
    """Check the health status of all microservices."""
    await interaction.response.defer()
    
    services = [
        ("Balance API", f"{BALANCE_API_URL}/health"),
        ("Client API", f"{CLIENT_API_URL}/health"),
        ("Coin API", f"{COIN_API_URL}/health"),
        ("Bet API", f"{BET_API_URL}/health")
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
        ("", ""),
        ("🎰 **Comandos de Apostas**", ""),
        ("/bet_create <título> <descrição> <opção1> <opção2>", "Criar nova aposta (Admin)"),
        ("/bet_list", "Listar apostas ativas"),
        ("/bet_info <id>", "Ver detalhes de uma aposta"),
        ("/bet_place <id> <opção> <valor>", "Fazer uma aposta"),
        ("/bet_finalize <id> <opção_vencedora>", "Finalizar aposta (Admin)"),
        ("/bet_cancel <id>", "Cancelar aposta e reembolsar (Admin)"),
        ("/my_bets", "Ver suas apostas"),
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
    embed.set_footer(text="💡 Dica: Use IDs parciais nas apostas (primeiros 8 caracteres são suficientes)")
    
    await interaction.followup.send(embed=embed)

# ===== ERROR HANDLING =====

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
