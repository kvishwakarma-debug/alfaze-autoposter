import json
import os
import random
import requests
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

SEED_PAGES = [
    {"username": "shayari.quotes.love", "followers": "45k", "niche": "Love Shayari"},
    {"username": "urdupoetry.lovers", "followers": "78k", "niche": "Urdu Poetry"},
    {"username": "alfaz_e_dil", "followers": "32k", "niche": "Dard Shayari"},
    {"username": "hindi.shayari.quotes", "followers": "120k", "niche": "Hindi Shayari"},
    {"username": "shayari_junction", "followers": "56k", "niche": "Sad Shayari"},
    {"username": "quotes__hub", "followers": "28k", "niche": "English Quotes"},
    {"username": "deep.lines", "followers": "91k", "niche": "Deep Quotes"},
    {"username": "sukoon_e_alfaz", "followers": "37k", "niche": "Sukoon Shayari"},
    {"username": "the.shayar", "followers": "110k", "niche": "Shayari"},
    {"username": "broken.hearts.quotes", "followers": "41k", "niche": "Breakup"},
]

def generate_dm(partner, day=55):
    return f"""Hi @{partner['username']} 👋

Aapka {partner['niche']} wala page dekha, kaafi genuine laga! 👌
Mai @alfaze.ulfat chalata hu - 100 Days Deep Quotes + Chai Shayari.

Kya hum week me 1 collab post karein? Day {day} ka quote ready hai.
Dono ki reach 2x hogi, Insta collab ko push karta hai.

Interested ho to bolo, invite bhej du?"""

def send_telegram(msg):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHATID")
    if not token or not chat_id:
        print("Telegram secrets missing, skipping")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": msg})
        print("Telegram sent")
    except Exception as e:
        print(f"Telegram error {e}")

def main():
    os.makedirs("collab/data", exist_ok=True)
    now_ist = datetime.now(IST)
    today = random.sample(SEED_PAGES, 5)
    
    output = {"date": now_ist.strftime("%d-%m-%Y %I:%M %p IST"), "targets": []}
    tg_message = f"🤝 Aaj ke 5 Collab Targets - {output['date']}\n\n"
    
    for i, p in enumerate(today, 1):
        dm = generate_dm(p, random.randint(52, 70))
        output["targets"].append({
            "username": p["username"],
            "url": f"https://instagram.com/{p['username']}",
            "followers": p["followers"],
            "niche": p["niche"],
            "dm": dm,
            "status": "pending"
        })
        tg_message += f"{i}. @{p['username']} ({p['followers']} - {p['niche']})\nLink: https://instagram.com/{p['username']}\nDM: {dm}\n\n---\n\n"
    
    tg_message += "Note: 1-1 ghante gap pe DM karo"
    
    with open("collab/data/collab_today.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    send_telegram(tg_message)

if __name__ == "__main__":
    main()
