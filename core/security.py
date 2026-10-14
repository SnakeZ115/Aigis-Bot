"""
Capa de seguridad e identificación para Aigis.
Garantiza que sólo el propietario autorizado pueda interactuar con el bot o ejecutar comandos.
"""
import discord
from config import config, logger


class SecurityManager:
    """Verifica y audita la identidad de los emisores de mensajes."""

    @staticmethod
    def is_authorized(message: discord.Message) -> bool:
        """
        Determina si un mensaje proviene del usuario autorizado.
        """
        # Ignorar mensajes emitidos por el propio bot u otros bots
        if message.author.bot:
            return False

        # Si el OWNER_ID no está configurado, bloquear por seguridad
        if not config.owner_id:
            logger.warning("Intento de comando rechazado: DISCORD_OWNER_ID no está configurado en .env.")
            return False

        # Verificar si el ID del autor coincide con el dueño
        if message.author.id != config.owner_id:
            logger.warning(
                "Intento de acceso NO AUTORIZADO detectado: Usuario %s (ID: %s)",
                message.author.name,
                message.author.id,
            )
            return False

        # Si hay un canal específico configurado y el mensaje no es en MD ni en dicho canal
        if config.allowed_channel_id:
            if not isinstance(message.channel, discord.DMChannel) and message.channel.id != config.allowed_channel_id:
                logger.debug(
                    "Mensaje autorizado ignorado por no pertenecer al canal designado (%s).",
                    message.channel.id,
                )
                return False

        return True


security = SecurityManager()
