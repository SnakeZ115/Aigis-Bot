"""
Registro central de herramientas para Aigis.
Expone los esquemas de herramientas para Ollama (Function Calling)
y el despachador de ejecución.
"""
from typing import Any
import inspect
from config import logger
from tools.system_tools import (
    schedule_shutdown,
    cancel_shutdown,
    execute_immediate_shutdown,
    restart_pc,
    sleep_pc,
    get_system_status,
)
from tools.app_tools import (
    launch_application,
    close_application,
    list_running_applications,
)
from tools.util_tools import (
    take_screenshot,
    list_scheduled_tasks,
    cancel_scheduled_task,
)
from tools.steam_tools import get_game_reviews

# Definiciones de herramientas compatibles con Ollama / OpenAI Tool Calling Schema
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "schedule_shutdown",
            "description": "Programa el apagado de la computadora después de un número específico de minutos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "minutes": {
                        "type": "integer",
                        "description": "Minutos de espera antes de apagar la computadora (ej: 20).",
                    }
                },
                "required": ["minutes"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_shutdown",
            "description": "Cancela cualquier apagado de la computadora que haya sido programado previamente.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_immediate_shutdown",
            "description": "Apaga la computadora de forma inmediata (en 5 segundos).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "restart_pc",
            "description": "Reinicia la computadora de inmediato.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sleep_pc",
            "description": "Pone la computadora en modo de suspensión.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_status",
            "description": "Obtiene el estado actual del hardware: uso de CPU, memoria RAM, espacio en disco, batería y tiempo encendido.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "launch_application",
            "description": "Abre o ejecuta una aplicación en la computadora (ej: chrome, spotify, notepad, calc, steam, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Nombre o comando de la aplicación a abrir.",
                    }
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "close_application",
            "description": "Cierra una aplicación o proceso por su nombre (ej: chrome.exe, notepad.exe, spotify.exe).",
            "parameters": {
                "type": "object",
                "properties": {
                    "process_name": {
                        "type": "string",
                        "description": "Nombre del ejecutable o proceso a cerrar.",
                    }
                },
                "required": ["process_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_running_applications",
            "description": "Lista las aplicaciones o procesos con mayor consumo de memoria en este momento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Cantidad de procesos a listar (por defecto 10).",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Toma una captura de pantalla del monitor principal de la computadora.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_scheduled_tasks",
            "description": "Lista todas las tareas pendientes programadas en el sistema (ej: apagados programados).",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_scheduled_task",
            "description": "Cancela una tarea programada según su identificador (ID).",
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                        "description": "ID de la tarea a cancelar.",
                    }
                },
                "required": ["job_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_game_reviews",
            "description": "Busca un juego de Steam por su nombre y obtiene el resumen de calificaciones, porcentaje de aprobación y reseñas de la comunidad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "game_name": {
                        "type": "string",
                        "description": "Nombre del videojuego a buscar (ej: Cyberpunk 2077, Hollow Knight, Elden Ring, Portal 2).",
                    }
                },
                "required": ["game_name"],
            },
        },
    },
]

# Diccionario de funciones ejecutables
TOOL_FUNCTIONS = {
    "schedule_shutdown": schedule_shutdown,
    "cancel_shutdown": cancel_shutdown,
    "execute_immediate_shutdown": execute_immediate_shutdown,
    "restart_pc": restart_pc,
    "sleep_pc": sleep_pc,
    "get_system_status": get_system_status,
    "launch_application": launch_application,
    "close_application": close_application,
    "list_running_applications": list_running_applications,
    "take_screenshot": take_screenshot,
    "list_scheduled_tasks": list_scheduled_tasks,
    "cancel_scheduled_task": cancel_scheduled_task,
    "get_game_reviews": get_game_reviews,
}


async def execute_tool(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Ejecuta una herramienta por nombre (síncrona o asíncrona) con los argumentos proporcionados."""
    func = TOOL_FUNCTIONS.get(tool_name)
    if not func:
        logger.error("Herramienta no encontrada: '%s'", tool_name)
        return {"error": f"Herramienta '{tool_name}' no existe en el registro."}

    logger.info("Ejecutando herramienta '%s' con argumentos: %s", tool_name, arguments)
    try:
        if inspect.iscoroutinefunction(func):
            result = await func(**arguments)
        else:
            result = func(**arguments)
        return result
    except Exception as e:
        logger.error("Error al ejecutar '%s': %s", tool_name, e)
        return {"error": f"Fallo al ejecutar herramienta: {str(e)}"}
