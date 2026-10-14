"""
Módulo de Configuración para Aigis.
Carga variables de entorno y provee configuraciones validadas al resto de la aplicación.
"""
import os
import sys
import logging
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

# Cargar variables de entorno si el archivo existe
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


@dataclass
class Config:
    # Discord
    discord_token: str
    owner_id: int
    prefix: str
    allowed_channel_id: int | None

    # Ollama
    ollama_host: str
    ollama_model: str
    ollama_temperature: float

    # General
    assistant_name: str
    log_level: str
    base_dir: Path

    @classmethod
    def load(cls) -> "Config":
        token = os.getenv("DISCORD_BOT_TOKEN", "").strip()
        raw_owner_id = os.getenv("DISCORD_OWNER_ID", "").strip()

        if not token or token == "tu_token_aqui":
            print("[ADVERTENCIA] 'DISCORD_BOT_TOKEN' no está configurado o tiene el valor por defecto en .env.")

        owner_id = 0
        if raw_owner_id:
            try:
                owner_id = int(raw_owner_id)
            except ValueError:
                print(f"[ERROR] 'DISCORD_OWNER_ID' debe ser un número entero válido. Valor actual: '{raw_owner_id}'")

        raw_channel_id = os.getenv("DISCORD_ALLOWED_CHANNEL_ID", "").strip()
        allowed_channel_id = int(raw_channel_id) if raw_channel_id.isdigit() else None

        return cls(
            discord_token=token,
            owner_id=owner_id,
            prefix=os.getenv("DISCORD_PREFIX", "!"),
            allowed_channel_id=allowed_channel_id,
            ollama_host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "qwen3:8b"),
            ollama_temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
            assistant_name=os.getenv("ASSISTANT_NAME", "Aigis"),
            log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
            base_dir=BASE_DIR,
        )


config = Config.load()

# Configuración básica de logging
logging.basicConfig(
    level=getattr(logging, config.log_level, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("Aigis")
