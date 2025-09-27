# Este arquivo vai conter as funções para interagir com as coleções do MongoDB

# Coleção para as configurações dos servidores
async def get_guild_settings(db, guild_id):
    """ Encontra as configurações de um servidor ou cria uma nova se não existir. """
    settings = await db.guild_settings.find_one({"guild_id": guild_id})
    if not settings:
        # Configurações padrão
        default_settings = {
            "guild_id": guild_id,
            "log_channel_id": None,
            "automod": {
                "anti_link": False,
                "anti_spam": False,
                "anti_mention": False,
            }
        }
        await db.guild_settings.insert_one(default_settings)
        return default_settings
    return settings

async def update_guild_settings(db, guild_id, new_settings):
    """ Atualiza as configurações de um servidor. """
    await db.guild_settings.update_one({"guild_id": guild_id}, {"$set": new_settings}, upsert=True)

# Coleção para as advertências
async def add_warn(db, guild_id, user_id, moderator_id, reason):
    """ Adiciona uma advertência a um usuário. """
    warn = {
        "guild_id": guild_id,
        "user_id": user_id,
        "moderator_id": moderator_id,
        "reason": reason,
        "timestamp": discord.utils.utcnow()
    }
    await db.warnings.insert_one(warn)
    return warn