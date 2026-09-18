"""Gestión automática de FFmpeg (binario estático) para convertir a MP3.

Busca un ffmpeg existente (sistema o local); si no hay, descarga una
versión estática que no requiere instalación y la guarda en /ffmpeg.
"""

import logging
import os
import platform
import shutil
import tarfile
import tempfile
import threading
import urllib.request
import zipfile
from pathlib import Path

log = logging.getLogger("tubetomp3")

FFMPEG_DIR = Path(__file__).resolve().parent / "ffmpeg"
NOMBRE_BINARIO = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
FFMPEG_BIN = FFMPEG_DIR / NOMBRE_BINARIO

_DOWNLOAD_LOCK = threading.Lock()

# Builds estáticos (sin dependencias, mínimo tamaño). URLs "latest" estables.
_URLS = {
    "linux:x86_64": (
        "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz",
        "tar.xz",
    ),
    "linux:aarch64": (
        "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz",
        "tar.xz",
    ),
    "windows:x86_64": (
        "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
        "zip",
    ),
    "windows:aarch64": (
        "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-winarm64-gpl.zip",
        "zip",
    ),
}

_HEADERS = {"User-Agent": "TubeToMP3"}


def clave_plataforma() -> str:
    """Normaliza sistema+arquitectura a una clave de _URLS."""
    sistema = platform.system().lower()
    maquina = platform.machine().lower()
    if maquina in ("amd64", "x86_64"):
        maquina = "x86_64"
    elif maquina in ("arm64", "aarch64"):
        maquina = "aarch64"
    return f"{sistema}:{maquina}"


def ubicar_existente() -> str | None:
    """Devuelve un ffmpeg ya presente (sistema primero, luego el local)."""
    ruta = shutil.which("ffmpeg")
    if ruta:
        return ruta
    return str(FFMPEG_BIN) if FFMPEG_BIN.is_file() else None


def asegurar_ffmpeg(progreso=None) -> str | None:
    """Devuelve la ruta de ffmpeg, descargándolo si hace falta.

    Si la descarga no es posible (offline o plataforma no soportada),
    devuelve None y la app cae al audio original.

    `progreso` es un callable opcional que recibe el porcentaje (0-100)
    de la descarga en curso.
    """
    ruta = ubicar_existente()
    return ruta or descargar_ffmpeg(progreso=progreso)


def descargar_ffmpeg(progreso=None) -> str | None:
    """Descarga (una sola vez) el binario estático de FFmpeg."""
    if FFMPEG_BIN.is_file():
        return str(FFMPEG_BIN)

    url, tipo = _URLS.get(clave_plataforma(), (None, None))
    if url is None:
        log.warning("FFmpeg automático no disponible en esta plataforma (%s).", clave_plataforma())
        return None

    with _DOWNLOAD_LOCK:
        if FFMPEG_BIN.is_file():
            return str(FFMPEG_BIN)

        FFMPEG_DIR.mkdir(exist_ok=True)
        log.info("Descargando FFmpeg (una sola vez) desde %s ...", url)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                paquete = Path(tmp) / f"ffmpeg.{tipo}"
                _descargar(url, paquete, progreso=progreso)
                _extraer_binario(paquete, tmp)
            log.info("FFmpeg instalado en %s", FFMPEG_BIN)
        except Exception:
            log.exception("No se pudo descargar FFmpeg; se usará el audio original.")
            return None

    return str(FFMPEG_BIN) if FFMPEG_BIN.is_file() else None


def _descargar(url: str, destino: Path, progreso=None) -> None:
    request = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(request, timeout=120) as respuesta:
        total = int(respuesta.headers.get("Content-Length", 0))
        recibido = 0
        with open(destino, "wb") as f:
            while chunk := respuesta.read(1 << 20):
                f.write(chunk)
                recibido += len(chunk)
                if total:
                    p = recibido * 100 // total
                    log.info("FFmpeg: %d%% (%d/%d MB)", p, recibido // (1 << 20), total // (1 << 20))
                    if progreso:
                        progreso(p)


def _extraer_binario(paquete: Path, tmp: str) -> None:
    if paquete.suffix == ".zip":
        with zipfile.ZipFile(paquete) as z:
            z.extractall(tmp)
    else:
        with tarfile.open(paquete, "r:*") as t:
            t.extractall(tmp)

    origen = None
    for raiz, _, ficheros in os.walk(tmp):
        for f in ficheros:
            if f == NOMBRE_BINARIO:
                origen = Path(raiz) / f
                break
        if origen:
            break

    if origen is None:
        raise RuntimeError(f"No se encontró {NOMBRE_BINARIO} dentro del paquete.")

    shutil.copy2(origen, FFMPEG_BIN)
    if os.name != "nt":
        FFMPEG_BIN.chmod(FFMPEG_BIN.stat().st_mode | 0o111)