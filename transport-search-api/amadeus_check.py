"""Standalone script: prove Amadeus live API is called and returns real data."""
import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

AMADEUS_BASE = "https://test.api.amadeus.com"
CID = os.getenv("AMADEUS_CLIENT_ID", "3U0F7vgHIN9Xvq31WiQnVVPB6ohfYpT9")
CSE = os.getenv("AMADEUS_CLIENT_SECRET", "g83BzbXv4GzafOCT")


async def main():
    async with httpx.AsyncClient(timeout=20) as c:

        # ── Step 1: OAuth token ──────────────────────────────────────────────
        r = await c.post(
            f"{AMADEUS_BASE}/v1/security/oauth2/token",
            data={"grant_type": "client_credentials", "client_id": CID, "client_secret": CSE},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        body = r.json()
        token = body.get("access_token")
        print(f"[AUTH]   status={r.status_code}  token_chars={len(token or '')}  "
              f"expires_in={body.get('expires_in')}s  "
              f"token_type={body.get('token_type')}")
        if not token:
            print("AUTH FAILED — check credentials")
            return

        # ── Step 2: Flight-offers search (Kolkata -> Kochi / Kerala) ────────
        print("\n[SEARCH] Kolkata (CCU) -> Kochi/Kerala (COK)  date=2026-03-20")
        r2 = await c.get(
            f"{AMADEUS_BASE}/v2/shopping/flight-offers",
            params={
                "originLocationCode": "CCU",
                "destinationLocationCode": "COK",
                "departureDate": "2026-03-20",
                "adults": 1,
                "max": 5,
                "currencyCode": "INR",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        data = r2.json()
        offers = data.get("data", [])
        print(f"         HTTP {r2.status_code}  |  offers returned from Amadeus: {len(offers)}")
        print()

        airline_names = {
            "6E": "IndiGo", "SG": "SpiceJet", "AI": "Air India",
            "UK": "Vistara", "QP": "Akasa Air", "IX": "Air India Expr",
        }

        for i, offer in enumerate(offers, 1):
            itinerary = offer["itineraries"][0]
            segments = itinerary["segments"]
            carrier = segments[0]["carrierCode"]
            fn = f"{carrier}{segments[0]['number']}"
            dep = segments[0]["departure"]["at"]
            arr = segments[-1]["arrival"]["at"]
            dur = itinerary.get("duration", "")
            stops = len(segments) - 1
            price = offer["price"]["grandTotal"]
            cur = offer["price"]["currency"]
            name = airline_names.get(carrier, carrier)
            print(f"  #{i}  {fn:<8}  {name:<16}  dep={dep}  arr={arr}  "
                  f"dur={dur}  stops={stops}  price={price} {cur}")

        print()
        if offers:
            print("[RESULT] Confirmed: live Amadeus data used (NOT mock).")
        else:
            print("[RESULT] No offers returned — mock fallback would be triggered.")


asyncio.run(main())
