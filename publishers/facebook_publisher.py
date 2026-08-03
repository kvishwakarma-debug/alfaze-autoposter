import requests, time

def post_to_fb_reel(video_url, page_id, access_token, caption):
    print(f"Posting FB Video: {video_url}")
    # FB Page pe reel nahi, normal video ke roop me post karo - 100% kaam karta hai
    r = requests.post(f"https://graph.facebook.com/v20.0/{page_id}/videos", data={
        "file_url": video_url,
        "description": caption,
        "access_token": access_token
    }).json()
    print("FB Video Publish:", r)
    return r
