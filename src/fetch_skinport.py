import os
import requests
import sqlite3
from datetime import datetime

URL = "https://api.skinport.com/v1/items"


def fetch_items():

    # Hämtar ALLA CS2-items från Skinport i ett enda anrop

    params = {"app_id": 730, "currency": "SEK", "tradable": 0}
    headers = {"Accept-Encoding": "br"}  # Skinport kräver Brotli
    response = requests.get(URL, params=params, headers=headers, timeout=30)

    if response.status_code != 200:
        print(f"Fel: status {response.status_code}")
        print(response.text)
        return None

    return response.json()


def filter_ak_factory_new(items):

    # Behåller bara AK-47 | ... (Factory New), utan StatTrak/Souvenir

    return [
        item for item in items
        if item["market_hash_name"].startswith("AK-47 | ")
        and item["market_hash_name"].endswith("(Factory New)")
    ]


def setup_database():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/prices.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skinport_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skin_name TEXT NOT NULL,
            min_price REAL,
            median_price REAL,
            quantity INTEGER,
            fetched_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def save_items(conn, items):
    now = datetime.now().isoformat()
    rows = [
        (i["market_hash_name"], i.get("min_price"), i.get("median_price"), i.get("quantity"), now)
        for i in items
    ]
    conn.executemany(
        "INSERT INTO skinport_prices (skin_name, min_price, median_price, quantity, fetched_at) "
        "VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()


def main():
    items = fetch_items()
    if items is None:
        return

    print(f"Hämtade {len(items)} items totalt")
    ak_items = filter_ak_factory_new(items)
    print(f"Varav {len(ak_items)} AK-47 Factory New")

    if ak_items:
        print("Exempel på hur en rad ser ut:", ak_items[0])

    conn = setup_database()
    save_items(conn, ak_items)
    conn.close()
    print("Klart!")


if __name__ == "__main__":
    main()