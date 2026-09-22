#!/usr/bin/env bash
# Compila TubeToMP3 a un AppImage de Linux.
#
# Requisitos: Python 3.10+, curl, ImageMagick (convert) y red.
# Para máxima compatibilidad conviene compilar en una distro antigua
# (Debian 11 / Ubuntu 20.04) o con Docker; ver nota en README.
set -euo pipefail
cd "$(dirname "$0")"

NOMBRE="tubetomp3"
APPDIR_FOLDER="TubeToMP3.AppDir"
APPIMAGE_TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"

echo "[1/4] Entorno virtual y dependencias"
if [ ! -d venv ]; then
    python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt pyinstaller

echo "[2/4] Compilando con PyInstaller (onedir, yt-dlp incrustado, ffmpeg autodescarga)"
# gi (PyGObject) es lo que usa pywebview en Linux para la ventana nativa.
# Solo se empaqueta si está disponible; si no, la app usará el navegador (Plan B).
COLLECT_GI="--collect-all gi"
if ! python3 -c "import gi" >/dev/null 2>&1; then
    echo "  (gi no disponible → la ventana nativa requeriria: sudo apt install python3-gi gir1.2-webkit2-4.1)"
    COLLECT_GI=""
fi
pyinstaller --noconfirm --clean --onedir --name "$NOMBRE" \
    --collect-all yt_dlp \
    $COLLECT_GI \
    --collect-all pywebview \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --noupx app.py

# Recorte: GTK empaqueta 1,4 GB de iconos/temas que la ventana web no usa
rm -rf "dist/$NOMBRE/_internal/share/icons" "dist/$NOMBRE/_internal/share/themes"

echo "[3/4] Armando el AppDir"
rm -rf "$APPDIR_FOLDER"
mkdir -p "$APPDIR_FOLDER/usr/bin" \
         "$APPDIR_FOLDER/usr/share/applications" \
         "$APPDIR_FOLDER/usr/share/icons/hicolor/256x256/apps"
cp -r "dist/$NOMBRE/"* "$APPDIR_FOLDER/usr/bin/"

cat > "$APPDIR_FOLDER/AppRun" <<'EOF'
#!/bin/sh
# Punto de entrada del AppImage ($APPDIR lo define el runtime).
exec "$APPDIR/usr/bin/tubetomp3" "$@"
EOF
chmod +x "$APPDIR_FOLDER/AppRun"

cat > "$APPDIR_FOLDER/tubetomp3.desktop" <<'EOF'
[Desktop Entry]
Type=Application
Name=TubeToMP3
Comment=Convierte YouTube a MP3 en tu PC
Exec=TubeToMP3
Icon=tubetomp3
Terminal=false
Categories=AudioVideo;Audio;
EOF

convert -background none static/logo.svg -resize 256x256 \
    "$APPDIR_FOLDER/usr/share/icons/hicolor/256x256/apps/tubetomp3.png"
# appimagetool exige el icono además en la raíz del AppDir
cp "$APPDIR_FOLDER/usr/share/icons/hicolor/256x256/apps/tubetomp3.png" \
    "$APPDIR_FOLDER/tubetomp3.png"

echo "[4/4] Generando el AppImage con appimagetool"
TOOL="$(mktemp -d)/appimagetool-x86_64.AppImage"
curl -Ls "$APPIMAGE_TOOL_URL" -o "$TOOL"
chmod +x "$TOOL"
APPIMAGE_EXTRACT_AND_RUN=1 "$TOOL" "$APPDIR_FOLDER"

echo "[5/5] Colocando el ejecutable en ejecutables/Linux/"
mkdir -p ejecutables/Linux
mv -f TubeToMP3-x86_64.AppImage ejecutables/Linux/
rm -rf "$APPDIR_FOLDER"

echo ""
echo "Listo: ejecutables/Linux/TubeToMP3-x86_64.AppImage"
echo "Pruébalo con: ./ejecutables/Linux/TubeToMP3-x86_64.AppImage"
echo "(los datos de descargas/ffmpeg se guardan en ~/.local/share/tubetomp3)"