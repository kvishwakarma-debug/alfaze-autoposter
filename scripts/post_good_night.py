"""
Good Night Auto Poster - Alfaze Ulfat - FIXED TEXT CUT + FOOTER
Location: scripts/post_good_night.py
Uses: IG_USER_ID, PAGE_ACCESS_TOKEN, PAGE_ID
Fix: Smaller Hindi font, more padding, English font for footer
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

# Hindi fonts
HINDI_FONTS = [
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSerifDevanagari-Medium.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
]

# English footer fonts - ye boxes fix karega
ENGLISH_FONTS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
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
    full = f"{prompt}, dark blue night aesthetic, 1080x1080, moody paper texture, high quality, no window frame, no text"
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
    # Safe overlay - thoda zyada transparent + bigger
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    draw_overlay = ImageDraw.Draw(overlay)
    # Center safe zone: 20% to 75%
    draw_overlay.rectangle([(W*0.05, H*0.25),(W*0.95, H*0.75)], fill=(0,0,15,110))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    
    # FIX 1: Text size chhota kiya 54 -> 42
    main_font = get_hindi_font(42)
    # FIX 2: Footer ke liye English font - boxes fix
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

    # FIX 3: Side padding badhaya W-180 -> W-240 (120px each side)
    max_width = W - 240
    lines = wrap(shayari, main_font, max_width)
    
    # Center calculation with smaller line height
    line_height = 62  # pehle 78 tha
    total_height = len(lines) * line_height
    start_y = (H - total_height)//2 - 10
    start_x = 120  # pehle 90 tha - ab safe

    for line in lines:
        # Center align each line
        bbox = draw.textbbox((0,0), line, font=main_font)
        text_w = bbox[2] - bbox[0]
        x = (W - text_w)//2
        # Soft shadow for readability
        draw.text((x+2, start_y+2), line, font=main_font, fill="#000000", stroke_width=0)
        draw.text((x, start_y), line, font=main_font, fill="#F5F1E8", stroke_width=0)
        start_y += line_height

    # FIX 4: Footer with English font - bottom right but safe
    bbox = draw.textbbox((0,0), footer, font=footer_font)
    fx = W - (bbox[2]-bbox[0]) - 35
    fy = H - (bbox[3]-bbox[1]) - 30
    # Footer background for visibility
    draw.text((fx+1, fy+1), footer, font=footer_font, fill="#000000")
    draw.text((fx, fy), footer, font=footer_font, fill="#E8DDD0")
    
    img.convert("RGB").save(OUTPUT_IMAGE, quality=95)
    print(f"Poster created: {OUTPUT_IMAGE} - Lines: {len(lines)} Font: 42px")
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
    print(f"DEBUG - IG_USER_ID: {bool(ig_user_id)} len={len(ig_user_id) if ig_user_id else 0}")
    print(f"DEBUG - PAGE_ACCESS_TOKEN: {bool(token)} len={len(token) if token else 0}")
    if not token or not ig_user_id:
        print("Skipping IG: Token or ID empty")
        return False
    container_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    payload = {"image_url": image_url, "caption": caption, "access_token": token}
    r = requests.post(container_url, data=payload, timeout=60)
    print(f"IG Container: {r.status_code} - {r.text[:800]}")
    if r.status_code != 200:
        return False
    creation_id = r.json().get("id")
    time.sleep(15)
    publish_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    r2 = requests.post(publish_url, data={"creation_id": creation_id, "access_token": token}, timeout=60)
    print(f"IG Publish: {r2.status_code} - {r2.text[:800]}")
    return r2.status_code == 200

def publish_to_facebook(image_url, caption):
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    page_id = os.environ.get("PAGE_ID")
    print(f"DEBUG - PAGE_ID: {bool(page_id)} len={len(page_id) if page_id else 0}")
    if not token or not page_id:
        return False
    fb_url = f"https://graph.facebook.com/v20.0/{page_id}/photos"
    payload = {"url": image_url, "caption": caption, "access_token": token}
    r = requests.post(fb_url, data=payload, timeout=60)
    print(f"FB Publish: {r.status_code} - {r.text[:800]}")
    return r.status_code == 200


def publish_to_instagram_story(image_url):
    """Instagram Story - 24h story"""
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    ig_user_id = os.environ.get("IG_USER_ID")
    if not token or not ig_user_id:
        print("Skipping IG Story: Token/ID empty")
        return False
    print(f"Publishing to IG Story: {ig_user_id}")
    # Stories need media_type=STORIES
    container_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media"
    payload = {
        "image_url": image_url,
        "media_type": "STORIES",
        "access_token": token
    }
    r = requests.post(container_url, data=payload, timeout=60)
    print(f"IG Story Container: {r.status_code} - {r.text[:800]}")
    if r.status_code != 200:
        return False
    creation_id = r.json().get("id")
    if not creation_id:
        return False
    time.sleep(15)
    publish_url = f"https://graph.facebook.com/v20.0/{ig_user_id}/media_publish"
    r2 = requests.post(publish_url, data={"creation_id": creation_id, "access_token": token}, timeout=60)
    print(f"IG Story Publish: {r2.status_code} - {r2.text[:800]}")
    return r2.status_code == 200

def publish_to_facebook_story(image_url):
    """Facebook Page Story - 24h story"""
    token = os.environ.get("PAGE_ACCESS_TOKEN")
    page_id = os.environ.get("PAGE_ID")
    if not token or not page_id:
        print("Skipping FB Story: Token/PageID empty")
        return False
    print(f"Publishing to FB Story: {page_id}")
    # FB Photo Stories API
    fb_url = f"https://graph.facebook.com/v20.0/{page_id}/photo_stories"
    payload = {
        "url": image_url,
        "access_token": token
    }
    r = requests.post(fb_url, data=payload, timeout=60)
    print(f"FB Story Publish: {r.status_code} - {r.text[:800]}")
    # Fallback: try /stories endpoint if photo_stories fails
    if r.status_code != 200:
        fb_url2 = f"https://graph.facebook.com/v20.0/{page_id}/stories"
        payload2 = {
            "photo_image_url": image_url,
            "access_token": token
        }
        r2 = requests.post(fb_url2, data=payload2, timeout=60)
        print(f"FB Story Fallback: {r2.status_code} - {r2.text[:800]}")
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
    # Stories - no caption needed, image only
    ig_story_ok = publish_to_instagram_story(public_url)
    fb_story_ok = publish_to_facebook_story(public_url)
    print(f"\nResults: IG Feed={'OK' if ig_ok else 'FAIL'} FB Feed={'OK' if fb_ok else 'FAIL'} IG Story={'OK' if ig_story_ok else 'FAIL'} FB Story={'OK' if fb_story_ok else 'FAIL'}")
