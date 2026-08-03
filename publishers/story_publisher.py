import requests
import time

def post_to_story(video_url, ig_user_id, access_token):
    print(f"Posting Story: {video_url}")
    r = requests.post(f"https://graph.facebook.com/v20.0/{ig_user_id}/media", data={
        "media_type": "STORIES",
        "video_url": video_url,
        "access_token": access_token
    }).json()
    print("Story Container:", r)
    if "id" not in r:
        return r
    cid = r["id"]
    for i in range(18):
        time.sleep(5)
        s = requests.get(f"https://graph.facebook.com/v20.0/{cid}?fields=status_code&access_token={access_token}").json()
        print(f"Story status {i*5}s: {s}")
        if s.get("status_code") == "FINISHED":
            break
    r2 = requests.post(f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish", data={
        "creation_id": cid,
        "access_token": access_token
    }).json()
    print("Story Publish:", r2)
    return r2
