from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="UK Housing Affordability Intelligence API",
    description=(
        "Combines HM Land Registry Price Paid Data, ONS Annual Survey of Hours and Earnings, "
        "and ONS Private Rental Market Summary to provide affordability insights across UK regions."
    ),
    version="1.0.0",
    contact={
        "name": "COMP3011 Coursework",
        "url": "https://github.com/AlexJGeorge1/COMP3011-housing-api",
    },
    license_info={"name": "MIT"},
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Service health check")
def health_check():
    """Returns a simple status message confirming the API is running."""
    return {"status": "ok", "version": "1.0.0"}


# ── Routers ───────────────────────────────────────────────────────────────────
from app.auth import router as auth_router
from app.routers.listings import router as listings_router
from app.routers.regions import router as regions_router
from app.routers.affordability import router as affordability_router
from app.routers.trends import router as trends_router
from app.routers.rent_to_buy import router as rent_to_buy_router
from app.routers.search import router as search_router
from app.routers.insights import router as insights_router

app.include_router(auth_router)
app.include_router(listings_router)
app.include_router(regions_router)
app.include_router(affordability_router)
app.include_router(trends_router)
app.include_router(rent_to_buy_router)
app.include_router(search_router)
app.include_router(insights_router)
