import discord
from discord import app_commands
import aiohttp
from typing import Optional
from tools.utils import make_api_request
from tools.constants import GENAI_API_URL

def genai_commands(bot):
    @bot.tree.command(name="mestre", description="Peça para a IA responder uma pergunta ou resolver um problema")
    @app_commands.describe(
        prompt="Sua pergunta ou comando para a IA",
        provider="Modelo de IA (openai, gemini, etc)",
        system_prompt="Prompt de sistema para afinar a resposta (opcional)",
    )
    async def mestre(
        interaction: discord.Interaction,
        prompt: str,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """Envia um prompt para o serviço de IA e retorna a resposta."""
        await interaction.response.defer()
        payload = {"prompt": prompt}
        if provider:
            payload["provider"] = provider
        if system_prompt:
            payload["system_prompt"] = system_prompt
        async with aiohttp.ClientSession() as session:
            status, response = await make_api_request(
                session, 'POST', f"{GENAI_API_URL}/generate", payload
            )
        if status == 200 and response and isinstance(response, dict) and response.get("response"):
            response_header = f"Prompt: {prompt}\n\n"
            response_body = response.get("response", "Falha ao obter resposta da IA.")
            if system_prompt:
                response_header += f"Orientação da mensagem: {system_prompt}"
            
            embed = discord.Embed(
                title="🤖 Resposta da IA",
                description=response_header + "\n\n"  + response_body,
                color=discord.Color.purple()
            )
        else:
            error_msg = response.get('detail', 'Erro desconhecido') if isinstance(response, dict) else str(response)
            embed = discord.Embed(
                title="❌ Erro na IA",
                description=f"Falha ao obter resposta da IA: {error_msg}",
                color=discord.Color.red()
            )
        await interaction.followup.send(embed=embed, )

