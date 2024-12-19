from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
from dotenv import load_dotenv  # Para cargar variables de entorno, si lo necesitas localmente

# Cargar las variables de entorno
load_dotenv()

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    url = data.get('url')
    format = data.get('format')

    if not url or not format:
        return jsonify({'error': 'Missing URL or format'}), 400

    try:
        # Acceder a las variables de entorno de Render
        cookies_data = os.getenv('YOUTUBE_COOKIES')  # Obtener las cookies como texto
        user_agent = os.getenv('USER_AGENT')  # Obtener el User-Agent

        if not cookies_data or not user_agent:
            return jsonify({'error': 'Missing cookies or user-agent in environment variables'}), 400

        # Guardar las cookies en un archivo temporal
        cookies_file = 'cookies.txt'
        with open(cookies_file, 'w') as f:
            f.write(cookies_data)

        # Configurar las opciones de yt-dlp
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format == 'mp3' else None,
            'cookiefile': cookies_file,  # Usar el archivo de cookies
            'headers': {
                'User-Agent': user_agent  # Usar el User-Agent configurado
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format == 'mp3':
                filename = f"{os.path.splitext(filename)[0]}.mp3"

        # Eliminar el archivo de cookies temporal después de su uso
        os.remove(cookies_file)

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
