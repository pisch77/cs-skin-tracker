import sqlite3
import pandas as pd

conn = sqlite3.connect("data/prices.db")
df = pd.read_sql("SELECT skin_name, min_price, median_price, quantity, fetched_at FROM skinport_prices", conn)
print(df.sort_values("min_price", ascending=False).to_string())
conn.close()