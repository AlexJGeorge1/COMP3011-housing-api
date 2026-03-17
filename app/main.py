from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.middleware import ErrorHandlingMiddleware
from app.auth import router as auth_router
from app.routers.listings import router as listings_router
from app.routers.regions import router as regions_router
from app.routers.affordability import router as affordability_router
from app.routers.trends import router as trends_router
from app.routers.rent_to_buy import router as rent_to_buy_router
from app.routers.search import router as search_router
from app.routers.insights import router as insights_router

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

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get(
    "/health",
    tags=["Health"],
    summary="Service health check",
    description="Verifies that the API service is currently running and responsive.",
    responses={
        200: {
            "description": "API is healthy and running.",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "version": "1.0.0"}
                }
            }
        }
    }
)
def health_check():
    """
    Returns a simple status JSON payload confirming the API is running.
    Useful for load balancers or container orchestration platforms to check service liveness.
    """
    return {"status": "ok", "version": "1.0.0"}


app.include_router(auth_router)
app.include_router(listings_router)
app.include_router(regions_router)
app.include_router(affordability_router)
app.include_router(trends_router)
app.include_router(rent_to_buy_router)
app.include_router(search_router)
app.include_router(insights_router)


# ── Dashboard (local only, excluded from git) ──
_DASHBOARD = Path(__file__).resolve().parent.parent / "static" / "dashboard.html"


@app.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
def dashboard():
    return _DASHBOARD.read_text()
