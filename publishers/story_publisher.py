import requests, time

def post_to_story(video_url, ig_user_id, access_token):
    print(f"Posting Story: {video_url}")
    # 1. Container
    r = requests.post(f"https://graph.facebook.com/v20.0/{ig_user_id}/media", data={
        "media_type": "STORIES",
        "video_url": video_url,
        "access_token": access_token
    }).json()
    print("Story Container:", r)
    if "id" not in r:
        return
    
    creation_id = r["id"]
    # 2. WAIT - 30 sec tak check karo ready hua ki nahi
    for i in range(6):
        print(f"Waiting for story ready... {i*5}s")
        time.sleep(5)
        status = requests.get(f"https://graph.facebook.com/v20.0/{creation_id}?fields=status_code&access_token={access_token}").json()
        print(f"Story status: {status}")
        if status.get("status_code") == "FINISHED":
            break
    
    # 3. Publish
    r2 = requests.post(f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish", data={
        "creation_id": creation_id,
        "access_token": access_token
    }).json()
    print("Story Publish:", r2)
