"""
Herramientas de utilidad para Aigis (captura de pantalla, consulta de tareas).
"""
import os
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab
from core.scheduler import scheduler
from config import config, logger

SCREENSHOTS_DIR = config.base_dir / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)


def take_screenshot() -> dict:
    """Toma una captura de la pantalla principal y guarda la imagen."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = SCREENSHOTS_DIR / filename

        # Captura de pantalla
        screenshot = ImageGrab.grab()
        screenshot.save(filepath, "PNG")

        logger.info("Captura de pantalla guardada en: %s", filepath)
        return {
            "success": True,
            "filepath": str(filepath),
            "message": "Captura de pantalla tomada exitosamente.",
        }
    except Exception as e:
        logger.error("Error al tomar captura de pantalla: %s", e)
        return {
            "success": False,
            "filepath": None,
            "message": f"Error al tomar captura: {e}",
        }


def list_scheduled_tasks() -> list[dict]:
    """Retorna la lista de tareas programadas actualmente."""
    return scheduler.list_jobs()


def cancel_scheduled_task(job_id: str) -> str:
    """Cancela una tarea programada específica según su ID."""
    success = scheduler.cancel_job(job_id)
    if success:
        return f"Tarea con ID '{job_id}' cancelada exitosamente."
    return f"No se encontró ninguna tarea con el ID '{job_id}'."
