from fastapi import APIRouter, Query
from app.services.price_service import (
    get_base100_indexed_prices,
    get_price_volume,
    get_kpis,
    get_symbols
)

router = APIRouter()


@router.get("/symbols")
def symbols():
    return get_symbols()


@router.get("/prices")
def prices(
    span: int = Query(20, description="EMA span"),
    symbol: str | None = Query(None, description="Stock symbol")
):
    return get_base100_indexed_prices(span=span, symbol=symbol)

@router.get("/price-volume")
def price_volume(
    symbol: str = Query(..., description="Stock symbol")
):
    return get_price_volume(symbol)



@router.get("/kpis")
def kpis(
    symbol: str = Query(..., description="Stock symbol")
):
    return get_kpis(symbol)
