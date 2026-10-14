"""
Herramientas del sistema para Aigis.
Control de energía (apagado, reinicio, suspensión) y diagnóstico del hardware.
"""
import os
import time
import subprocess
import psutil
from core.scheduler import scheduler
from config import logger


def execute_immediate_shutdown() -> str:
    """Ejecuta el comando inmediato de apagado en Windows."""
    logger.warning("EJECUTANDO APAGADO DEL SISTEMA...")
    try:
        subprocess.run(["shutdown", "/s", "/t", "5"], check=True)
        return "El sistema se apagará en 5 segundos."
    except Exception as e:
        return f"Error al apagar el sistema: {e}"


def schedule_shutdown(minutes: int) -> str:
    """Programa el apagado de la computadora en N minutos."""
    if minutes <= 0:
        return execute_immediate_shutdown()

    result = scheduler.schedule_shutdown(minutes, execute_immediate_shutdown)
    if result["success"]:
        return (
            f"Apagado programado correctamente para dentro de {minutes} minutos "
            f"(a las {result['target_time']})."
        )
    return "No se pudo programar el apagado del sistema."


def cancel_shutdown() -> str:
    """Cancela cualquier apagado programado, tanto en el scheduler como en Windows."""
    cancelled_scheduler = scheduler.cancel_shutdown()
    try:
        # También cancelamos en Windows por si había algún timer nativo
        subprocess.run(["shutdown", "/a"], capture_output=True, text=True)
        native_cancelled = True
    except Exception:
        native_cancelled = False

    if cancelled_scheduler or native_cancelled:
        return "El apagado programado ha sido cancelado con éxito."
    return "No había ningún apagado programado pendiente."


def restart_pc() -> str:
    """Reinicia la computadora."""
    logger.warning("EJECUTANDO REINICIO DEL SISTEMA...")
    try:
        subprocess.run(["shutdown", "/r", "/t", "5"], check=True)
        return "El sistema se reiniciará en 5 segundos."
    except Exception as e:
        return f"Error al reiniciar el sistema: {e}"


def sleep_pc() -> str:
    """Pone la computadora en modo suspensión."""
    logger.info("Poniendo el sistema en suspensión...")
    try:
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], check=True)
        return "El sistema ha entrado en modo de suspensión."
    except Exception as e:
        return f"Error al suspender el sistema: {e}"


def get_system_status() -> dict:
    """Obtiene métricas de uso de hardware (CPU, RAM, Disco, Batería y Uptime)."""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)

    # RAM
    ram = psutil.virtual_memory()
    ram_total_gb = round(ram.total / (1024 ** 3), 2)
    ram_used_gb = round(ram.used / (1024 ** 3), 2)
    ram_percent = ram.percent

    # Disco principal (C:)
    try:
        disk = psutil.disk_usage("C:\\")
        disk_total_gb = round(disk.total / (1024 ** 3), 2)
        disk_free_gb = round(disk.free / (1024 ** 3), 2)
        disk_percent = disk.percent
    except Exception:
        disk_total_gb, disk_free_gb, disk_percent = 0, 0, 0

    # Batería (si aplica)
    battery = psutil.sensors_battery()
    battery_info = "No disponible (PC de escritorio)"
    if battery:
        battery_info = f"{battery.percent}% ({'Cargando' if battery.power_plugged else 'Descargando'})"

    # Tiempo de actividad (Uptime)
    boot_time = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    uptime_str = f"{hours}h {minutes}m"

    return {
        "cpu_usage_percent": f"{cpu_percent}%",
        "ram": f"{ram_used_gb} GB / {ram_total_gb} GB ({ram_percent}%)",
        "disk_c": f"{disk_free_gb} GB libres de {disk_total_gb} GB ({disk_percent}% en uso)",
        "battery": battery_info,
        "uptime": uptime_str,
    }
