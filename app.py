# app.py
from flask import Flask, request, jsonify
import redis
import json
import uuid
import time

# Kết nối Redis (host, port, password theo info free tier của bạn)
r = redis.Redis(
    host='REDIS_HOST',
    port=REDIS_PORT,
    password='REDIS_PASSWORD',
    decode_responses=True
)

app = Flask(__name__)

# ----- config chống spam cơ bản -----
MAX_PER_MIN_PER_IP = 30  # 30 request / phút / IP
API_SECRET = "YOUR_API_SECRET"  # đơn giản

def rate_limit(ip):
    key = f"rate:{ip}:{int(time.time() // 60)}"
    cnt = r.incr(key)
    if cnt == 1:
        r.expire(key, 60)
    return cnt <= MAX_PER_MIN_PER_IP

@app.route("/api/comment", methods=["POST"])
def api_comment():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # Check API secret đơn giản
    secret = request.args.get("secret") or request.headers.get("X-Api-Key")
    if secret != API_SECRET:
        return jsonify({"error": "Invalid secret"}), 403

    if not rate_limit(ip):
        return jsonify({"error": "Too many requests"}), 429

    try:
        data = request.get_json(force=True)
    except:
        return jsonify({"error": "Invalid JSON"}), 400

    required = ["cookie", "uid", "dtsg", "comment_text", "id_cm"]
    for k in required:
        if k not in data or not data[k]:
            return jsonify({"error": f"Missing {k}"}), 400

    job_id = str(uuid.uuid4())
    job_data = {
        "job_id": job_id,
        "ip": ip,
        "params": {
            "cookie": data["cookie"],
            "uid": data["uid"],
            "dtsg": data["dtsg"],
            "comment_text": data["comment_text"],
            "id_cm": data["id_cm"]
        },
        "ts": time.time()
    }

    # Push vào queue Redis (list)
    r.rpush("queue:fb_comment", json.dumps(job_data))
    # Set status pending
    r.set(f"job:{job_id}:status", "pending", ex=300)

    return jsonify({"job_id": job_id, "status": "queued"})

@app.route("/api/result/<job_id>")
def api_result(job_id):
    status = r.get(f"job:{job_id}:status")
    if not status:
        return jsonify({"error": "Job not found"}), 404

    if status == "pending":
        return jsonify({"status": "pending"})

    # Đọc result
    res = r.get(f"job:{job_id}:result")
    try:
        res = json.loads(res)
    except:
        pass

    return jsonify({"status": status, "result": res})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
