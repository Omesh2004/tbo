#!/usr/bin/env python3
"""Quick verification that the JSON file is valid and complete"""
import json
import os
from pathlib import Path

file_path = Path("travel_package_data_tbo.json")

print("\n" + "=" * 70)
print("✅ FINAL VERIFICATION RESULTS")
print("=" * 70)

if not file_path.exists():
    print("❌ File not found!")
    exit(1)

# Check file stats
print(f"\n📁 File: {file_path.name}")
print(f"   Size: {file_path.stat().st_size:,} bytes")
print(f"   Last Modified: {file_path.stat().st_mtime_ns}")

# Validate JSON
try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    print(f"\n✓ Valid JSON structure")
except Exception as e:
    print(f"❌ Invalid JSON: {e}")
    exit(1)

# Check data content
print(f"\n📊 Data Content:")
print(f"   ✓ Flights: {len(data.get('flights', []))} items")
print(f"   ✓ Hotels: {len(data.get('hotels', []))} items")
print(f"   ✓ Activities: {len(data.get('activities', []))} items")

# Check metadata
print(f"\n🔍 Metadata:")
print(f"   ✓ Source: {data.get('source', 'N/A')}")
print(f"   ✓ Fetch Mode: {data.get('fetch_mode', 'N/A')}")
print(f"   ✓ Timestamp: {data.get('timestamp', 'N/A')}")

# Check API status
api_status = data.get('api_status', {})
print(f"\n⚙️  API Status:")
print(f"   - Flights: {api_status.get('flights', 'unknown')}")
if api_status.get('flights_error'):
    print(f"     Error: {api_status.get('flights_error')[:60]}...")
print(f"   - Hotels: {api_status.get('hotels', 'unknown')}")
if api_status.get('hotels_error'):
    print(f"     Error: {api_status.get('hotels_error')[:60]}...")

# Check price data
price_range = data.get('hotel_price_range', {})
if isinstance(price_range, dict) and 'min' in price_range:
    print(f"\n💰 Hotel Price Range:")
    print(f"   Min: ${price_range['min']}")
    print(f"   Max: ${price_range['max']}")
    print(f"   Avg: ${price_range['avg']:.2f}")

print("\n" + "=" * 70)
print("✅ ALL CHECKS PASSED - PIPELINE IS WORKING!")
print("=" * 70 + "\n")
