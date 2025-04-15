from flask import Flask, request, render_template, jsonify, send_file, url_for
import os
import yt_dlp

convertidor = Flask(__name__)

@convertidor.route('/')
def retornar_html():
    return render_template('index.html')

@convertidor.route('/convert', methods=['POST'])
def convert():
    youtube_url = request.form['youtube_url']

    # Validación de la URL
    if not ("youtube.com" in youtube_url or "youtu.be" in youtube_url):
        return jsonify({'error': 'URL no válida', 'estado': 'fallido'})
    
    try:
        # Configuración de opciones para yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        # Crear la carpeta de descargas si no existe
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        # Descargar el audio usando yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            file_name = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            print(f"Archivo convertido y disponible: {file_name}")

        # Devuelve el estado y el enlace de descarga
        return jsonify({'estado': 'completado', 'archivo': url_for('descargar', filename=os.path.basename(file_name)), 'nombre': os.path.basename(file_name)})

    except Exception as e:
        return jsonify({'error': str(e), 'estado': 'fallido'})

@convertidor.route('/downloads/<filename>')
def descargar(filename):
    file_path = os.path.join('downloads', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "Error: El archivo no existe.", 404

if __name__ == '__main__':
    convertidor.run(debug=True, host="0.0.0.0", port=5000)
