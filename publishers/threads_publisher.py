import requests
import time
import os

def post_to_threads(image_url, caption):
    tid = os.getenv("THREADS_USER_ID") or os.getenv("IG_USER_ID")
    token = os.getenv("PAGE_ACCESS_TOKEN")
    if not tid:
        print("THREADS_USER_ID not set, skipping threads")
        return
    print(f"Posting to Threads: {image_url}")
    try:
        r = requests.post(f"https://graph.threads.net/v1.0/{tid}/threads", data={
            "media_type": "IMAGE",
            "image_url": image_url,
            "text": caption[:450],
            "access_token": token
        }).json()
        print("Threads Container:", r)
        if "id" not in r:
            return r
        time.sleep(15)
        r2 = requests.post(f"https://graph.threads.net/v1.0/{tid}/threads_publish", data={
            "creation_id": r["id"],
            "access_token": token
        }).json()
        print("Threads Publish:", r2)
        return r2
    except Exception as e:
        print(f"Threads error: {e}")
        return None
