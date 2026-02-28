"""
Example client for Hotel Search Engine API
Shows how to use the API endpoints in your applications
"""

import requests
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000"
RESULTS_FILE = "search_results.json"


class HotelSearchClient:
    """Client for Hotel Search Engine API"""
    
    def __init__(self, base_url=API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def simple_search(self, query, num_results=10):
        """
        Simple search using GET endpoint
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            List of hotels or None on error
        """
        try:
            params = {
                'query': query,
                'num_results': num_results
            }
            response = self.session.get(
                f"{self.base_url}/search/simple",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Found {data['total_results']} hotels")
                return data['results']
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.json())
                return None
                
        except Exception as e:
            print(f"Error during search: {e}")
            return None
    
    def search(self, query, num_results=10):
        """
        Search hotels using POST endpoint
        
        Args:
            query: Search query
            num_results: Number of results
            
        Returns:
            Dict with results and metadata
        """
        try:
            payload = {
                'query': query,
                'num_results': num_results
            }
            response = self.session.post(
                f"{self.base_url}/search",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def advanced_search(self, query, max_results=10, min_rating=0, max_price=float('inf')):
        """
        Advanced search with filtering and cost analysis
        
        Args:
            query: Search query
            max_results: Maximum results
            min_rating: Minimum rating filter
            max_price: Maximum price per night
            
        Returns:
            Dict with hotel results and cost analysis
        """
        try:
            payload = {
                'query': query,
                'max_results': max_results,
                'min_rating': min_rating,
                'max_price': max_price
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/hotels",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error: {response.status_code}")
                print(response.json())
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def get_latest_results(self):
        """Get latest search results from file"""
        try:
            response = self.session.get(
                f"{self.base_url}/results",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                print(f"No previous results found")
                return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def display_results(self, results, show_cost_analysis=True):
        """Pretty print hotel results"""
        if not results:
            print("No results to display")
            return
        
        print(f"\n{'='*80}")
        print(f"  HOTEL SEARCH RESULTS")
        print(f"{'='*80}\n")
        
        if isinstance(results, dict) and 'hotels' in results:
            hotels = results['hotels']
            print(f"Found {len(hotels)} hotels\n")
            
            for idx, hotel in enumerate(hotels, 1):
                print(f"{idx}. {hotel['name']}")
                print(f"   Location: {hotel['location']}")
                print(f"   Rating: ⭐ {hotel['rating']}/5 ({hotel['rating_count']} reviews)")
                print(f"   Price: ${hotel['price_per_night']:.2f}/night")
                print(f"   Stars: {'★' * hotel['stars']}{'☆' * (5 - hotel['stars'])}")
                print(f"   Amenities: {', '.join(hotel['amenities'])}")
                print(f"   Available: {'Yes' if hotel['availability'] else 'No'}")
                print()
            
            # Display cost analysis
            if show_cost_analysis and 'cost_analysis' in results:
                self.display_cost_analysis(results['cost_analysis'])
        
        elif isinstance(results, list):
            # Simple list of hotels
            print(f"Found {len(results)} hotels\n")
            
            for idx, hotel in enumerate(results, 1):
                print(f"{idx}. {hotel['name']}")
                print(f"   Location: {hotel['location']}")
                print(f"   Rating: ⭐ {hotel['rating']}/5")
                print(f"   Price: ${hotel['price_per_night']:.2f}/night")
                print(f"   Amenities: {', '.join(hotel['amenities'])}")
                print()
    
    def display_cost_analysis(self, analysis):
        """Display cost analysis information"""
        print(f"{'='*80}")
        print(f"  COST ANALYSIS")
        print(f"{'='*80}\n")
        
        print(f"Price Range: {analysis['price_range']}/night")
        print(f"  Minimum: ${analysis['min_price']:.2f}")
        print(f"  Average: ${analysis['avg_price']:.2f}")
        print(f"  Maximum: ${analysis['max_price']:.2f}")
        
        print(f"\n7-Night Stay Costs:")
        costs = analysis['estimated_total_cost_7nights']
        print(f"  Budget Option:   ${costs['minimum']:.2f}")
        print(f"  Mid-Range:       ${costs['average']:.2f}")
        print(f"  Luxury Option:   ${costs['maximum']:.2f}")
        print()


def example_simple_search():
    """Example: Simple hotel search"""
    print("EXAMPLE 1: Simple Hotel Search")
    print("-" * 50)
    
    client = HotelSearchClient()
    
    # Check if API is running
    if not client.health_check():
        print("⚠️ API is not running. Make sure to start the service first:")
        print("   docker-compose up")
        return
    
    # Search for hotels
    hotels = client.simple_search("5 star hotels in Athens", num_results=5)
    
    if hotels:
        for hotel in hotels:
            print(f"  {hotel['name']}: ⭐{hotel['rating']} | ${hotel['price_per_night']:.2f}/night")


def example_advanced_search():
    """Example: Advanced search with filters and cost analysis"""
    print("\n\nEXAMPLE 2: Advanced Search with Filtering")
    print("-" * 50)
    
    client = HotelSearchClient()
    
    # Search with filters
    results = client.advanced_search(
        query="luxury hotels in Paris",
        max_results=10,
        min_rating=4.0,
        max_price=500
    )
    
    if results:
        client.display_results(results['data'])


def example_filter_results_locally():
    """Example: Filter results locally after retrieval"""
    print("\n\nEXAMPLE 3: Filter Results Locally")
    print("-" * 50)
    
    client = HotelSearchClient()
    
    # Get search results
    full_results = client.advanced_search(
        query="hotels in London",
        max_results=20
    )
    
    if full_results and 'hotels' in full_results['data']:
        hotels = full_results['data']['hotels']
        
        # Filter for high-rated budget hotels
        budget_quality = [h for h in hotels if h['rating'] >= 4.0 and h['price_per_night'] <= 150]
        
        print(f"Found {len(budget_quality)} high-rated budget hotels:")
        for hotel in budget_quality:
            print(f"  {hotel['name']}: ⭐{hotel['rating']} | ${hotel['price_per_night']:.2f}/night")


def example_multi_destination_search():
    """Example: Search multiple destinations"""
    print("\n\nEXAMPLE 4: Multi-Destination Search")
    print("-" * 50)
    
    client = HotelSearchClient()
    destinations = [
        ("luxury hotels in Paris", 4.0),
        ("5 star hotels in Athens", 4.5),
        ("hotels in Dubai near beach", 4.0)
    ]
    
    all_hotels = []
    
    for query, min_rating in destinations:
        print(f"\nSearching: {query}")
        results = client.advanced_search(query, min_rating=min_rating)
        
        if results and 'hotels' in results['data']:
            hotels = results['data']['hotels']
            all_hotels.extend(hotels)
            print(f"  Found {len(hotels)} hotels")
    
    # Sort by rating
    all_hotels.sort(key=lambda x: x['rating'], reverse=True)
    
    print(f"\n\nTop 5 Hotels Across All Destinations:")
    for idx, hotel in enumerate(all_hotels[:5], 1):
        print(f"{idx}. {hotel['name']} ({hotel['location']}): ⭐{hotel['rating']}")


def example_cost_computation():
    """Example: Compute total trip cost"""
    print("\n\nEXAMPLE 5: Trip Cost Computation")
    print("-" * 50)
    
    client = HotelSearchClient()
    
    # Search for hotels
    results = client.advanced_search(
        query="hotels in Barcelona",
        max_results=10,
        max_price=300
    )
    
    if results and 'cost_analysis' in results['data']:
        analysis = results['data']['cost_analysis']
        
        # Compute costs for different trip durations
        nights = [3, 5, 7, 10, 14]
        
        print(f"\nTrip Cost Estimates:")
        print(f"  Hotel Price Range: {analysis['price_range']}/night")
        print()
        
        for night_count in nights:
            min_cost = analysis['min_price'] * night_count
            avg_cost = analysis['avg_price'] * night_count
            max_cost = analysis['max_price'] * night_count
            
            print(f"{night_count}-Night Trip:")
            print(f"  Budget:  ${min_cost:,.2f}")
            print(f"  Average: ${avg_cost:,.2f}")
            print(f"  Luxury:  ${max_cost:,.2f}")
            print()


if __name__ == "__main__":
    print("="*50)
    print("HOTEL SEARCH ENGINE API - CLIENT EXAMPLES")
    print("="*50)
    
    # Run examples
    try:
        example_simple_search()
        # Uncomment to run other examples:
        # example_advanced_search()
        # example_filter_results_locally()
        # example_multi_destination_search()
        # example_cost_computation()
        
        print("\n\n" + "="*50)
        print("Examples completed!")
        print("="*50)
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
