from flask import Flask, request, jsonify
import redis
import json
import time
import base64

# ================= CONFIG =================
REDIS_URL = "redis://red-d4so7skcjiac739nr6a0:6379"
QUEUE_KEY = "fb_jobs"
RESULT_KEY = "fb_results"

# ================= APP ====================
app = Flask(__name__)
r = redis.from_url(REDIS_URL, decode_responses=True)

# ================= ROUTES =================
@app.route("/")
def home():
    return "TOOLFB API OK"

@app.route("/api/comment", methods=["POST"])
def api_comment():
    try:
        data = request.json

        job_id = str(int(time.time() * 1000))
        payload = {
            "job_id": job_id,
            "cookie": data["cookie"],
            "uid": data["uid"],
            "dtsg": data["dtsg"],
            "text": data["text"],
            "id_cm": data["id_cm"]
        }

        r.rpush(QUEUE_KEY, json.dumps(payload))

        return jsonify({
            "status": "queued",
            "job_id": job_id
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/api/result/<job_id>")
def api_result(job_id):
    res = r.get(f"{RESULT_KEY}:{job_id}")
    if not res:
        return jsonify({"status": "processing"})
    return jsonify(json.loads(res))
