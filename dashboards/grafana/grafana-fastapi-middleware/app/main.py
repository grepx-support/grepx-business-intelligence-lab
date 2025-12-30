from fastapi import FastAPI
from app.api.rest_prices import router as price_router
from app.api.rest_indicators import router as indicator_router




app = FastAPI(title="Grafana + FastAPI + MongoDB")

app.include_router(price_router, prefix="/api")
app.include_router(indicator_router, prefix="/api")


@app.get("/")
def health():
    return {"status": "ok"}
