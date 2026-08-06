"""
Good Night Auto Poster - Alfaze Ulfat - FINAL WITH PUBLISHING
Location: scripts/post_good_night.py
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

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Medium.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
]

def get_font(size):
    for path in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
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
    full = f"{prompt}, dark blue night aesthetic, 1080x1080, moody paper texture, high quality"
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
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(overlay).rectangle([(0,H*0.30),(W,H*0.68)], fill=(0,0,20,75))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    main_font = get_font(54)
    footer_font = get_font(26)
    shayari = entry['shayari']
    footer = entry.get('footer_text', FOOTER_TEXT)
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
    lines = wrap(shayari, main_font, W-180)
    start_y = H//2 - len(lines)*39 - 20
    start_x = 90
    for line in lines:
        draw.text((start_x,start_y),line,font=main_font,fill="#F5F1E8",stroke_width=1,stroke_fill="#1A1A2E")
        start_y+=78
    bbox = draw.textbbox((0,0),footer,font=footer_font)
    fx = W - (bbox[2]-bbox[0]) - 45
    fy = H - (bbox[3]-bbox[1]) - 40
    draw.text((fx,fy),footer,font=footer_font,fill="#E8DDD0")
    img.convert("RGB").save(OUTPUT_IMAGE, quality=96)
    print(f"Poster created: {OUTPUT_IMAGE}")
    return OUTPUT_IMAGE

def upload_to_uguu(p):
    print(f"Uploading {p} to uguu.se...")
    try:
        r = requests.post("https://uguu.se/upload.php", files={"files[]": open(p,'rb')}, timeout=60)
        if r.status_code==200:
            j = r.json()
            url = j['files'][0]['url']
            print(f"uguu URL: {url}")
            return url
        print(f"uguu failed: {r.text[:200]}")
    except Exception as e:
        print(f"uguu error: {e}")
    return None

def publish_to_instagram(image_url, caption):
    """Graph API v20.0 - same fix as English quotes"""
    token = os.environ.get("ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")
    if not token or not ig_user_id:
        print("Skipping IG: ACCESS_TOKEN or IG_USER_ID not set")
        return False
    
    print(f"Publishing to Instagram: {ig_user_id}")
    # Step 1: Create container
    container_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": token
    }
    r = requests.post(container_url, data=payload, timeout=60)
    print(f"IG Container Response: {r.status_code} - {r.text[:500]}")
    if r.status_code != 200:
        return False
    
    creation_id = r.json().get("id")
    if not creation_id:
        return False
    
    # Wait for processing
    time.sleep(10)
    
    # Step 2: Publish
    publish_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    payload2 = {
        "creation_id": creation_id,
        "access_token": token
    }
    r2 = requests.post(publish_url, data=payload2, timeout=60)
    print(f"IG Publish Response: {r2.status_code} - {r2.text[:500]}")
    return r2.status_code == 200

def publish_to_facebook(image_url, caption):
    token = os.environ.get("ACCESS_TOKEN")
    page_id = os.environ.get("FB_PAGE_ID")
    if not token or not page_id:
        print("Skipping FB: ACCESS_TOKEN or FB_PAGE_ID not set")
        return False
    
    print(f"Publishing to Facebook Page: {page_id}")
    fb_url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": token
    }
    r = requests.post(fb_url, data=payload, timeout=60)
    print(f"FB Publish Response: {r.status_code} - {r.text[:500]}")
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
        print("Failed to get public URL, cannot publish")
        exit(1)
    
    caption = f"{entry['shayari']}\n\n{FOOTER_TEXT}\n\n#goodnight #nightthoughts #alfazeulfat #shayari #hindishayari #raat #sukoon"
    
    print("\n--- Starting Publishing ---")
    ig_ok = publish_to_instagram(public_url, caption)
    fb_ok = publish_to_facebook(public_url, caption)
    
    print(f"\nResults: IG={'OK' if ig_ok else 'FAIL'} FB={'OK' if fb_ok else 'FAIL'}")
    print(f"Done: {poster} -> {public_url}")
