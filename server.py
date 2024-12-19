from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os

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
        cookies_file = os.getenv('YOUTUBE_COOKIES')  # Ruta al archivo de cookies
        user_agent = os.getenv('USER_AGENT')  # User-Agent para el request

        # Configurar las opciones de yt-dlp
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format == 'mp3' else None,
            'cookiefile': cookies_file,  # Usar el archivo de cookies configurado en Render
            'headers': {
                'User-Agent': user_agent  # Usar el User-Agent configurado en Render
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format == 'mp3':
                filename = f"{os.path.splitext(filename)[0]}.mp3"

        return send_file(filename, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
