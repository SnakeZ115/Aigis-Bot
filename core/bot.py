"""
Cliente y controlador de eventos de Discord para Aigis.
Gestiona el ciclo de vida del bot, filtrado de seguridad, y despacho de respuestas.
"""
from pathlib import Path
import discord
from discord.ext import commands
from config import config, logger
from core.security import security
from core.brain import brain


class AigisBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix=config.prefix,
            intents=intents,
            help_command=None,
        )

    async def setup_hook(self):
        """Se ejecuta antes de conectar el bot."""
        logger.info("Iniciando componentes de Aigis...")

    async def on_ready(self):
        """Notificación cuando el bot se conecta exitosamente a Discord."""
        logger.info("==========================================")
        logger.info(" %s conectada y en línea en Discord!", config.assistant_name)
        logger.info(" Usuario: %s (ID: %s)", self.user.name, self.user.id)
        logger.info(" Propietario autorizado ID: %s", config.owner_id)
        logger.info(" Modelo local activo: %s", config.ollama_model)
        logger.info("==========================================")

        # Establecer estado personalizado de Discord
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"a tus órdenes | {config.prefix}help",
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

        # Verificar conexión con Ollama
        ollama_ok = await brain.check_connection()
        if not ollama_ok:
            logger.warning("ADVERTENCIA: Ollama no respondió en el arranque. Asegúrate de tenerlo ejecutándose.")

    async def on_message(self, message: discord.Message):
        """Procesa cada mensaje recibido."""
        # 1. Filtro estricto de seguridad: sólo el propietario
        if not security.is_authorized(message):
            return

        # 2. Verificar si el mensaje está dirigido a Aigis
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mention = self.user in message.mentions
        starts_with_prefix = message.content.startswith(config.prefix)
        is_allowed_channel = (
            config.allowed_channel_id is not None
            and message.channel.id == config.allowed_channel_id
        )

        should_process = is_dm or is_mention or starts_with_prefix or is_allowed_channel
        if not should_process:
            return

        # Limpiar mención o prefijo del texto
        content = message.content
        if is_mention:
            content = content.replace(f"<@{self.user.id}>", "").replace(f"<@!{self.user.id}>", "")
        elif starts_with_prefix:
            content = content[len(config.prefix):]

        clean_prompt = content.strip()
        if not clean_prompt:
            await message.reply(f"¿Sí? Estoy aquí. ¿Qué necesitas que haga?")
            return

        # Procesar comandos tradicionales rápidos primero si los hay
        if clean_prompt.lower() == "ping":
            await message.reply(f"Pong! Latencia: {round(self.latency * 1000)}ms.")
            return

        # 3. Procesar a través del cerebro IA (Ollama)
        logger.info("Mensaje recibido de %s: '%s'", message.author.name, clean_prompt)
        async with message.channel.typing():
            result = await brain.think_and_reply(clean_prompt)

        reply_text = result.get("reply_text", "Listo.")
        attachment_path = result.get("attachment_path")

        # 4. Enviar respuesta con o sin archivo adjunto (captura de pantalla)
        try:
            if attachment_path and Path(attachment_path).exists():
                discord_file = discord.File(attachment_path, filename=Path(attachment_path).name)
                await message.reply(content=reply_text, file=discord_file)
            else:
                # Si el mensaje supera los 2000 caracteres de Discord, dividirlo
                if len(reply_text) > 2000:
                    for chunk in [reply_text[i : i + 1950] for i in range(0, len(reply_text), 1950)]:
                        await message.reply(chunk)
                else:
                    await message.reply(reply_text)
        except Exception as e:
            logger.error("Error al enviar respuesta a Discord: %s", e)
            await message.channel.send(f"Ocurrió un error al enviar la respuesta: {e}")


bot = AigisBot()
