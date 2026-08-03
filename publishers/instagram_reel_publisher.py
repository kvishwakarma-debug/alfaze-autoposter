import requests, time

def post_to_instagram_reel(video_url, ig_user_id, access_token, caption):
    print(f"Posting IG Reel: {video_url}")
    # 1. Container for REEL
    r = requests.post(f"https://graph.facebook.com/v20.0/{ig_user_id}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "share_to_feed": True,
        "access_token": access_token
    }).json()
    print("Reel Container:", r)
    if "id" not in r:
        return r
    
    cid = r["id"]
    # 2. Wait for FINISHED
    for i in range(6):
        time.sleep(5)
        status = requests.get(f"https://graph.facebook.com/v20.0/{cid}?fields=status_code&access_token={access_token}").json()
        print(f"Reel status: {status}")
        if status.get("status_code") == "FINISHED":
            break
    
    # 3. Publish
    r2 = requests.post(f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish", data={
        "creation_id": cid,
        "access_token": access_token
    }).json()
    print("Reel Publish:", r2)
    return r2
