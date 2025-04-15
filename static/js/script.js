async function procesarDescarga() {
    const youtubeUrl = document.getElementById("youtube_url").value;
    const mensaje = document.getElementById("mensaje");
    const botonConvertir = document.getElementById("boton-convertir");
    const botonDescarga = document.getElementById("boton-descarga");
    
    // Reiniciar estado anterior antes de comenzar una nueva conversión
    mensaje.textContent = "";
    botonDescarga.style.display = "none"; // Ocultar el botón de descarga previo
    botonDescarga.href = ""; // Limpiar cualquier enlace previo
    botonConvertir.disabled = true;

    if (!youtubeUrl) {
        mensaje.textContent = "Por favor, ingrese una URL válida.";
        botonConvertir.disabled = false;
        return;
    }

    mensaje.textContent = "Procesando descarga...";

    try {
        const formData = new FormData();
        formData.append('youtube_url', youtubeUrl);

        const response = await fetch('/convert', {
            method: 'POST',
            body: formData,
        });

        const data = await response.json();

        if (data.estado === "completado") {
            mensaje.textContent = "";
            botonDescarga.style.display = "block";
            botonDescarga.href = data.archivo; // Enlace generado por el backend
            botonDescarga.textContent = `Descargar ${data.nombre}`; // Texto dinámico
        } else {
            mensaje.textContent = "Error: " + (data.error || "Falló la conversión");
        }
    } catch (error) {
        mensaje.textContent = "Ocurrió un error inesperado.";
    } finally{
        botonConvertir.disabled = false;
    }
}