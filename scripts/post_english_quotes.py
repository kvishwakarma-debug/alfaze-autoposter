# scripts/post_english_quotes.py - English Quotes (1080x1080 Post) - FIXED
import sys, os, json, re, glob, textwrap, random, time, requests, urllib.parse, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
REPO = os.getenv("GITHUB_REPOSITORY")

def load_quotes():
    p = os.path.join(os.path.dirname(__file__), "english_quotes_data.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

QUOTES_LIST = load_quotes()

def get_next_quote():
    existing = glob.glob("public/images/en_day*_*.jpg")
    max_day = 0
    for f in existing:
        m = re.search(r'en_day(\d+)_', os.path.basename(f))
        if m:
            d = int(m.group(1))
            if d > max_day:
                max_day = d
    next_day = max_day + 1 if max_day > 0 else 1
    idx = (next_day - 1) % len(QUOTES_LIST)
    for item in QUOTES_LIST:
        if item.get('id') == next_day:
            return item, next_day
    return QUOTES_LIST[idx], next_day

def wrap_text_smart(text, width=32):
    lines = []
    for para in text.split("\n"):
        wrapped = textwrap.wrap(para, width=width, break_long_words=False)
        lines.extend(wrapped if wrapped else [""])
    return lines

def get_background_image(prompt, day_num):
    encoded = urllib.parse.quote(prompt + ", photorealistic, cinematic, dark blue tones, lonely, no text")
    # Retry logic
    for attempt in range(3):
        try:
            bg_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&nologo=true&seed={day_num+random.randint(1,99999)+attempt}"
            print(f"Try {attempt+1}: {bg_url}")
            r = requests.get(bg_url, timeout=60)
            if r.status_code == 200 and len(r.content) > 10000:
                # Check if it's actually an image
                if r.headers.get('content-type','').startswith('image') or r.content[:4] == b'\xff\xd8\xff\xe0' or b'JFIF' in r.content[:20] or b'PNG' in r.content[:10]:
                    open("bg_en.jpg","wb").write(r.content)
                    # Test open
                    test = Image.open("bg_en.jpg")
                    test.verify()
                    return Image.open("bg_en.jpg").convert("RGB")
        except Exception as e:
            print(f"BG attempt {attempt+1} failed: {e}")
            time.sleep(2)

    # FALLBACK: Agar image na aaye to khud se dark moody background banao (second wale jaisa)
    print("Using fallback dark moody background")
    img = Image.new("RGB", (1080,1080), (15, 25, 40))
    draw = ImageDraw.Draw(img)
    # Add some bokeh lights effect
    for _ in range(20):
        x = random.randint(0,1080)
        y = random.randint(0,600)
        r = random.randint(10,40)
        brightness = random.randint(80,180)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(brightness, brightness//2, brightness//4, 100))
    # Add rain effect lines
    for _ in range(300):
        x1 = random.randint(0,1080)
        y1 = random.randint(0,1080)
        x2 = x1 + random.randint(-2,2)
        y2 = y1 + random.randint(10,25)
        draw.line([x1,y1,x2,y2], fill=(100,120,150,80), width=1)
    return img

def create_quote_post(quote_data, day_num):
    prompt = quote_data.get('bg_prompt', 'dark rainy cafe interior at night, moody lonely aesthetic')
    print(f"BG Gen Day {day_num}: {prompt}")

    full_img = get_background_image(prompt, day_num).resize((1080,1080), Image.LANCZOS)

    # Perfect second wala gradient
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
        try:
            font_quote = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf", 42)
            font_wm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 19)
        except:
            font_quote = ImageFont.load_default()
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
    ts = int(datetime.datetime.now().timestamp())
    feed_path = f"public/images/en_day{day_num}_{ts}.jpg"
    full_img.save(feed_path, "JPEG", quality=96)
    print(f"Saved to {feed_path}")
    return feed_path

def make_caption(quote_data, day_num):
    tags = quote_data.get('hashtags', '#DeepQuotes #AlfazeUlfat #EnglishQuotes')
    return f"{quote_data.get('text','')}\n\n.\n.\n{tags}"

def post_to_insta_image(image_url, caption):
    r1 = requests.post(f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media",
                       data={"image_url": image_url, "caption": caption, "access_token": ACCESS_TOKEN}).json()
    print("Image Container:", r1)
    if "id" not in r1:
        return r1
    for i in range(10):
        time.sleep(3)
        s = requests.get(f"https://graph.facebook.com/v20.0/{r1['id']}?fields=status_code&access_token={ACCESS_TOKEN}").json()
        if s.get("status_code") == "FINISHED" or "status_code" not in s:
            break
    r2 = requests.post(f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish",
                       data={"creation_id": r1["id"], "access_token": ACCESS_TOKEN}).json()
    print("Publish:", r2)
    return r2

if __name__ == "__main__":
    import subprocess
    quote_data, day_num = get_next_quote()
    print(f"Posting English Day {day_num}")

    local_path = create_quote_post(quote_data, day_num)

    subprocess.run(["git","config","--global","user.name","Alfaze Bot"], check=True)
    subprocess.run(["git","config","--global","user.email","bot@alfaze.com"], check=True)
    subprocess.run(["git","add", local_path], check=True)
    subprocess.run(["git","commit","-m",f"Add English Quote Day {day_num}"], check=True)
    subprocess.run(["git","push"], check=True)
    time.sleep(12)

    base = f"https://raw.githubusercontent.com/{REPO}/main/"
    image_url = base + local_path
    caption = make_caption(quote_data, day_num)
    post_to_insta_image(image_url, caption)
