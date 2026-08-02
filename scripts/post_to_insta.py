import os
import requests
import random
from PIL import Image, ImageDraw, ImageFont
import textwrap
import time

# --- CONFIG ---
IG_USER_ID = os.getenv("IG_USER_ID") # 17841466917552608
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN") # Tumhara Page Token
IMAGE_PATH = "generated_image.jpg"

# Shayari List
SHAYARIS = [
    "Mohabbat me nahi hai farq jeene aur marne ka,\nUsi ko dekh ke jeete hain jis kafir pe dum nikle",
    "Dil-e-nadaan tujhe hua kya hai,\nAakhir is dard ki dawa kya hai",
    "Bahut kareeb aati ja rahi ho,\nBichadne ka irada kar liya kya?",
    "Ishq ne ghalib nikamma kar diya,\nWarna hum bhi aadmi the kaam ke"
]

def create_shayari_image(text):
    # 1080x1080 Insta Post
    img = Image.new('RGB', (1080, 1080), color=(20, 20, 20))
    draw = ImageDraw.Draw(img)

    try:
        # Hindi font try, nahi to default
        font = ImageFont.truetype("NotoSansDevanagari-Bold.ttf", 60)
        small_font = ImageFont.truetype("NotoSansDevanagari-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Text wrap
    lines = textwrap.wrap(text, width=25)
    y_text = 300
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((1080-w)/2, y_text), line, font=font, fill=(255, 255, 255))
        y_text += 80

    # Branding
    draw.text((50, 1000), "@alfaze.ulfat", font=small_font, fill=(200, 200, 200))

    img.save(IMAGE_PATH)
    print("Image saved")
    return IMAGE_PATH

def upload_image_0x0(image_path):
    """ Naya Uploader - catbox band hai to 0x0.st use karenge - 100% working """
    print("Uploading to 0x0.st...")
    try:
        with open(image_path, 'rb') as f:
            resp = requests.post("https://0x0.st", files={"file": f}, timeout=30)
            if resp.status_code == 200:
                url = resp.text.strip()
                print(f"Image URL: {url}")
                return url
    except Exception as e:
        print(f"0x0 failed: {e}")

    # Fallback 2: tmpfiles.org
    print("Trying tmpfiles.org...")
    try:
        with open(image_path, 'rb') as f:
            resp = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=30).json()
            url = resp['data']['url'].replace("tmpfiles.org/dl", "tmpfiles.org/dl-direct")
            print(f"Image URL: {url}")
            return url
    except Exception as e:
        raise Exception(f"Upload failed: {e}")

def post_to_instagram(image_url, caption):
    # Step 1: Create Container
    url1 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media"
    payload1 = {
        "image_url": image_url,
        "caption": caption + "\n\n#shayari #alfazeulfat #urdu #hindi",
        "access_token": ACCESS_TOKEN
    }
    r1 = requests.post(url1, data=payload1).json()
    print("Container Response:", r1)

    if "id" not in r1:
        raise Exception(f"Container failed: {r1}")

    creation_id = r1["id"]

    # Wait for processing
    time.sleep(5)

    # Step 2: Publish
    url2 = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/media_publish"
    payload2 = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    r2 = requests.post(url2, data=payload2).json()
    print("Publish Response:", r2)
    return r2

if __name__ == "__main__":
    print(f"DEBUG: IG_ID={IG_USER_ID[:5]}... Token={ACCESS_TOKEN[:10]}...")

    shayari = random.choice(SHAYARIS)
    img_path = create_shayari_image(shayari)
    public_url = upload_image_0x0(img_path)

    result = post_to_instagram(public_url, shayari)

    if "id" in result:
        print("✅ POST SUCCESSFUL! ID:", result["id"])
    else:
        raise Exception(f"Upload failed: {result}")
