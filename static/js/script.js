const formulario = document.getElementById("formulario");
const inputUrl = document.getElementById("youtube_url");
const botonConvertir = document.getElementById("boton-convertir");
const mensaje = document.getElementById("mensaje");
const porcentaje = document.getElementById("porcentaje");
const barraLlenado = document.getElementById("barra-llenado");
const barraContenedor = document.getElementById("barra-contenedor");
const areaProgreso = document.getElementById("area-progreso");
const areaResultado = document.getElementById("area-resultado");
const mensajeError = document.getElementById("mensaje-error");
const botonDescarga = document.getElementById("boton-descarga");
const detalleResultado = document.getElementById("detalle-resultado");

let trabajoFinalizado = false;

formulario.addEventListener("submit", (evento) => {
    evento.preventDefault();
    iniciarConversion();
});

function reiniciarUi() {
    trabajoFinalizado = false;
    ocultar(mensajeError);
    ocultar(areaResultado);
    mostrar(areaProgreso);
    barraLlenado.style.width = "0%";
    porcentaje.textContent = "0%";
    mensaje.textContent = "Preparando…";
    document.getElementById("detalle").textContent = "";
    botonConvertir.disabled = true;
    botonConvertir.classList.add("cargando");
}

function mostrar(elemento) {
    elemento.classList.remove("oculto");
}

function ocultar(elemento) {
    elemento.classList.add("oculto");
}

function setBarra(p) {
    p = Math.max(0, Math.min(100, Math.round(p)));
    barraLlenado.style.width = p + "%";
    porcentaje.textContent = p + "%";
    barraContenedor.setAttribute("aria-valuenow", String(p));
}

function mostrarError(texto) {
    mensajeError.textContent = texto;
    mostrar(mensajeError);
    ocultar(areaProgreso);
}

async function iniciarConversion() {
    const url = inputUrl.value.trim();

    if (!url) {
        mostrarError("Por favor, ingresa una URL de YouTube.");
        return;
    }

    reiniciarUi();

    let jobId;
    try {
        const formData = new FormData();
        formData.append("youtube_url", url);

        const respuesta = await fetch("/convert", { method: "POST", body: formData });
        const datos = await respuesta.json();

        if (datos.estado !== "iniciado") {
            mostrarError("Error: " + (datos.error || "Falló la conversión."));
            restaurarBoton();
            return;
        }
        jobId = datos.job_id;
    } catch (err) {
        mostrarError("No se pudo conectar con el servidor. Verifica que siga activo.");
        restaurarBoton();
        return;
    }

    const fuente = new EventSource(`/stream/${jobId}`);

    fuente.addEventListener("progreso", (evento) => {
        const datos = JSON.parse(evento.data);

        if (datos.tipo === "ffmpeg" || datos.tipo === "video") {
            setBarra(datos.porcentaje);
        }
        mensaje.textContent = datos.mensaje || "Procesando…";
    });

    fuente.addEventListener("ok", (evento) => {
        const datos = JSON.parse(evento.data);
        trabajoFinalizado = true;
        fuente.close();

        ocultar(areaProgreso);
        ocultar(mensajeError);
        mostrar(areaResultado);
        botonDescarga.href = datos.archivo;
        botonDescarga.setAttribute("download", "");
        botonDescarga.textContent = `Descargar ${datos.nombre}`;

        if (datos.modo === "audio-nativo") {
            detalleResultado.textContent = "FFmpeg no disponible: se descargó el audio original. Para MP3, vuelve a intentarlo con internet.";
        } else {
            detalleResultado.textContent = "Convertido a MP3 · 192 kbps";
        }
        restaurarBoton();
    });

    fuente.addEventListener("error", (evento) => {
        if (trabajoFinalizado) return;
        try {
            const datos = JSON.parse(evento.data);
            mostrarError("Error: " + (datos.mensaje || "Falló la conversión."));
        } catch (err) {
            if (evento && evento.data) {
                mostrarError("Error: Falló la conversión.");
            }
        }
        fuente.close();
        restaurarBoton();
    });

    fuente.onerror = () => {
        // El stream se cerró sin evento terminal (servidor/trabajo caducó)
        if (trabajoFinalizado) return;
        if (!mensajeError.textContent) {
            mostrarError("La conexión con el servidor se interrumpió.");
        }
        fuente.close();
        restaurarBoton();
    };
}

function restaurarBoton() {
    botonConvertir.disabled = false;
    botonConvertir.classList.remove("cargando");
}