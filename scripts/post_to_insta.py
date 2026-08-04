import sys, os, json, re, glob, textwrap, random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from publishers.youtube_music import ensure_music_for_shayari
from publishers.story_publisher import post_to_story
from publishers.facebook_publisher import post_to_fb_reel

import requests, time, subprocess, urllib.parse, datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip, AudioFileClip

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
REPO = os.getenv("GITHUB_REPOSITORY")

def load_shayaris():
    path = os.path.join(os.path.dirname(__file__), "shayari_data.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

SHAYARI_LIST = load_shayaris()

def get_next_day_and_shayari():
    existing = glob.glob("public/images/day*_*.jpg")
    existing += glob.glob("public/images/reel_day*_*.mp4")

    max_day = 0
    for f in existing:
        m = re.search(r'day(\d+)_', os.path.basename(f))
        if m:
            d = int(m.group(1))
            if d > max_day:
                max_day = d

    if max_day == 0:
        # public/images khali hai to JSON ke first ID se - tumhara 17
        next_day = SHAYARI_LIST[0].get('id', 17) if SHAYARI_LIST else 17
    else:
        next_day = max_day + 1

    print(f"Last Day: {max_day}, Next Day: {next_day}")

    for item in SHAYARI_LIST:
        if item.get('id') == next_day:
            return item, next_day

    # Agar next_day JSON me nahi hai to loop se le lo
    idx = (next_day - SHAYARI_LIST[0]['id']) % len(SHAYARI_LIST) if SHAYARI_LIST else 0
    return SHAYARI_LIST[idx], next_day

def wrap_text_smart(text, width=30):
    lines = []
    for para in text.split("\n"):
        wrapped = textwrap.wrap(para, width=width, break_long_words=False)
        lines.extend(wrapped if wrapped else [""])
    return lines

def create_chai_post(shayari_data, day_num):
    text_for_image = shayari_data.get('text', '')
    prompt = shayari_data.get("bg_prompt", "foggy railway station bench chai misty morning cinematic")
    encoded = urllib.parse.quote(prompt + ", photorealistic, ultra hd, 8k, sharp focus, moody, foggy morning, no text")
    bg_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={day_num}&enhance=true"

    print(f"Generating BG Day {day_num}: {prompt}")
    r = requests.get(bg_url, timeout=120)
    open("bg.jpg","wb").write(r.content)
    full_img = Image.open("bg.jpg").convert("RGB").resize((1080,1920), Image.LANCZOS)

    draw = ImageDraw.Draw(full_img, "RGBA")
    try:
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_wm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    except:
        try:
            font_bold = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf", 40)
            font_wm = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", 26)
        except:
            font_bold = ImageFont.load_default()
            font_wm = font_bold

    # NO BLACK BOX - Direct white text with black stroke + center + side padding
    wrapped_lines = wrap_text_smart(text_for_image, width=30)
    total_text_height = len(wrapped_lines) * 60
    y = (1920 - total_text_height) // 2

    for line in wrapped_lines:
        bbox = draw.textbbox((0,0), line, font=font_bold)
        w = bbox[2]-bbox[0]
        x = (1080-w)//2
        draw.text((x,y), line, font=font_bold, fill="white", stroke_width=6, stroke_fill="black")
        y+=60

    draw.text((25, 1855), f"@alfaze.ulfat | Day {day_num}/365", font=font_wm, fill="white", stroke_width=3, stroke_fill="black")

    os.makedirs("public/images", exist_ok=True)
    ts = int(datetime.datetime.now().timestamp())
    feed_path = f"public/images/day{day_num}_{ts}.jpg"
    reel_img_path = f"public/images/day{day_num}_{ts}_reel.jpg"
    full_img.save(feed_path, "JPEG", quality=95)
    full_img.save(reel_img_path, "JPEG", quality=95)

    subprocess.run(["git","config","--global","user.name","Alfaze Bot"], check=True)
    subprocess.run(["git","config","--global","user.email","bot@alfaze.com"], check=True)
    subprocess.run(["git","add",feed_path, reel_img_path], check=True)
    subprocess.run(["git","commit","-m",f"Add Day {day_num}"], check=True)
    subprocess.run(["git","push"], check=True)
    time.sleep(10)
    feed_url = f"https://raw.githubusercontent.com/{REPO}/main/{feed_path}"
    return feed_url, reel_img_path

def image_to_reel_with_music(image_path, day_num, shayari_data):
    try:
        music_path = ensure_music_for_shayari(shayari_data) # Har baar ALAG gaana
        print(f"Music for Day {day_num}: {music_path}")
        ts = int(datetime.datetime.now().timestamp())
        out_hd = f"public/images/reel_day{day_num}_{ts}.mp4"
        out_story = f"public/images/story_day{day_num}_{ts}.mp4"

        def make_video(out_path, bitrate):
            clip = ImageClip(image_path).set_duration(7)
            if music_path and os.path.exists(music_path):
                try:
                    audio = AudioFileClip(music_path)
                    if audio.duration < 7:
                        from moviepy.audio.fx.all import audio_loop
                        audio = audio_loop(audio, duration=7)
                    else:
                        # Har baar alag hissa - random 7 sec
                        start = random.uniform(0, max(0, audio.duration-7))
                        audio = audio.subclip(start, start+7)
                    audio = audio.volumex(0.35)
                    clip = clip.set_audio(audio)
                except Exception as e:
                    print(f"Audio mix fail: {e}")
            clip.write_videofile(out_path, fps=30, codec='libx264', audio_codec='aac', bitrate=bitrate, logger=None)
            return out_path

        make_video(out_hd, "5000k")
        make_video(out_story, "1500k")

        subprocess.run(["git","add",out_hd, out_story], check=True)
        subprocess.run(["git","commit","-m",f"Add Reels {day_num}"], check=True)
        subprocess.run(["git","push"], check=True)
        time.sleep(10)
        base = f"https://raw.githubusercontent.com/{REPO}/main/"
        return base+out_hd, base+out_story
    except Exception as e:
        print(f"Reel fail: {e}")
        return None, None

def make_caption(shayari_data, day_num):
    text = shayari_data.get('text', '')
    tags = shayari_data.get('hashtags', '#ChaiAurKhayal #AlfazeUlfat #Shayari')
    return f"{text}\n\n☕ Chai Aur Khayal - Day {day_num}/365\n\nChai ke saath thoda sukoon. Aapki aaj ki chai kaisi rahi? Comment me batao.\n\n.\n{tags} Day{day_num}of365 AlfazeUlfat SadLofi HindiShayari Reels"

def post_to_insta_reel(video_url, caption):
    r1 = requests.post(f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media", data={"media_type": "REELS","video_url": video_url,"caption": caption,"access_token": ACCESS_TOKEN}).json()
    print("Reel Container:", r1)
    if "id" not in r1:
        return r1
    for i in range(12):
        time.sleep(5)
        s = requests.get(f"https://graph.facebook.com/v20.0/{r1['id']}?fields=status_code&access_token={ACCESS_TOKEN}").json()
        if s.get("status_code") == "FINISHED":
            break
    r2 = requests.post(f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish", data={"creation_id": r1["id"], "access_token": ACCESS_TOKEN}).json()
    print("Reel Publish:", r2)
    return r2

if __name__ == "__main__":
    shayari_data, day_num = get_next_day_and_shayari()
    existing = glob.glob(f"public/images/day{day_num}_*.jpg")
    if existing and os.getenv("GITHUB_EVENT_NAME") == "schedule":
        print(f"Day {day_num} already posted, skipping")
        exit(0)

    print(f"Posting Day {day_num}: {shayari_data.get('text','')[:50]}")
    public_url, reel_local_path = create_chai_post(shayari_data, day_num)
    caption = make_caption(shayari_data, day_num)
    reel_url_hd, reel_url_story = image_to_reel_with_music(reel_local_path, day_num, shayari_data)

    if reel_url_hd:
        post_to_insta_reel(reel_url_hd, caption)
        post_to_story(reel_url_story, IG_USER_ID, ACCESS_TOKEN)
        try:
            post_to_fb_reel(reel_url_hd, PAGE_ID, ACCESS_TOKEN, caption)
        except Exception as e:
            print(f"FB Reel fail: {e}")
