"""
Train service — simulates Indian Railways data for routes between major cities.
Replace the _TRAIN_DATA table with a live IRCTC / RailYatri API call when available.
"""
import logging
from typing import List, Tuple, Dict, Any
from app.models.transport_models import TransportOption

logger = logging.getLogger(__name__)

# ── Static train dataset keyed by (origin_lower, destination_lower) ───────────
# Each entry is a list of train schedules.
_TRAIN_DATA: Dict[Tuple[str, str], List[Dict[str, Any]]] = {
    ("kolkata", "delhi"): [
        {
            "train_number": "12301",
            "train_name": "Rajdhani Express",
            "departure": "21:40",
            "arrival": "10:05+1",
            "duration": "12h 25m",
            "price": 1505,
            "train_class": "3A",
        },
        {
            "train_number": "12303",
            "train_name": "Poorva Express",
            "departure": "08:05",
            "arrival": "06:00+1",
            "duration": "21h 55m",
            "price": 735,
            "train_class": "SL",
        },
        {
            "train_number": "12381",
            "train_name": "Poorva Express",
            "departure": "23:55",
            "arrival": "19:30+1",
            "duration": "19h 35m",
            "price": 820,
            "train_class": "SL",
        },
    ],
    ("delhi", "kolkata"): [
        {
            "train_number": "12302",
            "train_name": "Rajdhani Express",
            "departure": "16:55",
            "arrival": "09:55+1",
            "duration": "17h 00m",
            "price": 1505,
            "train_class": "3A",
        },
        {
            "train_number": "12304",
            "train_name": "Poorva Express",
            "departure": "08:45",
            "arrival": "07:15+1",
            "duration": "22h 30m",
            "price": 735,
            "train_class": "SL",
        },
    ],
    ("mumbai", "delhi"): [
        {
            "train_number": "12951",
            "train_name": "Mumbai Rajdhani",
            "departure": "17:00",
            "arrival": "08:35+1",
            "duration": "15h 35m",
            "price": 1560,
            "train_class": "3A",
        },
        {
            "train_number": "12137",
            "train_name": "Punjab Mail",
            "departure": "19:05",
            "arrival": "10:33+1",
            "duration": "27h 28m",
            "price": 680,
            "train_class": "SL",
        },
    ],
    ("delhi", "mumbai"): [
        {
            "train_number": "12952",
            "train_name": "Mumbai Rajdhani",
            "departure": "16:25",
            "arrival": "08:15+1",
            "duration": "15h 50m",
            "price": 1560,
            "train_class": "3A",
        },
        {
            "train_number": "12138",
            "train_name": "Punjab Mail",
            "departure": "20:05",
            "arrival": "22:05+1",
            "duration": "26h 00m",
            "price": 700,
            "train_class": "SL",
        },
    ],
    ("delhi", "bangalore"): [
        {
            "train_number": "22691",
            "train_name": "Rajdhani Express",
            "departure": "20:30",
            "arrival": "05:20+2",
            "duration": "32h 50m",
            "price": 1810,
            "train_class": "3A",
        },
    ],
    ("bangalore", "delhi"): [
        {
            "train_number": "22692",
            "train_name": "Rajdhani Express",
            "departure": "20:25",
            "arrival": "09:50+2",
            "duration": "37h 25m",
            "price": 1810,
            "train_class": "3A",
        },
    ],
    ("mumbai", "bangalore"): [
        {
            "train_number": "11301",
            "train_name": "Udyan Express",
            "departure": "08:05",
            "arrival": "06:00+1",
            "duration": "21h 55m",
            "price": 620,
            "train_class": "SL",
        },
    ],
    ("kolkata", "mumbai"): [
        {
            "train_number": "12809",
            "train_name": "Mumbai Mail",
            "departure": "11:45",
            "arrival": "08:05+2",
            "duration": "44h 20m",
            "price": 940,
            "train_class": "SL",
        },
    ],
    ("kolkata", "kochi"): [
        {
            "train_number": "12659",
            "train_name": "Gurudev Express",
            "departure": "23:50",
            "arrival": "05:20+2",
            "duration": "29h 30m",
            "price": 1850,
            "train_class": "3A",
        },
        {
            "train_number": "16311",
            "train_name": "Bikaner Kochuveli Express",
            "departure": "12:40",
            "arrival": "23:55+1",
            "duration": "35h 15m",
            "price": 920,
            "train_class": "SL",
        },
    ],
    ("kochi", "kolkata"): [
        {
            "train_number": "12660",
            "train_name": "Gurudev Express",
            "departure": "22:35",
            "arrival": "04:25+2",
            "duration": "29h 50m",
            "price": 1850,
            "train_class": "3A",
        },
    ],
    ("kolkata", "kerala"): [
        {
            "train_number": "12659",
            "train_name": "Gurudev Express (to Kochi)",
            "departure": "23:50",
            "arrival": "05:20+2",
            "duration": "29h 30m",
            "price": 1850,
            "train_class": "3A",
        },
        {
            "train_number": "16311",
            "train_name": "Bikaner Kochuveli Express",
            "departure": "12:40",
            "arrival": "23:55+1",
            "duration": "35h 15m",
            "price": 920,
            "train_class": "SL",
        },
    ],
    ("kerala", "kolkata"): [
        {
            "train_number": "12660",
            "train_name": "Gurudev Express",
            "departure": "22:35",
            "arrival": "04:25+2",
            "duration": "29h 50m",
            "price": 1850,
            "train_class": "3A",
        },
    ],
    ("chennai", "delhi"): [
        {
            "train_number": "12433",
            "train_name": "Chennai Rajdhani",
            "departure": "15:00",
            "arrival": "10:25+1",
            "duration": "27h 25m",
            "price": 1700,
            "train_class": "3A",
        },
    ],
    ("delhi", "chennai"): [
        {
            "train_number": "12434",
            "train_name": "Chennai Rajdhani",
            "departure": "22:30",
            "arrival": "04:30+2",
            "duration": "30h 00m",
            "price": 1700,
            "train_class": "3A",
        },
    ],
}


def _normalize_city(name: str) -> str:
    mapping = {
        "new delhi": "delhi",
        "bengaluru": "bangalore",
        "bombay": "mumbai",
        "madras": "chennai",
        "calcutta": "kolkata",
        # State names → representative city used as key
        "kerala": "kerala",    # kept as-is, has its own key above
        "karnataka": "bangalore",
        "tamil nadu": "chennai",
        "west bengal": "kolkata",
        "maharashtra": "mumbai",
        "rajasthan": "jaipur",
        "trivandrum": "trivandrum",
        "thiruvananthapuram": "trivandrum",
        "kochi": "kochi",
        "cochin": "kochi",
    }
    lower = name.lower().strip()
    return mapping.get(lower, lower)


def _build_datetime(date_str: str, time_str: str) -> str:
    """Combine date + HH:MM into an ISO datetime, ignoring +N day suffix."""
    clean_time = time_str.split("+")[0].strip()
    return f"{date_str}T{clean_time}:00"


async def search_trains(
    origin: str,
    destination: str,
    departure_date: str,
) -> List[TransportOption]:
    org = _normalize_city(origin)
    dst = _normalize_city(destination)
    key = (org, dst)

    schedules = _TRAIN_DATA.get(key, [])
    if not schedules:
        logger.info("No train data for route %s → %s", origin, destination)
        return []

    results: List[TransportOption] = []
    for train in schedules:
        dep_dt = _build_datetime(departure_date, train["departure"])
        arr_raw = train["arrival"]
        # Compute arrival date offset
        extra_days = 0
        if "+" in arr_raw:
            parts = arr_raw.split("+")
            arr_raw = parts[0].strip()
            try:
                extra_days = int(parts[1])
            except ValueError:
                pass

        from datetime import date as date_cls, timedelta
        base = date_cls.fromisoformat(departure_date)
        arr_date = (base + timedelta(days=extra_days)).isoformat()
        arr_dt = f"{arr_date}T{arr_raw}:00"

        results.append(
            TransportOption(
                type="train",
                provider="Indian Railways",
                train_number=train["train_number"],
                train_name=train["train_name"],
                train_class=train["train_class"],
                origin=origin.title(),
                destination=destination.title(),
                departure_time=dep_dt,
                arrival_time=arr_dt,
                duration=train["duration"],
                price=float(train["price"]),
                currency="INR",
            )
        )

    logger.info("Found %d train(s) for %s → %s", len(results), origin, destination)
    return results
