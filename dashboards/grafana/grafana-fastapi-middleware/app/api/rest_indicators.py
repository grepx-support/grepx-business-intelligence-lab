from fastapi import APIRouter, Query
from app.services.indicator_service import get_rsi, get_sma


router = APIRouter()

@router.get("/rsi")
def rsi(
    symbol: str = Query(..., description="Stock symbol")
):
    return get_rsi(symbol)

@router.get("/sma")
def sma(symbol: str = Query(..., description="Stock symbol")):
    return get_sma(symbol)
