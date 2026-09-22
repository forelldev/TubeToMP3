# TubeToMP3

Convierte enlaces de YouTube a **MP3** de forma local y gratuita. Aplicación web ligera basada en Flask y yt-dlp que se ejecuta en tu propia máquina.

## Requisitos

- **Python 3.10+** → https://www.python.org/downloads/
- **FFmpeg** _(no hace falta instalarlo)_: la app lo descarga automáticamente la primera vez que conviertes (una sola vez; ~40 MB en Linux, ~100 MB en Windows) en Windows y Linux (x86_64/ARM64). Solo así se genera MP3.

## Instalación (una sola vez)

Es recomendable usar un **entorno virtual** para no interferir con el Python del sistema.

```bash
# 1. Clonar el repositorio
git clone https://github.com/forelldev/TubeToMP3.git
cd TubeToMP3

# 2. Crear el entorno virtual (una vez)
python3 -m venv venv

# 3. Activarlo
#    Windows:  venv\Scripts\activate
#    Linux/macOS: source venv/bin/activate

# 4. Instalar las dependencias dentro del entorno
pip install -r requirements.txt
```

> **Debian / Ubuntu:** si `pip install` falla con `externally-managed-environment` (PEP 668), significa que el Python del sistema no permite instalar paquetes globalmente. Con el entorno virtual de arriba se resuelve. Si falta el módulo `venv`, instálalo: `sudo apt install python3-venv`.
>
> **Sin entorno virtual (si estás usando tu propio Python):** basta con `pip install -r requirements.txt`.

## Ejecución

Con el entorno virtual activado:

```bash
python app.py
```

Se abrirá **una ventana nativa del sistema** (sin navegador) con la app en `http://127.0.0.1:5000` (5001, 5002… si el 5000 está ocupado). Pega el enlace de YouTube, presiona **Convertir** y descarga el audio.

## Ventana de escritorio (sin navegador)

La app usa **pywebview** para abrirse en una ventana real del sistema operativo que pinta la interfaz tal cual (GTK/WebKit en Linux, WebView2 en Windows), conservando el progreso en vivo (SSE).

- **Windows:** usa el runtime WebView2, ya incluido en Windows 10/11 → funciona sin instalar nada.
- **Linux:** requiere las librerías del sistema `libwebkit2gtk-4.1` y PyGObject (`sudo apt install python3-gi gir1.2-webkit2-4.1 libwebkit2gtk-4.1-0` en Debian/Ubuntu).
- **Plan B automático:** si el webview no está disponible (librerías ausentes, PC cabeza, etc.), la app **cae automáticamente al navegador** en vez de fallar.
- Para forzar el navegador: ejecutar con `TUBETOMP3_NAVEGADOR=1`.

## Alternativa sin comandos (Windows)

Haz doble clic en `iniciar.bat`: crea el entorno, instala las dependencias y arranca la app. En Linux/macOS usa `./iniciar.sh`.

## FFmpeg (automático)

La app detecta si falta FFmpeg y descarga un binario estático (~90 MB) a la carpeta `ffmpeg/` **la primera vez que conviertes** — no requiere instalación ni conocimientos. Si la descarga no es posible (sin internet o macOS), cae al audio original.

Si prefieres tenerlo tú mismo, se usará el del sistema:

**Windows:** descarga [FFmpeg Essentials](https://www.gyan.dev/ffmpeg/builds/) y añade la carpeta `bin` a la variable PATH.

**Linux:** `sudo apt install ffmpeg`

**macOS:** `brew install ffmpeg`

## Crear un .exe (Windows)

Para repartir la app como un único ejecutable portátil:

**Opción A — Compilar en tu máquina:** ejecuta `build.bat` (instala PyInstaller y genera `ejecutables\Windows\TubeToMP3.exe`). Necesitas Python 3.10+ en Windows (PyInstaller no compila "en cruz", así que hay que compilar en Windows).

**Opción B — Compilar en GitHub (recomendada):** sube el proyecto a GitHub (ya está el workflow). Ve a **Actions → Build Windows .exe → Run workflow**, o crea una *release* con una etiqueta `v*` y el `.exe` se adjuntará automáticamente desde `ejecutables/Windows/`.

Detalles de cada opción:

| Tamaño | Qué incluye | Comportamiento |
|---|---|---|
| ~60–90 MB | Flask + yt-dlp + interfaz | El `.exe` descarga FFmpeg automáticamente la **primera vez** que se convierte y lo guarda junto a él. Sin perder calidad: MP3 a 192 kbps. |

El `.exe` es de un solo archivo: los recursos de solo lectura (interfaz) se leen del interior, y todo lo que se escribe (`downloads/`, `ffmpeg/`, `downloader.log`) se crea en la **misma carpeta del ejecutable**.

> **Aviso:** Windows Defender puede mostrar "Editor desconocido" al arrancarlo (el `.exe` no está firmado). Los usuarios deben pulsar *Más información → Ejecutar de todos modos*.

## AppImage (Linux)

Ejecuta `build_appimage.sh` (instala PyInstaller y `appimagetool`, y genera `ejecutables/Linux/TubeToMP3-x86_64.AppImage`). Funciona sin instalar nada, en cualquier distro moderna con FUSE.

| Tamaño | Contenido | Comportamiento |
|---|---|---|
| ~70 MB | Flask + yt-dlp + pywebview + interfaz | Abre en una **ventana nativa**. FFmpeg se autodescarga la primera vez (~40 MB). Los datos (`downloads/`, `ffmpeg/`, `downloader.log`) se guardan en `~/.local/share/tubetomp3/` (el AppImage está montado en solo lectura). |

> **Librerías del sistema:** el AppImage necesita WebKitGTK instalado en el equipo del usuario (`libwebkit2gtk-4.1-0`, `python3-gi` y `gir1.2-webkit2-4.1` en Debian/Ubuntu). Sin ellos, la app usa el navegador (Plan B).

> **Compatibilidad:** el AppImage usa la `glibc` de la distro donde compiles. Para repartirlo a otros, compílalo en la **más antigua** que quieras soportar (Debian 11 / Ubuntu 20.04) o con un contenedor Docker de esa versión.

## Estructura del proyecto

```
TubeToMP3/
├── app.py                # Aplicación Flask (backend)
├── ffmpeg_util.py        # Descarga y gestión automática de FFmpeg
├── build.bat             # Genera ejectables\Windows\TubeToMP3.exe (hay que ejecutarlo en Windows)
├── build_appimage.sh     # Genera ejectables/Linux/TubeToMP3-x86_64.AppImage
├── iniciar.bat           # Arranque con doble clic (Windows)
├── iniciar.sh            # Arranque con doble clic (Linux/macOS)
├── requirements.txt      # Dependencias de Python
├── templates/
│   └── index.html        # Página principal
├── static/
│   ├── css/styles.css    # Estilos
│   ├── js/script.js      # Interacción del frontend
│   └── logo.svg          # Icono usada por los ejecutables
├── ejecutables/          # Versiones portátiles (una carpeta por sistema)
│   ├── Windows/          # TubeToMP3.exe (generado con build.bat)
│   └── Linux/            # TubeToMP3-x86_64.AppImage (generado con build_appimage.sh)
├── downloads/            # Se crea automáticamente; aquí se guardan los audios
└── ffmpeg/               # Se crea automáticamente (binario estático, ~90 MB)
```

## Cómo funciona

1. El usuario pega una URL de YouTube en la interfaz.
2. El backend valida la URL (solo hosts de YouTube) y genera el trabajo de conversión.
3. La interfaz muestra el **progreso en vivo**: primero FFmpeg (solo la primera vez, con su porcentaje) y luego la descarga del audio.
4. Si no hay FFmpeg se descarga automáticamente y se convierte a MP3 (192 kbps).
5. Cuando termina, aparece el botón **Descargar** y el archivo queda guardado en `downloads/`.

## Notas

- La app escucha solo en `127.0.0.1` (no expone nada a tu red local) y usa el puerto 5000 (con reseva automática si estuviera ocupado).
- **Dónde se guarda cada cosa** (depende de cómo se ejecute):
  - Modo fuente: en la carpeta del proyecto (`downloads/`, `ffmpeg/`, `downloader.log`).
  - AppImage: en `~/.local/share/tubetomp3/` (el AppImage es solo lectura).
  - `.exe` de Windows: en la misma carpeta del ejecutable.
- **Limpieza automática:** los audios descargados se borran solos al superar **7 días** de antigüedad (se revisa cada 12 h). Se configura con la variable `TUBETOMP3_DIAS_DESCARGAS` (0 = conservar para siempre).
- Registro de actividad en `downloader.log`.

## Solución de problemas

### Error `HTTP 403 Forbidden` al convertir

YouTube bloquea temporalmente el cliente o la IP. Soluciones en orden:

1. **Actualiza yt-dlp** (es lo más frecuente): `python -m pip install -U yt-dlp`
2. Prueba de nuevo — la app ya reintenta con varios clientes de YouTube automáticamente.
3. Si persiste, espera unos minutos (YouTube limita por IP) o prueba desde otra red/VPN.