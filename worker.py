import redis
import json
import time
from fb_logic import fb_comment

REDIS_URL = "redis://red-d4so7skcjiac739nr6a0:6379"
QUEUE_KEY = "fb_jobs"
RESULT_KEY = "fb_results"

r = redis.from_url(REDIS_URL, decode_responses=True)

def main():
    print("WORKER STARTED")
    while True:
        job = r.lpop(QUEUE_KEY)
        if not job:
            time.sleep(1)
            continue

        data = json.loads(job)
        job_id = data["job_id"]

        try:
            ok, result = fb_comment(
                data["cookie"],
                data["uid"],
                data["dtsg"],
                data["text"],
                data["id_cm"]
            )

            r.set(
                f"{RESULT_KEY}:{job_id}",
                json.dumps({
                    "status": "success" if ok else "failed",
                    "result": result
                }),
                ex=300
            )

        except Exception as e:
            r.set(
                f"{RESULT_KEY}:{job_id}",
                json.dumps({
                    "status": "error",
                    "error": str(e)
                }),
                ex=300
            )

if __name__ == "__main__":
    main()
