@echo off
REM Verificar si Python está en PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python no está instalado o no está en la variable PATH.
    echo Por favor, instala Python o verifica las variables de entorno.
    pause
    exit /b
)

REM Directorio donde se encuentran los scripts
set SCRIPT_DIR=%~dp0

REM Ejecutar el script Fw_Install.py
echo Ejecutando Fw_Install.py...
python "%SCRIPT_DIR%Fw_Install.py"
if %errorlevel% neq 0 (
    echo Error al ejecutar Fw_Install.py
    pause
    exit /b
)

REM Ejecutar el script H20_install_params.py
echo Ejecutando H20_install_params.py...
python "%SCRIPT_DIR%H20_install_params.py"
if %errorlevel% neq 0 (
    echo Error al ejecutar H20_install_params.py
    pause
    exit /b
)

REM Ejecutar el script open_Mavlink.py
echo Ejecutando open_Mavlink.py...
python "%SCRIPT_DIR%open_Mavlink.py"
if %errorlevel% neq 0 (
    echo Error al ejecutar open_Mavlink.py
    pause
    exit /b
)

echo Todos los scripts se han ejecutado correctamente.
pause