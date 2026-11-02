import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="CS Skin Tracker", layout="wide")


@st.cache_data(ttl=600)
def load_data():
    #Läser alla prisrader från databasen.
    conn = sqlite3.connect("data/prices.db")
    df = pd.read_sql(
        "SELECT skin_name, min_price, median_price, quantity, fetched_at FROM skinport_prices",
        conn,
    )
    conn.close()
    df["fetched_at"] = pd.to_datetime(df["fetched_at"])
    df["date"] = df["fetched_at"].dt.date
    return df


df = load_data()

st.title("CS2 AK-47 Factory New – Price Tracker")
st.caption("Prices in SEK from Skinport. Data collected daily via GitHub Actions.")

if df.empty:
    st.warning("No data yet.")
    st.stop()

# Dagens läge 
st.header("Current prices")
latest = df[df["fetched_at"] == df.groupby("skin_name")["fetched_at"].transform("max")]
st.dataframe(
    latest[["skin_name", "min_price", "median_price", "quantity"]]
    .sort_values("min_price", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
)

# Vinnare och förlorare 
st.header("Winners and losers")
col_a, col_b = st.columns(2)
days = col_a.slider("Period (days)", 1, 30, 7)
min_qty = col_b.slider("Minimum listings (filters out thin markets)", 1, 20, 3)

cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
window = df[df["fetched_at"] >= cutoff].sort_values("fetched_at")

if window["date"].nunique() < 2:
    st.info("Not enough history yet. Winners and losers appear once there are at least two days of data.")
else:
    first = window.groupby("skin_name").first()
    last = window.groupby("skin_name").last()
    change = pd.DataFrame({
        "start_price": first["min_price"],
        "end_price": last["min_price"],
        "listings": last["quantity"],
    })
    change["change_%"] = ((change["end_price"] / change["start_price"] - 1) * 100).round(1)
    change = change[change["listings"] >= min_qty].dropna()

    winners = change.sort_values("change_%", ascending=False).head(5)
    losers = change.sort_values("change_%").head(5)

    left, right = st.columns(2)
    left.subheader("Top 5 winners")
    left.dataframe(winners)
    right.subheader("Top 5 losers")
    right.dataframe(losers)

# Prisgraf per skin 
st.header("Price history")
skin = st.selectbox("Choose a skin", sorted(df["skin_name"].unique()))
history = df[df["skin_name"] == skin].set_index("fetched_at")[["min_price", "median_price"]]
st.line_chart(history)