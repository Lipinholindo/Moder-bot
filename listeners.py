import discord
from discord.ext import commands
from database.db import get_guild_settings

class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        # Busca as configurações do servidor no DB
        settings = await get_guild_settings(self.bot.db, message.guild.id)
        if not settings["automod"]["anti_link"]:
            return # Se o anti-link estiver desligado, não faz nada

        # Lógica do Anti-Link
        if "http://" in message.content or "https://" in message.content:
            # Ignora se o usuário tem permissão de gerenciar mensagens
            if not message.author.guild_permissions.manage_messages:
                await message.delete()
                await message.channel.send(f"{message.author.mention}, você não pode enviar links aqui!", delete_after=5)

        # A lógica do anti-spam e anti-menção seria adicionada aqui de forma similar

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        
        settings = await get_guild_settings(self.bot.db, message.guild.id)
        log_channel_id = settings.get("log_channel_id")

        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(
                    title="Mensagem Deletada",
                    description=f"**Autor:** {message.author.mention}\n**Canal:** {message.channel.mention}",
                    color=discord.Color.red()
                )
                embed.add_field(name="Conteúdo", value=f"```{message.content}```", inline=False)
                await log_channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))