import redis, json, os, time
from fb_logic import fb_comment

r = redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)

print("WORKER STARTED")

while True:
    job = r.blpop("fb_queue", timeout=5)
    if not job:
        continue

    data = json.loads(job[1])
    p = data["data"]
    job_id = data["job_id"]

    ok, fb_result = fb_comment(
        p["cookie"],
        p["uid"],
        p["dtsg"],
        p["comment_text"],
        p["id_cm"]
    )

    time.sleep(2)  # chống FB quét

    if ok:
        r.set(
            f"job:{job_id}",
            json.dumps({
                "status": "success",
                "fb": fb_result
            }),
            ex=300
        )
    else:
        r.set(
            f"job:{job_id}",
            json.dumps({
                "status": "error",
                "fb": fb_result
            }),
            ex=300
        )
        
