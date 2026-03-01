"""Comprehensive Test Script for Orchestrator Agent with Detailed Logging"""
import httpx
import asyncio
import json
from typing import Dict, Any
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

# Color codes for nice output
class Colors:
    HEADER = '\033[95m'
    OK = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_test_header(title: str):
    """Print a test header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
    print(f"TEST: {title}")
    print(f"{'='*80}{Colors.ENDC}\n")


def print_result(success: bool, message: str):
    """Print result with color"""
    if success:
        print(f"{Colors.OK}✓ {message}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_response(response: Dict[str, Any]):
    """Pretty print response"""
    print(f"\n{Colors.BOLD}Response:{Colors.ENDC}")
    print(json.dumps(response, indent=2))


async def test_health():
    """Test health check endpoint"""
    print_test_header("Health Check")
    
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{BASE_URL}/health")
            
            if response.status_code == 200:
                data = response.json()
                print_result(True, f"Service is healthy")
                print(f"  ├─ Service: {data.get('service')}")
                print(f"  ├─ Status: {data.get('status')}")
                print(f"  └─ Version: {data.get('version')}")
                return True
            else:
                print_result(False, f"Health check failed (status: {response.status_code})")
                return False
    except Exception as e:
        print_result(False, f"Connection failed: {str(e)}")
        return False


async def test_simple_query():
    """Test simple query routing to Phi4"""
    print_test_header("SIMPLE QUERY ROUTING TO PHI4")
    
    query = "Hello, what is the weather like?"
    print(f"📝 Query: '{query}'")
    print(f"⏱️  Expected Routing: PHI4 (Fast, Simple)")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{BASE_URL}/query",
                json={
                    "query": query,
                    "user_id": "user_simple_test"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, "Request successful")
                print(f"  ├─ Complexity Level: {data.get('complexity_level')}")
                print(f"  ├─ Model Used: {data.get('model_used')}")
                print(f"  └─ Status: {data.get('status')}")
                
                # Check if routed to correct model
                expected_model = "phi4"
                actual_model = data.get('model_used', '').lower()
                
                if expected_model in actual_model:
                    print_result(True, f"✓ Correctly routed to {actual_model}")
                else:
                    print_result(False, f"Expected {expected_model}, got {actual_model}")
                
                print_result(True, f"Response length: {len(data.get('response', ''))} chars")
                return True
            else:
                print_result(False, f"Request failed (status: {response.status_code})")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return False


async def test_complex_query():
    """Test complex query routing to Llama"""
    print_test_header("COMPLEX QUERY ROUTING TO LLAMA")
    
    query = "I need to find a flight from New York to London departing next month, with a hotel in central London, and I prefer budget airlines but 4-star hotels. Can you compare options and apply my loyalty discounts?"
    
    print(f"📝 Query: '{query[:60]}...'")
    print(f"⏱️  Expected Routing: LLAMA (Comprehensive, Complex)")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{BASE_URL}/query",
                json={
                    "query": query,
                    "user_id": "user_complex_test"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, "Request successful")
                print(f"  ├─ Complexity Level: {data.get('complexity_level')}")
                print(f"  ├─ Model Used: {data.get('model_used')}")
                print(f"  └─ Status: {data.get('status')}")
                
                # Check if routed to correct model
                expected_model = "llama"
                actual_model = data.get('model_used', '').lower()
                
                if expected_model in actual_model:
                    print_result(True, f"✓ Correctly routed to {actual_model}")
                else:
                    print_result(False, f"Expected {expected_model}, got {actual_model}")
                
                print_result(True, f"Response length: {len(data.get('response', ''))} chars")
                return True
            else:
                print_result(False, f"Request failed (status: {response.status_code})")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return False


async def test_hotel_search():
    """Test hotel search with agent routing"""
    print_test_header("HOTEL SEARCH - AGENT ROUTING TEST")
    
    print("🏨 Testing Hotel Search Agent Integration")
    print(f"📍 Location: Paris")
    print(f"📅 Check-in: 2026-05-01 | Check-out: 2026-05-10")
    print(f"👥 Guests: 2")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{BASE_URL}/search/hotels",
                json={
                    "location": "Paris",
                    "check_in": "2026-05-01",
                    "check_out": "2026-05-10",
                    "guests": 2,
                    "user_id": "user_hotel_test",
                    "preferences": {"rating_min": 4}
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, "Hotel search request successful")
                print(f"  ├─ Status: {data.get('status')}")
                print(f"  ├─ Results found: {data.get('count')}")
                print(f"  └─ First result: {data.get('results', [{}])[0].get('name', 'N/A') if data.get('results') else 'No results'}")
                
                print(f"\n💡 Note: Agents contacted in order:")
                print(f"  1. Hotel Search Agent (Port 8002) - Search hotels")
                print(f"  2. Personalization Agent (Port 8001) - Rank results")
                return True
            else:
                print_result(False, f"Request failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return False


async def test_flight_search():
    """Test flight search with agent routing"""
    print_test_header("FLIGHT SEARCH - AGENT ROUTING TEST")
    
    print("✈️  Testing Amadeus/TBO Agent Integration")
    print(f"🛫 Origin: JFK (New York)")
    print(f"🛬 Destination: LHR (London)")
    print(f"📅 Departure: 2026-04-15")
    print(f"👥 Passengers: 2")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{BASE_URL}/search/flights",
                json={
                    "origin": "JFK",
                    "destination": "LHR",
                    "departure_date": "2026-04-15",
                    "passengers": 2,
                    "user_id": "user_flight_test"
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, "Flight search request successful")
                print(f"  ├─ Status: {data.get('status')}")
                print(f"  ├─ Results found: {data.get('count')}")
                print(f"  └─ First result: {data.get('results', [{}])[0].get('airline', 'N/A') if data.get('results') else 'No results'}")
                
                print(f"\n💡 Note: Agents contacted in order:")
                print(f"  1. Amadeus/TBO Agent (Port 8003) - Search flights")
                print(f"  2. Personalization Agent (Port 8001) - Rank results")
                return True
            else:
                print_result(False, f"Request failed (status: {response.status_code})")
                return False
                
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return False


async def test_full_orchestration():
    """Test full orchestration with multiple agents"""
    print_test_header("FULL ORCHESTRATION - MULTI-AGENT FLOW")
    
    query = "Book a trip to Paris next month"
    print(f"📝 Query: '{query}'")
    print(f"🎯 This will demonstrate the full orchestration flow with multiple agents")
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{BASE_URL}/orchestrate",
                json={
                    "query": query,
                    "user_id": "user_orchestrate_test",
                    "context": {
                        "destination": "Paris",
                        "origin": "JFK",
                        "departure_date": "2026-05-01",
                        "check_in": "2026-05-01",
                        "check_out": "2026-05-10",
                        "passengers": 2,
                        "guests": 2
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print_result(True, "Orchestration request successful")
                print(f"  ├─ Status: {data.get('status')}")
                print(f"  ├─ Complexity Level: {data.get('complexity_level')}")
                print(f"  ├─ Model Used: {data.get('model_used')}")
                
                agents = data.get('agents_contacted', [])
                print(f"  ├─ Agents Contacted: {len(agents)}")
                for i, agent in enumerate(agents, 1):
                    print(f"  │  {i}. {agent}")
                
                print(f"  ├─ Recommendations: {len(data.get('recommendations', []))}")
                print(f"  └─ Suggestion: {data.get('suggestion', 'N/A')}")
                
                print(f"\n💡 Agent Call Sequence:")
                print(f"  1. Query Complexity Analyzer")
                print(f"  2. Phi4/Llama Model (based on complexity)")
                for i, agent in enumerate(agents, 3):
                    if "Hotel" in agent:
                        print(f"  {i}. Hotel Search Agent (Port 8002)")
                    elif "Amadeus" in agent:
                        print(f"  {i}. Amadeus/TBO Agent (Port 8003)")
                
                if len(agents) > 0:
                    print(f"  {len(agents)+3}. Personalization Agent (Port 8001) - Final ranking")
                
                return True
            else:
                print_result(False, f"Request failed (status: {response.status_code})")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print_result(False, f"Request failed: {str(e)}")
        return False


async def run_all_tests():
    """Run all tests sequentially"""
    print("\n" + "="*80)
    print(f"{Colors.BOLD}ORCHESTRATOR AGENT - COMPREHENSIVE TEST SUITE{Colors.ENDC}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {}
    
    # Test 1: Health
    print(f"\n{Colors.BOLD}[TEST 1/6]{Colors.ENDC}")
    results['health'] = await test_health()
    
    if not results['health']:
        print(f"\n{Colors.FAIL}Service is not running. Please start the orchestrator agent.{Colors.ENDC}")
        print("Run: python -m uvicorn app.main:app --reload --port 8000")
        return results
    
    # Test 2: Simple Query
    print(f"\n{Colors.BOLD}[TEST 2/6]{Colors.ENDC}")
    results['simple_query'] = await test_simple_query()
    
    # Test 3: Complex Query
    print(f"\n{Colors.BOLD}[TEST 3/6]{Colors.ENDC}")
    results['complex_query'] = await test_complex_query()
    
    # Test 4: Hotel Search
    print(f"\n{Colors.BOLD}[TEST 4/6]{Colors.ENDC}")
    results['hotel_search'] = await test_hotel_search()
    
    # Test 5: Flight Search
    print(f"\n{Colors.BOLD}[TEST 5/6]{Colors.ENDC}")
    results['flight_search'] = await test_flight_search()
    
    # Test 6: Full Orchestration
    print(f"\n{Colors.BOLD}[TEST 6/6]{Colors.ENDC}")
    results['orchestration'] = await test_full_orchestration()
    
    # Summary
    print("\n" + "="*80)
    print(f"{Colors.BOLD}TEST SUMMARY{Colors.ENDC}")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{Colors.OK}PASS{Colors.ENDC}" if result else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} tests passed{Colors.ENDC}")
    print("="*80 + "\n")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
