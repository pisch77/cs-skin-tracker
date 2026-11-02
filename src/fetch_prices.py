import requests
import sqlite3
import time
from datetime import datetime

SKINS = [
    "AK-47 | Bloodsport (Factory New)",
]
#    "AK-47 | Redline (Factory New)",
#    "AK-47 | Asiimov (Factory New)"
#    "AK-47 | Vulcan (Factory New)",
#    "AK-47 | Neon Rider (Factory New)",
#    "AK-47 | Nightwish (Factory New)",
#    "AK-47 | The Empress (Factory New)",
#    "AK-47 | Elite Build (Factory New)",
#    "AK-47 | Slate (Factory New)"

APP_ID = 730 #cs2 app id on steam
CURRENCY = 3 #3 for sek, 1 for dollar

def fetch_price(market_hash_name): 
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        "appid": APP_ID,
        "currency": CURRENCY,
        "market_hash_name": market_hash_name
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"Wrong download of {market_hash_name}: status {response.status_code}")
        print(f"Response body: {response.text}")
        print(f"Headers: {dict(response.headers)}")
        return None

    data = response.json()
    if not data.get("success"):
        print(f"No data found for {market_hash_name}")
        return None

    return data

def setup_database():
    conn = sqlite3.connect("data/prices.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skin_name TEXT NOT NULL,
            lowest_price TEXT,
            median_price TEXT,
            volume TEXT,
            fetched_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

def save_price(conn, skin_name, data):
    """Sparar en hämtad prisrad i databasen."""
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO price_history (skin_name, lowest_price, median_price, volume, fetched_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        skin_name,
        data.get("lowest_price"),
        data.get("median_price"),
        data.get("volume"),
        datetime.now().isoformat()
    ))
    conn.commit()

def main():
    conn = setup_database()

    for skin in SKINS:
        print(f"Fetching: {skin}")
        data = fetch_price(skin)

        if data:
            save_price(conn, skin, data)
            print(f"  -> Saved: {data}")

        time.sleep(30)  # Wait 30 seconds for call

    conn.close()
    print("Finished!")

if __name__ == "__main__":
    main()



