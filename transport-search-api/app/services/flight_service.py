"""
Amadeus Flight Service
Uses the Amadeus Test API (sandbox) -- same credentials already used in tbo/testamad.py
Auth:   POST https://test.api.amadeus.com/v1/security/oauth2/token
Search: GET  https://test.api.amadeus.com/v2/shopping/flight-offers
"""
import os
import re
import logging
from typing import List, Optional
from datetime import datetime, timedelta

import httpx

from app.models.transport_models import TransportOption

logger = logging.getLogger(__name__)

# -- Amadeus API config --------------------------------------------------------
AMADEUS_BASE_URL      = "https://test.api.amadeus.com"
AMADEUS_CLIENT_ID     = os.getenv("AMADEUS_CLIENT_ID",     "3U0F7vgHIN9Xvq31WiQnVVPB6ohfYpT9")
AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET", "g83BzbXv4GzafOCT")

# -- City -> IATA code table ---------------------------------------------------
CITY_TO_IATA = {
    # --- Indian cities ---
    "delhi": "DEL", "new delhi": "DEL",
    "mumbai": "BOM", "bombay": "BOM",
    "kolkata": "CCU", "calcutta": "CCU",
    "chennai": "MAA", "madras": "MAA",
    "bangalore": "BLR", "bengaluru": "BLR",
    "hyderabad": "HYD",
    "ahmedabad": "AMD",
    "pune": "PNQ",
    "jaipur": "JAI",
    "kochi": "COK", "cochin": "COK",
    "goa": "GOI",
    "lucknow": "LKO",
    "patna": "PAT",
    "bhubaneswar": "BBI",
    "bhopal": "BHO",
    "indore": "IDR",
    "nagpur": "NAG",
    "srinagar": "SXR",
    "amritsar": "ATQ",
    "chandigarh": "IXC",
    "visakhapatnam": "VTZ", "vizag": "VTZ",
    "coimbatore": "CJB",
    "trichy": "TRZ", "tiruchirappalli": "TRZ",
    "madurai": "IXM",
    "varanasi": "VNS",
    "ranchi": "IXR",
    "raipur": "RPR",
    "guwahati": "GAU",
    "dibrugarh": "DIB",
    "bagdogra": "IXB",
    "port blair": "IXZ",
    "leh": "IXL",
    "jammu": "IXJ",
    "udaipur": "UDR",
    "jodhpur": "JDH",
    "aurangabad": "IXU",
    "hubli": "HBX",
    "mangalore": "IXE",
    "tiruvandrum": "TRV", "thiruvananthapuram": "TRV", "trivandrum": "TRV",
    "calicut": "CCJ", "kozhikode": "CCJ",
    "agra": "AGR",
    "varanasi": "VNS", "banaras": "VNS",
    "dehradun": "DED",
    "shimla": "SLV",
    "kullu": "KUU", "manali": "KUU",
    "dharamsala": "DHM",
    "gorakhpur": "GOP",
    "allahabad": "IXD", "prayagraj": "IXD",
    "surat": "STV",
    "vadodara": "BDQ",
    "rajkot": "RAJ",
    "bhavnagar": "BHU",
    "silchar": "IXS",
    "jorhat": "JRH",
    "tezpur": "TEZ",
    "imphal": "IMF",
    "aizawl": "AJL",
    "agartala": "IXA",
    "shillong": "SHL",
    "lilabari": "LMB",
    "deoghar": "DGH",
    "darbhanga": "DBR",
    "kushinagar": "KBK",
    "hindon": "HDO",
    # Indian state names -> primary airport
    "kerala": "COK",
    "rajasthan": "JAI",
    "punjab": "ATQ",
    "karnataka": "BLR",
    "tamil nadu": "MAA",
    "west bengal": "CCU",
    "maharashtra": "BOM",
    "andhra pradesh": "HYD",
    "telangana": "HYD",
    "odisha": "BBI",
    "assam": "GAU",
    "bihar": "PAT",
    "uttarakhand": "DED",
    "himachal pradesh": "KUU",
    "jammu and kashmir": "SXR",
    "ladakh": "IXL",
    "gujarat": "AMD",
    "madhya pradesh": "BHO",
    "chhattisgarh": "RPR",
    "jharkhand": "IXR",
    "tripura": "IXA",
    "meghalaya": "SHL",
    "manipur": "IMF",
    # --- Middle East ---
    "dubai": "DXB",
    "abu dhabi": "AUH",
    "sharjah": "SHJ",
    "doha": "DOH",
    "riyadh": "RUH",
    "jeddah": "JED",
    "muscat": "MCT",
    "kuwait": "KWI", "kuwait city": "KWI",
    "bahrain": "BAH", "manama": "BAH",
    "amman": "AMM",
    "beirut": "BEY",
    "tel aviv": "TLV",
    # --- South / Southeast Asia ---
    "singapore": "SIN",
    "bangkok": "BKK", "suvarnabhumi": "BKK",
    "phuket": "HKT",
    "chiang mai": "CNX",
    "kuala lumpur": "KUL", "kl": "KUL",
    "penang": "PEN",
    "kota kinabalu": "BKI",
    "jakarta": "CGK",
    "bali": "DPS", "denpasar": "DPS",
    "colombo": "CMB",
    "dhaka": "DAC",
    "kathmandu": "KTM",
    "male": "MLE",
    "yangon": "RGN",
    "ho chi minh city": "SGN", "saigon": "SGN",
    "hanoi": "HAN",
    "da nang": "DAD",
    "phnom penh": "PNH",
    "manila": "MNL",
    "cebu": "CEB",
    # --- East Asia ---
    "hong kong": "HKG",
    "beijing": "PEK",
    "shanghai": "PVG",
    "guangzhou": "CAN",
    "shenzhen": "SZX",
    "chengdu": "CTU",
    "xiamen": "XMN",
    "tokyo": "NRT", "narita": "NRT",
    "osaka": "KIX",
    "nagoya": "NGO",
    "sapporo": "CTS",
    "fukuoka": "FUK",
    "seoul": "ICN", "incheon": "ICN",
    "busan": "PUS",
    "taipei": "TPE",
    "macau": "MFM",
    # --- South Asia / Central Asia ---
    "islamabad": "ISB",
    "lahore": "LHE",
    "karachi": "KHI",
    "tashkent": "TAS",
    "almaty": "ALA",
    "kabul": "KBL",
    # --- Europe ---
    "london": "LHR", "heathrow": "LHR",
    "london gatwick": "LGW", "gatwick": "LGW",
    "london stansted": "STN",
    "paris": "CDG", "charles de gaulle": "CDG",
    "paris orly": "ORY",
    "amsterdam": "AMS",
    "frankfurt": "FRA",
    "munich": "MUC",
    "berlin": "BER",
    "madrid": "MAD",
    "barcelona": "BCN",
    "rome": "FCO", "fiumicino": "FCO",
    "milan": "MXP", "malpensa": "MXP",
    "zurich": "ZRH",
    "geneva": "GVA",
    "vienna": "VIE",
    "brussels": "BRU",
    "lisbon": "LIS",
    "copenhagen": "CPH",
    "stockholm": "ARN",
    "oslo": "OSL",
    "helsinki": "HEL",
    "athens": "ATH",
    "istanbul": "IST",
    "warsaw": "WAW",
    "budapest": "BUD",
    "prague": "PRG",
    "dublin": "DUB",
    "edinburgh": "EDI",
    "manchester": "MAN",
    "birmingham": "BHX",
    "nice": "NCE",
    "zurich": "ZRH",
    "dusseldorf": "DUS",
    "hamburg": "HAM",
    "venice": "VCE",
    "florence": "FLR",
    "naples": "NAP",
    "porto": "OPO",
    "seville": "SVQ",
    "valencia": "VLC",
    "lyon": "LYS",
    "toulouse": "TLS",
    "bucharest": "OTP",
    "sofia": "SOF",
    "zagreb": "ZAG",
    "belgrade": "BEG",
    "kyiv": "KBP", "kiev": "KBP",
    "moscow": "SVO",
    "saint petersburg": "LED", "st petersburg": "LED",
    # --- Africa ---
    "cairo": "CAI",
    "johannesburg": "JNB",
    "cape town": "CPT",
    "nairobi": "NBO",
    "lagos": "LOS",
    "accra": "ACC",
    "addis ababa": "ADD",
    "casablanca": "CMN",
    "tunis": "TUN",
    "algiers": "ALG",
    "kigali": "KGL",
    "dar es salaam": "DAR",
    "entebbe": "EBB",
    # --- North America ---
    "new york": "JFK", "nyc": "JFK",
    "new york city": "JFK",
    "new jersey": "EWR", "newark": "EWR",
    "los angeles": "LAX", "la": "LAX",
    "chicago": "ORD",
    "san francisco": "SFO", "sf": "SFO",
    "houston": "IAH",
    "dallas": "DFW",
    "miami": "MIA",
    "boston": "BOS",
    "seattle": "SEA",
    "atlanta": "ATL",
    "denver": "DEN",
    "las vegas": "LAS",
    "orlando": "MCO",
    "washington": "IAD", "washington dc": "IAD", "dc": "IAD",
    "washington dulles": "IAD",
    "washington reagan": "DCA",
    "philadelphia": "PHL",
    "phoenix": "PHX",
    "minneapolis": "MSP",
    "detroit": "DTW",
    "charlotte": "CLT",
    "san diego": "SAN",
    "salt lake city": "SLC",
    "portland": "PDX",
    "nashville": "BNA",
    "austin": "AUS",
    "san antonio": "SAT",
    "new orleans": "MSY",
    "pittsburgh": "PIT",
    "kansas city": "MCI",
    "st louis": "STL",
    "baltimore": "BWI",
    "raleigh": "RDU",
    "indianapolis": "IND",
    "columbus": "CMH",
    "cincinnati": "CVG",
    "memphis": "MEM",
    "louisville": "SDF",
    "richmond": "RIC",
    "buffalo": "BUF",
    "rochester": "ROC",
    "albany": "ALB",
    "jacksonville": "JAX",
    "tampa": "TPA",
    "fort lauderdale": "FLL",
    "west palm beach": "PBI",
    "albuquerque": "ABQ",
    "tucson": "TUS",
    "el paso": "ELP",
    "oklahoma city": "OKC",
    "tulsa": "TUL",
    "omaha": "OMA",
    "sacramento": "SMF",
    "san jose": "SJC",
    "los angeles": "LAX",
    "burbank": "BUR",
    "long beach": "LGB",
    "ontario california": "ONT",
    "honolulu": "HNL", "hawaii": "HNL",
    "anchorage": "ANC", "alaska": "ANC",
    # Canada
    "toronto": "YYZ",
    "vancouver": "YVR",
    "montreal": "YUL",
    "calgary": "YYC",
    "ottawa": "YOW",
    "edmonton": "YEG",
    "winnipeg": "YWG",
    # Mexico / Caribbean
    "mexico city": "MEX",
    "cancun": "CUN",
    "guadalajara": "GDL",
    "monterrey": "MTY",
    "havana": "HAV",
    "san juan": "SJU",
    # South America
    "sao paulo": "GRU", "são paulo": "GRU",
    "rio de janeiro": "GIG",
    "buenos aires": "EZE",
    "bogota": "BOG", "bogotá": "BOG",
    "santiago": "SCL",
    "lima": "LIM",
    "quito": "UIO",
    "caracas": "CCS",
    # --- Oceania ---
    "sydney": "SYD",
    "melbourne": "MEL",
    "brisbane": "BNE",
    "perth": "PER",
    "auckland": "AKL",
    "christchurch": "CHC",
}


def city_to_iata(city: str) -> Optional[str]:
    """Return IATA airport code for a city name, or None if city is unknown."""
    code = CITY_TO_IATA.get(city.lower().strip())
    if code:
        return code
    # Accept if it looks like a valid IATA code already (3 uppercase letters)
    stripped = city.strip().upper()
    if len(stripped) == 3 and stripped.isalpha():
        return stripped
    logger.warning("city_to_iata: unknown city '%s' -- cannot resolve IATA code", city)
    return None


def _parse_iso_duration(iso: str) -> str:
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", iso or "")
    if not m:
        return "N/A"
    h = int(m.group(1) or 0)
    mins = int(m.group(2) or 0)
    return f"{h}h {mins}m"


# -- Airline code -> name lookup -----------------------------------------------
_AIRLINE_NAMES = {
    # Indian carriers
    "6E": "IndiGo", "SG": "SpiceJet", "AI": "Air India",
    "UK": "Vistara", "QP": "Akasa Air", "G8": "Go First",
    "IX": "Air India Express", "I5": "Air Asia India",
    # Gulf / Middle East
    "EK": "Emirates", "QR": "Qatar Airways", "EY": "Etihad",
    "FZ": "flydubai", "WY": "Oman Air", "GF": "Gulf Air",
    "KU": "Kuwait Airways", "SV": "Saudia", "UL": "SriLankan Airlines",
    "PG": "Bangkok Airways", "FD": "Thai AirAsia", "TG": "Thai Airways",
    # South / Southeast Asian
    "SQ": "Singapore Airlines", "MI": "SilkAir", "TR": "Scoot",
    "MH": "Malaysia Airlines", "AK": "AirAsia", "OD": "Batik Air (Malaysia)",
    "CX": "Cathay Pacific", "KA": "Cathay Dragon",
    "GA": "Garuda Indonesia", "JT": "Lion Air",
    "NH": "ANA", "JL": "Japan Airlines", "7C": "Jeju Air",
    # European
    "LH": "Lufthansa", "BA": "British Airways", "AF": "Air France",
    "TK": "Turkish Airlines", "OS": "Austrian Airlines",
    "KL": "KLM", "IB": "Iberia", "AZ": "ITA Airways",
    "SK": "Scandinavian Airlines", "LX": "Swiss",
    # Others
    "ET": "Ethiopian Airlines", "MS": "EgyptAir", "KQ": "Kenya Airways",
    "AC": "Air Canada", "AA": "American Airlines", "UA": "United Airlines",
    "DL": "Delta Air Lines", "B6": "JetBlue",
}


def _airline_name(code: str) -> str:
    return _AIRLINE_NAMES.get(code, code)


# -- Mock fallback -------------------------------------------------------------
_ROUTE_DURATIONS = {
    frozenset(["DEL", "BOM"]): 135, frozenset(["DEL", "MAA"]): 165,
    frozenset(["DEL", "BLR"]): 165, frozenset(["DEL", "CCU"]): 120,
    frozenset(["DEL", "HYD"]): 150, frozenset(["DEL", "COK"]): 210,
    frozenset(["DEL", "GOI"]): 150, frozenset(["DEL", "JAI"]): 60,
    frozenset(["BOM", "MAA"]): 120, frozenset(["BOM", "BLR"]): 90,
    frozenset(["BOM", "CCU"]): 165, frozenset(["BOM", "HYD"]): 90,
    frozenset(["BOM", "COK"]): 90,  frozenset(["BOM", "GOI"]): 60,
    frozenset(["BOM", "PNQ"]): 30,  frozenset(["MAA", "BLR"]): 60,
    frozenset(["MAA", "CCU"]): 150, frozenset(["MAA", "HYD"]): 75,
    frozenset(["MAA", "COK"]): 75,  frozenset(["BLR", "CCU"]): 165,
    frozenset(["BLR", "HYD"]): 75,  frozenset(["BLR", "COK"]): 105,
    frozenset(["CCU", "HYD"]): 120, frozenset(["CCU", "COK"]): 150,
    frozenset(["CCU", "MAA"]): 150, frozenset(["HYD", "COK"]): 90,
    frozenset(["COK", "TRV"]): 40,
}

_MOCK_AIRLINES = [
    {"name": "IndiGo",    "code": "6E", "fn_start": 200,  "factor": 1.00},
    {"name": "SpiceJet",  "code": "SG", "fn_start": 100,  "factor": 0.90},
    {"name": "Air India", "code": "AI", "fn_start": 400,  "factor": 1.30},
    {"name": "Vistara",   "code": "UK", "fn_start": 800,  "factor": 1.50},
    {"name": "Akasa Air", "code": "QP", "fn_start": 1100, "factor": 0.85},
]
_DEP_SLOTS = [5, 7, 9, 12, 15, 18, 20]


def _mock_flights(
    origin_city: str, destination_city: str,
    origin_code: str, destination_code: str,
    departure_date: str, adults: int,
) -> List[TransportOption]:
    key = frozenset([origin_code, destination_code])
    duration_min = _ROUTE_DURATIONS.get(key, 180)
    base_price = duration_min * 28 * max(1, adults)
    seed_val = (ord(origin_code[0]) + ord(destination_code[0])) % len(_MOCK_AIRLINES)
    chosen = [_MOCK_AIRLINES[(seed_val + i) % len(_MOCK_AIRLINES)] for i in range(3)]
    slots = _DEP_SLOTS[seed_val % len(_DEP_SLOTS):: 3] or _DEP_SLOTS[:3]

    results: List[TransportOption] = []
    for i, airline in enumerate(chosen):
        dep_hour = slots[i % len(slots)]
        dep_min = (seed_val * 7 + i * 15) % 60
        dep_dt = datetime.strptime(departure_date, "%Y-%m-%d").replace(hour=dep_hour, minute=dep_min)
        arr_dt = dep_dt + timedelta(minutes=duration_min + i * 5)
        price = round(base_price * airline["factor"] / 100) * 100 + i * 200
        fn_num = airline["fn_start"] + seed_val * 3 + i + 1
        h, m = divmod(duration_min + i * 5, 60)
        results.append(TransportOption(
            type="flight",
            provider=airline["name"],
            airline_code=airline["code"],
            flight_number=f"{airline['code']}-{fn_num}",
            origin=origin_city.title(),
            destination=destination_city.title(),
            departure_time=dep_dt.strftime("%Y-%m-%dT%H:%M"),
            arrival_time=arr_dt.strftime("%Y-%m-%dT%H:%M"),
            duration=f"{h}h {m}m",
            price=float(price),
            currency="INR",
            stops=0,
            cabin_class="Economy",
        ))
    logger.info("Mock: generated %d flight(s) for %s->%s", len(results), origin_code, destination_code)
    return results


# -- Amadeus helpers -----------------------------------------------------------
async def _get_amadeus_token(client: httpx.AsyncClient) -> Optional[str]:
    try:
        resp = await client.post(
            f"{AMADEUS_BASE_URL}/v1/security/oauth2/token",
            data={
                "grant_type":    "client_credentials",
                "client_id":     AMADEUS_CLIENT_ID,
                "client_secret": AMADEUS_CLIENT_SECRET,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=15,
        )
        resp.raise_for_status()
        token = resp.json().get("access_token")
        if not token:
            logger.error("Amadeus auth: no access_token in response")
        return token
    except Exception as exc:
        logger.error("Amadeus auth failed: %s", exc)
        return None


def _parse_amadeus_offers(
    offers: list, origin_city: str, destination_city: str,
) -> List[TransportOption]:
    results: List[TransportOption] = []
    for offer in offers:
        try:
            itinerary  = offer["itineraries"][0]
            segments   = itinerary["segments"]
            first_seg  = segments[0]
            last_seg   = segments[-1]
            carrier    = first_seg.get("carrierCode", "")
            flight_num = f"{carrier}{first_seg.get('number', '')}"
            dep_time   = first_seg["departure"]["at"][:16]
            arr_time   = last_seg["arrival"]["at"][:16]
            duration   = _parse_iso_duration(itinerary.get("duration", ""))
            stops      = len(segments) - 1
            price_data = offer.get("price", {})
            price      = float(price_data.get("grandTotal") or price_data.get("total") or 0)
            currency   = price_data.get("currency", "EUR")
            results.append(TransportOption(
                type="flight",
                provider=_airline_name(carrier),
                airline_code=carrier,
                flight_number=flight_num,
                origin=origin_city.title(),
                destination=destination_city.title(),
                departure_time=dep_time,
                arrival_time=arr_time,
                duration=duration,
                price=price,
                currency=currency,
                stops=stops,
                cabin_class="Economy",
            ))
        except Exception as parse_err:
            logger.debug("Skipping offer: %s", parse_err)
    return results


# -- Public API ----------------------------------------------------------------
async def search_flights(
    origin_city: str,
    destination_city: str,
    departure_date: str,
    adults: int = 1,
) -> List[TransportOption]:
    """Search flights via Amadeus API.

    Returns real Amadeus results when available.
    Falls back to mock data only for *known* Indian domestic routes when the
    Amadeus API itself is unavailable (auth failure, network error, etc.).
    Returns an empty list when a city name cannot be resolved to an IATA code
    so that callers know no results were found rather than showing fake data.
    """
    origin_code      = city_to_iata(origin_city)
    destination_code = city_to_iata(destination_city)

    # If either city is unknown, we cannot query Amadeus reliably.
    if not origin_code or not destination_code:
        unknown = []
        if not origin_code:
            unknown.append(f"origin='{origin_city}'")
        if not destination_code:
            unknown.append(f"destination='{destination_city}'")
        logger.warning(
            "Cannot resolve IATA code for %s -- returning no flights",
            ", ".join(unknown),
        )
        return []

    async with httpx.AsyncClient(timeout=30) as client:
        token = await _get_amadeus_token(client)
        if not token:
            # Auth failure is an infra issue; fall back to mock only for known domestic routes
            key = frozenset([origin_code, destination_code])
            if key in _ROUTE_DURATIONS:
                logger.warning("Amadeus auth unavailable -- using mock flight data for known route")
                return _mock_flights(origin_city, destination_city, origin_code, destination_code, departure_date, adults)
            logger.warning("Amadeus auth unavailable and route is unknown -- returning no flights")
            return []

        try:
            resp = await client.get(
                f"{AMADEUS_BASE_URL}/v2/shopping/flight-offers",
                params={
                    "originLocationCode":      origin_code,
                    "destinationLocationCode": destination_code,
                    "departureDate":           departure_date,
                    "adults":                  adults,
                    "max":                     5,
                    "currencyCode":            "INR",
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=25,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("Amadeus search failed: %s", exc)
            # Fall back to mock only for known Indian domestic routes
            key = frozenset([origin_code, destination_code])
            if key in _ROUTE_DURATIONS:
                logger.info("Using mock data for known domestic route %s->%s", origin_code, destination_code)
                return _mock_flights(origin_city, destination_city, origin_code, destination_code, departure_date, adults)
            logger.info("Amadeus failed and route %s->%s is not in mock table -- returning no flights", origin_code, destination_code)
            return []

    offers = data.get("data", [])
    logger.info("Amadeus returned %d offer(s) for %s->%s", len(offers), origin_code, destination_code)

    if not offers:
        logger.info("Amadeus returned 0 offers for %s->%s", origin_code, destination_code)
        return []

    return _parse_amadeus_offers(offers, origin_city, destination_city)
