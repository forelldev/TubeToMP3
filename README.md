# TubeToMP3

Convierte enlaces de YouTube a **MP3** de forma local y gratuita. Aplicación ligera basada en Flask y yt-dlp que se ejecuta en tu propia máquina, sin subir nada a ningún servidor.

Elige tu perfil a continuación:

- [**Solo quiero descargar**](#para-los-que-solo-quieren-descargar) → ya hay un AppImage listo.
- [**Usuario avanzado**](#para-usuarios-avanzados-ejecutar-sin-compilar-nada) → ejecutar desde el código, sin empaquetar.
- [**Desarrollador**](#para-desarrolladores-generar-los-ejecutables) → compilar el `.exe` de Windows o el AppImage de Linux.

---

## Para los que solo quieren descargar

Dentro de la carpeta **`ejecutables/`** están las versiones listas para usar, una por sistema operativo:

```
ejecutables/
├── Windows/        → TubeToMP3.exe   (próximamente, aún no generado)
└── Linux/          → TubeToMP3-x86_64.AppImage   (LISTO, 80 MB)
```

**Linux (ya disponible):** la app abre en una **ventana propia** (sin navegador).

```bash
chmod +x ejecutables/Linux/TubeToMP3-x86_64.AppImage
./ejecutables/Linux/TubeToMP3-x86_64.AppImage
```

- Si falla la ventana, se abre el navegador automáticamente (Plan B).
- En la primera conversión descarga FFmpeg solo (~40 MB) a `~/.local/share/tubetomp3/ffmpeg/`.
- Requiere FUSE y, para la ventana nativa, WebKitGTK. En Debian/Ubuntu: `sudo apt install python3-gi gir1.2-webkit2-4.1 libwebkit2gtk-4.1-0`.

**Windows (próximamente):** el `TubeToMP3.exe` **aún no ha sido compilado**. Se genera con `build.bat` en un equipo Windows (ver sección de desarrolladores). En cuanto exista, irá dentro de `ejecutables/Windows/`.

---

## Para usuarios avanzados (ejecutar sin compilar nada)

No necesitas ningún ejecutable: se corre directamente desde el código. Requiere **Python 3.10+** → https://www.python.org/downloads/

```bash
# 1. Clonar
git clone https://github.com/forelldev/TubeToMP3.git
cd TubeToMP3

# 2. Entorno virtual (una vez)
#    Windows:  python -m venv venv
#    Linux/Mac: python3 -m venv --system-site-packages venv

# 3. Activarlo
#    Windows:  venv\Scripts\activate
#    Linux/Mac: source venv/bin/activate

# 4. Dependencias (una vez)
pip install -r requirements.txt

# 5. Arrancar
python app.py
```

Con el entorno activado, también puedes usar los lanzadores de un clic: `iniciar.bat` (Windows) o `./iniciar.sh` (Linux/macOS) — crean el entorno, instalan lo necesario y arrancan.

> **Sin venv (PEP 668):** en Debian/Ubuntu el pip del sistema está "externally-managed". Con el entorno virtual de arriba se resuelve; si falta: `sudo apt install python3-venv`.

### Dónde va cada cosa

| Modo | `downloads/` | `ffmpeg/` | log |
|---|---|---|---|
| Desde el código | carpeta del proyecto | carpeta del proyecto | `downloader.log` |
| AppImage (Linux) | `~/.local/share/tubetomp3/` | `~/.local/share/tubetomp3/ffmpeg/` | `~/.local/share/tubetomp3/` |
| `.exe` (Windows) | junto al ejecutable | junto al ejecutable | junto al ejecutable |

- **Limpieza automática:** los audios con más de **7 días** se borran solos (cada 12 h). Configurable con la variable `TUBETOMP3_DIAS_DESCARGAS` (0 = conservar todo).
- **Ventana nativa:** la app usa pywebview (GTK/WebKit en Linux, WebView2 en Windows). Si no está disponible, cae al navegador. Para forzar navegador: `TUBETOMP3_NAVEGADOR=1 python app.py`.
- **FFmpeg:** se autodescarga la primera vez; si no hay internet, cae al audio original.

---

## Para desarrolladores: generar los ejecutables

### Compilar el `.exe` de Windows

Requisitos:
- Un **PC con Windows** (PyInstaller no compila "en cruz"; no se puede hacer desde Linux).
- **Python 3.10+** instalado, marcando *"Add python.exe to PATH"*.

Pasos:

```bat
build.bat
```

Genera `ejecutables\Windows\TubeToMP3.exe` (un solo archivo, con yt-dlp y pywebview dentro, FFmpeg autodescargable).

**Alternativa sin Windows — GitHub Actions:** por defecto el repositorio incluye el workflow `.github/workflows/build-exe.yml`.

1. Sube el proyecto a GitHub.
2. Ve a **Actions → Build Windows .exe → Run workflow**.
3. Descarga el artefacto `TubeToMP3-windows-exe` (contiene el `.exe`).
4. Si en vez de "Run workflow" creas una *release* con etiqueta `v*`, el `.exe` se adjunta solo a la release (desde `ejecutables/Windows/`).

### Compilar el AppImage de Linux

Requisitos:
- Linux x86_64 con **bash**, **curl**, **ImageMagick** (`convert`) y acceso a internet.
- Para que la ventana nativa quede empaquetada, que existan PyGObject y WebKitGTK: `sudo apt install python3-gi gir1.2-webkit2-4.1 libwebkit2gtk-4.1-0` (Debian/Ubuntu). Sin ellos, el AppImage seguirá compilando, pero dentro abrirá el navegador en vez de la ventana.

Pasos:

```bash
./build_appimage.sh
```

Genera `ejecutables/Linux/TubeToMP3-x86_64.AppImage` (~80 MB). El script instala PyInstaller y `appimagetool`, compila y coloca el resultado automáticamente en su sitio.

> **Compatibilidad:** el AppImage arrastra la `glibc` de la distro donde compiles. Para repartirlo a otros, compílalo en la distro más antigua que quieras soportar (Debian 11 / Ubuntu 20.04) o en un contenedor Docker de esa versión.

### Aviso común a ambos ejecutables

El `.exe`/`.AppImage` no están firmados: Windows Defender / SmartScreen y algunos sistemas pedirán permiso la primera vez (*Más información → Ejecutar de todos modos*). Es normal en software de distribución casera.

---

## Estructura del proyecto

```
TubeToMP3/
├── app.py                # Aplicación Flask (backend) + ventana nativa
├── ffmpeg_util.py        # Descarga y gestión automática de FFmpeg
├── requirements.txt      # Dependencias: Flask, yt-dlp, pywebview
├── build.bat             # Genera ejecutables\Windows\TubeToMP3.exe (en Windows)
├── build_appimage.sh     # Genera ejecutables/Linux/TubeToMP3-x86_64.AppImage
├── iniciar.bat           # Lanzador de un clic (Windows)
├── iniciar.sh            # Lanzador de un clic (Linux/macOS)
├── templates/
│   └── index.html        # Página principal
├── static/
│   ├── css/styles.css    # Estilos
│   ├── js/script.js      # Interacción del frontend
│   └── logo.svg          # Icono de los ejecutables
├── ejecutables/          # Versiones portátiles (una por sistema)
│   ├── Windows/          # TubeToMP3.exe (próximamente)
│   └── Linux/            # TubeToMP3-x86_64.AppImage (listo)
├── downloads/            # Se crea solo; aquí se guardan los audios (modo fuente)
└── ffmpeg/               # Se crea solo; binario estático (modo fuente)
```

## Cómo funciona

1. El usuario pega una URL de YouTube en la interfaz.
2. El backend valida la URL (solo hosts de YouTube) y genera un trabajo de conversión.
3. La interfaz muestra el **progreso en vivo** por SSE: primero FFmpeg (solo la primera vez) y luego la descarga del audio.
4. Con FFmpeg disponible se convierte a **MP3 192 kbps**; si no, cae al audio original.
5. Al terminar, el botón **Descargar** copia el audio a la carpeta *Descargas* del sistema; el original queda en `downloads/` y se limpia solo pasados 7 días.

## Solución de problemas

### Error `HTTP 403 Forbidden` al convertir

YouTube bloquea temporalmente el cliente o la IP. Soluciones en orden:

1. **Actualiza yt-dlp** (lo más frecuente): `python -m pip install -U yt-dlp`.
2. Prueba de nuevo — la app ya reintenta con varios clientes de YouTube automáticamente.
3. Si persiste, espera unos minutos (YouTube limita por IP) o prueba desde otra red/VPN.