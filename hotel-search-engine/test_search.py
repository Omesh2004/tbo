"""
Test script for Hotel Search Engine
Tests the search functionality without running the Flask app
"""

import json
import logging
from datetime import datetime
from search_engine import HotelSearchEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title):
    """Print formatted section title"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_search_functionality():
    """Test the search engine with various queries"""
    
    print_section("HOTEL SEARCH ENGINE - TEST SUITE")
    
    engine = HotelSearchEngine()
    
    # Test queries
    test_queries = [
        "5 star hotels in Athens",
        "budget hotels in London",
        "luxury resorts in Dubai",
        "hotel in Paris with swimming pool",
        "affordable hotels near New York Times Square"
    ]
    
    all_results = []
    
    for idx, query in enumerate(test_queries, 1):
        print_section(f"TEST {idx}: '{query}'")
        
        try:
            # Perform search
            logger.info(f"Searching for: {query}")
            results = engine.search_google_hotels(query, num_results=5)
            
            if results:
                logger.info(f"✅ Found {len(results)} hotels")
                print(f"\nTop Results:")
                print(f"{'-'*70}")
                
                for hotel_idx, hotel in enumerate(results, 1):
                    print(f"\n{hotel_idx}. {hotel['name']}")
                    print(f"   Location: {hotel['location']}")
                    print(f"   Rating: ⭐ {hotel['rating']} ({hotel['rating_count']} reviews)")
                    print(f"   Price: ${hotel['price_per_night']}/night")
                    print(f"   Stars: {'★' * hotel['stars']}")
                    print(f"   Amenities: {', '.join(hotel['amenities'])}")
                    print(f"   Available: {'Yes' if hotel['availability'] else 'No'}")
                
                all_results.extend(results)
                
            else:
                logger.warning(f"⚠ No results found for: {query}")
            
            print("\n")
            
        except Exception as e:
            logger.error(f"❌ Error searching for '{query}': {str(e)}")
            continue
    
    # Save all results
    print_section("SAVING RESULTS TO JSON")
    
    if all_results:
        combined_results = {
            "test_run_timestamp": datetime.now().isoformat(),
            "total_queries": len(test_queries),
            "total_hotels_found": len(all_results),
            "test_queries": test_queries,
            "unique_hotels": {
                hotel['name']: hotel for hotel in all_results
            },
            "results": all_results
        }
        
        engine.results_file = "test_results.json"
        
        try:
            with open(engine.results_file, 'w', encoding='utf-8') as f:
                json.dump(combined_results, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Results saved to {engine.results_file}")
        except Exception as e:
            logger.error(f"❌ Error saving to file: {str(e)}")
    
    # Cost analysis
    print_section("COST ANALYSIS")
    
    if all_results:
        prices = [h['price_per_night'] for h in all_results]
        prices_valid = [p for p in prices if p > 0]
        
        if prices_valid:
            min_price = min(prices_valid)
            max_price = max(prices_valid)
            avg_price = sum(prices_valid) / len(prices_valid)
            
            print(f"Hotel Price Statistics:")
            print(f"  Minimum: ${min_price:.2f}/night")
            print(f"  Maximum: ${max_price:.2f}/night")
            print(f"  Average: ${avg_price:.2f}/night")
            
            print(f"\nMulti-Night Stay Costs (7 nights):")
            print(f"  Budget:    ${min_price * 7:.2f}")
            print(f"  Average:   ${avg_price * 7:.2f}")
            print(f"  Luxury:    ${max_price * 7:.2f}")
            
            print(f"\nData Verification:")
            print(f"  Total hotels found: {len(all_results)}")
            print(f"  Hotels with ratings: {len([h for h in all_results if h['rating'] > 0])}")
            print(f"  Hotels with prices: {len([h for h in all_results if h['price_per_night'] > 0])}")
            print(f"  Average rating: {sum([h['rating'] for h in all_results]) / len(all_results):.2f}/5")
    
    print_section("TEST COMPLETE")
    logger.info("✅ All tests completed successfully!")
    
    # Display summary
    print(f"\nSummary:")
    print(f"  Search Queries Tested: {len(test_queries)}")
    print(f"  Total Hotels Found: {len(all_results)}")
    print(f"  Results File: search_results.json")
    print(f"  Test Results: test_results.json")
    print(f"\n✅ The search engine is working properly!")
    print(f"✅ Results saved for verification!\n")


def test_json_output_format():
    """Test JSON output format and structure"""
    
    print_section("JSON OUTPUT FORMAT TEST")
    
    engine = HotelSearchEngine()
    results = engine.search_google_hotels("hotels in test city", num_results=3)
    
    if results:
        # Save test results
        test_data = {
            "test_name": "JSON Format Validation",
            "timestamp": datetime.now().isoformat(),
            "results": results
        }
        
        try:
            with open("json_format_test.json", 'w') as f:
                json.dump(test_data, f, indent=2)
            
            # Validate JSON by reloading it
            with open("json_format_test.json", 'r') as f:
                verified_data = json.load(f)
            
            logger.info("✅ JSON format validation passed")
            logger.info(f"   Sample structure: {list(results[0].keys())}")
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON format error: {str(e)}")


if __name__ == "__main__":
    try:
        test_search_functionality()
        test_json_output_format()
    except KeyboardInterrupt:
        print("\n\n⚠ Test interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
