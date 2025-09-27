import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

# Importa as funções do nosso arquivo de banco de dados
from database.db import add_warn

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Expulsa um membro do servidor.")
    @app_commands.describe(membro="O membro a ser expulso.", motivo="O motivo da expulsão.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Nenhum motivo fornecido."):
        if membro == interaction.user or membro.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("Você não pode expulsar este membro.", ephemeral=True)

        await membro.kick(reason=motivo)
        embed = discord.Embed(
            title="Membro Expulso",
            description=f"**{membro.name}** foi expulso por **{interaction.user.name}**.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Motivo", value=motivo)
        await interaction.response.send_message(embed=embed)
        # Lógica de log aqui...

    @app_commands.command(name="ban", description="Bane um membro do servidor.")
    @app_commands.describe(membro="O membro a ser banido.", motivo="O motivo do banimento.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, membro: discord.Member, motivo: str = "Nenhum motivo fornecido."):
        # Lógica similar ao kick, mas usando membro.ban()
        await membro.ban(reason=motivo)
        await interaction.response.send_message(f"{membro.display_name} foi banido com sucesso.")

    @app_commands.command(name="mute", description="Coloca um membro de castigo (timeout).")
    @app_commands.describe(membro="O membro a ser silenciado.", duracao="Duração (ex: 10m, 1h, 1d).", motivo="O motivo.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, membro: discord.Member, duracao: str, motivo: str = "Nenhum motivo fornecido."):
        # Lógica de conversão de duração (ex: '10m' -> timedelta(minutes=10)) precisa ser implementada
        # Exemplo simples:
        if duracao.endswith('m'):
            minutes = int(duracao[:-1])
            delta = timedelta(minutes=minutes)
        elif duracao.endswith('h'):
            hours = int(duracao[:-1])
            delta = timedelta(hours=hours)
        else:
            return await interaction.response.send_message("Formato de duração inválido. Use 'm' para minutos ou 'h' para horas.", ephemeral=True)

        await membro.timeout(delta, reason=motivo)
        await interaction.response.send_message(f"{membro.display_name} foi silenciado por {duracao}.")

    @app_commands.command(name="warn", description="Adverte um membro.")
    @app_commands.describe(membro="O membro a ser advertido.", motivo="O motivo da advertência.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, membro: discord.Member, motivo: str):
        await add_warn(self.bot.db, interaction.guild.id, membro.id, interaction.user.id, motivo)
        await interaction.response.send_message(f"{membro.display_name} foi advertido. Motivo: {motivo}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))