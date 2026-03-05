"""
Quick test script — run after starting the server with:
    uvicorn app.main:app --reload --port 8001

Usage:
    python test_api.py
"""
import asyncio
import httpx
import json

BASE = "http://localhost:8001"

TEST_CASES = [
    {
        "label": "Kolkata → Delhi (sort by price)",
        "payload": {"origin": "Kolkata", "destination": "Delhi", "date": "2026-03-20", "sort_by": "price"},
    },
    {
        "label": "Mumbai → Bangalore (sort by duration)",
        "payload": {"origin": "Mumbai", "destination": "Bangalore", "date": "2026-03-25", "sort_by": "duration"},
    },
    {
        "label": "Delhi → Jaipur (bus + train only route)",
        "payload": {"origin": "Delhi", "destination": "Jaipur", "date": "2026-03-22"},
    },
    {
        "label": "Health check",
        "endpoint": "/health",
        "method": "GET",
    },
]


async def run_tests():
    async with httpx.AsyncClient(timeout=60) as client:
        for case in TEST_CASES:
            print(f"\n{'='*60}")
            print(f"TEST: {case['label']}")
            print("="*60)
            try:
                method = case.get("method", "POST")
                endpoint = case.get("endpoint", "/api/search-transport")
                if method == "GET":
                    resp = await client.get(f"{BASE}{endpoint}")
                else:
                    resp = await client.post(f"{BASE}{endpoint}", json=case["payload"])

                print(f"Status: {resp.status_code}")
                data = resp.json()

                if "transport_options" in data:
                    print(f"Total results: {data['total_results']}")
                    for opt in data["transport_options"]:
                        t = opt["type"].upper()
                        print(
                            f"  [{t}] {opt['provider']:30s}  "
                            f"{opt['departure_time'][11:16]} → {opt['arrival_time'][11:16]}  "
                            f"({opt['duration']:10s})  INR {opt['price']:.0f}"
                        )
                else:
                    print(json.dumps(data, indent=2))

            except Exception as e:
                print(f"ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(run_tests())
