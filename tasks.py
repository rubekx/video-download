from yt_dlp import YoutubeDL
import os
import uuid

DOWNLOAD_FOLDER = "/app/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def download_video_task(url):
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': filepath,
        'noplaylist': True,
        'quiet': True
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return {
        "status": "done",
        "file": filename
    }