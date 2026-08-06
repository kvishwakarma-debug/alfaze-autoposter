
# collab/collab_finder.py - SAFE Collab Partner Finder
import json, os, random
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

def main():
    os.makedirs("collab/data", exist_ok=True)
    now_ist = datetime.now(IST)
    
    today = random.sample(SEED_PAGES, 5)
    
    output = {
        "date": now_ist.strftime("%d-%m-%Y %I:%M %p IST"),
        "targets": []
    }
    
    print(f"=== Collab Hunt - {output['date']} ===\n")
    
    for i, p in enumerate(today, 1):
        dm = generate_dm(p, random.randint(52, 70))
        print(f"{i}. @{p['username']} ({p['followers']} - {p['niche']})")
        print(f"   https://instagram.com/{p['username']}")
        print(f"   DM:\n{dm}\n")
        print("-"*60)
        
        output["targets"].append({
            "username": p["username"],
            "url": f"https://instagram.com/{p['username']}",
            "followers": p["followers"],
            "niche": p["niche"],
            "dm": dm,
            "status": "pending"
        })
    
    # Save for tracking
    with open("collab/data/collab_today.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Saved to collab/data/collab_today.json")
    print("⚠️ MANUAL DM only - Bot se mat bhejo, 5/day max")

if __name__ == "__main__":
    main()
