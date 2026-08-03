import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.LANCZOS

from publishers.music_mixer import ensure_music
from publishers.story_publisher import post_to_story
from publishers.facebook_publisher import post_to_fb_reel

import requests, random, time, subprocess, urllib.parse, glob
from PIL import Image, ImageDraw, ImageFont
from datetime import date, datetime
from moviepy.editor import ImageClip, AudioFileClip

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
REPO = os.getenv("GITHUB_REPOSITORY")

SHAYARIS = {
17: "सुबह की चाय में तेरी यादों का धुआँ है,\nहर घूँट के साथ तू और याद आता है।",
18: "बारिश, चाय और तुम्हारी बातें,\nतीनों का नशा उतरता ही नहीं है।",
19: "सहरा सी है ये ज़िन्दगी मेरी,\nएक तुम हो जो चाय सी नमी देते हो।",
20: "किताबों के पन्ने पलटते-पलटते,\nएक ख़याल में तुम पलट आते हो।",
21: "छत पर चाय, और ख़यालों में तुम,\nइससे बेहतर सुबह हो ही नहीं सकती।",
22: "जंगल की ख़ामोशी, चाय की गर्मी,\nऔर दिल में बस तुम्हारी नर्मी।",
23: "झील किनारे चाय, और ख़यालों में तुम,\nइससे ज़्यादा सुकून कहाँ मिलेगा यार।",
24: "काम के बोझ में भी सुकून है,\nजब चाय के बहाने तुम याद आते हो।",
25: "गाँव की सुबह, चूल्हे की चाय,\nऔर तुम्हारी यादों की मीठी सी गहराई।",
26: "घाट किनारे चाय, और ज़िन्दगी का ख़याल,\nहर घूँट में छुपा है एक सवाल।",
27: "चलती ट्रेन, खिड़की पर चाय,\nऔर तुम्हारी याद का सफ़र जारी है।",
28: "समुंदर किनारे चाय, और लहरों में तुम,\nइस दिल को और क्या चाहिए, बस तुम।",
29: "कैंटीन की चाय में दोस्ती का ज़ायका है,\nऔर उसी ज़ायके में तुम्हारी कमी का एहसास है।",
30: "अलाव की आँच, हाथों में चाय,\nऔर ख़यालों में बस तेरी ही परछाई।",
31: "सुबह की पहली चाय, और तुम्हारा पहला ख़याल,\nदिन की शुरुआत इससे बेहतर क्या होगी।"
}
BG_PROMPTS = {
17: "early morning balcony chai sunrise, steaming kulhad chai",
18: "rainy window chai monsoon, kulhad chai on windowsill with raindrops",
19: "desert sunset chai, kulhad on sand dune dramatic sky",
20: "old books stack with kulhad chai on wooden table warm light",
21: "rooftop chai sunrise city view, kulhad on ledge",
22: "misty forest morning chai on wooden stump jungle background",
23: "peaceful lake side chai on rock water reflection morning",
24: "office desk laptop kulhad chai work from home cozy",
25: "village chulha morning kulhad chai on mud stove village",
26: "Varanasi ganga ghat morning chai on stone steps",
27: "Indian train window chai kulhad on sill moving blur landscape",
28: "beach sunset chai on sand waves kulhad",
29: "college canteen steel table kulhad chai students blurred behind",
30: "winter bonfire night hands holding kulhad chai near fire sparks, cinematic, 8k",
31: "morning terrace chai with newspaper kulhad steam sunrise"
}
HASHTAGS = {
17: "#SubahKiChai",18: "#BaarishAurChai",19: "#Sehra",20: "#Kitabein",21: "#ChhatParChai",22: "#JungleVibes",23: "#JheelKinare",24: "#WorkAndChai",25: "#GaonKiSubah",26: "#GhatKiChai",27: "#TrainJourney",28: "#Samundar",29: "#CanteenChai",30: "#Alaav",31: "#PehliChai"
}

def create_chai_post(text, day_num):
    prompt = BG_PROMPTS.get(day_num, "kulhad chai cinematic")
    encoded = urllib.parse.quote(prompt + ", photorealistic, ultra hd, 8k, sharp focus, cinematic lighting")
    # HD quality 1080x1920 direct
    bg_url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1920&nologo=true&seed={day_num}&enhance=true"
    print(f"Generating HD BG Day {day_num}")
    r = requests.get(bg_url, timeout=120)
    open("bg.jpg","wb").write(r.content)

    # Original HD image
    full_img = Image.open("bg.jpg").convert("RGB")
    if full_img.size!= (1080,1920):
        full_img = full_img.resize((1080,1920), Image.LANCZOS)

    # 1. FEED IMAGE = 1080x1350 center crop from 1920
    feed_img = full_img.crop((0, 285, 1080, 1635)) # center 1350 height
    draw = ImageDraw.Draw(feed_img, "RGBA")
    try:
        font_main = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf", 52)
        font_wm = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf", 30)
    except:
        font_main = ImageFont.load_default()
        font_wm = ImageFont.load_default()

    y = 500
    for line in text.split("\n"):
        bbox = draw.textbbox((0,0), line, font=font_main)
        x = (1080-(bbox[2]-bbox[0]))//2
        # Better stroke
        draw.text((x,y), line, font=font_main, fill="white", stroke_width=6, stroke_fill="black")
        y+=70
    draw.text((35,1280), f"@alfaze.ulfat | Day {day_num}/365", font=font_wm, fill="white", stroke_width=3, stroke_fill="black")

    # 2. REEL/STORY IMAGE = Full 1080x1920 with same text but lower
    reel_img = full_img.copy()
    draw2 = ImageDraw.Draw(reel_img, "RGBA")
    y2 = 750
    for line in text.split("\n"):
        bbox = draw2.textbbox((0,0), line, font=font_main)
        x = (1080-(bbox[2]-bbox[0]))//2
        draw2.text((x,y2), line, font=font_main, fill="white", stroke_width=6, stroke_fill="black")
        y2+=70
    draw2.text((35,1830), f"@alfaze.ulfat | Day {day_num}/365", font=font_wm, fill="white", stroke_width=3, stroke_fill="black")

    os.makedirs("public/images", exist_ok=True)
    ts = int(datetime.now().timestamp())
    feed_path = f"public/images/day{day_num}_{ts}.jpg"
    reel_img_path = f"public/images/day{day_num}_{ts}_reel.jpg"

    feed_img.save(feed_path, "JPEG", quality=95, subsampling=0)
    reel_img.save(reel_img_path, "JPEG", quality=95, subsampling=0)

    subprocess.run(["git","config","--global","user.name","Alfaze Bot"], check=True)
    subprocess.run(["git","config","--global","user.email","bot@alfaze.com"], check=True)
    subprocess.run(["git","add",feed_path, reel_img_path], check=True)
    subprocess.run(["git","commit","-m",f"Add Day {day_num} HD"], check=True)
    subprocess.run(["git","push"], check=True)
    time.sleep(15)

    feed_url = f"https://raw.githubusercontent.com/{REPO}/main/{feed_path}"
    return feed_url, reel_img_path

def image_to_reel_with_music(image_path, day_num):
    try:
        music_path = ensure_music()
        out = f"public/images/reel_day{day_num}_{int(datetime.now().timestamp())}.mp4"
        print(f"Creating HD reel: {out}")
        # No resize! Already 1080x1920
        clip = ImageClip(image_path).set_duration(7)
        if music_path and os.path.exists(music_path):
            try:
                audio = AudioFileClip(music_path)
                if audio.duration >= 2:
                    if audio.duration < 7:
                        from moviepy.audio.fx.all import audio_loop
                        audio = audio_loop(audio, duration=7)
                    else:
                        audio = audio.subclip(0,7)
                    audio = audio.volumex(0.4)
                    clip = clip.set_audio(audio)
            except Exception as e:
                print(f"Audio fail: {e}")
