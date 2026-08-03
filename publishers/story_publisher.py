import requests

def post_to_story(video_url, ig_user_id, access_token):
    url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    data = {"media_type": "STORIES", "video_url": video_url, "access_token": access_token}
    res = requests.post(url, data=data).json()
    if 'id' not in res: 
        print("Story create fail:", res); return
    pub_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    requests.post(pub_url, data={"creation_id": res['id'], "access_token": access_token})
    print("✅ Story posted!")
