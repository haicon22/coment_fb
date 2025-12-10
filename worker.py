# worker.py
import redis
import json
import time
from fb_logic import fb_comment

r = redis.Redis(
    host='REDIS_HOST',
    port=REDIS_PORT,
    password='REDIS_PASSWORD',
    decode_responses=True
)

def process_job(job):
    job_id = job["job_id"]
    params = job["params"]

    ok, result = fb_comment(
        params["cookie"],
        params["uid"],
        params["dtsg"],
        params["comment_text"],
        params["id_cm"]
    )

    if ok:
        r.set(f"job:{job_id}:status", "done", ex=300)
        r.set(f"job:{job_id}:result", json.dumps(result), ex=300)
    else:
        r.set(f"job:{job_id}:status", "error", ex=300)
        r.set(f"job:{job_id}:result", json.dumps({"error": result}), ex=300)


def main():
    print("Worker started...")
    while True:
        # BLPOP: lấy job, block max 5 giây
        item = r.blpop("queue:fb_comment", timeout=5)
        if not item:
            continue

        _, data = item
        try:
            job = json.loads(data)
            process_job(job)
        except Exception as e:
            print("Error processing job:", e)
            # có thể log thêm

if __name__ == "__main__":
    main()
