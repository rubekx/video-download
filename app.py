from flask import Flask, request, jsonify, send_file
from redis import Redis
from rq import Queue
from rq.job import Job
import os

from tasks import download_video_task, get_video_info

app = Flask(__name__)

redis_conn = Redis(host="redis", port=6379)
queue = Queue(connection=redis_conn)

DOWNLOAD_FOLDER = "/app/downloads"

@app.route("/info", methods=["POST"])
def fetch_info():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL é obrigatória"}), 400
    
    try:
        resolutions = get_video_info(url)
        return jsonify({"resolutions": resolutions})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/download", methods=["POST"])
def create_job():
    data = request.json
    url = data.get("url")
    resolution = data.get("resolution", "best")

    if not url:
        return jsonify({"error": "URL é obrigatória"}), 400

    job = queue.enqueue(download_video_task, url, resolution)

    return jsonify({
        "job_id": job.id,
        "status": "queued"
    })


@app.route("/status/<job_id>")
def job_status(job_id):
    job = Job.fetch(job_id, connection=redis_conn)

    if job.is_finished:
        return jsonify({
            "status": "finished",
            "result": job.result
        })

    elif job.is_failed:
        return jsonify({"status": "failed"})

    else:
        return jsonify({
            "status": job.get_status(),
            "progress": job.meta.get("progress"),
            "speed": job.meta.get("speed"),
            "eta": job.meta.get("eta")
        })


@app.route("/file/<filename>")
def get_file(filename):
    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

    if not os.path.exists(filepath):
        return jsonify({"error": "arquivo não encontrado"}), 404

    return send_file(filepath, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)