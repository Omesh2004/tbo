"""
Hotel Search Engine API Test Client
Tests the Flask API with JSON requests and verifies responses
"""

import json
import requests
from datetime import datetime
from time import sleep

# Configuration
API_URL = "http://localhost:5000"
TIMEOUT = 5

class APITester:
    """Test the Hotel Search Engine API"""
    
    def __init__(self, base_url=API_URL):
        self.base_url = base_url
        self.results = []
    
    def test_health(self):
        """Test the /health endpoint"""
        print("\n" + "="*70)
        print("TEST 1: Health Check Endpoint")
        print("="*70)
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=TIMEOUT)
            print(f"Status Code: {response.status_code}")
            print("Request: GET /health")
            print("Response JSON:")
            print(json.dumps(response.json(), indent=2))
            self.results.append(("Health Check", response.status_code == 200))
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Health Check", False))
            return False
    
    def test_search_get(self):
        """Test the /search/simple GET endpoint"""
        print("\n" + "="*70)
        print("TEST 2: Simple Search (GET) Endpoint")
        print("="*70)
        
        params = {
            'query': '5 star hotels in Athens',
            'num_results': 5
        }
        
        print(f"Request: GET /search/simple")
        print(f"Query Parameters: {json.dumps(params, indent=2)}")
        
        try:
            response = requests.get(
                f"{self.base_url}/search/simple",
                params=params,
                timeout=TIMEOUT
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\nResponse JSON:")
                print(json.dumps(data, indent=2)[:500] + "...")  # First 500 chars
                
                # Validate response structure
                required_fields = ['status', 'query', 'total_results', 'results']
                has_all_fields = all(field in data for field in required_fields)
                
                self.results.append(("Search GET", has_all_fields))
                return has_all_fields
            else:
                print(f"Response: {response.text}")
                self.results.append(("Search GET", False))
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Search GET", False))
            return False
    
    def test_search_post(self):
        """Test the /search POST endpoint"""
        print("\n" + "="*70)
        print("TEST 3: Hotel Search (POST) Endpoint")
        print("="*70)
        
        payload = {
            'query': 'budget hotels in London',
            'num_results': 5
        }
        
        print(f"Request: POST /search")
        print("JSON Body:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = requests.post(
                f"{self.base_url}/search",
                json=payload,
                timeout=TIMEOUT
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\nResponse JSON (first 500 chars):")
                print(json.dumps(data, indent=2)[:500] + "...")
                
                # Validate response structure
                required_fields = ['status', 'query', 'total_results', 'results']
                has_all_fields = all(field in data for field in required_fields)
                
                self.results.append(("Search POST", has_all_fields))
                return has_all_fields
            else:
                print(f"Response: {response.text[:200]}")
                self.results.append(("Search POST", False))
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Search POST", False))
            return False
    
    def test_api_v1(self):
        """Test the /api/v1/hotels endpoint (advanced with filtering)"""
        print("\n" + "="*70)
        print("TEST 4: API v1 - Advanced Search with Filtering")
        print("="*70)
        
        payload = {
            'query': 'luxury hotels in Paris',
            'max_results': 10,
            'min_rating': 4.0,
            'max_price': 500
        }
        
        print(f"Request: POST /api/v1/hotels")
        print("JSON Body:")
        print(json.dumps(payload, indent=2))
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/hotels",
                json=payload,
                timeout=TIMEOUT
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\nResponse JSON (first 800 chars):")
                response_str = json.dumps(data, indent=2)
                print(response_str[:800] + "...")
                
                # Validate response structure
                required_fields = ['status', 'data']
                has_structure = all(field in data for field in required_fields)
                
                if has_structure and 'data' in data:
                    data_fields = ['query', 'hotels', 'cost_analysis']
                    has_data_fields = all(field in data['data'] for field in data_fields)
                    
                    print("\n✅ Response has cost_analysis with:")
                    if 'cost_analysis' in data['data']:
                        analysis = data['data']['cost_analysis']
                        print(f"  - Price Range: {analysis.get('price_range')}")
                        print(f"  - 7-Night Cost: ${analysis.get('estimated_total_cost_7nights', {}).get('average', 'N/A')}")
                    
                    self.results.append(("API v1", has_data_fields))
                    return has_data_fields
                else:
                    self.results.append(("API v1", False))
                    return False
            else:
                print(f"Response: {response.text[:200]}")
                self.results.append(("API v1", False))
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("API v1", False))
            return False
    
    def test_results_endpoint(self):
        """Test the /results endpoint"""
        print("\n" + "="*70)
        print("TEST 5: Get Latest Results Endpoint")
        print("="*70)
        
        print(f"Request: GET /results")
        
        try:
            response = requests.get(
                f"{self.base_url}/results",
                timeout=TIMEOUT
            )
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\nResponse JSON (first 500 chars):")
                print(json.dumps(data, indent=2)[:500] + "...")
                
                # Validate response structure
                has_status = 'status' in data
                self.results.append(("Get Results", has_status))
                return has_status
            elif response.status_code == 404:
                print("✅ No previous results (expected on first run)")
                self.results.append(("Get Results", True))
                return True
            else:
                print(f"Response: {response.text[:200]}")
                self.results.append(("Get Results", False))
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Get Results", False))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        for test_name, passed in self.results:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status}: {test_name}")
        
        passed = sum(1 for _, p in self.results if p)
        total = len(self.results)
        
        print(f"\nResult: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All API tests passed! The API is working correctly.")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        
        print("\n" + "="*70)
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*70)
        print("HOTEL SEARCH ENGINE API - TEST SUITE")
        print("="*70)
        print(f"Testing API at: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run tests
        self.test_health()
        sleep(1)
        self.test_search_get()
        sleep(1)
        self.test_search_post()
        sleep(1)
        self.test_api_v1()
        sleep(1)
        self.test_results_endpoint()
        
        # Print summary
        self.print_summary()


if __name__ == "__main__":
    print("\n⏳ Starting API tests...")
    print("Make sure the API is running: python app.py")
    print("Or with Docker: docker-compose up\n")
    
    tester = APITester()
    
    try:
        tester.run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API")
        print(f"Make sure the API is running at {API_URL}")
        print("\nStart API with:")
        print("  cd hotel-search-engine")
        print("  python app.py")
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
