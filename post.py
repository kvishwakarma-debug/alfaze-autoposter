import requests, random, time, os
from PIL import Image, ImageDraw, ImageFont

IG_USER_ID = os.getenv("IG_ID")
TOKEN = os.getenv("IG_TOKEN")

QUOTES = [
    "Mohabbat adhuri rahi to kya hua,\nDil to sacha tha na?",
    "Alfaaz hi to hain,\nJo zakhm dete hain aur marham bhi.",
    "Tum yaad nahi aate,\nBas khayalon se jaate nahi.",
    "Ishq me sabr aana chahiye,\nWarna mohabbat bekaar hai.",
    "Humne bhi kisi se pyaar kiya tha,\nBas kismat ko manzoor nahi tha.",
    "Dil tuta hai par shikayat nahi,\nMohabbat aaj bhi tumse hi hai.",
    "Alfaze Ulfat ka yahi usool hai,\nJo dil me hai wahi zubaan par hai."
]

def create_image(text):
    img = Image.new('RGB', (1080, 1350), color=(15,15,15))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 55)
    except:
        font = ImageFont.load_default()
    # glow effect
    draw.multiline_text((540, 600), text, font=font, fill=(255,255,255), anchor="mm", align="center", spacing=20, stroke_width=2, stroke_fill=(0,0,0))
    draw.text((540, 1250), "@alfaze.ulfat", font=font, fill=(130,130,130), anchor="mm")
    path = "quote.jpg"
    img.save(path, quality=95)
    return path

def post():
    quote = random.choice(QUOTES)
    caption = f"{quote}\n\n.\n.\n#alfazeulfat #shayari #urdushayari #hindi shayari #lovequotes #sadshayari #quotes"
    img_path = create_image(quote)
    
    # Step 1 - create container
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    with open(img_path, 'rb') as f:
        r = requests.post(url, data={'caption': caption, 'access_token': TOKEN}, files={'source': f})
    print("Upload response:", r.text)
    data = r.json()
    if 'id' not in data:
        raise Exception(f"Upload failed {data}")
    creation_id = data['id']
    time.sleep(20)
    # Step 2 - publish
    pub_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    pr = requests.post(pub_url, data={'creation_id': creation_id, 'access_token': TOKEN})
    print("Publish response:", pr.text)

if __name__ == "__main__":
    post()
