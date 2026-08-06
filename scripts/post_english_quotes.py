# scripts/post_english_quotes.py - FINAL - No Git Delay + 3 Platforms - FIXED UPLOADER
# scripts/post_english_quotes.py - ULTIMATE FIX - Working Uploader + Correct Flow
import sys, os, json, re, glob, textwrap, random, time, requests, urllib.parse, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from PIL import Image, ImageDraw, ImageFont
@@ -106,41 +106,70 @@ def create_quote_post(quote_data, day_num):
    print(f"Saved to {feed_path}")
    return feed_path

def upload_to_catbox(image_path):
def get_instant_url(image_path):
    print("Uploading for instant URL...")
    # Try 1: Catbox
    # Try 1: Uguu.se - currently most stable
    try:
        print("Trying Catbox...")
        print("Trying uguu.se...")
        with open(image_path, 'rb') as f:
            r = requests.post("https://catbox.moe/user/api.php",
                              data={"reqtype": "fileupload"},
                              files={"fileToUpload": f}, timeout=30)
            print(f"Catbox response: {r.status_code} - {r.text[:200]}")
            if r.status_code == 200 and "https://" in r.text:
                url = r.text.strip()
                print(f"Catbox SUCCESS: {url}")
            r = requests.post("https://uguu.se/upload.php", files={"files[]": f}, timeout=30)
            print(f"uguu response: {r.status_code} - {r.text[:300]}")
            if r.status_code == 200:
                j = r.json()
                if "files" in j and len(j["files"]) > 0:
                    url = j["files"][0]["url"]
                    print(f"uguu SUCCESS: {url}")
                    return url
    except Exception as e:
        print(f"uguu failed: {e}")

    # Try 2: tmpfiles.org
    try:
        print("Trying tmpfiles.org...")
        with open(image_path, 'rb') as f:
            r = requests.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=30)
            print(f"tmpfiles: {r.text[:400]}")
            j = r.json()
            if j.get("status") == "success":
                page_url = j["data"]["url"]
                # convert to direct dl link
                dl_url = page_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
                print(f"tmpfiles SUCCESS: {dl_url}")
                return dl_url
    except Exception as e:
        print(f"tmpfiles failed: {e}")

    # Try 3: file.io
    try:
        print("Trying file.io...")
        with open(image_path, 'rb') as f:
            r = requests.post("https://file.io", files={"file": f}, timeout=30)
            print(f"file.io: {r.text[:400]}")
            j = r.json()
            if j.get("success"):
                url = j.get("link")
                print(f"file.io SUCCESS: {url}")
                return url
    except Exception as e:
        print(f"Catbox failed: {e}")
        print(f"file.io failed: {e}")

    # Try 2: 0x0.st - most reliable on GitHub
    # Try 4: Catbox Litterbox (72h temp)
    try:
        print("Trying 0x0.st...")
        print("Trying litterbox...")
        with open(image_path, 'rb') as f:
            r = requests.post("https://0x0.st", files={"file": f}, timeout=30)
            print(f"0x0.st response: {r.status_code} - {r.text[:200]}")
            r = requests.post("https://litterbox.catbox.moe/resources/internals/api.php",
                              data={"reqtype": "fileupload", "time": "72h"},
                              files={"fileToUpload": f}, timeout=30)
            print(f"litterbox: {r.status_code} - {r.text[:200]}")
            if r.status_code == 200 and "https://" in r.text:
                url = r.text.strip()
                print(f"0x0.st SUCCESS: {url}")
                print(f"litterbox SUCCESS: {url}")
                return url
    except Exception as e:
        print(f"0x0.st failed: {e}")
        print(f"litterbox failed: {e}")

    # Fallback: GitHub raw with wait
    print("All instant uploaders failed, using GitHub raw with 25 sec wait...")
    time.sleep(25)
    base = f"https://raw.githubusercontent.com/{REPO}/main/"
    return base + image_path
    print("All instant uploaders failed!")
    return None

def make_caption(quote_data, day_num):
    tags = quote_data.get('hashtags', '#DeepQuotes #AlfazeUlfat #EnglishQuotes #HealingQuotes')
@@ -189,19 +218,33 @@ def post_to_facebook_page(image_url, caption):
    quote_data, day_num = get_next_quote()
    print(f"Posting English Day {day_num} at UTC {datetime.datetime.utcnow()}")
    local_path = create_quote_post(quote_data, day_num)
    image_url = upload_to_catbox(local_path)
    caption = make_caption(quote_data, day_num)
    print(f"FINAL IMAGE URL FOR POSTING: {image_url}")
    post_to_insta_post(image_url, caption)
    time.sleep(5)
    post_to_insta_story(image_url)
    time.sleep(5)
    post_to_facebook_page(image_url, caption)

    # STEP 1: Pehle Git Push karo taaki fallback ready rahe
    print("Pushing to GitHub first for fallback...")
    try:
        subprocess.run(["git","config","--global","user.name","Alfaze Bot"], check=True)
        subprocess.run(["git","config","--global","user.email","bot@alfaze.com"], check=True)
        subprocess.run(["git","add", local_path], check=True)
        subprocess.run(["git","commit","-m",f"Add English Quote Day {day_num}"], check=True)
        subprocess.run(["git","push"], check=True)
        print("Git push done")
    except Exception as e:
        print(f"Git push failed but post done: {e}")
        print(f"Git push failed: {e}")

    # STEP 2: Instant URL try karo
    image_url = get_instant_url(local_path)

    # STEP 3: Agar instant fail hua to GitHub raw use karo with 40 sec wait
    if not image_url:
        print("Using GitHub raw as fallback with 40 sec wait...")
        time.sleep(40)
        base = f"https://raw.githubusercontent.com/{REPO}/main/"
        image_url = base + local_path + f"?v={int(time.time())}"

    print(f"FINAL IMAGE URL FOR POSTING: {image_url}")
    caption = make_caption(quote_data, day_num)
    post_to_insta_post(image_url, caption)
    time.sleep(5)
    post_to_insta_story(image_url)
    time.sleep(5)
    post_to_facebook_page(image_url, caption)
