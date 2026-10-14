"""
Punto de entrada principal para Aigis.
Inicializa el planificador de tareas y arranca el bot de Discord.
"""
import asyncio
import sys
from config import config, logger
from core.scheduler import scheduler
from core.bot import bot


def main():
    print(r"""
       /\  _       _     
      /  \| |     (_)    
     / /\ \ | __ _ _ ___ 
    / ____ \| |/ _` | / __|
   /_/    \_\_|\__, |_|\___|
                __/ |       
               |___/        
    Asistente Personal de Control de Sistema
    """)

    # Validaciones previas
    if not config.discord_token or config.discord_token == "tu_token_aqui":
        logger.critical(
            "ERROR: No has configurado 'DISCORD_BOT_TOKEN' en el archivo .env.\n"
            "Copia el archivo .env.example a .env y coloca tus credenciales."
        )
        sys.exit(1)

    if not config.owner_id:
        logger.warning(
            "ADVERTENCIA: 'DISCORD_OWNER_ID' no está configurado. El bot no procesará mensajes "
            "hasta que especifiques tu ID de Discord en el archivo .env."
        )

    # Iniciar el planificador de tareas en segundo plano
    # scheduler.start()

    # Arrancar el bot de Discord
    try:
        logger.info("Iniciando conexión con Discord...")
        bot.run(config.discord_token)
    except KeyboardInterrupt:
        logger.info("Interrupción por teclado detectada. Cerrando Aigis...")
    except Exception as e:
        logger.critical("Error fatal al ejecutar el bot: %s", e)
    finally:
        scheduler.shutdown()
        logger.info("Aigis ha finalizado su ejecución.")


if __name__ == "__main__":
    main()
