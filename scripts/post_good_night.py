"""
Good Night Auto Poster - Alfaze Ulfat - NO BOX VERSION + Story
Location: scripts/post_good_night.py
Uses: IG_USER_ID, PAGE_ACCESS_TOKEN, PAGE_ID
Fix: No transparent box, direct text on background with glow
"""

import json, random, os, requests, time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
JSON_FILE = os.path.join(os.path.dirname(__file__), "good_night_shayari_with_backgrounds.json")
TRACKER_FILE = os.path.join(os.path.dirname(__file__), "last_good_night_index.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OUTPUT_IMAGE = os.path.join(OUTPUT_DIR, "good_night.jpg")

FOOTER_TEXT = "@alfaze.ulfat -- Good Night :)"

HINDI_FONTS = [
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Medium.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]

ENGLISH_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]

def get_hindi_font(size):
    for p in HINDI_FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def get_english_font(size):
    for p in ENGLISH_FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

def get_random_entry():
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    last_idx = -1
    if os.path.exists(TRACKER_FILE):
        try:
            last_idx = json.load(open(TRACKER_FILE, encoding='utf-8')).get('last_index', -1)
        except:
            pass
    idx = random.randint(0, len(data)-1)
    while idx == last_idx and len(data) > 1:
        idx = random.randint(0, len(data)-1)
    json.dump({"last_index": idx, "last_id": data[idx]['id'], "time": str(datetime.now())}, open(TRACKER_FILE,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
    return data[idx]

def generate_background(prompt):
    # No window, clean night sky for direct text
    full = f"{prompt}, beautiful clear night sky with stars and soft moon, dark blue, no window, no frame, no building, clean, 1080x1080"
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(full)}?width=1080&height=1080&nologo=true&model=flux&seed={random.randint(0,999999)}"
    print(f"Generating BG: {full[:80]}...")
    r = requests.get(url, timeout=90)
    if r.status_code == 200:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        open(OUTPUT_IMAGE,'wb').write(r.content)
        return OUTPUT_IMAGE
    print(f"BG failed {r.status_code}")
    return None

def create_poster(entry, bg_path):
    img = Image.open(bg_path).convert("RGBA")
    W,H = img.size
    # NO BOX - direct on background
    draw = ImageDraw.Draw(img)
    
    main_font = get_hindi_font(44)  # Chhota for no cut
    footer_font = get_english_font(22)
    
    shayari = entry['shayari']
    footer = FOOTER_TEXT

    def wrap(text,font,max_w):
        words=text.split(); lines=[]; cur=""
        for w in words:
            test=cur+" "+w if cur else w
            if draw.textbbox((0,0),test,font=font)[2] > max_w:
                if cur: lines.append(cur)
                cur=w
            else: cur=test
        if cur: lines.append(cur)
        return lines

    max_width = W - 260  # More padding, no box so need safe
    lines = wrap(shayari, main_font, max_width)
    
    line_height = 64
    total_height = len(lines) * line_height
    start_y = (H - total_height)//2

    for line in lines:
        bbox = draw.textbbox((0,0), line, font=main_font)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w)//2
        
        # Strong glow/shadow for direct background visibility - NO BOX NEEDED
        # Multiple shadows for glow effect
        for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (-1,0), (1,0), (0,-1), (0,1)]:
            draw.text((x+dx, start_y+dy), line, font=main_font, fill="#000000")
        # Main text in soft white
        draw.text((x, start_y), line, font=main_font, fill="#FFFFFF")
        start_y += line_height

    # Footer - LEFT SIDE with margin - no cut
    fx = 40  # left margin 40px
    fy = H - 45  # bottom margin 45px
    # Shadow for visibility
    draw.text((fx+1, fy+1), footer, font=footer_font, fill="#000000")
    draw.text((fx, fy), footer, font=footer_font, fill="#E0E0E0")
    
    img.convert("RGB").save(OUTPUT_IMAGE, quality=95)
    print(f"Poster created NO BOX: {OUTPUT_IMAGE} Lines:{len(lines)}")
    return OUTPUT_IMAGE

def upload_to_uguu(p):
    print(f"Uploading {p} to uguu.se...")
    try:
        r = requests.post("https://uguu.se/upload.php", files={"files[]": open(p,'rb')}, timeout=60)
        if r.status_code==200:
            url = r.json()['files'][0]['url']
            print(f"uguu URL: {url}")
            return url
        print(f"uguu failed: {r.text[:200]}")
    except Exception as e:
        print(f"uguu error: {e}")
    return None

def publish_to_instagram(image_url, caption):
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")
    print(f"DEBUG IG_USER_ID: {bool(ig_user_id)} len={len(ig_user_id) if ig_user_id else 0}")
    print(f"DEBUG TOKEN: {bool(token)} len={len(token) if token else 0}")
    if not token or not ig_user_id:
        print("Skipping IG Feed")
        return False
    container_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    payload = {"image_url": image_url, "caption": caption, "access_token": token}
    r = requests.post(container_url, data=payload, timeout=60)
    print(f"IG Feed Container: {r.status_code} - {r.text[:600]}")
    if r.status_code != 200:
        return False
    creation_id = r.json().get("id")
    time.sleep(15)
    publish_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    r2 = requests.post(publish_url, data={"creation_id": creation_id, "access_token": token}, timeout=60)
    print(f"IG Feed Publish: {r2.status_code} - {r2.text[:600]}")
    return r2.status_code == 200

def publish_to_instagram_story(image_url):
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")
    if not token or not ig_user_id:
        return False
    print(f"Publishing IG Story: {ig_user_id}")
    container_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    payload = {"image_url": image_url, "media_type": "STORIES", "access_token": token}
    r = requests.post(container_url, data=payload, timeout=60)
    print(f"IG Story Container: {r.status_code} - {r.text[:600]}")
    if r.status_code != 200:
        return False
    creation_id = r.json().get("id")
    time.sleep(15)
    publish_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    r2 = requests.post(publish_url, data={"creation_id": creation_id, "access_token": token}, timeout=60)
    print(f"IG Story Publish: {r2.status_code} - {r2.text[:600]}")
    return r2.status_code == 200

def publish_to_facebook(image_url, caption):
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    page_id = os.environ.get("PAGE_ID")
    if not token or not page_id:
        return False
    print(f"Publishing FB Feed: {page_id}")
    fb_url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    payload = {"url": image_url, "caption": caption, "access_token": token}
    r = requests.post(fb_url, data=payload, timeout=60)
    print(f"FB Feed: {r.status_code} - {r.text[:600]}")
    return r.status_code == 200

def publish_to_facebook_story(image_url):
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    page_id = os.environ.get("PAGE_ID")
    if not token or not page_id:
        return False
    print(f"Publishing FB Story: {page_id}")
    fb_url = f"https://graph.facebook.com/v20.0/{page_id}/photo_stories"
    payload = {"url": image_url, "access_token": token}
    r = requests.post(fb_url, data=payload, timeout=60)
    print(f"FB Story: {r.status_code} - {r.text[:600]}")
    if r.status_code != 200:
        fb_url2 = f"https://graph.facebook.com/v20.0/{page_id}/stories"
        payload2 = {"photo_image_url": image_url, "access_token": token}
        r2 = requests.post(fb_url2, data=payload2, timeout=60)
        print(f"FB Story Fallback: {r2.status_code} - {r2.text[:600]}")
        return r2.status_code == 200
    return r.status_code == 200

if __name__=="__main__":
    entry = get_random_entry()
    print(f"Selected [{entry['id']}]: {entry['shayari']}")
    bg = generate_background(entry['background_prompt'])
    if not bg:
        exit(1)
    poster = create_poster(entry, bg)
    public_url = upload_to_uguu(poster)
    if not public_url:
        exit(1)
    caption = f"{entry['shayari']}\n\n{FOOTER_TEXT}\n\n#goodnight #alfazeulfat"
    print("\n--- Starting Publishing ---")
    ig_ok = publish_to_instagram(public_url, caption)
    fb_ok = publish_to_facebook(public_url, caption)
    ig_story_ok = publish_to_instagram_story(public_url)
    fb_story_ok = publish_to_facebook_story(public_url)
    print(f"\nResults: IG Feed={ig_ok} FB Feed={fb_ok} IG Story={ig_story_ok} FB Story={fb_story_ok}")
