"""TubeToMP3: convierte enlaces de YouTube a MP3 con progreso en vivo.

Aplicación Flask ligera basada en yt-dlp. FFmpeg se descarga solo la
primera vez (para MP3); si la descarga no es posible, se sirve el audio
original (m4a/webm).

El progreso (FFmpeg, descarga y conversión) se envía al navegador en
tiempo real mediante Server-Sent Events (SSE).
"""

import json
import logging
import os
import queue
import socket
import sys
import threading
import uuid
import webbrowser
from pathlib import Path
from urllib.parse import quote, urlparse

import yt_dlp
from flask import Flask, Response, jsonify, render_template, request, send_file
from werkzeug.utils import safe_join

from ffmpeg_util import asegurar_ffmpeg, configurar_directorio

BASE_DIR = Path(__file__).resolve().parent

# --- Modo compilado (PyInstaller) ----------------------------------------
# En un .exe de un solo archivo el código se descomprime a _MEIPASS (temporal,
# se borra al cerrar). Los recursos de solo lectura (templates/static) se leen
# de ahí, mientras que todo lo que se escribe (descargas, ffmpeg, registro)
# debe ir AL LADO del ejecutable para no perderse.
FROZEN = getattr(sys, "frozen", False)
if FROZEN:
    RES_BASE = Path(getattr(sys, "_MEIPASS"))
    DATA_BASE = Path(sys.executable).resolve().parent
else:
    RES_BASE = BASE_DIR
    DATA_BASE = BASE_DIR

DOWNLOAD_DIR = DATA_BASE / "downloads"
configurar_directorio(DATA_BASE)

# Hosts aceptados (comparación exacta para evitar suplantaciones tipo youtube.com.evil.com)
ALLOWED_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
}

log = logging.getLogger("tubetomp3")

app = Flask(
    __name__,
    template_folder=str(RES_BASE / "templates"),
    static_folder=str(RES_BASE / "static"),
)

# Trabajos de conversión en curso: job_id -> {"eventos": queue.Queue}
JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


def configurar_logging() -> None:
    """Log a archivo y consola."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(DATA_BASE / "downloader.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def es_url_valida(url: str) -> bool:
    """Valida que la URL sea realmente de YouTube, no solo una palabra dentro del texto."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        host = urlparse(url).hostname or ""
    except ValueError:
        return False
    return host.lower() in ALLOWED_HOSTS


def ruta_final(info: dict, prep_path: str) -> str:
    """Resuelve la ruta real del archivo descargado (post-procesado si aplica)."""
    for desc in info.get("requested_downloads") or []:
        fp = desc.get("filepath")
        if fp and os.path.isfile(fp):
            return fp
    if os.path.isfile(prep_path):
        return prep_path
    # El postprocesador MP3 reescribe la extensión del contenedor original
    base = os.path.splitext(prep_path)[0] + ".mp3"
    return base if os.path.isfile(base) else prep_path


def puerto_disponible(inicio: int = 5000, intentos: int = 20) -> int:
    """Usa el puerto 5000 por defecto; si está ocupado, prueba los siguientes."""
    for puerto in range(inicio, inicio + intentos):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", puerto))
                return puerto
            except OSError:
                continue
    raise RuntimeError("No se encontró un puerto libre.")


# ---------------------------------------------------------------------------
# Trabajos de conversión (hilo + cola de eventos para SSE)
# ---------------------------------------------------------------------------

def _crear_job() -> str:
    job_id = uuid.uuid4().hex
    with JOBS_LOCK:
        JOBS[job_id] = {"eventos": queue.Queue()}
    return job_id


def _emitir(job_id: str, tipo: str, datos: dict | None = None) -> None:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
    if job:
        job["eventos"].put({"tipo": tipo, "datos": datos or {}})


def _limpiar_job(job_id: str) -> None:
    with JOBS_LOCK:
        JOBS.pop(job_id, None)


def _hook_video(job_id: str, estado: dict) -> None:
    """Hook de yt-dlp para propagar el progreso de la descarga del audio."""
    if estado.get("status") == "finished":
        _emitir(job_id, "progreso", {"tipo": "mp3", "mensaje": "Convertiendo a MP3…", "porcentaje": 100})
        return
    total = estado.get("total_bytes") or estado.get("total_bytes_estimate") or 0
    descargado = estado.get("downloaded_bytes") or 0
    if total:
        p = min(100, int(descargado * 100 / total))
        _emitir(job_id, "progreso", {"tipo": "video", "porcentaje": p, "mensaje": f"Descargando desde YouTube… {p}%"})


def _trabajo_convertir(youtube_url: str, job_id: str) -> None:
    try:
        DOWNLOAD_DIR.mkdir(exist_ok=True)

        # Garantiza MP3: si no hay ffmpeg, se descarga solo mostrando el %
        def progreso_ffmpeg(p: int) -> None:
            _emitir(job_id, "progreso", {"tipo": "ffmpeg", "porcentaje": p, "mensaje": f"Descargando FFmpeg (solo la primera vez)… {p}%"})

        ffmpeg = asegurar_ffmpeg(progreso=progreso_ffmpeg)
        es_mp3 = ffmpeg is not None

        ydl_opts = {
            "format": "bestaudio/best",
            "noplaylist": True,
            "outtmpl": str(DOWNLOAD_DIR / "%(title)s.%(ext)s"),
            # Mitiga HTTP 403: reintenta la extracción con varios clientes de YouTube
            "extractor_args": {"youtube": {"player_client": ["default", "android", "tv", "web"]}},
        }
        if es_mp3:
            ydl_opts["ffmpeg_location"] = ffmpeg
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        _emitir(job_id, "progreso", {"tipo": "video", "porcentaje": 0, "mensaje": "Preparando tu conversión a MP3…"})

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.add_progress_hook(lambda d: _hook_video(job_id, d))
            info = ydl.extract_info(youtube_url, download=True)
            archivo = ruta_final(info, ydl.prepare_filename(info))

        if not os.path.isfile(archivo):
            raise RuntimeError("No se pudo localizar el archivo descargado.")

        nombre = os.path.basename(archivo)
        modo = "mp3" if es_mp3 else "audio-nativo"
        log.info("Audio listo: %s (%s)", nombre, modo)

        _emitir(job_id, "ok", {
            "archivo": "/downloads/" + quote(nombre),
            "nombre": nombre,
            "modo": modo,
        })

    except Exception as e:
        log.exception("Error convirtiendo %s", youtube_url)
        _emitir(job_id, "error", {"mensaje": str(e)})

    finally:
        threading.Timer(120, _limpiar_job, args=(job_id,)).start()


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------

@app.route("/")
def retornar_html():
    return render_template("index.html")


@app.route("/convert", methods=["POST"])
def convert():
    youtube_url = request.form.get("youtube_url", "").strip()

    if not youtube_url:
        return jsonify({"error": "Debe ingresar una URL de YouTube.", "estado": "fallido"}), 400
    if not es_url_valida(youtube_url):
        return jsonify({"error": "URL no válida. Solo se aceptan enlaces de YouTube.", "estado": "fallido"}), 400

    job_id = _crear_job()
    hilo = threading.Thread(target=_trabajo_convertir, args=(youtube_url, job_id), daemon=True)
    hilo.start()

    return jsonify({"estado": "iniciado", "job_id": job_id}), 202


@app.route("/stream/<job_id>")
def stream(job_id):
    """Server-Sent Events: progreso en vivo del trabajo de conversión."""

    def generar():
        try:
            while True:
                with JOBS_LOCK:
                    job = JOBS.get(job_id)
                if job is None:
                    yield "event: error\ndata: {\"mensaje\":\"Trabajo no encontrado (¿caducó?).\"}\n\n"
                    return
                try:
                    evento = job["eventos"].get(timeout=1)
                except queue.Empty:
                    continue
                tipo = evento["tipo"]
                datos = json.dumps(evento["datos"], ensure_ascii=False)
                yield f"event: {tipo}\ndata: {datos}\n\n"
                if tipo in ("ok", "error"):
                    return
        except GeneratorExit:
            pass

    return Response(generar(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/downloads/<path:filename>")
def descargar(filename):
    # safe_join impide el path traversal (../ fuera de la carpeta de descargas)
    ruta = safe_join(str(DOWNLOAD_DIR), filename)
    if ruta and os.path.isfile(ruta):
        return send_file(ruta, as_attachment=True)
    return "Error: El archivo no existe.", 404


if __name__ == "__main__":
    configurar_logging()
    puerto = puerto_disponible()
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{puerto}")).start()
    log.info("TubeToMP3 disponible en http://127.0.0.1:%s", puerto)
    app.run(debug=False, host="127.0.0.1", port=puerto, threaded=True)