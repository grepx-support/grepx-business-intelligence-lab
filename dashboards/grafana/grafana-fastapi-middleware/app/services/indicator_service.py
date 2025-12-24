from app.core.database import db
import math

# =========================
# RSI (generic, safe)
# =========================
def get_rsi(symbol: str):
    collection_name = f"{symbol.lower()}_rsi"

    if collection_name not in db.list_collection_names():
        return []

    col = db[collection_name]

    cursor = col.find(
        {},
        {
            "_id": 0,
            "date": 1,
            "rsi_14": 1
        }
    ).sort("date", 1)

    output = []

    for d in cursor:
        rsi_val = d.get("rsi_14")

     
        if rsi_val is None:
            continue

        rsi_val = float(rsi_val)

        if math.isnan(rsi_val) or math.isinf(rsi_val):
            continue

        output.append({
            "time": d["date"],
            "rsi": round(rsi_val, 2)
        })

    return output

# SMA (generic, safe)
def get_sma(symbol: str):
    collection_name = f"{symbol.lower()}_sma"

    if collection_name not in db.list_collection_names():
        return []

    col = db[collection_name]

    cursor = col.find(
        {},
        {
            "_id": 0,
            "date": 1,
            "sma_10": 1,
            "sma_20": 1,
            "sma_50": 1,
            "sma_100": 1,
            "sma_200": 1
        }
    ).sort("date", 1)

    output = []

    for d in cursor:
        row = {
            "time": f"{d['date']}T00:00:00Z"
        }

        for key in ["sma_10", "sma_20", "sma_50", "sma_100", "sma_200"]:
            val = d.get(key)
            if val is None:
                continue

            try:
                val = float(val)
                if math.isnan(val) or math.isinf(val):
                    continue
                row[key] = round(val, 2)
            except:
                continue

        output.append(row)

    return output
