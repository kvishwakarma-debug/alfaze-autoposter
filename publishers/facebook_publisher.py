import requests
def post_to_fb_reel(video_url, page_id, access_token, caption):
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    data = {"video_url": video_url, "description": caption, "access_token": access_token}
    r = requests.post(url, data=data)
    print("✅ FB Reel posted:", r.json())
