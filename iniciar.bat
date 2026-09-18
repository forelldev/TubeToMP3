@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python no esta instalado.
    echo Instala Python desde https://www.python.org/downloads/ y vuelve a ejecutar este archivo.
    pause
    exit /b 1
)

if not exist venv (
    echo [1/3] Creando entorno virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo [2/3] Instalando dependencias...
python -m pip install --disable-pip-version-check -r requirements.txt

echo [3/3] Iniciando TubeToMP3...
python app.py

call venv\Scripts\deactivate.bat
pause