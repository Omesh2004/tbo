"""
Hotel Search Engine API
Main Flask application for serving hotel search functionality
"""

import json
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from search_engine import HotelSearchEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize search engine
search_engine = HotelSearchEngine()

# Configuration
MAX_RESULTS = int(os.getenv('MAX_RESULTS', 10))
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Hotel Search Engine',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/search', methods=['POST'])
def search_hotels():
    """
    Search for hotels based on query
    
    Expected JSON body:
    {
        "query": "5 star hotels in Athens",
        "num_results": 10
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing "query" parameter',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        query = data.get('query', '').strip()
        num_results = int(data.get('num_results', MAX_RESULTS))
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Query cannot be empty',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        if num_results < 1 or num_results > 50:
            num_results = MAX_RESULTS
        
        logger.info(f"Search request: query='{query}', num_results={num_results}")
        
        # Perform search
        results = search_engine.search_google_hotels(query, num_results)
        
        # Save results to file
        file_path = search_engine.save_results(results, query)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'total_results': len(results),
            'results': results,
            'results_file': file_path,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except json.JSONDecodeError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid JSON in request body',
            'timestamp': datetime.now().isoformat()
        }), 400
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/search/simple', methods=['GET'])
def search_hotels_simple():
    """
    Simple GET endpoint for hotel search
    
    Query parameters:
    - query: search query (required)
    - num_results: number of results (optional, default: MAX_RESULTS)
    
    Example: /search/simple?query=hotels+in+Athens&num_results=5
    """
    try:
        query = request.args.get('query', '').strip()
        num_results = int(request.args.get('num_results', MAX_RESULTS))
        
        if not query:
            return jsonify({
                'status': 'error',
                'message': 'Missing "query" parameter',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        if num_results < 1 or num_results > 50:
            num_results = MAX_RESULTS
        
        logger.info(f"Simple search request: query='{query}', num_results={num_results}")
        
        # Perform search
        results = search_engine.search_google_hotels(query, num_results)
        
        # Save results to file
        file_path = search_engine.save_results(results, query)
        
        return jsonify({
            'status': 'success',
            'query': query,
            'total_results': len(results),
            'results': results,
            'results_file': file_path,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 400
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/results', methods=['GET'])
def get_latest_results():
    """Get the latest search results saved in file"""
    try:
        results = search_engine.load_results()
        
        if not results:
            return jsonify({
                'status': 'error',
                'message': 'No previous search results found',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': results,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving results: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/v1/hotels', methods=['POST'])
def api_v1_search():
    """
    API v1 endpoint for hotel search
    Compatible with external AI agents
    
    Expected JSON:
    {
        "query": "luxury hotels in Paris",
        "max_results": 10,
        "min_rating": 3.5,
        "max_price": 500
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'code': 'MISSING_QUERY',
                'message': 'Query parameter is required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        query = data.get('query', '').strip()
        max_results = int(data.get('max_results', MAX_RESULTS))
        min_rating = float(data.get('min_rating', 0))
        max_price = float(data.get('max_price', float('inf')))
        
        logger.info(f"API v1 search: query='{query}', max_results={max_results}")
        
        # Perform search
        results = search_engine.search_google_hotels(query, max_results)
        
        # Filter results
        filtered_results = [
            h for h in results
            if h['rating'] >= min_rating and h['price_per_night'] <= max_price
        ]
        
        # Save results
        file_path = search_engine.save_results(results, query)
        
        return jsonify({
            'status': 'success',
            'code': 'SEARCH_COMPLETE',
            'data': {
                'query': query,
                'filters_applied': {
                    'min_rating': min_rating,
                    'max_price': max_price
                },
                'total_found': len(results),
                'total_filtered': len(filtered_results),
                'hotels': filtered_results,
                'results_file': file_path,
                'cost_analysis': _analyze_costs(filtered_results)
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"API v1 error: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'code': 'INTERNAL_ERROR',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def _analyze_costs(hotels: list) -> dict:
    """Analyze cost metrics from hotel list"""
    if not hotels:
        return {
            'min_price': 0,
            'max_price': 0,
            'avg_price': 0,
            'median_price': 0,
            'price_range': '$0 - $0',
            'total_nights': 7,
            'estimated_total_cost_7nights': 0
        }
    
    prices = [h['price_per_night'] for h in hotels if h.get('price_per_night', 0) > 0]
    prices.sort()
    
    min_price = min(prices) if prices else 0
    max_price = max(prices) if prices else 0
    avg_price = sum(prices) / len(prices) if prices else 0
    median_price = prices[len(prices)//2] if prices else 0
    
    # Standard 7-night stay
    nights = 7
    min_total = min_price * nights
    max_total = max_price * nights
    avg_total = avg_price * nights
    
    return {
        'min_price': round(min_price, 2),
        'max_price': round(max_price, 2),
        'avg_price': round(avg_price, 2),
        'median_price': round(median_price, 2),
        'price_range': f'${round(min_price, 2)} - ${round(max_price, 2)}',
        'total_nights': nights,
        'estimated_total_cost_7nights': {
            'minimum': round(min_total, 2),
            'maximum': round(max_total, 2),
            'average': round(avg_total, 2)
        },
        'currency': 'USD',
        'sample_cost_calculations': {
            f"{nights}_nights": {
                'budget_option': round(min_total, 2),
                'mid_range': round((min_total + max_total) / 2, 2),
                'luxury_option': round(max_total, 2)
            }
        }
    }


@app.route('/', methods=['GET'])
def index():
    """Welcome endpoint with API documentation"""
    return jsonify({
        'service': 'Hotel Search Engine API',
        'version': '1.0.0',
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'health_check': {
                'method': 'GET',
                'path': '/health',
                'description': 'Check service health'
            },
            'search_post': {
                'method': 'POST',
                'path': '/search',
                'description': 'Search for hotels (JSON body)',
                'example': {
                    'query': '5 star hotels in Athens',
                    'num_results': 10
                }
            },
            'search_get': {
                'method': 'GET',
                'path': '/search/simple?query=hotels+in+Athens&num_results=5',
                'description': 'Simple hotel search via query parameters'
            },
            'latest_results': {
                'method': 'GET',
                'path': '/results',
                'description': 'Get latest search results from file'
            },
            'api_v1': {
                'method': 'POST',
                'path': '/api/v1/hotels',
                'description': 'API v1 endpoint with advanced filtering and cost analysis',
                'example': {
                    'query': 'luxury hotels in Paris',
                    'max_results': 10,
                    'min_rating': 3.5,
                    'max_price': 500
                }
            }
        },
        'notes': 'Results are saved to search_results.json for verification'
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'path': request.path,
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    logger.info(f"Starting Hotel Search Engine API on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
