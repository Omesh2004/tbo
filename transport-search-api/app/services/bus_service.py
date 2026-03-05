"""
Bus service — simulates inter-city bus/coach operators for Indian routes.
Replace with a live RedBus / AbhiBus API integration when available.
"""
import logging
from typing import List, Tuple, Dict, Any
from app.models.transport_models import TransportOption

logger = logging.getLogger(__name__)

_BUS_DATA: Dict[Tuple[str, str], List[Dict[str, Any]]] = {
    ("kolkata", "delhi"): [
        {
            "operator": "Shyamoli NR Travels",
            "departure": "17:00",
            "arrival": "20:00+1",
            "duration": "27h 00m",
            "price": 1200,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket", "Water Bottle"],
        },
        {
            "operator": "SRS Travels",
            "departure": "20:00",
            "arrival": "05:00+2",
            "duration": "33h 00m",
            "price": 850,
            "bus_type": "Non-AC Sleeper",
            "amenities": ["Charging Point"],
        },
    ],
    ("delhi", "kolkata"): [
        {
            "operator": "Shyamoli Paribahan",
            "departure": "18:00",
            "arrival": "21:00+1",
            "duration": "27h 00m",
            "price": 1150,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket", "Water Bottle"],
        },
    ],
    ("mumbai", "delhi"): [
        {
            "operator": "Neeta Volvo",
            "departure": "17:30",
            "arrival": "09:30+1",
            "duration": "16h 00m",
            "price": 1400,
            "bus_type": "Volvo AC Sleeper",
            "amenities": ["AC", "USB Charging", "Blanket", "Entertainment"],
        },
        {
            "operator": "Orange Travels",
            "departure": "20:00",
            "arrival": "14:00+1",
            "duration": "18h 00m",
            "price": 980,
            "bus_type": "AC Semi-Sleeper",
            "amenities": ["AC", "USB Charging"],
        },
    ],
    ("delhi", "mumbai"): [
        {
            "operator": "Neeta Volvo",
            "departure": "18:00",
            "arrival": "10:00+1",
            "duration": "16h 00m",
            "price": 1400,
            "bus_type": "Volvo AC Sleeper",
            "amenities": ["AC", "USB Charging", "Blanket"],
        },
    ],
    ("bangalore", "mumbai"): [
        {
            "operator": "VRL Travels",
            "departure": "19:00",
            "arrival": "13:00+1",
            "duration": "18h 00m",
            "price": 1100,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket", "Water Bottle"],
        },
        {
            "operator": "SRS Travels",
            "departure": "21:30",
            "arrival": "16:30+1",
            "duration": "19h 00m",
            "price": 780,
            "bus_type": "Non-AC Sleeper",
            "amenities": ["Charging Point"],
        },
    ],
    ("mumbai", "bangalore"): [
        {
            "operator": "VRL Travels",
            "departure": "19:30",
            "arrival": "14:00+1",
            "duration": "18h 30m",
            "price": 1100,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket"],
        },
    ],
    ("delhi", "jaipur"): [
        {
            "operator": "RSRTC Volvo",
            "departure": "06:00",
            "arrival": "11:00",
            "duration": "5h 00m",
            "price": 320,
            "bus_type": "Volvo AC",
            "amenities": ["AC"],
        },
        {
            "operator": "Intercity Smart Bus",
            "departure": "08:00",
            "arrival": "13:30",
            "duration": "5h 30m",
            "price": 250,
            "bus_type": "AC Seater",
            "amenities": ["AC", "USB Charging"],
        },
    ],
    ("jaipur", "delhi"): [
        {
            "operator": "RSRTC Volvo",
            "departure": "07:00",
            "arrival": "12:30",
            "duration": "5h 30m",
            "price": 320,
            "bus_type": "Volvo AC",
            "amenities": ["AC"],
        },
    ],
    ("mumbai", "pune"): [
        {
            "operator": "MSRTC Shivneri",
            "departure": "07:00",
            "arrival": "10:30",
            "duration": "3h 30m",
            "price": 310,
            "bus_type": "Volvo AC",
            "amenities": ["AC"],
        },
        {
            "operator": "IntrCity SmartBus",
            "departure": "09:00",
            "arrival": "13:00",
            "duration": "4h 00m",
            "price": 249,
            "bus_type": "AC Seater",
            "amenities": ["AC", "USB Charging", "WiFi"],
        },
    ],
    ("pune", "mumbai"): [
        {
            "operator": "MSRTC Shivneri",
            "departure": "06:30",
            "arrival": "10:00",
            "duration": "3h 30m",
            "price": 310,
            "bus_type": "Volvo AC",
            "amenities": ["AC"],
        },
    ],
    ("bangalore", "chennai"): [
        {
            "operator": "KSRTC Airavat",
            "departure": "22:00",
            "arrival": "06:00+1",
            "duration": "8h 00m",
            "price": 550,
            "bus_type": "Volvo AC Sleeper",
            "amenities": ["AC", "Blanket"],
        },
        {
            "operator": "SRM Travels",
            "departure": "23:00",
            "arrival": "07:30+1",
            "duration": "8h 30m",
            "price": 420,
            "bus_type": "AC Semi-Sleeper",
            "amenities": ["AC"],
        },
    ],
    ("chennai", "bangalore"): [
        {
            "operator": "KSRTC Airavat",
            "departure": "22:30",
            "arrival": "07:00+1",
            "duration": "8h 30m",
            "price": 550,
            "bus_type": "Volvo AC Sleeper",
            "amenities": ["AC", "Blanket"],
        },
    ],
    ("kolkata", "kochi"): [
        {
            "operator": "KPN Travels",
            "departure": "16:00",
            "arrival": "20:00+2",
            "duration": "52h 00m",
            "price": 2200,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket", "Water Bottle", "Charging Point"],
        },
        {
            "operator": "SRS Travels",
            "departure": "18:00",
            "arrival": "00:00+3",
            "duration": "54h 00m",
            "price": 1650,
            "bus_type": "Non-AC Sleeper",
            "amenities": ["Charging Point"],
        },
    ],
    ("kochi", "kolkata"): [
        {
            "operator": "KPN Travels",
            "departure": "17:00",
            "arrival": "21:00+2",
            "duration": "52h 00m",
            "price": 2200,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket", "Charging Point"],
        },
    ],
    ("kolkata", "kerala"): [
        {
            "operator": "KPN Travels",
            "departure": "16:00",
            "arrival": "20:00+2",
            "duration": "52h 00m",
            "price": 2200,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket", "Water Bottle", "Charging Point"],
        },
        {
            "operator": "SRS Travels",
            "departure": "18:00",
            "arrival": "00:00+3",
            "duration": "54h 00m",
            "price": 1650,
            "bus_type": "Non-AC Sleeper",
            "amenities": ["Charging Point"],
        },
    ],
    ("kerala", "kolkata"): [
        {
            "operator": "KPN Travels",
            "departure": "17:00",
            "arrival": "21:00+2",
            "duration": "52h 00m",
            "price": 2200,
            "bus_type": "AC Sleeper",
            "amenities": ["AC", "Blanket", "Charging Point"],
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
        # State names and alternate city names
        "kerala": "kerala",    # kept as-is, has its own key above
        "karnataka": "bangalore",
        "tamil nadu": "chennai",
        "west bengal": "kolkata",
        "maharashtra": "mumbai",
        "rajasthan": "jaipur",
        "cochin": "kochi",
        "trivandrum": "trivandrum",
        "thiruvananthapuram": "trivandrum",
    }
    lower = name.lower().strip()
    return mapping.get(lower, lower)


def _build_datetime(date_str: str, time_str: str) -> str:
    clean_time = time_str.split("+")[0].strip()
    return f"{date_str}T{clean_time}:00"


async def search_buses(
    origin: str,
    destination: str,
    departure_date: str,
) -> List[TransportOption]:
    org = _normalize_city(origin)
    dst = _normalize_city(destination)
    key = (org, dst)

    schedules = _BUS_DATA.get(key, [])
    if not schedules:
        logger.info("No bus data for route %s → %s", origin, destination)
        return []

    results: List[TransportOption] = []
    for bus in schedules:
        dep_dt = _build_datetime(departure_date, bus["departure"])

        arr_raw = bus["arrival"]
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
                type="bus",
                provider=bus["operator"],
                bus_type=bus["bus_type"],
                amenities=bus.get("amenities", []),
                origin=origin.title(),
                destination=destination.title(),
                departure_time=dep_dt,
                arrival_time=arr_dt,
                duration=bus["duration"],
                price=float(bus["price"]),
                currency="INR",
            )
        )

    logger.info("Found %d bus(es) for %s → %s", len(results), origin, destination)
    return results
