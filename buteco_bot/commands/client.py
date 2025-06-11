from tools.utils import get_or_create_user
import discord

def client_commands(bot):
    @bot.tree.command(name="registro", description="Registre-se no sistema do butecoBot")
    async def registro(interaction: discord.Interaction):
        """Register a user in the system."""
        await interaction.response.defer(ephemeral=True)
        
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
        
        await interaction.followup.send(embed=embed, ephemeral=True)

