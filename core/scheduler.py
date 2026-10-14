"""
Planificador de tareas en segundo plano para Aigis.
Permite ejecutar acciones en el futuro (ej: apagar la PC en X minutos, recordatorios)
y consultarlas o cancelarlas dinámicamente.
"""
from datetime import datetime, timedelta
from typing import Callable, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from config import logger

SHUTDOWN_JOB_ID = "scheduled_pc_shutdown"


class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False

    def start(self):
        """Inicia el planificador asíncrono."""
        if not self._is_running:
            self.scheduler.start()
            self._is_running = True
            logger.info("Planificador de tareas iniciado exitosamente.")

    def shutdown(self):
        """Detiene el planificador."""
        if self._is_running:
            self.scheduler.shutdown()
            self._is_running = False
            logger.info("Planificador de tareas detenido.")

    def schedule_once(
        self,
        func: Callable,
        run_date: datetime,
        job_id: str,
        name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
    ) -> bool:
        """Programa la ejecución única de una función en una fecha/hora dada."""
        try:
            # Si el trabajo ya existe, lo reemplazamos
            self.scheduler.add_job(
                func,
                trigger="date",
                run_date=run_date,
                id=job_id,
                name=name,
                args=args or [],
                kwargs=kwargs or {},
                replace_existing=True,
            )
            logger.info("Tarea programada: '%s' para las %s", name, run_date.strftime("%Y-%m-%d %H:%M:%S"))
            return True
        except Exception as e:
            logger.error("Error al programar la tarea '%s': %s", name, e)
            return False

    def schedule_shutdown(self, minutes: int, shutdown_fn: Callable) -> dict[str, Any]:
        """Programa un apagado de la computadora en N minutos."""
        run_date = datetime.now() + timedelta(minutes=minutes)
        success = self.schedule_once(
            func=shutdown_fn,
            run_date=run_date,
            job_id=SHUTDOWN_JOB_ID,
            name=f"Apagar PC en {minutes} minutos",
        )
        return {
            "success": success,
            "minutes": minutes,
            "target_time": run_date.strftime("%H:%M:%S"),
            "target_date": run_date.strftime("%Y-%m-%d"),
        }

    def cancel_shutdown(self) -> bool:
        """Cancela cualquier apagado programado activo."""
        try:
            self.scheduler.remove_job(SHUTDOWN_JOB_ID)
            logger.info("Apagado programado cancelado con éxito.")
            return True
        except JobLookupError:
            return False

    def cancel_job(self, job_id: str) -> bool:
        """Cancela un trabajo por su ID."""
        try:
            self.scheduler.remove_job(job_id)
            logger.info("Tarea '%s' cancelada.", job_id)
            return True
        except JobLookupError:
            return False

    def list_jobs(self) -> list[dict[str, Any]]:
        """Obtiene la lista de todas las tareas pendientes."""
        jobs = []
        for job in self.scheduler.get_jobs():
            next_run = job.next_run_time
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S") if next_run else "Inmediato",
            })
        return jobs


scheduler = TaskScheduler()
