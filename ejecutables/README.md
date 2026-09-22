# Ejecutables de TubeToMP3

Aquí se guardan las versiones portátiles, una carpeta por sistema operativo.

| Carpeta | Archivo | Estado |
|---|---|---|
| `Linux/` | `TubeToMP3-x86_64.AppImage` | listo para usar |
| `Windows/` | `TubeToMP3.exe` | se genera en una máquina Windows (ver nota) |

**Linux:** el AppImage ya está compilado y funcional. Para regenerarlo: `./build_appimage.sh` en la raíz del proyecto.

**Windows:** el `.exe` **no se puede compilar desde Linux** (PyInstaller no hace compilación cruzada). Se genera ejecutando `build.bat` en la raíz del proyecto desde un equipo Windows; el resultado queda automáticamente en `Windows\TubeToMP3.exe`.

Cada subcarpeta contiene su propia nota con los detalles.