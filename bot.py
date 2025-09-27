import os
import discord
from discord.ext import commands
import motor.motor_asyncio
from dotenv import load_dotenv
import asyncio

# Carrega as variáveis do arquivo .env
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

class MyBot(commands.Bot):
    def __init__(self):
        # --- Configuração das Intents ---
        # Intents são permissões que o bot precisa para receber certos eventos
        intents = discord.Intents.default()
        intents.message_content = True  # Necessária para o automod ler mensagens
        intents.members = True          # Necessária para eventos de membros

        # --- Inicialização do Bot ---
        # O prefixo de comando '!' não é mais tão usado com slash commands, mas é bom ter
        super().__init__(command_prefix='!', intents=intents)

        # --- Conexão com o Banco de Dados ---
        self.db_client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        self.db = self.db_client["meuBotDB"] # Nome do seu banco de dados

    async def setup_hook(self):
        """ Carrega os cogs da pasta /cogs """
        print("Carregando cogs...")
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"Cog '{filename[:-3]}' carregado com sucesso.")
                except Exception as e:
                    print(f"Erro ao carregar o cog '{filename[:-3]}': {e}")

    async def on_ready(self):
        """ Evento que é chamado quando o bot está pronto """
        print(f'Logado como {self.user} (ID: {self.user.id})')
        print('------')
        # Sincroniza os comandos de barra com o Discord.
        # Essencial para que os comandos apareçam.
        try:
            synced = await self.tree.sync()
            print(f"Sincronizados {len(synced)} comandos de barra.")
        except Exception as e:
            print(f"Erro ao sincronizar comandos: {e}")


async def main():
    bot = MyBot()
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())