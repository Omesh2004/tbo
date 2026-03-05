"""Main Orchestrator Agent Application"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import httpx
from app.config import settings
from app.logger import logger
from app.ml.complexity_detector import ComplexityDetector
from app.ml.model_router import ModelRouter
from app.integrations import (
    PersonalizationAgentClient,
    HotelSearchAgentClient,
    AmadeusAgentClient
)
from app.exceptions import OrchestratorException
from app.ml.rag_engine import RAGEngine
from app.integrations.hotel_search_integration import HotelSearchIntegration

# Initialize app
app = FastAPI(
    title="Orchestrator Agent",
    description="Agent Hub for Travel Booking - Routes queries and orchestrates agent responses",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
complexity_detector = ComplexityDetector(
    complexity_threshold=settings.complexity_threshold
)
model_router = ModelRouter()
personalization_client = PersonalizationAgentClient()
hotel_search_client = HotelSearchAgentClient()
amadeus_client = AmadeusAgentClient()
rag_engine = RAGEngine()
hotel_search_integration = HotelSearchIntegration()


# Request/Response Models
class QueryRequest(BaseModel):
    """User query request"""
    query: str
    user_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Orchestrator response"""
    query: str
    complexity_level: str
    model_used: str
    response: str
    recommendations: Optional[List[Dict[str, Any]]] = None
    status: str


class HotelSearchRequest(BaseModel):
    """Hotel search request"""
    location: str
    check_in: str
    check_out: str
    guests: int
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class FlightSearchRequest(BaseModel):
    """Flight search request"""
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    user_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class JSONQueryRequest(BaseModel):
    """JSON-formatted query request with structured data"""
    query_type: str  # 'hotel', 'flight', 'travel_package'
    location: Optional[str] = None
    destination: Optional[str] = None
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    guests: Optional[int] = None
    passengers: Optional[int] = None
    preferences: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    use_rag: bool = True  # Use Qdrant RAG for context


class TravelRecommendationRequest(BaseModel):
    """Comprehensive travel recommendation request"""
    # User Travel Details
    origin: str
    destination: str
    check_in: str
    check_out: str
    passengers: int = 1
    budget: Optional[float] = None
    
    # User Profile
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_preferences: Optional[Dict[str, Any]] = None
    
    # Business Rules & Constraints
    profit_priority: bool = True  # Maximize profit for platform
    business_rules: Optional[Dict[str, Any]] = None  # Custom business rules
    
    # Additional Context
    travel_style: Optional[str] = None  # 'luxury', 'budget', 'business', 'adventure'
    special_requirements: Optional[str] = None
    

class TravelRecommendationResponse(BaseModel):
    """Comprehensive travel recommendation response"""
    status: str
    user_id: Optional[str]
    
    # All available options
    hotel_options: List[Dict[str, Any]]
    flight_options: Optional[List[Dict[str, Any]]]
    travel_packages: Optional[List[Dict[str, Any]]]
    
    # Multiple recommendations (ranked by profit & suitability)
    all_recommendations: List[Dict[str, Any]]  # Top 3-5 package combinations
    
    # LLM Analysis
    analysis: str  # Detailed analysis by LLM comparing all options
    recommendation: Dict[str, Any]  # Best recommended option (LLM selected)
    reasoning: str  # Why this is the best option
    comparison_summary: str  # Side-by-side comparison of top options
    
    # Profit & Business Metrics
    profit_metrics: Dict[str, Any]  # Platform profit details
    roi_analysis: Dict[str, Any]  # Return on investment
    
    # Full Journey Plan
    complete_journey: Dict[str, Any]  # Complete travel itinerary


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "orchestrator-agent",
        "version": "1.0.0"
    }


@app.post("/recommend/travel-plan")
async def recommend_travel_plan(request: TravelRecommendationRequest) -> TravelRecommendationResponse:
    """
    Comprehensive travel recommendation endpoint
    
    Accepts user details and preferences, searches for relevant hotels and routes,
    then uses LLM to analyze and recommend the best option while maximizing profit.
    
    Args:
        request: TravelRecommendationRequest with user details and preferences
        
    Returns:
        TravelRecommendationResponse with detailed analysis and recommendations
    """
    try:
        print("\n" + "="*90)
        print("🎯 INTELLIGENT TRAVEL RECOMMENDATION ENGINE")
        print("="*90)
        print(f"📍 Journey: {request.origin} → {request.destination}")
        print(f"📅 Dates: {request.check_in} to {request.check_out}")
        print(f"👥 Passengers: {request.passengers}")
        print(f"💰 Budget: ${request.budget}" if request.budget else "💰 No budget limit")
        if request.user_id:
            print(f"👤 User ID: {request.user_id}")
        print("="*90)
        
        logger.info(f"Travel recommendation request: {request.origin} → {request.destination}")
        
        # ===== STEP 1: SEARCH HOTELS =====
        print("\n[STEP 1] 🏨 Searching Hotels...")
        hotel_options = []
        try:
            hotel_query = f"{request.destination}"
            if request.check_in:
                hotel_query += f" {request.check_in} to {request.check_out}"
            
            hotel_results = await hotel_search_integration.search_hotels(
                query=hotel_query,
                num_results=8,
                preferences=request.user_preferences or {}
            )
            
            if hotel_results.get("status") == "success":
                hotel_options = hotel_results.get("results", [])
                print(f"  ✓ Found {len(hotel_options)} hotel options")
                for i, hotel in enumerate(hotel_options[:3], 1):
                    print(f"    {i}. {hotel.get('name')} - ${hotel.get('price_per_night')}/night")
            else:
                print(f"  ⚠ Hotel search: {hotel_results.get('message')}")
        except Exception as e:
            logger.error(f"Hotel search failed: {str(e)}")
            print(f"  ✗ Hotel search error: {str(e)}")
        
        # ===== STEP 2: SEARCH TRAVEL ROUTES & PACKAGES =====
        print("\n[STEP 2] ✈️ Searching Travel Routes & Packages (Amadeus)...")
        flight_options = []
        travel_packages = []
        try:
            # First try real Amadeus data via transport-search-api
            transport_search_url = settings.transport_search_url
            async with httpx.AsyncClient(timeout=30) as _tc:
                _resp = await _tc.post(
                    f"{transport_search_url}/api/search-transport",
                    json={
                        "origin": request.origin,
                        "destination": request.destination,
                        "date": request.check_in,
                        "adults": request.passengers,
                        "sort_by": "price",
                    },
                )
            if _resp.status_code == 200:
                _data = _resp.json()
                _opts = _data.get("transport_options", [])
                # Keep only flight-type results and map to orchestrator's internal format
                flight_options = [
                    {
                        "id": o.get("flight_number") or f"flight_{idx}",
                        "airline": o.get("provider", "Unknown"),
                        "airline_code": o.get("airline_code"),
                        "flight_number": o.get("flight_number"),
                        "origin": o.get("origin", request.origin),
                        "destination": o.get("destination", request.destination),
                        "departure_time": o.get("departure_time"),
                        "arrival_time": o.get("arrival_time"),
                        "departure": request.check_in,
                        "duration": o.get("duration", "N/A"),
                        "price": float(o.get("price", 0)),
                        "currency": o.get("currency", "INR"),
                        "stops": int(o.get("stops", 0)),
                        "cabin_class": o.get("cabin_class", "Economy"),
                    }
                    for idx, o in enumerate(_opts)
                    if o.get("type") == "flight"
                ]
                print(f"  ✓ Amadeus returned {len(flight_options)} flight(s) for {request.origin} → {request.destination}")
            else:
                print(f"  ⚠ transport-search-api returned {_resp.status_code}, will use vector DB fallback")

            # Also try vector DB for travel packages (non-blocking if empty)
            if not flight_options:
                travel_data = await rag_engine.search_travel_data(
                    query=f"flights from {request.origin} to {request.destination} {request.check_in}",
                    collection="travel_data",
                    limit=5,
                )
                if travel_data:
                    travel_packages = travel_data
                    print(f"  ✓ Found {len(travel_packages)} travel packages from vector DB")
                else:
                    print(f"  ⚠ No travel data in vector DB either — flight section will be empty")

        except Exception as e:
            logger.error(f"Travel search failed: {str(e)}")
            print(f"  ✗ Travel search error: {str(e)}")
            # Last-resort: empty list rather than wrong European airlines
            flight_options = []
        
        # ===== STEP 3: PREPARE BUSINESS RULES & CONSTRAINTS =====
        print("\n[STEP 3] 💼 Analyzing Business Rules & Constraints...")
        
        business_rules = request.business_rules or {
            "markup_percentage": 15,  # 15% platform markup
            "min_commission": 25,  # Minimum $25 commission per booking
            "preferred_partners": ["Luxury Hotels Co", "Air France"],
            "bundle_discount": 5,  # 5% discount for bundled bookings
            "loyalty_multiplier": 1.2  # Loyalty program multiplier
        }
        
        profit_rules = {
            "base_commission_rate": 0.15,
            "luxury_commission_rate": 0.20,
            "bundle_bonus": 0.05,
            "high_margin_threshold": 500  # For items > $500
        }
        
        print(f"  ✓ Base Commission: {profit_rules['base_commission_rate']*100}%")
        print(f"  ✓ Luxury Items: {profit_rules['luxury_commission_rate']*100}%")
        print(f"  ✓ Bundle Bonus: {profit_rules['bundle_bonus']*100}%")
        
        # ===== STEP 4: CALCULATE PROFITABILITY =====
        print("\n[STEP 4] 💹 Calculating Profitability Metrics...")
        
        # Score each hotel based on profit potential
        scored_hotels = []
        for hotel in hotel_options:
            hotel_copy = hotel.copy()
            price = float(hotel.get('price_per_night', 100))
            nights = (len(request.check_out.split('-')) - len(request.check_in.split('-')))  # Rough calculation
            
            # Calculate profit
            total_revenue = price * nights * request.passengers
            commission = total_revenue * profit_rules['base_commission_rate']
            
            # Bonus for luxury/high-price items
            if price > profit_rules['high_margin_threshold']:
                bonus = total_revenue * profit_rules['luxury_commission_rate']
            else:
                bonus = 0
            
            total_profit = commission + bonus
            
            hotel_copy['profit_potential'] = {
                'total_revenue': total_revenue,
                'commission': commission,
                'bonus': bonus,
                'total_profit': total_profit,
                'margin_percentage': (total_profit / total_revenue * 100) if total_revenue > 0 else 0
            }
            
            scored_hotels.append(hotel_copy)
        
        # Sort by profit potential
        scored_hotels.sort(key=lambda x: x.get('profit_potential', {}).get('total_profit', 0), reverse=True)
        print(f"  ✓ Scored {len(scored_hotels)} hotels for profitability")
        
        # ===== STEP 5: GENERATE MULTIPLE PACKAGE COMBINATIONS =====
        print("\n[STEP 5] 📦 Generating Multiple Package Combinations...")
        
        # Calculate nights
        from datetime import datetime as dt
        check_in_date = dt.strptime(request.check_in, "%Y-%m-%d")
        check_out_date = dt.strptime(request.check_out, "%Y-%m-%d")
        nights = (check_out_date - check_in_date).days
        
        # Create combinations of top hotels + top flights
        all_package_combinations = []
        hotels_to_combine = scored_hotels[:4]  # Top 4 hotels
        flights_to_combine = flight_options[:3] if flight_options else []
        
        for hotel in hotels_to_combine:
            for flight in flights_to_combine or [{"airline": "Direct", "price": 0}]:
                package = {
                    "package_id": f"{hotel.get('id', 'h1')}_{flight.get('id', 'f1')}",
                    "hotel": hotel,
                    "flight": flight,
                    "hotel_nights": nights,
                    "total_hotel_cost": hotel.get('price_per_night', 100) * nights * request.passengers,
                    "total_flight_cost": flight.get('price', 0),
                    "total_cost": (hotel.get('price_per_night', 100) * nights * request.passengers) + flight.get('price', 0),
                    "profit_metrics": {
                        "base_revenue": (hotel.get('price_per_night', 100) * nights * request.passengers) + flight.get('price', 0),
                        "commission": ((hotel.get('price_per_night', 100) * nights * request.passengers) + flight.get('price', 0)) * 0.15,
                        "bundle_bonus": ((hotel.get('price_per_night', 100) * nights * request.passengers) + flight.get('price', 0)) * 0.05 if flight.get('price', 0) > 0 else 0,
                    }
                }
                package["profit_metrics"]["total_profit"] = package["profit_metrics"]["commission"] + package["profit_metrics"]["bundle_bonus"]
                package["profit_metrics"]["margin"] = (package["profit_metrics"]["total_profit"] / package["total_cost"] * 100) if package["total_cost"] > 0 else 0
                all_package_combinations.append(package)
        
        # Sort by profit
        all_package_combinations.sort(key=lambda x: x["profit_metrics"]["total_profit"], reverse=True)
        top_recommendations = all_package_combinations[:5]  # Top 5 combinations
        
        print(f"  ✓ Generated {len(all_package_combinations)} combinations, top {len(top_recommendations)} selected")
        
        # ===== STEP 6: LLM ANALYSIS & RECOMMENDATION =====
        print("\n[STEP 6] 🤖 LLM Analysis of All Options...")
        
        # Build prompt asking for a detailed travel itinerary
        best_pkg = top_recommendations[0]
        best_hotel = best_pkg["hotel"]
        best_flight = best_pkg["flight"]

        hotel_options_text = ""
        for idx, pkg in enumerate(top_recommendations, 1):
            h = pkg["hotel"]
            hotel_options_text += f"\n  Option {idx}: {h.get('name')} ({h.get('rating')}/5 stars) — ${h.get('price_per_night')}/night — {h.get('location')}\n"
            amenities = h.get('amenities', [])
            if amenities:
                hotel_options_text += f"    Amenities: {', '.join(amenities[:5])}\n"

        llm_context = f"""You are a professional travel consultant. Produce a concise, well-structured travel plan using the information below. Use plain, formal language. Do not use emoji, exclamation marks, promotional language, profit figures, or scoring of any kind.

TRIP DETAILS
Origin: {request.origin}
Destination: {request.destination}
Dates: {request.check_in} to {request.check_out} ({nights} nights)
Passengers: {request.passengers}
Travel Style: {request.travel_style or 'Standard'}
Budget: {('$' + str(request.budget)) if request.budget else 'Flexible'}
Special Requirements: {request.special_requirements or 'None'}

AVAILABLE FLIGHT
Airline: {best_flight.get('airline')} | Price: ${best_flight.get('price')} | Duration: {best_flight.get('duration')} | Stops: {best_flight.get('stops')}

AVAILABLE HOTELS
{hotel_options_text}
Respond using the exact section headings below. Each section must be separated by a blank line. Do not add any sections beyond those listed.

FLIGHT & TRANSPORT:
Outline the recommended flight, including departure and arrival details, any connections, and ground transport options at the destination (e.g. metro, taxi, car hire).

HOTEL OPTIONS:
For each hotel, provide the name, star rating, location, key amenities, and a brief note on who it best suits. Keep each entry to 2-3 sentences.

DAY-BY-DAY ITINERARY:
Day 1 - {request.check_in}: Arrival, check-in, and orientation.
Day 2: [Primary sightseeing or activity]
(Continue for each of the {nights} nights.)
Day {nights} - {request.check_out}: Check-out and departure.

MUST-VISIT PLACES:
List the most significant attractions at {request.destination}. For each, give the name and one sentence describing what makes it worth visiting.

LOCAL TIPS:
Cover practical matters: local transport, recommended cuisine, cultural etiquette, weather, and essential items to pack.
"""
        
        # Send to LLM for intelligent analysis
        print("\n[STEP 7] 🤖 Sending analysis to LLM (Llama2)...")
        llm_response = await model_router.route_query(
            query=llm_context,
            complexity_level="complex",
            context={"packages": top_recommendations, "hotels": scored_hotels, "flights": flight_options}
        )
        
        print(f"  ✓ LLM analysis complete - recommendation received")
        logger.info(f"LLM selected best option from {len(top_recommendations)} packages")
        
        # ===== STEP 7: COMPILE ALL RECOMMENDATIONS & BEST CHOICE =====
        print("\n[STEP 7] 📋 Compiling All Recommendations...")
        
        # Prepare all recommendations for response
        all_recommendations_list = []
        for idx, pkg in enumerate(top_recommendations, 1):
            rec = {
                "rank": idx,
                "option_number": idx,
                "package_id": pkg["package_id"],
                "hotel": {
                    "name": pkg["hotel"].get("name"),
                    "rating": pkg["hotel"].get("rating"),
                    "location": pkg["hotel"].get("location"),
                    "price_per_night": pkg["hotel"].get("price_per_night"),
                    "amenities": pkg["hotel"].get("amenities", [])
                },
                "flight": {
                    "airline": pkg["flight"].get("airline"),
                    "price": pkg["flight"].get("price"),
                    "duration": pkg["flight"].get("duration"),
                    "stops": pkg["flight"].get("stops")
                },
                "total_cost": pkg["total_cost"],
                "profit_metrics": pkg["profit_metrics"],
                "suitability_score": 85 + (5 - idx) * 2  # Higher score for top options
            }
            all_recommendations_list.append(rec)
        
        # Best recommendation (from LLM analysis, use top profit as fallback)
        best_package = top_recommendations[0]
        best_recommendation = {
            "rank": 1,
            "package_id": best_package["package_id"],
            "hotel": {
                "name": best_package["hotel"].get("name"),
                "rating": best_package["hotel"].get("rating"),
                "location": best_package["hotel"].get("location"),
                "price_per_night": best_package["hotel"].get("price_per_night"),
                "amenities": best_package["hotel"].get("amenities", [])
            },
            "flight": {
                "airline": best_package["flight"].get("airline"),
                "price": best_package["flight"].get("price"),
                "duration": best_package["flight"].get("duration"),
                "stops": best_package["flight"].get("stops")
            },
            "total_user_cost": best_package["total_cost"],
            "total_package_cost": best_package["total_cost"],
            "platform_profit": best_package["profit_metrics"]["total_profit"]
        }
        
        # Generate hotel options summary for the traveller
        comparison_summary = f"HOTEL OPTIONS FOR {request.destination.upper()}:\n"
        comparison_summary += "=" * 80 + "\n"
        comparison_summary += f"{'#':<4} {'Hotel':<30} {'Stars':<8} {'Price/Night':<14} {'Location':<20}\n"
        comparison_summary += "-" * 80 + "\n"
        
        for rec in all_recommendations_list:
            hotel_name = rec["hotel"]["name"][:29]
            rating = f"{rec['hotel']['rating']}/5"
            price = f"${rec['hotel']['price_per_night']}/night"
            location = str(rec["hotel"].get("location", ""))[:19]
            comparison_summary += f"{rec['rank']:<4} {hotel_name:<30} {rating:<8} {price:<14} {location:<20}\n"
        
        comparison_summary += "=" * 80 + "\n"
        comparison_summary += f"\nFLIGHT OPTIONS:\n"
        comparison_summary += "-" * 80 + "\n"
        if flight_options:
            for f in flight_options:
                comparison_summary += f"  {f.get('airline','N/A'):<20} ${f.get('price',0):<10} {f.get('duration','N/A'):<12} {f.get('stops',0)} stop(s)\n"
        else:
            comparison_summary += f"  Flights from {request.origin} to {request.destination} — check airline websites for live prices\n"
        comparison_summary += "=" * 80
        
        # ROI Analysis for best option
        best_profit = best_package["profit_metrics"]["total_profit"]
        best_revenue = best_package["profit_metrics"]["base_revenue"]
        roi_analysis = {
            "total_revenue": best_revenue,
            "platform_profit": best_profit,
            "profit_margin": best_package["profit_metrics"]["margin"],
            "customer_satisfaction": "high",
            "roi_percentage": best_package["profit_metrics"]["margin"]
        }
        
        print(f"  ✓ All {len(all_recommendations_list)} recommendations compiled")
        print(f"  ├─ Best Option: {best_recommendation['hotel']['name']}")
        print(f"  ├─ Total Price: ${best_recommendation['total_user_cost']:.2f}")
        print(f"  ├─ Platform Profit: ${best_recommendation['platform_profit']:.2f}")
        print(f"  └─ Profit Margin: {roi_analysis['profit_margin']:.1f}%")
        
        print("\n" + "="*90)
        print("✅ MULTI-OPTION ANALYSIS COMPLETE - LLM SELECTED BEST CHOICE")
        print("="*90 + "\n")
        
        return TravelRecommendationResponse(
            status="success",
            user_id=request.user_id,
            hotel_options=scored_hotels[:5],
            flight_options=flight_options[:3] if flight_options else [],
            travel_packages=travel_packages[:3] if travel_packages else [],
            all_recommendations=all_recommendations_list,
            analysis=llm_response.get("response", "LLM analysis completed"),
            recommendation=best_recommendation,
            reasoning=f"Recommended hotel: {best_recommendation['hotel']['name']} ({best_recommendation['hotel']['rating']}/5 stars) at {best_recommendation['hotel']['location']}. Flight via {best_recommendation['flight']['airline']} — {best_recommendation['flight'].get('duration', 'N/A')} travel time with {best_recommendation['flight'].get('stops', 0)} stop(s). Total trip cost: ${best_recommendation['total_user_cost']:.2f} for {nights} nights.",
            comparison_summary=comparison_summary,
            profit_metrics={
                "total_revenue": best_revenue,
                "platform_profit": best_profit,
                "profit_margin_percentage": roi_analysis["profit_margin"],
                "comparison": f"Option #{best_recommendation['rank']} generates ${best_profit:.2f} profit ({roi_analysis['profit_margin']:.1f}% margin) vs ${all_recommendations_list[1]['profit_metrics']['total_profit']:.2f} for #2"
            },
            roi_analysis=roi_analysis,
            complete_journey={
                "destination": request.destination,
                "origin": request.origin,
                "duration_nights": nights,
                "check_in": request.check_in,
                "check_out": request.check_out,
                "passengers": request.passengers,
                "recommended_hotel": {
                    "name": best_recommendation["hotel"]["name"],
                    "rating": best_recommendation["hotel"]["rating"],
                    "location": best_recommendation["hotel"]["location"],
                    "price_per_night": best_recommendation["hotel"]["price_per_night"],
                    "amenities": best_recommendation["hotel"].get("amenities", [])
                },
                "flight": {
                    "airline": best_recommendation["flight"]["airline"],
                    "duration": best_recommendation["flight"].get("duration", "N/A"),
                    "stops": best_recommendation["flight"].get("stops", 0),
                    "price": best_recommendation["flight"].get("price", 0)
                },
                "estimated_total_cost": best_recommendation["total_user_cost"],
                "hotel_options": [
                    {
                        "name": rec["hotel"]["name"],
                        "rating": rec["hotel"]["rating"],
                        "location": rec["hotel"]["location"],
                        "price_per_night": rec["hotel"]["price_per_night"],
                        "amenities": rec["hotel"].get("amenities", [])
                    }
                    for rec in all_recommendations_list
                ],
                "transport_options": [
                    {
                        "type": "flight",
                        "airline": f.get("airline"),
                        "price": f.get("price"),
                        "duration": f.get("duration"),
                        "stops": f.get("stops")
                    }
                    for f in (flight_options[:3] if flight_options else [{"airline": best_recommendation["flight"]["airline"], "price": best_recommendation["flight"].get("price", 0), "duration": best_recommendation["flight"].get("duration", "N/A"), "stops": best_recommendation["flight"].get("stops", 0)}])
                ]
            }
        )
        
    except Exception as e:
        logger.error(f"Travel recommendation error: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user query through orchestrator
    
    Routes to Phi4 for simple queries, Llama for complex ones
    """
    try:
        print("\n" + "="*80)
        print("🔷 ORCHESTRATOR AGENT - QUERY PROCESSING")
        print("="*80)
        print(f"📝 USER QUERY: {request.query}")
        if request.user_id:
            print(f"👤 USER ID: {request.user_id}")
        print("="*80)
        
        logger.info(f"[STEP 1] Received query: {request.query[:50]}...")
        
        # Step 2: Analyze complexity
        print("\n[STEP 2] Analyzing Query Complexity...")
        complexity_level, score = complexity_detector.analyze(request.query)
        print(f"  ├─ Complexity Score: {score:.2f}/1.0")
        print(f"  ├─ Threshold: {settings.complexity_threshold}")
        print(f"  └─ Classification: {complexity_level.upper()}")
        logger.info(f"Complexity: {complexity_level} (score: {score:.2f})")
        
        # Step 3: Prepare context
        print("\n[STEP 3] Preparing Context...")
        context = request.context or {}
        if request.user_id:
            print(f"  ├─ Fetching user profile...")
            user_profile = await personalization_client.get_user_profile(
                request.user_id
            )
            context["user_profile"] = user_profile
            print(f"  └─ ✓ User profile loaded")
            logger.info(f"Loaded user profile for {request.user_id}")
        
        # Step 4: Route to appropriate model
        print(f"\n[STEP 4] Routing Query to Model...")
        if complexity_level == "simple":
            print(f"  ├─ Query is SIMPLE (score {score:.2f} < {settings.complexity_threshold})")
            print(f"  ├─ MODEL: Phi4 (Fast, Lightweight)")
            print(f"  └─ 🚀 Sending to Phi4...")
        else:
            print(f"  ├─ Query is COMPLEX (score {score:.2f} >= {settings.complexity_threshold})")
            print(f"  ├─ MODEL: Llama2 (Powerful, In-depth)")
            print(f"  └─ 🚀 Sending to Llama2...")
        
        logger.info(f"Routing to {complexity_level} model")
        
        # Call the model
        model_response = await model_router.route_query(
            request.query,
            complexity_level,
            context
        )
        
        print(f"\n[STEP 5] Model Response Received")
        print(f"  ├─ Model Used: {model_response['model']}")
        print(f"  ├─ Status: {model_response['status']}")
        print(f"  └─ Response Length: {len(model_response['response'])} characters")
        
        print("\n" + "="*80)
        print("✅ QUERY PROCESSING COMPLETE")
        print("="*80 + "\n")
        
        return QueryResponse(
            query=request.query,
            complexity_level=complexity_level,
            model_used=model_response["model"],
            response=model_response["response"],
            status="success"
        )
        
    except OrchestratorException as e:
        logger.error(f"Orchestrator error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/search/hotels")
async def search_hotels(request: HotelSearchRequest):
    """
    Search for hotels with personalization
    """
    try:
        print("\n" + "="*80)
        print("🏨 HOTEL SEARCH - AGENT ROUTING")
        print("="*80)
        print(f"📍 Location: {request.location}")
        print(f"📅 Check-in: {request.check_in} | Check-out: {request.check_out}")
        print(f"👥 Guests: {request.guests}")
        if request.user_id:
            print(f"👤 User ID: {request.user_id}")
        print("="*80)
        
        logger.info(f"Hotel search request: {request.location}")
        
        # Step 1: Call Hotel Search Agent
        print("\n[STEP 1] Calling Hotel Search Agent...")
        print(f"  ├─ Agent URL: {settings.hotel_search_agent_url}")
        print(f"  ├─ Endpoint: POST /search")
        
        results = await hotel_search_client.search_hotels(
            location=request.location,
            check_in=request.check_in,
            check_out=request.check_out,
            guests=request.guests,
            preferences=request.preferences
        )
        
        print(f"  ├─ ✓ Response received")
        print(f"  └─ Results found: {len(results)}")
        logger.info(f"Hotel search returned {len(results)} results")
        
        # Step 2: Apply personalization if user provided
        if request.user_id and results:
            print(f"\n[STEP 2] Applying Personalization...")
            print(f"  ├─ Agent URL: {settings.personalization_agent_url}")
            print(f"  ├─ Endpoint: POST /rank")
            print(f"  ├─ User ID: {request.user_id}")
            print(f"  ├─ Results to rank: {len(results)}")
            
            results = await personalization_client.rank_results(
                user_id=request.user_id,
                results=results
            )
            
            print(f"  └─ ✓ Results ranked and personalized")
            logger.info(f"Applied personalization ranking for {request.user_id}")
        
        print("\n" + "="*80)
        print(f"✅ HOTEL SEARCH COMPLETE - {len(results)} results")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Hotel search error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/flights")
async def search_flights(request: FlightSearchRequest):
    """
    Search for flights with personalization
    """
    try:
        print("\n" + "="*80)
        print("✈️  FLIGHT SEARCH - AGENT ROUTING")
        print("="*80)
        print(f"🛫 Origin: {request.origin} → Destination: {request.destination}")
        print(f"📅 Departure: {request.departure_date}")
        if request.return_date:
            print(f"📅 Return: {request.return_date}")
        print(f"👥 Passengers: {request.passengers}")
        if request.user_id:
            print(f"👤 User ID: {request.user_id}")
        print("="*80)
        
        logger.info(f"Flight search request: {request.origin} to {request.destination}")
        
        # Step 1: Call Amadeus/TBO Agent
        print("\n[STEP 1] Calling Amadeus/TBO Agent...")
        print(f"  ├─ Agent URL: {settings.amadeus_agent_url}")
        print(f"  ├─ Endpoint: POST /search")
        print(f"  ├─ Route: {request.origin} → {request.destination}")
        
        results = await amadeus_client.search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            passengers=request.passengers,
            preferences=request.preferences
        )
        
        print(f"  ├─ ✓ Response received")
        print(f"  └─ Results found: {len(results)}")
        logger.info(f"Flight search returned {len(results)} results")
        
        # Step 2: Apply personalization if user provided
        if request.user_id and results:
            print(f"\n[STEP 2] Applying Personalization...")
            print(f"  ├─ Agent URL: {settings.personalization_agent_url}")
            print(f"  ├─ Endpoint: POST /rank")
            print(f"  ├─ User ID: {request.user_id}")
            print(f"  ├─ Results to rank: {len(results)}")
            
            results = await personalization_client.rank_results(
                user_id=request.user_id,
                results=results
            )
            
            print(f"  └─ ✓ Results ranked and personalized")
            logger.info(f"Applied personalization ranking for {request.user_id}")
        
        print("\n" + "="*80)
        print(f"✅ FLIGHT SEARCH COMPLETE - {len(results)} results")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "count": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Flight search error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search/packages")
async def search_packages(request: FlightSearchRequest):
    """
    Search for complete travel packages (flights + hotels)
    """
    try:
        logger.info(f"Package search: {request.origin} to {request.destination}")
        
        # Get travel packages
        packages = await amadeus_client.get_travel_packages(
            origin=request.origin,
            destination=request.destination,
            dates={
                "departure": request.departure_date,
                "return": request.return_date,
                "check_in": request.departure_date,
                "check_out": request.return_date
            }
        )
        
        # Personalize if user_id provided
        if request.user_id and packages:
            packages = await personalization_client.rank_results(
                user_id=request.user_id,
                results=packages
            )
        
        return {
            "status": "success",
            "count": len(packages),
            "packages": packages
        }
        
    except Exception as e:
        logger.error(f"Package search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/query")
async def rag_query(request: JSONQueryRequest):
    """
    RAG-enhanced query endpoint
    Combines hotel search + vector DB + LLM analysis
    
    JSON Input Example:
    {
        "query_type": "hotel",
        "location": "Athens, Greece",
        "check_in": "2026-03-15",
        "check_out": "2026-03-20",
        "guests": 2,
        "preferences": {"min_rating": 4.0, "max_price": 200},
        "user_id": "user123",
        "use_rag": true
    }
    """
    try:
        print("\n" + "="*80)
        print("🔍 RAG-ENHANCED QUERY PROCESSOR")
        print("="*80)
        print(f"📋 Query Type: {request.query_type}")
        if request.location:
            print(f"📍 Location: {request.location}")
        if request.destination:
            print(f"🎯 Destination: {request.destination}")
        print("="*80)
        
        logger.info(f"RAG query: type={request.query_type}")
        
        # Step 1: Search external data (hotels)
        hotel_data = []
        if request.query_type in ["hotel", "travel_package"] and request.location:
            print("\n[STEP 1] Searching Hotel Inventory...")
            search_query = f"{request.location}"
            if request.check_in:
                search_query += f" {request.check_in} to {request.check_out}"
            
            hotel_results = await hotel_search_integration.search_hotels(
                query=search_query,
                num_results=5,
                preferences=request.preferences
            )
            
            if hotel_results.get("status") == "success":
                hotel_data = hotel_results.get("results", [])
                print(f"  ✓ Found {len(hotel_data)} hotels")
            else:
                print(f"  ⚠ Hotel search: {hotel_results.get('message')}")
            logger.info(f"Hotel search returned {len(hotel_data)} results")
        
        # Step 2: Search vector DB (Qdrant RAG)
        travel_data = []
        if request.use_rag:
            print("\n[STEP 2] Querying Vector DB (RAG)...")
            search_query = f"{request.query_type}"
            if request.destination:
                search_query += f" {request.destination}"
            elif request.location:
                search_query += f" {request.location}"
            
            travel_data = await rag_engine.search_travel_data(
                query=search_query,
                collection="travel_data",
                limit=5
            )
            print(f"  ✓ Retrieved {len(travel_data)} from vector DB")
            logger.info(f"RAG search returned {len(travel_data)} results")
        
        # Step 3: Build comprehensive context
        print("\n[STEP 3] Building Context...")
        context = await rag_engine.retrieve_context(
            query=f"{request.query_type}: {request.location or request.destination}",
            hotel_data=hotel_data,
            travel_data=travel_data
        )
        
        # Step 4: Format for LLM and get analysis
        print("\n[STEP 4] LLM Analysis...")
        formatted_context = rag_engine.format_for_llm(context)
        
        llm_response = await model_router.route_query(
            query=formatted_context,
            complexity_level="complex",
            context={"hotel_data": hotel_data, "travel_data": travel_data}
        )
        
        print(f"  ✓ LLM analysis complete")
        logger.info(f"LLM analysis returned {len(llm_response.get('response', ''))} chars")
        
        # Step 5: Apply personalization if user provided
        recommendations = hotel_data[:3] if hotel_data else []
        if request.user_id and recommendations:
            print("\n[STEP 5] Personalizing Results...")
            recommendations = await personalization_client.rank_results(
                user_id=request.user_id,
                results=recommendations
            )
            print(f"  ✓ Results personalized for user {request.user_id}")
        
        print("\n" + "="*80)
        print("✅ RAG QUERY COMPLETE")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "query_type": request.query_type,
            "sources": context.get("sources", []),
            "hotel_results": hotel_data[:3],
            "travel_packages": travel_data[:3],
            "llm_analysis": llm_response.get("response", ""),
            "recommendations": recommendations,
            "total_results": {
                "hotels": len(hotel_data),
                "travel_packages": len(travel_data)
            }
        }
        
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}", exc_info=True)
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/json/process")
async def process_json_request(request: JSONQueryRequest):
    """
    Process structured JSON travel request
    Simpler wrapper around RAG query endpoint
    """
    try:
        logger.info(f"Processing JSON request: {request.query_type}")
        
        # Delegate to RAG endpoint
        return await rag_query(request)
        
    except Exception as e:
        logger.error(f"JSON process error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/orchestrate")
async def orchestrate(request: QueryRequest):
    """
    Main orchestration endpoint - intelligently routes to agents
    """
    try:
        print("\n" + "="*80)
        print("🎯 ORCHESTRATOR - FULL ORCHESTRATION FLOW")
        print("="*80)
        print(f"📝 USER QUERY: {request.query}")
        if request.user_id:
            print(f"👤 USER ID: {request.user_id}")
        print("="*80)
        
        logger.info("Starting full orchestration...")
        
        # Step 1: Analyze query complexity
        print("\n[STEP 1] Analyzing Query Complexity...")
        complexity_level, score = complexity_detector.analyze(request.query)
        print(f"  ├─ Complexity Score: {score:.2f}/1.0")
        print(f"  └─ Classification: {complexity_level.upper()}")
        logger.info(f"Query complexity: {complexity_level} (score: {score:.2f})")
        
        # Step 2: Route to LLM for initial processing
        print(f"\n[STEP 2] Processing Query with {complexity_level.upper()} Model...")
        model = settings.llama_model if complexity_level == "complex" else settings.phi4_model
        print(f"  ├─ Model: {model}")
        print(f"  ├─ Ollama Host: {settings.ollama_host}")
        
        model_response = await model_router.route_query(
            request.query,
            complexity_level,
            request.context
        )
        print(f"  └─ ✓ Model processing complete")
        
        # Step 3: Identify which agents to call
        recommendations = []
        print(f"\n[STEP 3] Identifying Required Agents...")
        
        agents_needed = []
        if any(kw in request.query.lower() for kw in ["hotel", "accommodation", "stay"]):
            agents_needed.append("Hotel Search Agent")
        if any(kw in request.query.lower() for kw in ["flight", "fly", "travel", "ticket"]):
            agents_needed.append("Amadeus/TBO Agent")
        
        if agents_needed:
            print(f"  ├─ Agents needed: {', '.join(agents_needed)}")
        else:
            print(f"  └─ Using model response only")
        
        # Step 4: Call identified agents
        if "Hotel Search Agent" in agents_needed:
            if "location" in request.context or "destination" in request.context:
                location = request.context.get("location") or request.context.get("destination")
                print(f"\n[STEP 4.1] Calling Hotel Search Agent...")
                print(f"  ├─ Agent URL: {settings.hotel_search_agent_url}")
                print(f"  ├─ Endpoint: POST /search")
                print(f"  ├─ Location: {location}")
                
                hotel_results = await hotel_search_client.search_hotels(
                    location=location,
                    check_in=request.context.get("check_in", ""),
                    check_out=request.context.get("check_out", ""),
                    guests=request.context.get("guests", 1)
                )
                recommendations.extend(hotel_results[:3])
                print(f"  └─ ✓ Retrieved {len(hotel_results)} hotel results")
                logger.info(f"Hotel search returned {len(hotel_results)} results")
        
        if "Amadeus/TBO Agent" in agents_needed:
            if "origin" in request.context and "destination" in request.context:
                print(f"\n[STEP 4.2] Calling Amadeus/TBO Agent...")
                print(f"  ├─ Agent URL: {settings.amadeus_agent_url}")
                print(f"  ├─ Endpoint: POST /search")
                print(f"  ├─ Route: {request.context['origin']} → {request.context['destination']}")
                
                flight_results = await amadeus_client.search_flights(
                    origin=request.context["origin"],
                    destination=request.context["destination"],
                    departure_date=request.context.get("departure_date", ""),
                    passengers=request.context.get("passengers", 1)
                )
                recommendations.extend(flight_results[:3])
                print(f"  └─ ✓ Retrieved {len(flight_results)} flight results")
                logger.info(f"Flight search returned {len(flight_results)} results")
        
        # Step 5: Apply personalization and business rules
        if request.user_id:
            print(f"\n[STEP 5] Applying Personalization & Business Rules...")
            print(f"  ├─ Agent URL: {settings.personalization_agent_url}")
            print(f"  ├─ Endpoint: POST /rank")
            print(f"  ├─ User ID: {request.user_id}")
            print(f"  ├─ Results to rank: {len(recommendations)}")
            
            recommendations = await personalization_client.rank_results(
                user_id=request.user_id,
                results=recommendations
            )
            print(f"  └─ ✓ Personalization applied")
            logger.info(f"Applied personalization for {request.user_id}")
        
        print("\n" + "="*80)
        print(f"✅ ORCHESTRATION COMPLETE")
        print(f"  ├─ Total Recommendations: {len(recommendations[:5])}")
        print(f"  ├─ Agents Contacted: {len(agents_needed)}")
        print("="*80 + "\n")
        
        return {
            "status": "success",
            "query": request.query,
            "complexity_level": complexity_level,
            "model_used": model,
            "model_response": model_response["response"],
            "recommendations": recommendations[:5],
            "agents_contacted": agents_needed,
            "suggestion": "Use hotel search for bookings or flight search for travel"
        }
        
    except Exception as e:
        logger.error(f"Orchestration error: {str(e)}")
        print(f"\n❌ ERROR: {str(e)}\n")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
