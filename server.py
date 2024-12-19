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
        # Configuración de yt-dlp para usar cookies desde el navegador Chrome
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
            'format': 'bestaudio/best' if format == 'mp3' else 'best',
            'cookiesfrombrowser': ('chrome',),  # Usa las cookies del navegador Chrome
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }] if format == 'mp3' else None,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if format == 'mp3':
                filename = f"{os.path.splitext(filename)[0]}.mp3"

        return send_file(filename, as_attachment=True)

    except yt_dlp.utils.DownloadError as e:
        # Errores relacionados con yt-dlp
        return jsonify({'error': f'Error de descarga: {str(e)}'}), 500
    except Exception as e:
        # Otros errores
        return jsonify({'error': f'Error inesperado: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
