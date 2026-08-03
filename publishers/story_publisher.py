import requests
def post_to_story(video_url, ig_user_id, access_token):
    url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    data = {"media_type": "STORIES", "video_url": video_url, "access_token": access_token}
    r = requests.post(url, data=data).json()
    print("Story Container:", r)
    if "id" not in r: return
    import time; time.sleep(5)
    pub = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    r2 = requests.post(pub, data={"creation_id": r["id"], "access_token": access_token}).json()
    print("Story Publish:", r2)
