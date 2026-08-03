import requests

def post_to_fb_reel(video_url, page_id, access_token, caption):
    print(f"Posting FB Video: {video_url}")
    r = requests.post(f"https://graph.facebook.com/v20.0/{page_id}/videos", data={
        "file_url": video_url,
        "description": caption,
        "access_token": access_token
    }).json()
    print("FB Video Publish:", r)
    return r

def post_to_fb_feed(image_url, page_id, access_token, caption):
    print(f"Posting FB Feed Photo: {image_url}")
    r = requests.post(f"https://graph.facebook.com/v20.0/{page_id}/photos", data={
        "url": image_url,
        "caption": caption,
        "access_token": access_token
    }).json()
    print("FB Feed Publish:", r)
    return r
