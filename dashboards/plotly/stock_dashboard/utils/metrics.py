import numpy as np
import pandas as pd

TRADING_DAYS = 252

def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["symbol", "date"]).copy()
    df["returns"] = df.groupby("symbol")["close"].pct_change()
    return df

def add_normalized_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize prices to base 100 per symbol.
    Each symbol starts at 100 on its first valid date.
    """
    df = df.copy()
    
    # Ensure data is sorted by symbol and date
    df = df.sort_values(["symbol", "date"]).reset_index(drop=True)
    
    # Normalize per symbol using transform (returns Series, not DataFrame)
    df["norm_close"] = df.groupby("symbol")["close"].transform(
        lambda x: (x / x.iloc[0]) * 100.0 if x.iloc[0] > 0 else 100.0
    )
    
    return df

def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["symbol", "date"]).copy()
    pv = df["close"] * df["volume"]
    df["cum_pv"] = pv.groupby(df["symbol"]).cumsum()
    df["cum_vol"] = df["volume"].groupby(df["symbol"]).cumsum().replace(0, np.nan)
    df["vwap"] = df["cum_pv"] / df["cum_vol"]
    df.drop(["cum_pv", "cum_vol"], axis=1, inplace=True)
    return df

def monthly_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    m = (
        df.groupby(["symbol", "year", "month"])
        .agg(first_close=("close", "first"), last_close=("close", "last"))
        .reset_index()
    )
    m["monthly_return"] = np.where(
    m["first_close"] > 0,
    (m["last_close"] - m["first_close"]) / m["first_close"],
    np.nan
)
    return m

def yearly_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"] = df["date"].dt.year

    y = (
        df.groupby(["symbol", "year"])
        .agg(first_close=("close", "first"), last_close=("close", "last"))
        .reset_index()
    )
    y["yearly_return"] = (y["last_close"] - y["first_close"]) / y["first_close"]
    return y

def cagr_by_symbol(df: pd.DataFrame) -> pd.Series:
    rows = []
    for sym, sdf in df.groupby("symbol"):
        sdf = sdf.sort_values("date")
        if len(sdf) < 2:
            continue
        start = float(sdf["close"].iloc[0])
        end = float(sdf["close"].iloc[-1])
        years = max((sdf["date"].iloc[-1] - sdf["date"].iloc[0]).days / 365.25, 1e-9)
        cagr = (end / start) ** (1 / years) - 1
        rows.append((sym, cagr))
    return pd.Series(dict(rows)).sort_values(ascending=False)

def annual_vol_by_symbol(df: pd.DataFrame) -> pd.Series:
    # annualized volatility per symbol
    vol = df.groupby("symbol")["returns"].std() * np.sqrt(TRADING_DAYS)
    return vol.sort_values(ascending=False)

def sharpe_by_symbol(df: pd.DataFrame, rf=0.04) -> pd.Series:
    # Sharpe ≈ (CAGR - rf) / annual_vol
    c = cagr_by_symbol(df)
    v = annual_vol_by_symbol(df)
    aligned = c.index.intersection(v.index)
    s = (c.loc[aligned] - rf) / v.loc[aligned].replace(0, np.nan)
    return s.sort_values(ascending=False)

def max_drawdown_by_symbol(df: pd.DataFrame) -> pd.Series:
    out = {}
    for sym, sdf in df.groupby("symbol"):
        sdf = sdf.sort_values("date")
        peak = sdf["close"].cummax()
        dd = (sdf["close"] / peak) - 1
        out[sym] = float(dd.min())
    return pd.Series(out).sort_values()


def risk_table(df: pd.DataFrame, window=30) -> pd.DataFrame:
    """
    Industry-standard risk scoring used by Morningstar, Bloomberg, etc.
    Uses percentile-based approach: rank stocks 0-100 within dataset.
    """
    rows = []
    for sym, sdf in df.groupby("symbol"):
        sdf = sdf.sort_values("date")
        if len(sdf) < window + 5:
            continue
        
        # Daily volatility (last 30 days)
        vol30 = float(sdf["returns"].rolling(window).std().iloc[-1])
        ann_vol = vol30 * np.sqrt(TRADING_DAYS)
        
        # Maximum drawdown (all-time or period)
        max_dd = float(((sdf["close"] / sdf["close"].cummax()) - 1).min())
        
        # Sharpe Ratio (risk-adjusted return)
        total_return = (sdf["close"].iloc[-1] / sdf["close"].iloc[0]) - 1
        sharpe = total_return / (vol30 * np.sqrt(TRADING_DAYS)) if ann_vol > 0 else 0
        
        rows.append({
            "symbol": sym, 
            "ann_vol": ann_vol, 
            "max_drawdown": max_dd,
            "sharpe": sharpe
        })
    
    r = pd.DataFrame(rows)
    if r.empty:
        return r
    
    r["vol_percentile"] = r["ann_vol"].rank(pct=True) * 100
    r["dd_percentile"] = np.abs(r["max_drawdown"]).rank(pct=True) * 100
    
    r["risk_score"] = (0.6 * r["vol_percentile"] + 0.4 * r["dd_percentile"])
    
    r = r.sort_values("risk_score", ascending=False)
    
    print(f"\n=== PERCENTILE-BASED RISK SCORES ===")
    print(f"(0 = safest, 100 = riskiest among selected stocks)")
    for idx, row in r.iterrows():
        print(f"{row['symbol']}: {row['risk_score']:.2f}/100 " +
              f"(Vol %ile: {row['vol_percentile']:.0f}, DD %ile: {row['dd_percentile']:.0f})")
    
    return r