from fastapi import FastAPI

app = FastAPI(
    title="MarketHub Core API",
    description="Core backend API for the MarketHub platform",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "MarketHub Core API is running"}
