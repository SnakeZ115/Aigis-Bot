@echo off
setlocal
title Aigis - Configurador de Inicio Automatico

echo ===================================================
echo     Aigis: Configuracion de Inicio en Windows
echo ===================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "TARGET_VBS=%SCRIPT_DIR%run_background.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\Aigis.lnk"

echo Selecciona una opcion:
echo [1] Habilitar inicio automatico (Crear acceso directo en Startup)
echo [2] Deshabilitar inicio automatico (Eliminar de Startup)
echo [3] Salir
echo.

set /p OPTION="Opcion [1/2/3]: "

if "%OPTION%"=="1" (
    echo.
    echo Creando acceso directo en: %STARTUP_FOLDER%
    powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%TARGET_VBS%\"'; $s.WorkingDirectory = '%SCRIPT_DIR%..'; $s.Save()"
    echo.
    echo [EXITO] Aigis se iniciara automaticamente cada vez que enciendas tu PC!
) else if "%OPTION%"=="2" (
    if exist "%SHORTCUT_PATH%" (
        del "%SHORTCUT_PATH%"
        echo.
        echo [EXITO] Acceso directo eliminado de la carpeta de inicio.
    ) else (
        echo.
        echo No se encontro ningun inicio automatico configurado para Aigis.
    )
) else (
    echo Cancelado.
)

echo.
pause
