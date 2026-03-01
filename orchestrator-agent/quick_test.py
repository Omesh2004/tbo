#!/usr/bin/env python3
"""Quick test of orchestrator API"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 80)
print("QUICK API TEST - Orchestrator Agent")
print("=" * 80)

# Test 1: Health check
print("\n[TEST 1] Health Check")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"✗ Failed: {response.text}")
except Exception as e:
    print(f"✗ Error: {str(e)}")

# Test 2: Simple Query
print("\n[TEST 2] Simple Query (Should use Phi4)")
print("Query: 'What is the capital of France?'")
try:
    response = requests.post(
        f"{BASE_URL}/query",
        json={
            "query": "What is the capital of France?",
            "user_id": "test_user_1"
        },
        timeout=300  # 5 minute timeout
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Model Used: {data.get('model_used')}")
        print(f"✓ Complexity: {data.get('complexity_level')}")
        print(f"✓ Response: {data.get('response')[:200]}...")
    else:
        print(f"✗ Error: {response.text}")
except requests.exceptions.Timeout:
    print(f"✗ Request timed out after 300 seconds")
except Exception as e:
    print(f"✗ Error: {str(e)}")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)
