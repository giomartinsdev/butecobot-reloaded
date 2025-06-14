import discord
from discord import app_commands
import aiohttp
from typing import Optional
from tools.utils import get_or_create_user, make_api_request, requires_registration
from tools.constants import AI_API_URL, BALANCE_API_URL
import os
from dotenv import load_dotenv

load_dotenv()


def ai_commands(bot):        
    @bot.tree.command(name="mestre", description="Peça para a IA responder uma pergunta ou resolver um problema")
    @app_commands.describe(
        prompt="Sua pergunta ou comando para a IA",
        provider="Modelo de IA (openai, gemini, etc)",
        system_prompt="Prompt de sistema para afinar a resposta (opcional)",
    )
    @requires_registration()
    async def mestre(
        interaction: discord.Interaction,
        prompt: str,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """Envia um prompt para o serviço de IA e retorna a resposta."""

        sender = await get_or_create_user(str(interaction.user.id), interaction.user.display_name)
        
        amount = int(os.getenv('AI_USAGE_COST', 100))
        data = {
            "clientId": sender['id'],
            "amount": amount,
            "description": f"Pagamento por uso do serviço de IA: {prompt}"
        }

        status, response = await make_api_request(
            session, 'POST', f"{BALANCE_API_URL}/balance/subtract", data
        )
        
        if status != 200:
            embed = discord.Embed(
                title="❌ Falha no pagamento da AI",
                description="Falha ao pagar pelo uso do serviço de IA. Verifique seu saldo.",
                color=discord.Color.red()
            )

        await interaction.response.defer()
        payload = {"prompt": prompt}
        if provider:
            payload["provider"] = provider
        if system_prompt:
            payload["systemPrompt"] = system_prompt
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'POST', f"{AI_API_URL}/GenAI/generate", payload
            )
        if status == 200 and response and isinstance(response, dict) and response.get("text"):
            response_header = f"Prompt: {prompt}\n\n"
            response_body = response.get("text", "Falha ao obter resposta da IA.")
            if system_prompt:
                response_header += f"Orientação da mensagem: {system_prompt}"
            
            embed = discord.Embed(
                title="🤖 Resposta da IA",
                description=response_header + "\n\n"  + response_body,
                color=discord.Color.blue()
            )
        else:
            error_msg = response.get('error', 'Erro desconhecido') if isinstance(response, dict) else str(response)
            embed = discord.Embed(
                title="❌ Erro na IA",
                description=f"Falha ao obter resposta da IA: {error_msg}",
                color=discord.Color.red()
            )
        await interaction.followup.send(embed=embed)

