import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
import textwrap
import time

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

print(f"IG_USER_ID exists: {bool(IG_USER_ID)} | Value: {str(IG_USER_ID)[:4]}...")
print(f"ACCESS_TOKEN exists: {bool(ACCESS_TOKEN)}")

if not IG_USER_ID or not ACCESS_TOKEN:
    raise Exception("Secret missing!")

SHAYARIS = [
    "Mohabbat me nahi hai farq jeene aur marne ka,\nUsi ko dekh ke jeete hain jis kafir pe dum nikle",
    "Dil-e-nadaan tujhe hua kya hai,\nAakhir is dard ki dawa kya hai",
    "Bahut kareeb aati ja rahi ho,\nBichadne ka irada kar liya kya?"
]

def create_shayari_image(text):
    img = Image.new('RGB', (1080, 1080), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 50)
    except:
        font = ImageFont.load_default()
    lines = textwrap.wrap(text, width=28)
    y_text = 350
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        w = bbox[2]-bbox[0]
        draw.text(((1080-w)/2, y_text), line, font=font, fill=(255,255,255))
        y_text+=70
    img.save("generated_image.jpg", "JPEG", quality=95)
    print("Image saved as JPEG")
    return "generated_image.jpg"

def upload_image(image_path):
    print("Uploading...")
    # 1. file.io - DIRECT LINK deta hai, Insta ke liye best
    try:
        print("--> file.io")
        with open(image_path, 'rb') as f:
            r = requests.post("https://file.io", files={"file": f}, timeout=30).json()
            print(r)
            if r.get("success"):
                print(f"SUCCESS URL: {r['link']}")
                return r["link"]
    except Exception as e:
        print(f"file.io failed: {e}")

    # 2. tmpfiles.org - ab direct link banayenge
    try:
        print("--> tmpfiles.org")
        with open(image_path, 'rb') as f:
            r = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=30).json()
            print(r)
            if r.get("status") == "success":
                page_url = r["data"]["url"]
                print(f"Page URL: {page_url}")
                # Page url ko direct image url me convert
                # https://tmpfiles.org/abc/file.jpg -> https://tmpfiles.org/dl/abc/file.jpg
                direct = page_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
                print(f"Direct URL: {direct}")
                return direct
    except Exception as e:
        print(f"tmpfiles failed: {e}")

    # 3. uguu.se
    try:
        print("--> uguu.se")
        with open(image_path, 'rb') as f:
            r = requests.post("https://uguu.se/upload.php", files={"files[]": f}, timeout=30).json()
            url = r["files"][0]["url"]
            print(f"SUCCESS URL: {url}")
            return url
    except Exception as e:
        print(f"uguu failed: {e}")

    raise Exception("All hosts failed")

def post_to_instagram(image_url, caption):
    print(f"Posting: {image_url}")
    url1 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    payload1 = {"image_url": image_url, "caption": caption + "\n\n#shayari #alfazeulfat", "access_token": ACCESS_TOKEN}
    r1 = requests.post(url1, data=payload1).json()
    print("Container:", r1)
    if "id" not in r1:
        raise Exception(f"Container failed: {r1}")
    creation_id = r1["id"]
    time.sleep(15) # Insta ko time do
    url2 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
    payload2 = {"creation_id": creation_id, "access_token": ACCESS_TOKEN}
    r2 = requests.post(url2, data=payload2).json()
    print("Publish:", r2)
    return r2

if __name__ == "__main__":
    shayari = random.choice(SHAYARIS)
    img_path = create_shayari_image(shayari)
    public_url = upload_image(img_path)
    result = post_to_instagram(public_url, shayari)
    print(f"✅ DONE! {result}")
