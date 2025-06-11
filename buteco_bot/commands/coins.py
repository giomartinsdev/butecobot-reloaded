import discord
from discord import app_commands
from tools.utils import get_or_create_user, make_api_request
from tools.constants import BALANCE_API_URL, COIN_API_URL
import aiohttp

from typing import Optional

def coins_commands(bot):
    @bot.tree.command(name="ver_coins", description="Verifique seu saldo atual")
    async def ver_coins(interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Check balance for yourself or another user."""
        await interaction.response.defer(ephemeral=True)
        
        target_user = user if user else interaction.user
        discord_id = str(target_user.id)
        
        user_data = await get_or_create_user(discord_id, target_user.display_name)
        if not user_data:
            embed = discord.Embed(
                title="❌ Usuário Não Encontrado",
                description="Usuário não está registrado no sistema.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
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
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="coins", description="Colete suas moedas diárias")
    async def coins(interaction: discord.Interaction):
        """Claim daily coins."""
        await interaction.response.defer(ephemeral=True)
        
        discord_id = str(interaction.user.id)
        user_data = await get_or_create_user(discord_id, interaction.user.display_name)
        
        if not user_data:
            embed = discord.Embed(
                title="❌ Registration Required",
                description="Please use `/register` first!",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
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
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="historico_de_coins", description="Veja seu histórico de coletas diárias")
    @app_commands.describe(limit="Número de coletas para mostrar (máximo 30)")
    async def historico_de_coins(interaction: discord.Interaction, limit: int = 10):
        """Show user's daily claim history."""
        await interaction.response.defer(ephemeral=True)
        
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
            await interaction.followup.send(embed=embed, ephemeral=True)
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
                await interaction.followup.send(embed=embed, ephemeral=True)
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
        
        await interaction.followup.send(embed=embed, ephemeral=True)

