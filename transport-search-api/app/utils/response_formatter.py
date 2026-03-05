"""Normalize and sort transport results into a unified response."""
from typing import List
from app.models.transport_models import TransportOption, SearchResponse


def _duration_to_minutes(duration_str: str) -> int:
    """Convert duration string like '2h 15m' or '14h 30m' to total minutes."""
    total = 0
    parts = duration_str.lower().replace("hr", "h").replace("hrs", "h").replace("min", "m").replace("mins", "m")
    if "h" in parts:
        h_part, rest = parts.split("h", 1)
        try:
            total += int(h_part.strip()) * 60
        except ValueError:
            pass
        parts = rest
    if "m" in parts:
        m_part = parts.replace("m", "").strip()
        try:
            total += int(m_part)
        except ValueError:
            pass
    return total if total > 0 else 9999


def build_response(
    origin: str,
    destination: str,
    date: str,
    results: List[TransportOption],
    sort_by: str = "price",
) -> SearchResponse:
    if sort_by == "duration":
        results.sort(key=lambda x: _duration_to_minutes(x.duration))
    else:
        results.sort(key=lambda x: x.price)

    return SearchResponse(
        origin=origin,
        destination=destination,
        date=date,
        total_results=len(results),
        sort_by=sort_by,
        transport_options=results,
    )
