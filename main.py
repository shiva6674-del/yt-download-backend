from flask import Flask, request, jsonify, send_file
from yt_dlp import YoutubeDL
import os
import uuid

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return "YouTube Downloader is running."

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get('url')
    fmt = data.get('format', 'mp4')

    if not url:
        return jsonify({'error': 'Missing URL'}), 400

    filename = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_FOLDER, filename + '.%(ext)s')

    ydl_opts = {
        'format': 'bestaudio/best' if fmt == 'mp3' else 'best',
        'outtmpl': output_path,
    }

    if fmt == 'mp3':
        ydl_opts.update({
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Find downloaded file
    for file in os.listdir(DOWNLOAD_FOLDER):
        if filename in file:
            return jsonify({'download_url': request.host_url + 'file/' + file})

    return jsonify({'error': 'Download failed'}), 500

@app.route('/file/<path:filename>')
def serve_file(filename):
    return send_file(os.path.join(DOWNLOAD_FOLDER, filename), as_attachment=True)

app.run(host="0.0.0.0", port=8080)
