@echo off
title Aigis - Asistente IA
cd /d "%~dp0\.."

echo ===================================================
echo  Iniciando Aigis en modo Consola...
echo ===================================================

:: Verificar si existe entorno virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

python main.py
pause
