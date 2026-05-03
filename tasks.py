from yt_dlp import YoutubeDL
import os
import uuid
import re
from rq import get_current_job

DOWNLOAD_FOLDER = "/app/downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

def clean_ansi(text):
    if not text:
        return ""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def get_video_info(url):
    ydl_opts = {
        'noplaylist': True,
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            resolutions = set()
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('height'):
                    resolutions.add(f.get('height'))
            return sorted(list(resolutions), reverse=True)
        except Exception:
            return []

def download_video_task(url, resolution="best"):
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)
    job = get_current_job()

    def progress_hook(d):
        if job and d['status'] == 'downloading':
            progress = clean_ansi(d.get('_percent_str', '0%')).strip()
            speed = clean_ansi(d.get('_speed_str', '')).strip()
            eta = clean_ansi(d.get('_eta_str', '')).strip()
            
            job.meta['progress'] = progress
            job.meta['speed'] = speed
            job.meta['eta'] = eta
            job.save_meta()

    if resolution == "best":
        format_str = 'bestvideo+bestaudio/best'
    else:
        format_str = f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]/best'

    ydl_opts = {
        'format': format_str,
        'merge_output_format': 'mp4',
        'outtmpl': filepath,
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [progress_hook],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return {
        "status": "done",
        "file": filename
    }