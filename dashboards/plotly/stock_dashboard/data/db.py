import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]

def _colname(sym: str) -> str:
    return sym.lower()+ "_prices"

def load_price_data(symbols):
    frames = []

    for sym in symbols:
        col = _colname(sym)

        if col not in db.list_collection_names():
            print(f"NO COLLECTION FOR {sym} -> {col}")
            continue

        cursor = db[col].find(
            {},
            {"_id": 0, "date": 1, "close": 1, "volume": 1}
        ).sort("date", 1)

        df = pd.DataFrame(list(cursor))
        if df.empty:
            print(f"EMPTY DATAFRAME FOR {sym}")
            continue

        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date", "close"])
        df["volume"] = pd.to_numeric(df.get("volume", 0), errors="coerce").fillna(0)
        df["symbol"] = sym

        frames.append(df)

    if not frames:
        print("NO FRAMES CREATED")
        return pd.DataFrame()

    out = pd.concat(frames, ignore_index=True)
    out = out.sort_values(["symbol", "date"])
    return out
