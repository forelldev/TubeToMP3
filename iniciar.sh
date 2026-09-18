#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python 3 no está instalado."
    echo "Instálalo y vuelve a ejecutar: sudo apt install python3 python3-venv (Debian/Ubuntu)"
    exit 1
fi

if [ ! -d venv ]; then
    echo "[1/3] Creando entorno virtual..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "[2/3] Instalando dependencias..."
pip install --disable-pip-version-check -r requirements.txt

echo "[3/3] Iniciando TubeToMP3..."
python app.py