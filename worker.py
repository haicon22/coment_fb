import redis
import json
import os
import time
from fb_logic import fb_comment

REDIS_URL = "redis://red-d4so7skcjiac739nr6a0:6379"

import redis
r = redis.from_url(REDIS_URL, decode_responses=True)
print("WORKER STARTED")

while True:
    job = r.blpop("fb_queue", timeout=5)
    if not job:
        continue

    try:
        job_data = json.loads(job[1])
    except:
        continue

    job_id = job_data["job_id"]
    p = job_data["data"]

    ok, fb_result = fb_comment(
        p["cookie"],
        p["uid"],
        p["dtsg"],
        p["comment_text"],
        p["id_cm"]
    )

    # ✅ Delay tránh FB quét
    time.sleep(2)

    if ok:
        r.set(
            f"job:{job_id}",
            json.dumps({
                "status": "success",
                "fb_result": fb_result
            }),
            ex=300
        )
    else:
        r.set(
            f"job:{job_id}",
            json.dumps({
                "status": "error",
                "fb_result": fb_result
            }),
            ex=300
        )
