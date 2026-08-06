# scripts/post_english_quotes.py - FINAL FIX - 8:30 PM IST + 100 Quotes + All Ages Safe
import sys, os, json, re, glob, textwrap, random, time, requests, urllib.parse
from datetime import datetime, timezone, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
REPO = os.getenv("GITHUB_REPOSITORY")

# IST Timezone
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    return datetime.now(IST)

def load_quotes():
    p = os.path.join(os.path.dirname(__file__), "english_quotes_data.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

QUOTES_LIST = load_quotes()

def get_next_quote():
    now_ist = get_ist_time()
    print(f"Current IST: {now_ist.strftime('%d-%m-%Y %I:%M:%S %p')} - Target: 8:30 PM IST")

    existing = glob.glob("public/images/en_day*_*.jpg")
    max_day = 0
    for f in existing:
        m = re.search(r'en_day(\d+)_', os.path.basename(f))
        if m:
            d = int(m.group(1))
            if d > max_day:
                max_day = d
    next_day = max_day + 1 if max_day > 0 else 1
    next_day = ((next_day - 1) % 100) + 1 # 100 ke baad loop

    for item in QUOTES_LIST:
        if item.get('id') == next_day:
            return item, next_day
    idx = (next_day - 1) % len(QUOTES_LIST)
    return QUOTES_LIST[idx], next_day

def wrap_text_smart(text, width=32):
    lines = []
    for para in text.split("\n"):
        wrapped = textwrap.wrap(para, width=width, break_long_words=False)
        lines.extend(wrapped if wrapped else [""])
    return lines

def get_background_image(prompt, day_num):
    encoded = urllib.parse.quote(prompt + ", photorealistic, cinematic, dark blue tones, lonely, no text, rainy cafe night, clean, no people")
    sources = [
        f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true&seed={day_num+random.randint(1,99999)}",
        f"https://source.unsplash.com/1080x1080/?cafe,rain,night,moody,dark&sig={day_num+random.randint(1,99999)}",
        f"https://picsum.photos/seed/{day_num+random.randint(1,99999)}/1080/1080"
    ]
    for attempt, url in enumerate(sources):
        try:
            r = requests.get(url, timeout=40, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 15000:
                with open("bg_en.jpg","wb") as f:
                    f.write(r.content)
                try:
                    with Image.open("bg_en.jpg") as test:
                        test.verify()
                    img = Image.open("bg_en.jpg").convert("RGB")
                    if attempt > 0:
                        overlay = Image.new("RGB", img.size, (18, 28, 48))
                        img = Image.blend(img, overlay, 0.35)
                        img = img.point(lambda p: int(p * 0.75))
                    return img
                except:
                    continue
        except:
            time.sleep(1)
    img = Image.new("RGB", (1080,1080), (12, 20, 35))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(22):
        x = random.randint(0,1080); y = random.randint(0,700); rad = random.randint(25,90); b = random.randint(50,160)
        draw.ellipse([x-rad, y-rad, x+rad, y+rad], fill=(b, b//2, b//3, 70))
    return img

def create_quote_post(quote_data, day_num):
    prompt = quote_data.get('bg_prompt', 'dark rainy cafe interior at night, moody lonely aesthetic')
    full_img = get_background_image(prompt, day_num).resize((1080,1080), Image.LANCZOS)
    overlay = Image.new("RGBA", full_img.size, (0,0,0,0))
    d = ImageDraw.Draw(overlay)
    for y in range(1080):
        if y > 480:
            alpha = int((y-480)/600 * 235)
            d.rectangle([0,y,1080,y+1], fill=(0,0,0,alpha))
    full_img = Image.alpha_composite(full_img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(full_img)
    try:
        font_quote = ImageFont.truetype("/usr/share/fonts/liberation-serif/LiberationSerif-Italic.ttf", 42)
        font_wm = ImageFont.truetype("/usr/share/fonts/dejavu-serif-fonts/DejaVuSerif.ttf", 19)
    except:
        font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 42)
        font_wm = ImageFont.load_default()

    wrapped_lines = wrap_text_smart(quote_data.get('text',''), width=32)[:4]
    y = 1080 - (len(wrapped_lines)*60) - 140
    for line in wrapped_lines:
        bbox = draw.textbbox((0,0), line, font=font_quote)
        x = (1080 - (bbox[2]-bbox[0]))//2
        draw.text((x+2, y+2), line, font=font_quote, fill="black")
        draw.text((x, y), line, font=font_quote, fill="white")
        y+=60

    wm = "— @Alfaz-e-Ulfat"
    ww = draw.textbbox((0,0), wm, font=font_wm)[2]
    draw.text(((1080-ww)//2, 1035), wm, font=font_wm, fill=(230,230,230))

    os.makedirs("public/images", exist_ok=True)
    ts = int(get_ist_time().timestamp())
    feed_path = f"public/images/en_day{day_num}_{ts}.jpg"
    full_img.save(feed_path, "JPEG", quality=96)
    print(f"Saved to {feed_path}")
    return feed_path

def get_instant_url(image_path):
    print("Uploading for instant URL...")
    try:
        with open(image_path, 'rb') as f:
            r = requests.post("https://uguu.se/upload.php", files={"files[]": f}, timeout=30)
            if r.status_code == 200:
                j = r.json()
                if "files" in j and len(j["files"]) > 0:
                    return j["files"][0]["url"]
    except Exception as e:
        print(f"uguu failed: {e}")
    try:
        with open(image_path, 'rb') as f:
            r = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=30)
            j = r.json()
            if j.get("status") == "success":
                return j["data"]["url"].replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
    except Exception as e:
        print(f"tmpfiles failed: {e}")
    try:
        with open(image_path, 'rb') as f:
            r = requests.post("https://file.io", files={"file": f}, timeout=30)
            j = r.json()
            if j.get("success"):
                return j.get("link")
    except Exception as e:
        print(f"file.io failed: {e}")
    try:
        with open(image_path, 'rb') as f:
            r = requests.post("https://litterbox.catbox.moe/resources/internals/api.php",
                              data={"reqtype": "fileupload", "time": "72h"},
                              files={"fileToUpload": f}, timeout=30)
            if r.status_code == 200 and "https://" in r.text:
                return r
