from discord import app_commands
import discord
import aiohttp
from tools.utils import get_or_create_user, make_api_request, requires_registration
from tools.constants import BALANCE_API_URL, CLIENT_API_URL

def balance_commands(bot):
    @bot.tree.command(name="transferir", description="Transfira moedas para outro usuário")
    @app_commands.describe(
        recipient="O usuário para quem transferir moedas",
        amount="Quantidade de moedas para transferir",
        description="Descrição opcional para a transferência"
    )
    @requires_registration()
    async def transferir(interaction: discord.Interaction, recipient: discord.Member, amount: int, description: str = "Transferência de moedas"):
        """Transfer coins between users."""
        await interaction.response.defer(ephemeral=True)
        
        if amount <= 0:
            embed = discord.Embed(
                title="❌ Valor Inválido",
                description="O valor da transferência deve ser positivo!",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if recipient.id == interaction.user.id:
            embed = discord.Embed(
                title="❌ Transferência Inválida",
                description="Você não pode transferir moedas para si mesmo!",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        sender = await get_or_create_user(str(interaction.user.id), interaction.user.display_name)
        receiver = await get_or_create_user(str(recipient.id), recipient.display_name)
        
        if not sender or not receiver:
            embed = discord.Embed(
                title="❌ Usuário Não Encontrado",
                description="Um ou ambos os usuários não estão registrados.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
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
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            current_balance = balance_data.get('balance', 0)
            if current_balance < amount:
                embed = discord.Embed(
                    title="❌ Saldo Insuficiente",
                    description=f"Você tem {current_balance:,} moedas, mas precisa de {amount:,} moedas.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
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
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="top_patroes", description="Mostre os melhores usuários por saldo")
    @app_commands.describe(limit="Número de usuários para mostrar (máximo 20)")
    @requires_registration()
    async def top_patroes(interaction: discord.Interaction, limit: int = 10):
        """Show leaderboard of users by balance."""
        await interaction.response.defer(ephemeral=True)
        
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
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="extrato", description="Veja seu histórico de transações")
    @app_commands.describe(limit="Número de transações para mostrar (máximo 50)")
    @requires_registration()
    async def extrato(interaction: discord.Interaction, limit: int = 10):
        """Show user's transaction history."""
        await interaction.response.defer(ephemeral=True)
        
        if limit > 50:
            limit = 50
        if limit < 1:
            limit = 10
        
        discord_id = str(interaction.user.id)
        user_data = await get_or_create_user(discord_id, interaction.user.display_name)
        
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
                await interaction.followup.send(embed=embed, ephemeral=True)
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
        
        await interaction.followup.send(embed=embed, ephemeral=True)

