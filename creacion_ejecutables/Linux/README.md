# Linux — TubeToMP3-x86_64.AppImage

Ejecutable portátil para Linux x86_64, abre una **ventana nativa** (sin navegador).

## Uso

```bash
./TubeToMP3-x86_64.AppImage        # desde esta carpeta
```

o doble clic desde el gestor de archivos.

## Comportamiento

- La interfaz se abre en una **ventana propia** (WebKitGTK). Si faltan las librerías del sistema, usa el navegador automáticamente.
- **Dónde se guarda todo** (el AppImage es de solo lectura):
  - Audios descargados → `~/.local/share/tubetomp3/downloads/`
  - FFmpeg (primera descarga, ~40 MB) → `~/.local/share/tubetomp3/ffmpeg/`
  - Registro → `~/.local/share/tubetomp3/downloader.log`
- **Limpieza automática:** los audios con más de 7 días se borran solos (variable `TUBETOMP3_DIAS_DESCARGAS`; 0 = conservar siempre).
- Requiere **FUSE** si vas a ejecutarlo y falla el montaje: lanzarlo con `APPIMAGE_EXTRACT_AND_RUN=1`.

## Dependencias del sistema (para la ventana nativa)

Debian/Ubuntu:

```bash
sudo apt install python3-gi gir1.2-webkit2-4.1 libwebkit2gtk-4.1-0
```

Sin ellas, el AppImage igualmente funciona (caída automática al navegador).

## Regenerar

```bash
./build_appimage.sh    # en la raíz del proyecto
```

> **Compatibilidad:** el AppImage usa la glibc de la distro donde se compile. Para repartirlo a otros, compílalo en la distro más antigua que quieras soportar (Debian 11 / Ubuntu 20.04) o con un contenedor Docker de esa versión.