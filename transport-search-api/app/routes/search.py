"""Transport search route — runs all three services concurrently."""
import asyncio
import logging
from fastapi import APIRouter, HTTPException

from app.models.transport_models import SearchRequest, SearchResponse
from app.services.flight_service import search_flights
from app.services.train_service import search_trains
from app.services.bus_service import search_buses
from app.utils.response_formatter import build_response

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search-transport", response_model=SearchResponse, summary="Search all transport modes")
async def search_transport(request: SearchRequest) -> SearchResponse:
    """
    Search for flights, trains, and buses between two cities on a given date.

    - Queries all three services **concurrently**.
    - Returns a unified, sorted list of transport options.
    - Sort by `price` (default) or `duration`.
    """
    origin = request.origin.strip()
    destination = request.destination.strip()
    date_str = request.travel_date.isoformat()

    logger.info("Transport search: %s → %s on %s", origin, destination, date_str)

    # Run all three searches in parallel
    flights_task = search_flights(origin, destination, date_str, adults=request.adults)
    trains_task = search_trains(origin, destination, date_str)
    buses_task = search_buses(origin, destination, date_str)

    results_tuple = await asyncio.gather(
        flights_task, trains_task, buses_task, return_exceptions=True
    )

    all_results = []
    service_names = ["flight", "train", "bus"]
    for name, result in zip(service_names, results_tuple):
        if isinstance(result, Exception):
            logger.error("%s service error: %s", name, result)
        else:
            all_results.extend(result)

    if not all_results:
        raise HTTPException(
            status_code=404,
            detail=f"No transport options found for {origin} → {destination} on {date_str}.",
        )

    return build_response(
        origin=origin,
        destination=destination,
        date=date_str,
        results=all_results,
        sort_by=request.sort_by,
    )
