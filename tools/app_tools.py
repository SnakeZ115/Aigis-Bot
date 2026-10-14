"""
Herramientas para gestión de aplicaciones y procesos en Windows.
"""
import os
import subprocess
import psutil
from config import logger


# Mapeo rápido de alias comunes para facilitar abrir programas populares
APP_ALIASES = {
    "notepad": "notepad.exe",
    "bloc de notas": "notepad.exe",
    "calc": "calc.exe",
    "calculadora": "calc.exe",
    "chrome": "chrome",
    "google chrome": "chrome",
    "firefox": "firefox",
    "edge": "msedge",
    "spotify": "spotify",
    "steam": "steam",
    "discord": "discord",
    "code": "code",
    "vs code": "code",
    "visual studio code": "code",
    "explorer": "explorer.exe",
    "explorador": "explorer.exe",
    "terminal": "wt.exe",
}


def launch_application(app_name: str) -> str:
    """Inicia una aplicación en el sistema."""
    name_clean = app_name.strip().lower()
    target = APP_ALIASES.get(name_clean, app_name)

    logger.info("Intentando abrir la aplicación: %s (target: %s)", app_name, target)
    try:
        # Usamos start a través de la shell de Windows para resolver rutas del PATH y accesos directos
        subprocess.Popen(f'start "" "{target}"', shell=True)
        return f"Aplicación '{app_name}' iniciada correctamente."
    except Exception as e:
        return f"Error al intentar iniciar '{app_name}': {e}"


def close_application(process_name: str) -> str:
    """Cierra un proceso por su nombre (ej: chrome.exe, notepad.exe)."""
    clean_name = process_name.strip().lower()
    if not clean_name.endswith(".exe"):
        clean_name += ".exe"

    terminated_count = 0
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == clean_name:
                proc.terminate()
                terminated_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if terminated_count > 0:
        return f"Se cerraron {terminated_count} instancia(s) de '{clean_name}'."
    return f"No se encontró ningún proceso en ejecución con el nombre '{clean_name}'."


def list_running_applications(limit: int = 10) -> list[dict]:
    """Lista las aplicaciones o procesos principales ordenados por uso de memoria RAM."""
    processes = []
    for proc in psutil.process_iter(["name", "memory_percent", "cpu_percent"]):
        try:
            pinfo = proc.info
            if pinfo["name"] and pinfo["memory_percent"] is not None:
                processes.append({
                    "name": pinfo["name"],
                    "ram_percent": round(pinfo["memory_percent"], 1),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # Ordenar por uso de RAM descendente
    processes.sort(key=lambda p: p["ram_percent"], reverse=True)
    return processes[:limit]
