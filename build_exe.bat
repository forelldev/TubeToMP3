@echo off
REM Compila TubeToMP3 a un .exe portable (Opción 1: yt-dlp incrustado,
REM FFmpeg se autodescarga la primera vez que se usa).
REM Requisito: tener Python 3.10+ instalado en Windows.
setlocal
cd /d "%~dp0"

echo [1/3] Creando entorno virtual...
if not exist venv (
    python -m venv venv || goto :error
)
call venv\Scripts\activate.bat

echo [2/3] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt || goto :error
pip install pyinstaller || goto :error

echo [3/3] Generando el ejecutable...
pyinstaller --noconfirm --clean --onefile --windowed --name TubeToMP3 ^
    --collect-all yt_dlp ^
    --collect-all pywebview ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    app.py || goto :error

if not exist creacion_ejecutables\Windows mkdir creacion_ejecutables\Windows
copy /y dist\TubeToMP3.exe creacion_ejecutables\Windows\TubeToMP3.exe >nul || goto :error

echo.
echo  Listo: creacion_ejecutables\Windows\TubeToMP3.exe
echo  El primer uso descargara FFmpeg automaticamente (una sola vez).
pause
exit /b 0

:error
echo.
echo  Fallo durante la compilacion. Revisa el mensaje anterior.
pause
exit /b 1