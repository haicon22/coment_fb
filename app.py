from flask import Flask, request, jsonify
import redis
import json
import uuid
import os
import time

app = Flask(__name__)

# ===== REDIS =====
REDIS_URL = "redis://red-d4so7skcjiac739nr6a0:6379"

import redis
r = redis.from_url(REDIS_URL, decode_responses=True)
r.ping()  # test connect


@app.route("/")
def home():
    return "TOOLFB API OK"

# ===== GỬI JOB COMMENT =====
@app.route("/api/comment", methods=["POST"])
def api_comment():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # ✅ Rate limit IP (bắt buộc, để public không sập)
    key = f"rate:{ip}:{int(time.time() // 60)}"
    count = r.incr(key)
    if count == 1:
        r.expire(key, 60)
    if count > 10:
        return jsonify({
            "status": "error",
            "msg": "Too many requests, slow down"
        }), 429

    try:
        data = request.get_json(force=True)
    except:
        return jsonify({
            "status": "error",
            "msg": "Invalid JSON"
        }), 400

    need = ["cookie", "uid", "dtsg", "comment_text", "id_cm"]
    for k in need:
        if k not in data or not data[k]:
            return jsonify({
                "status": "error",
                "msg": f"Missing {k}"
            }), 400

    job_id = str(uuid.uuid4())

    job_data = {
        "job_id": job_id,
        "ip": ip,
        "data": {
            "cookie": data["cookie"],
            "uid": data["uid"],
            "dtsg": data["dtsg"],
            "comment_text": data["comment_text"],
            "id_cm": data["id_cm"]
        },
        "time": time.time()
    }

    # ✅ Đưa vào queue
    r.rpush("fb_queue", json.dumps(job_data))

    # ✅ Set trạng thái ban đầu
    r.set(
        f"job:{job_id}",
        json.dumps({"status": "pending"}),
        ex=300
    )

    return jsonify({
        "status": "queued",
        "job_id": job_id
    })


# ===== CHECK KẾT QUẢ =====
@app.route("/api/result/<job_id>")
def api_result(job_id):
    rs = r.get(f"job:{job_id}")
    if not rs:
        return jsonify({"status": "pending"})

    try:
        return jsonify(json.loads(rs))
    except:
        return jsonify({
            "status": "unknown",
            "raw": rs
        })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
