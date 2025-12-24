

from collections import defaultdict
import numpy as np
from app.core.database import db


# =========================
# EMA
# =========================
def ema(arr, span=20):
    arr = np.array(arr, dtype=float)
    ema_arr = np.zeros_like(arr)
    alpha = 2 / (span + 1)

    ema_arr[0] = arr[0]
    for i in range(1, len(arr)):
        ema_arr[i] = alpha * arr[i] + (1 - alpha) * ema_arr[i - 1]

    return ema_arr


# =========================
# Get available symbols
# =========================
def get_symbols():
    collections = [
        name for name in db.list_collection_names()
        if name.endswith("_prices")
    ]

    symbols = set()
    for col in collections:
        doc = db[col].find_one({}, {"symbol": 1, "_id": 0})
        if doc and "symbol" in doc:
            symbols.add(doc["symbol"].upper())

    return sorted(symbols)




    # =========================
# Price + Volume (SINGLE SYMBOL)
# =========================
def get_price_volume(symbol: str):
    col = db[f"{symbol}_prices"]

    cursor = col.find(
        {},
        {
            "_id": 0,
            "date": 1,
            "close": 1,
            "adjusted_close": 1,
            "volume": 1
        }
    ).sort("date", 1)

    output = []

    for d in cursor:
        price = d.get("adjusted_close") or d.get("close")
        if price is None:
            continue

        output.append({
            "time": d["date"],              # ISO date string
            "symbol": symbol.upper(),
            "price": float(price),
            "volume": int(d.get("volume", 0))
        })

    return output



# =========================
# Base-100 indexed prices
# =========================
def get_base100_indexed_prices(span: int = 20, symbol: str | None = None):
    collections = [
        name for name in db.list_collection_names()
        if name.endswith("_prices")
    ]

    price_dict = defaultdict(dict)
    all_dates = set()

    # -------------------------
    # Load data
    # -------------------------
    for col in collections:
        for d in db[col].find({}, {"_id": 0}):
            sym = d["symbol"].upper()

            # ✅ Symbol filter for Grafana
            if symbol and sym != symbol.upper():
                continue

            date = d["date"]
            price = d.get("adjusted_close") or d.get("close")

            if price is None:
                continue

            price_dict[sym][date] = float(price)
            all_dates.add(date)

    if not price_dict:
        return []

    symbols = sorted(price_dict.keys())
    date_list = sorted(all_dates)

    # -------------------------
    # Align series (forward fill)
    # -------------------------
    aligned = {}
    for s in symbols:
        first_val = None
        arr = []

        for date in date_list:
            if date in price_dict[s]:
                first_val = price_dict[s][date]

            if first_val is None:
                first_val = list(price_dict[s].values())[0]

            arr.append(price_dict[s].get(date, first_val))

        aligned[s] = np.array(arr, dtype=float)

    # -------------------------
    # EMA smoothing
    # -------------------------
    smoothed = {s: ema(aligned[s], span) for s in symbols}

    # -------------------------
    # Base-100 index
    # -------------------------
    indexed = {}
    for s in symbols:
        base = smoothed[s][0]
        indexed[s] = (smoothed[s] / base) * 100

    # -------------------------
    # Final JSON (Grafana-friendly)
    # -------------------------
    output = []
    for i, date in enumerate(date_list):
        row = {"date": date}
        for s in symbols:
            row[s] = round(indexed[s][i], 2)
        output.append(row)

    return output

    # =========================
# KPIs (LATEST SNAPSHOT)
# =========================
def get_kpis(symbol: str):
    col = db[f"{symbol}_prices"]

    # -------------------------
    # Latest trading day
    # -------------------------
    latest = col.find_one(
        {},
        sort=[("date", -1)],
        projection={
            "_id": 0,
            "date": 1,
            "open": 1,
            "high": 1,
            "low": 1,
            "close": 1,
            "volume": 1
        }
    )

    if not latest:
        return {}

    open_price = float(latest["open"])
    close_price = float(latest["close"])

    # -------------------------
    # 52 Week High / Low
    # -------------------------
    cursor_52w = col.find(
        {},
        projection={"_id": 0, "high": 1, "low": 1},
        sort=[("date", -1)],
        limit=252
    )

    highs, lows = [], []

    for d in cursor_52w:
        if "high" in d:
            highs.append(float(d["high"]))
        if "low" in d:
            lows.append(float(d["low"]))

    return {
        "symbol": symbol.upper(),
        "price": round(close_price, 2),
        # "as_of_date": latest["date"], 
        "change_pct": round(
            ((close_price - open_price) / open_price) * 100, 2
        ),
        "volume": int(latest.get("volume", 0)),
        "high_52w": round(max(highs), 2) if highs else None,
        "low_52w": round(min(lows), 2) if lows else None
    }

