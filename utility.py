import discord
from discord import app_commands
from discord.ext import commands

# Importa as funções do nosso arquivo de banco de dados
from database.db import get_guild_settings, update_guild_settings

# --- Classe da View para Paginação do Help ---
# Uma View é um componente que contém botões, menus, etc.
class HelpView(discord.ui.View):
    def __init__(self, bot, author):
        super().__init__(timeout=60.0)  # A view expira após 60 segundos de inatividade
        self.bot = bot
        self.author = author
        self.current_page = 0
        
        # Agrupa os comandos por Cog
        self.cogs = {}
        for cog_name, cog in self.bot.cogs.items():
            # Pega os comandos de barra do cog
            commands = cog.get_app_commands()
            if commands:
                # Esconde o cog 'Utility' da lista de ajuda, pois não é útil para o usuário final
                if cog_name != "Utility":
                    self.cogs[cog_name] = commands

        self.cog_names = list(self.cogs.keys())

    # Checa se o usuário que clicou no botão é o mesmo que usou o comando
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Você não pode controlar este menu de ajuda.", ephemeral=True)
            return False
        return True

    def create_embed(self):
        cog_name = self.cog_names[self.current_page]
        commands_list = self.cogs[cog_name]
        
        embed = discord.Embed(
            title=f"Categoria: {cog_name}",
            color=discord.Color.blue()
        )
        for cmd in commands_list:
            embed.add_field(name=f"/{cmd.name}", value=cmd.description, inline=False)
        
        embed.set_footer(text=f"Página {self.current_page + 1}/{len(self.cog_names)}")
        return embed

    async def update_buttons(self, interaction: discord.Interaction):
        # Desabilita o botão 'anterior' se estiver na primeira página
        self.children[0].disabled = self.current_page == 0
        # Desabilita o botão 'próximo' se estiver na última página
        self.children[1].disabled = self.current_page == len(self.cog_names) - 1
        
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.grey)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_buttons(interaction)

    @discord.ui.button(label="Próximo", style=discord.ButtonStyle.grey)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < len(self.cog_names) - 1:
            self.current_page += 1
            await self.update_buttons(interaction)

# --- Cog Principal de Utilidades ---
class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Cria um grupo de comandos para /config
    config_group = app_commands.Group(name="config", description="Comandos para configurar o bot.", default_permissions=discord.Permissions(administrator=True))

    @config_group.command(name="logs", description="Define o canal de logs do bot.")
    @app_commands.describe(canal="O canal de texto para enviar os logs.")
    async def set_logs(self, interaction: discord.Interaction, canal: discord.TextChannel):
        await update_guild_settings(self.bot.db, interaction.guild.id, {"log_channel_id": canal.id})
        await interaction.response.send_message(f"✅ O canal de logs foi definido para {canal.mention}.", ephemeral=True)

    @config_group.command(name="automod", description="Ativa ou desativa um módulo do automod.")
    @app_commands.describe(modulo="O módulo a ser configurado.", status="O novo status do módulo (Ligado/Desligado).")
    @app_commands.choices(modulo=[
        app_commands.Choice(name="Anti-Link", value="anti_link"),
        app_commands.Choice(name="Anti-Spam", value="anti_spam"),
        app_commands.Choice(name="Anti-Menção", value="anti_mention"),
    ])
    async def set_automod(self, interaction: discord.Interaction, modulo: app_commands.Choice[str], status: bool):
        update_key = f"automod.{modulo.value}"
        await update_guild_settings(self.bot.db, interaction.guild.id, {update_key: status})
        
        status_text = "ativado" if status else "desativado"
        await interaction.response.send_message(f"✅ O módulo **{modulo.name}** foi {status_text}.", ephemeral=True)

    @app_commands.command(name="help", description="Mostra todos os comandos disponíveis.")
    async def help(self, interaction: discord.Interaction):
        view = HelpView(self.bot, interaction.user)
        embed = view.create_embed()
        
        # Desabilita o botão 'anterior' na primeira página
        view.children[0].disabled = True
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))