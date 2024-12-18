from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)

# Permitir todas las solicitudes de cualquier origen
CORS(app, resources={r"/*": {"origins": "*"}}, allow_headers=["Content-Type"])

# Directorio donde se almacenarán los archivos descargados
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/convert', methods=['POST', 'OPTIONS'])
def convert():
    # Manejo de solicitudes OPTIONS (preflight)
    if request.method == 'OPTIONS':
        return '', 200

    data = request.json
    url = data.get('url')
    format = data.get('format')

    if not url or not format:
        return jsonify({'error': 'Missing URL or format'}), 400

    try:
        # Definimos las opciones para yt-dlp según el formato solicitado
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format == 'mp3' else None
        }

        # Ejecutamos yt-dlp para descargar el video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format == 'mp3':
                filename = f"{os.path.splitext(filename)[0]}.mp3"
        
        # Enviamos el archivo descargado como respuesta
        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
