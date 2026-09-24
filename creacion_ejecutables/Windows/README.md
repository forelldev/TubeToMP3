# Windows — TubeToMP3.exe

El ejecutable de Windows **se compila en un equipo Windows** (con Python 3.10+ instalado):

1. Abre una terminal (CMD) en la raíz del proyecto.
2. Ejecuta `build_exe.bat`.
3. El resultado queda en `creacion_ejecutables\Windows\TubeToMP3.exe`.

No se puede generar desde Linux/macOS: PyInstaller no compila "en cruz".

## Comportamiento

- Un solo archivo (`--onefile --windowed`), con yt-dlp y pywebview incrustados.
- Abre en una **ventana nativa** usando el runtime WebView2 (ya incluido en Windows 10/11) — sin navegador.
- En la **primera** conversión descarga FFmpeg automáticamente y lo guarda junto al ejecutable.
- Los datos (`downloads/`, `ffmpeg/`, `downloader.log`) se crean en la misma carpeta del `.exe`.
- Windows Defender pedirá permiso la primera vez ("Editor desconocido"): el ejecutable no está firmado. Pulsar *Más información → Ejecutar de todos modos*.