from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import os
from dotenv import load_dotenv

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
        # Obtener las variables de entorno para cookies y user-agent
        cookies = os.getenv('YOUTUBE_COOKIES')  # Obtener las cookies desde las variables de entorno
        user_agent = os.getenv('USER_AGENT')

        if not cookies or not user_agent:
            return jsonify({'error': 'Faltan las variables de entorno YOUTUBE_COOKIES o USER_AGENT'}), 500

        # Configurar las opciones de yt-dlp
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format == 'mp3' else None,
            'cookies': cookies,  # Pasar las cookies directamente
            'headers': {
                'User-Agent': user_agent  # Usar User-Agent configurado en Render
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format == 'mp3':
                filename = f"{os.path.splitext(filename)[0]}.mp3"

        # Verificar si el archivo existe
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            return jsonify({'error': 'El archivo no se pudo generar.'}), 500

    except Exception as e:
        return jsonify({'error': f'Ocurrió un error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
