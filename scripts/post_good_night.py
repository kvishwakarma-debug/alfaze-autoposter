"""
Good Night Auto Poster - Alfaze Ulfat
Location: scripts/post_good_night.py
JSON: scripts/good_night_shayari_with_backgrounds.json
Style: Night paper texture + crescent moon + clean serif Hindi font (final locked)
"""

import json
import random
import os
import requests
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# --- PATHS - tumhare file structure ke hisab se ---
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
    return None

def create_poster(entry, bg_path):
    img = Image.open(bg_path).convert("RGBA")
    W,H = img.size
    overlay = Image.new("RGBA",(W,H),(0,0,0,0))
    ImageDraw.Draw(overlay).rectangle([(0,H*0.30),(W,H*0.68)], fill=(0,0,20,75))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)
    main_font = get_font(54)
    footer_font = get_font(26) # thoda bada - final locked
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
    try:
        r = requests.post("https://uguu.se/upload.php", files={"files[]": open(p,'rb')}, timeout=60)
        if r.status_code==200:
            url = r.json()['files'][0]['url']
            print(f"uguu URL: {url}")
            return url
    except Exception as e:
        print(e)
    return None

if __name__=="__main__":
    entry = get_random_entry()
    print(f"Selected [{entry['id']}]: {entry['shayari']}")
    bg = generate_background(entry['background_prompt'])
    poster = create_poster(entry, bg)
    public_url = upload_to_uguu(poster)
    print(f"Done: {poster} -> {public_url}")
