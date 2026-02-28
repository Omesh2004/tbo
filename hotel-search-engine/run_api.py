"""
Hotel Search Engine API - Simple Runner
Start API, test it, and display results - all in one command
"""

import subprocess
import time
import requests
import json
import sys
from datetime import datetime

def print_header(title):
    """Print formatted header"""
    print("\n" + "╔" + "═"*78 + "╗")
    print("║" + title.center(78) + "║")
    print("╚" + "═"*78 + "╝\n")

def start_api():
    """Start the Flask API in background"""
    print_header("STARTING API SERVER")
    print("Starting Hotel Search Engine API...")
    
    try:
        # Start the app in background
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print(f"✓ API process started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"✗ Error starting API: {e}")
        return None

def wait_for_api(timeout=10):
    """Wait for API to be ready"""
    print("\n⏳ Waiting for API to start...", end='')
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            if response.status_code == 200:
                print(" ✓")
                return True
        except:
            pass
        
        time.sleep(0.5)
        print(".", end='', flush=True)
    
    print(" ✗")
    return False

def test_api():
    """Test the API with sample requests"""
    print_header("TESTING API ENDPOINTS")
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "endpoint": "/health",
            "data": None
        },
        {
            "name": "Simple Search",
            "method": "POST",
            "endpoint": "/search",
            "data": {
                "query": "5 star hotels in Athens",
                "num_results": 3
            }
        },
        {
            "name": "Advanced Search with Cost Analysis",
            "method": "POST",
            "endpoint": "/api/v1/hotels",
            "data": {
                "query": "luxury hotels in Paris",
                "max_results": 5,
                "min_rating": 4.0,
                "max_price": 500
            }
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\n{test['name']}")
        print("-" * 78)
        
        try:
            url = f"http://localhost:5000{test['endpoint']}"
            
            if test['method'] == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json=test['data'], timeout=5)
            
            print(f"✓ Request successful (Status: {response.status_code})")
            
            data = response.json()
            
            # Display results
            if "results" in data:
                hotels = data.get("results", [])
                print(f"✓ Found {len(hotels)} hotels")
                
                if hotels:
                    hotel = hotels[0]
                    print(f"  Sample: {hotel.get('name')} - ⭐{hotel.get('rating')} | ${hotel.get('price_per_night')}/night")
            
            elif "data" in data and "hotels" in data["data"]:
                hotels = data["data"]["hotels"]
                print(f"✓ Found {len(hotels)} hotels")
                
                if "cost_analysis" in data["data"]:
                    costs = data["data"]["cost_analysis"]
                    print(f"✓ Cost Analysis:")
                    print(f"    Price Range: {costs.get('price_range', 'N/A')}")
                    if "estimated_total_cost_7nights" in costs:
                        total = costs["estimated_total_cost_7nights"]
                        print(f"    7-Night Stay: ${total.get('average', 'N/A'):.2f} (avg)")
            
            results.append((test['name'], True, None))
        
        except requests.exceptions.ConnectionError:
            print(f"✗ Cannot connect to API")
            results.append((test['name'], False, "Connection refused"))
        except Exception as e:
            print(f"✗ Error: {str(e)[:100]}")
            results.append((test['name'], False, str(e)))
    
    # Print summary
    print("\n" + "="*78)
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! API is working correctly.")
    else:
        print(f"⚠ {total - passed} test(s) failed.")

def display_next_steps():
    """Display next steps"""
    print_header("NEXT STEPS")
    
    print("""
1. API IS RUNNING AT: http://localhost:5000

2. TEST WITH CURL:
   curl -X POST http://localhost:5000/api/v1/hotels \\
     -H "Content-Type: application/json" \\
     -d '{"query": "hotels in Athens", "max_results": 5}'

3. PYTHON INTEGRATION:
   import requests
   response = requests.post('http://localhost:5000/api/v1/hotels',
       json={'query': 'luxury hotels in Paris'})
   data = response.json()
   hotels = data['data']['hotels']

4. VIEW API DOCUMENTATION:
   python API_GUIDE.py

5. STOP THE API:
   Press Ctrl+C in this terminal

6. SAMPLE QUERIES TO TRY:
   - "5 star hotels in Athens"
   - "budget hotels in London"
   - "luxury resorts in Dubai"
   - "hotels near Eiffel Tower Paris"
   - "affordable accommodation in Tokyo"

7. USE IN YOUR PROJECT:
   - See client_example.py for full integration examples
   - See README.md for complete API documentation
   - Use test_api.py to run comprehensive tests

═══════════════════════════════════════════════════════════════════════════
    
API Documentation: http://localhost:5000/
View all endpoints and examples at root path

""")

def main():
    """Main runner"""
    print_header("HOTEL SEARCH ENGINE - API QUICK START")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Start API
    api_process = start_api()
    if not api_process:
        print("\n✗ Failed to start API")
        return
    
    # Wait for API to be ready
    if not wait_for_api():
        print("\n✗ API did not start within timeout")
        api_process.terminate()
        return
    
    # Test API
    test_api()
    
    # Display next steps
    display_next_steps()
    
    # Keep running
    try:
        print("API is running. Press Ctrl+C to stop...\n")
        api_process.wait()
    except KeyboardInterrupt:
        print("\n\nStopping API...")
        api_process.terminate()
        api_process.wait()
        print("✓ API stopped")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
