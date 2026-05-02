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

def progress_hook(d):
    job = get_current_job()
    if job and d['status'] == 'downloading':
        progress = clean_ansi(d.get('_percent_str', '0%')).strip()
        speed = clean_ansi(d.get('_speed_str', '')).strip()
        eta = clean_ansi(d.get('_eta_str', '')).strip()
        
        job.meta['progress'] = progress
        job.meta['speed'] = speed
        job.meta['eta'] = eta
        job.save_meta()

def download_video_task(url):
    filename = f"{uuid.uuid4()}.mp4"
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
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