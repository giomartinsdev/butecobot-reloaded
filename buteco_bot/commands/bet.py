from discord import app_commands
import discord
import aiohttp
from tools.utils import make_api_request, get_or_create_user, is_admin
from tools.constants import BET_API_URL

def bet_commands(bot):
    @bot.tree.command(name="evento_criar", description="Criar uma nova aposta (Admin)")
    @app_commands.describe(
        title="Título da aposta",
        description="Descrição da aposta",
        option1="Primeira opção para apostar",
        option2="Segunda opção para apostar"
    )
    async def evento_criar(interaction: discord.Interaction, title: str, description: str, option1: str, option2: str):
        """Create a new bet (Admin only)."""
        await interaction.response.defer()
        
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem criar apostas.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
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
                "option1": option1,
                "option2": option2
            }
            
            status, response = await make_api_request(
                session, 'POST', f"{BET_API_URL}/bet/event", bet_data
            )
            
            if status == 200:
                event_id = response.get('eventId', 'Unknown')
                embed = discord.Embed(
                    title="🎰 Aposta Criada com Sucesso!",
                    description=f"**{title}**\n{description}",
                    color=discord.Color.green()
                )
                embed.add_field(name="ID da Aposta", value=f"`{event_id}`", inline=False)
                embed.add_field(name="Opção 1", value=f"🅰️ {option1}", inline=True)
                embed.add_field(name="Opção 2", value=f"🅱️ {option2}", inline=True)
                embed.add_field(
                    name="Como Apostar",
                    value=f"Use `/bet_place {event_id} 1 [valor]` ou `/bet_place {event_id} 2 [valor]`",
                    inline=False
                )
                embed.set_footer(text=f"Criado por {interaction.user.display_name}")
            else:
                embed = discord.Embed(
                    title="❌ Erro ao Criar Aposta",
                    description="Falha ao criar a aposta. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
        
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="evento_info", description="Ver detalhes de uma aposta específica")
    @app_commands.describe(event_id="ID do evento de aposta para ver detalhes")
    async def evento_info(interaction: discord.Interaction, event_id: str):
        """Get detailed information about a specific bet event."""
        await interaction.response.defer()
        
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/event/{event_id}"
            )
            
            if status == 404:
                embed = discord.Embed(
                    title="❌ Aposta Não Encontrada",
                    description=f"Não foi possível encontrar a aposta com ID `{event_id}`.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            elif status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter informações da aposta.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            event = response.get('event', {})
            total_bets = response.get('totalBets', 0)
            option1_bets = response.get('option1Bets', 0)
            option2_bets = response.get('option2Bets', 0)
            
            status_emojis = {
                True: "🟢 Ativa" if not event.get('isFinished') else "🏁 Finalizada",
                False: "❌ Cancelada"
            }
            
            embed = discord.Embed(
                title=f"🎰 {event['title']}",
                description=event.get('description', ''),
                color=discord.Color.blue()
            )
            
            embed.add_field(name="ID", value=f"`{event['id']}`", inline=True)
            embed.add_field(
                name="Status", 
                value=status_emojis.get(event.get('isActive', False), "❓ Desconhecido"), 
                inline=True
            )
            embed.add_field(name="Pool Total", value=f"{event.get('totalBetAmount', 0):,} moedas", inline=True)
            embed.add_field(name="Total de Apostas", value=str(total_bets), inline=True)
            
            option1_amount = event.get('option1BetAmount', 0)
            option2_amount = event.get('option2BetAmount', 0)
            total_amount = event.get('totalBetAmount', 0)
            
            option1_percentage = (option1_amount / total_amount * 100) if total_amount > 0 else 0
            option2_percentage = (option2_amount / total_amount * 100) if total_amount > 0 else 0
            
            embed.add_field(
                name=f"🅰️ {event.get('option1', 'Opção 1')}",
                value=f"{option1_amount:,} moedas ({option1_percentage:.1f}%)\n{option1_bets} apostadores",
                inline=True
            )
            
            embed.add_field(
                name=f"🅱️ {event.get('option2', 'Opção 2')}",
                value=f"{option2_amount:,} moedas ({option2_percentage:.1f}%)\n{option2_bets} apostadores",
                inline=True
            )
            
            if event.get('isFinished') and event.get('winningOption'):
                winning_option_name = event.get('option1') if event.get('winningOption') == 1 else event.get('option2')
                embed.add_field(
                    name="🏆 Opção Vencedora",
                    value=winning_option_name,
                    inline=False
                )
            
            embed.set_footer(text="Criado por Administrador")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="eventos_listar", description="Listar todas as apostas ativas")
    async def eventos_listar(interaction: discord.Interaction):
        """List all active bets."""
        await interaction.response.defer(ephemeral=True)
        
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/events"
            )
            
            if status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter lista de apostas ativas.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            active_events = response.get('events', [])
            
            if not active_events:
                embed = discord.Embed(
                    title="🎰 Apostas Ativas",
                    description="Nenhuma aposta ativa no momento.",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="🎰 Apostas Ativas",
                    description=f"Encontradas {len(active_events)} apostas ativas:",
                    color=discord.Color.blue()
                )
                
                for event in active_events[:10]:
                    options_text = f"{event.get('option1', 'Opção 1')} vs {event.get('option2', 'Opção 2')}"
                    embed.add_field(
                        name=f"🎯 {event['title']}",
                        value=f"**ID:** `{event['id']}`\n**Opções:** {options_text}\n**Pool:** {event.get('totalBetAmount', 0):,} moedas",
                        inline=False
                    )
                
                if len(active_events) > 10:
                    embed.set_footer(text=f"Mostrando 10 de {len(active_events)} apostas ativas")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="evento_apostar", description="Fazer uma aposta")
    @app_commands.describe(
        event_id="ID do evento de aposta",
        choice="Opção para apostar (1 ou 2)",
        amount="Quantidade de moedas para apostar"
    )
    async def evento_apostar(interaction: discord.Interaction, event_id: str, choice: int, amount: int):
        """Place a bet on a specific choice."""
        await interaction.response.defer(ephemeral=True)
        
        if choice not in [1, 2]:
            embed = discord.Embed(
                title="❌ Opção Inválida",
                description="A opção deve ser 1 ou 2.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        if amount <= 0:
            embed = discord.Embed(
                title="❌ Valor Inválido",
                description="O valor da aposta deve ser positivo.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
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
            status, event_response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/event/{event_id}"
            )
            
            if status == 404:
                embed = discord.Embed(
                    title="❌ Aposta Não Encontrada",
                    description=f"Não foi possível encontrar a aposta com ID `{event_id}`.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            bet_data = {
                "userId": user_data['id'],
                "betEventId": event_id,
                "chosenOption": choice,
                "amount": amount
            }
            
            status, response = await make_api_request(
                session, 'POST', f"{BET_API_URL}/bet/place", bet_data
            )
            
            if status == 200:
                event_info = event_response.get('event', {})
                choice_name = event_info.get('option1') if choice == 1 else event_info.get('option2')
                
                embed = discord.Embed(
                    title="✅ Aposta Realizada com Sucesso!",
                    description=f"Você apostou **{amount:,} moedas** em **{choice_name}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Aposta", value=event_info.get('title', 'Desconhecida'), inline=False)
                embed.add_field(name="Sua Escolha", value=f"{'🅰️' if choice == 1 else '🅱️'} {choice_name}", inline=True)
            elif status == 400:
                error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
                embed = discord.Embed(
                    title="❌ Erro na Aposta",
                    description=error_msg,
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="❌ Falha na Aposta",
                    description="Falha ao realizar a aposta. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="evento_finalizar", description="Finalizar uma aposta e distribuir prêmios (Admin)")
    @app_commands.describe(
        event_id="ID do evento de aposta para finalizar",
        winning_choice="Opção vencedora (1 ou 2)"
    )
    async def evento_finalizar(interaction: discord.Interaction, event_id: str, winning_choice: int):
        """Finalize a bet and distribute prizes (Admin only)."""
        await interaction.response.defer()
        
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem finalizar apostas.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
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
            status, event_response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/event/{event_id}"
            )
            
            if status == 404:
                embed = discord.Embed(
                    title="❌ Aposta Não Encontrada",
                    description=f"Não foi possível encontrar a aposta com ID `{event_id}`.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            finalize_data = {
                "betEventId": event_id,
                "winningOption": winning_choice
            }
            
            status, response = await make_api_request(
                session, 'POST', f"{BET_API_URL}/bet/finalize", finalize_data
            )
            
            if status == 200:
                event_info = event_response.get('event', {})
                choice_name = event_info.get('option1') if winning_choice == 1 else event_info.get('option2')
                
                total_pool = event_info.get('totalBetAmount', 0)
                
                embed = discord.Embed(
                    title="🏁 Aposta Finalizada!",
                    description=f"**{event_info.get('title', 'Aposta')}** foi finalizada.",
                    color=discord.Color.gold()
                )
                embed.add_field(name="Opção Vencedora", value=f"{'🅰️' if winning_choice == 1 else '🅱️'} {choice_name}", inline=True)
                embed.add_field(name="Pool Total", value=f"{total_pool:,} moedas", inline=True)
                
                embed.add_field(
                    name="💰 Prêmios Distribuídos",
                    value="Os prêmios foram distribuídos proporcionalmente entre os vencedores!",
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

    @bot.tree.command(name="evento_cancelar", description="Cancelar uma aposta e reembolsar apostadores (Admin)")
    @app_commands.describe(event_id="ID do evento de aposta para cancelar")
    async def evento_cancelar(interaction: discord.Interaction, event_id: str):
        """Cancel a bet and refund all bettors (Admin only)."""
        await interaction.response.defer()
        
        if not is_admin(interaction.user):
            embed = discord.Embed(
                title="❌ Permissão Negada",
                description="Apenas administradores podem cancelar apostas.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            return
        
        async with aiohttp.ClientSession() as session:
            status, event_response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/event/{event_id}"
            )
            
            if status == 404:
                embed = discord.Embed(
                    title="❌ Aposta Não Encontrada",
                    description=f"Não foi possível encontrar a aposta com ID `{event_id}`.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            status, response = await make_api_request(
                session, 'DELETE', f"{BET_API_URL}/bet/event/{event_id}"
            )
            
            if status == 200:
                event_info = event_response.get('event', {})
                refunded_bets = response.get('refundedBets', 0)
                total_refunded = response.get('totalRefunded', 0)
                
                embed = discord.Embed(
                    title="❌ Aposta Cancelada",
                    description=f"**{event_info.get('title', 'Aposta')}** foi cancelada.",
                    color=discord.Color.orange()
                )
                embed.add_field(name="Reembolsos Processados", value=str(refunded_bets), inline=True)
                
                if refunded_bets > 0:
                    embed.add_field(name="Total Reembolsado", value=f"{total_refunded:,} moedas", inline=True)
                    embed.add_field(
                        name="💸 Reembolsos",
                        value="Todos os apostadores foram reembolsados automaticamente.",
                        inline=False
                    )
                
            elif status == 400:
                error_msg = response if isinstance(response, str) else response.get('detail', 'Erro desconhecido')
                embed = discord.Embed(
                    title="❌ Erro ao Cancelar",
                    description=error_msg,
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title="❌ Falha ao Cancelar",
                    description="Falha ao cancelar a aposta. Tente novamente mais tarde.",
                    color=discord.Color.red()
                )
        
        await interaction.followup.send(embed=embed)

    @bot.tree.command(name="minhas_apostas", description="Ver suas apostas")
    async def minhas_apostas(interaction: discord.Interaction):
        """Get user's betting history."""
        await interaction.response.defer(ephemeral=True)
        
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
            status, response = await make_api_request(
                session, 'GET', f"{BET_API_URL}/bet/user/{user_data['id']}"
            )
            
            if status != 200:
                embed = discord.Embed(
                    title="❌ Erro",
                    description="Falha ao obter suas apostas.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            user_bets = response.get('bets', [])
            
            if not user_bets:
                embed = discord.Embed(
                    title="🎰 Minhas Apostas",
                    description="Você ainda não fez nenhuma aposta.",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="🎰 Minhas Apostas",
                    description=f"Você tem {len(user_bets)} apostas:",
                    color=discord.Color.blue()
                )
                
                for bet in user_bets[:10]:
                    status_emoji = "🏁" if bet.get('isFinished') else "🟢"
                    result_text = ""
                    
                    if bet.get('isFinished'):
                        if bet.get('isWinner'):
                            result_text = " (🎉 GANHOU!)"
                        else:
                            result_text = " (❌ Perdeu)"
                    
                    embed.add_field(
                        name=f"{status_emoji} {bet['eventTitle']}{result_text}",
                        value=f"**Aposta:** {bet['amount']:,} moedas em {bet['chosenOptionText']}\n**ID:** `{bet['eventId']}`",
                        inline=False
                    )
                
                if len(user_bets) > 10:
                    embed.set_footer(text=f"Mostrando 10 de {len(user_bets)} apostas")
        
        await interaction.followup.send(embed=embed, ephemeral=True)

