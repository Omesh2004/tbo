"""Transport Search API — entry point."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.search import router as search_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)

app = FastAPI(
    title="Transport Search API",
    description=(
        "Unified travel search service that returns flights, trains, and buses "
        "for a given origin → destination route on a specific date."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api", tags=["Transport Search"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "transport-search-api", "version": "1.0.0"}
