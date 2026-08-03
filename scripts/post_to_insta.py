from publishers.music_mixer import ensure_music
from publishers.story_publisher import post_to_story
from publishers.facebook_publisher import post_to_fb_reel

import os, requests, random, textwrap, time, subprocess, urllib.parse
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, date
from moviepy.editor import ImageClip, AudioFileClip

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
REPO = os.getenv("GITHUB_REPOSITORY")
PAGE_ID = os.getenv("PAGE_ID") # <-- GitHub Secret me PAGE_ID bhi add karna hoga (tumhara FB Page ID)

#... tumhara SHAYARIS, BG_PROMPTS, HASHTAGS same rahega...

def create_chai_post(text, day_num):
    #... tumhara same image generation wala code yahan tak...
    # img.save(filepath...) tak same hai
    # Bas return me filepath bhi return karo
    os.makedirs("public/images", exist_ok=True)
    filename = f"day{day_num}_{int(datetime.now().timestamp())}.jpg"
    filepath = f"public/images/{filename}"
    img.save(filepath, "JPEG", quality=92)
    # git push wala part same
    subprocess.run(["git","config","--global","user.name","Alfaze Bot"], check=True)
    subprocess.run(["git","config","--global","user.email","bot@alfaze.com"], check=True)
    subprocess.run(["git","add",filepath], check=True)
    subprocess.run(["git","commit","-m",f"Add Day {day_num}"], check=True)
    subprocess.run(["git","push"], check=True)
    time.sleep(12)
    public_url = f"https://raw.githubusercontent.com/{REPO}/main/{filepath}"
    return public_url, filepath # <-- 2 cheez return

def image_to_reel_with_music(image_path, day_num):
    music_path = ensure_music()
    output_video = f"reel_day{day_num}.mp4"
    # 7 sec ka video image se
    clip = ImageClip(image_path).set_duration(7).resize((1080,1920)) # Reel size
    # Music add
    try:
        audio = AudioFileClip(music_path).subclip(0, 7).volumex(0.4)
        clip = clip.set_audio(audio)
    except:
        pass
    clip.write_videofile(output_video, fps=24, codec='libx264', audio_codec='aac', logger=None)
    return output_video

def make_caption(shayari, day_num):
    # tumhara same
    daily_tag = HASHTAGS.get(day_num, "#ChaiShayari #KulhadChai")
    return f"""{shayari}\n\n☕ Chai Aur Khayal - Day {day_num}/365\n\nChai ke saath thoda sukoon. Aapki aaj ki chai kaisi rahi?\nComment me batao.\n\n.\n#ChaiAurKhayal #AlfazeUlfat #Shayari {daily_tag} #MorningVibes"""

def post_to_instagram(image_url, caption, video_path=None):
    if video_path: # Agar video hai to reel ki tarah post karo
        # Pehle video ko public host karna padega (tum R2 use kar rahe ho toh)
        # Yahan mai image_url hi use kar raha, par video_url ke liye tumhe upload karna hoga
        # For now image hi post hoga, video ke liye hosting chahiye
        pass

    url1 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    r1 = requests.post(url1, data={"image_url": image_url, "caption": caption, "access_token": ACCESS_TOKEN}).json()
    print("Container:", r1)
    if "id" not in r1: raise Exception(r1)
    time.sleep(18)
    url2 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
    r2 = requests.post(url2, data={"creation_id": r1["id"], "access_token": ACCESS_TOKEN}).json()
    print("Publish:", r2)
    return r2, image_url

if __name__ == "__main__":
    START_DATE = date(2026, 7, 5)
    today_day = (date.today() - START_DATE).days + 1
    if today_day < 17: today_day = 17
    if today_day > 31: today_day = random.choice(list(SHAYARIS.keys()))
    shayari = SHAYARIS.get(today_day, SHAYARIS[29])
    print(f"Posting Day {today_day}")

    public_url, local_path = create_chai_post(shayari, today_day)
    caption = make_caption(shayari, today_day)

    # 1. Insta Feed Post (Image)
    result, url = post_to_instagram(public_url, caption)

    # 2. Video banao music ke saath
    reel_path = image_to_reel_with_music(local_path, today_day)
    # Video ko bhi github pe push karke public url banao (same like image)
    # Fir us url se Story + FB Reel
    try:
        reel_public_url = f"https://raw.githubusercontent.com/{REPO}/main/{reel_path}" # iske liye git add karna padega
        subprocess.run(["git","add",reel_path], check=True)
        subprocess.run(["git","commit","-m",f"Add Reel Day {today_day}"], check=True)
        subprocess.run(["git","push"], check=True)
        time.sleep(10)
        post_to_story(reel_public_url, IG_USER_ID, ACCESS_TOKEN)
        post_to_fb_reel(reel_public_url, PAGE_ID, ACCESS_TOKEN, caption)
    except Exception as e:
        print("Story/FB fail:", e)
