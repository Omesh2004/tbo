"""
Comprehensive Test Suite for Chat Personalization Service
Tests all components without requiring full Docker container running
"""

import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("CHAT PERSONALIZATION SERVICE - COMPREHENSIVE TEST SUITE")
print("=" * 80)

# ============================================================================
# TEST 1: CONFIGURATION IMPORT
# ============================================================================
print("\n[TEST 1] Configuration Module Import")
print("-" * 80)
try:
    from app.config import settings
    print(f"✓ Configuration loaded successfully")
    print(f"  - App Name: {settings.app_name}")
    print(f"  - API Version: {settings.api_version}")
    print(f"  - Debug Mode: {settings.debug}")
    print(f"  - Log Level: {settings.log_level}")
    print(f"  - Max Context Length: {settings.max_context_length}")
    print(f"  - Min Prompts for Analysis: {settings.min_prompts_for_analysis}")
    TEST_1_PASS = True
except Exception as e:
    print(f"✗ Configuration import FAILED: {str(e)}")
    TEST_1_PASS = False

# ============================================================================
# TEST 2: PYDANTIC MODELS
# ============================================================================
print("\n[TEST 2] Pydantic Models Validation")
print("-" * 80)
try:
    from app.models import (
        PromptInput, AnalysisRequest, LLMContextRequest,
        HealthCheckResponse, AnalysisResponse
    )
    
    # Test PromptInput
    prompt_data = PromptInput(
        user_id="test_user_001",
        prompt_text="I need luxury hotels in Paris",
        response_text="Here are options...",
        category="travel",
        tags=["luxury", "paris"]
    )
    print(f"✓ PromptInput model validated")
    print(f"  - User ID: {prompt_data.user_id}")
    print(f"  - Category: {prompt_data.category}")
    print(f"  - Tags: {prompt_data.tags}")
    
    # Test AnalysisRequest
    analysis_req = AnalysisRequest(
        user_id="test_user_001",
        force_reanalyze=False
    )
    print(f"✓ AnalysisRequest model validated")
    
    # Test LLMContextRequest
    context_req = LLMContextRequest(
        user_id="test_user_001"
    )
    print(f"✓ LLMContextRequest model validated")
    
    TEST_2_PASS = True
except Exception as e:
    print(f"✗ Pydantic models FAILED: {str(e)}")
    TEST_2_PASS = False

# ============================================================================
# TEST 3: ML ANALYZER - PROMPT ANALYSIS
# ============================================================================
print("\n[TEST 3] ML Analyzer - Prompt Analysis")
print("-" * 80)
try:
    from app.ml.analyzer import PromptAnalyzer
    
    analyzer = PromptAnalyzer()
    print(f"✓ PromptAnalyzer initialized successfully")
    
    # Test with sample prompts
    sample_prompts = [
        "I need luxury 5-star hotels in Paris with spa facilities",
        "Looking for budget-friendly accommodation in Bangkok under $50/night",
        "Can you recommend adventure activities in Nepal with experienced guides?",
        "I'm planning a family trip to Maldives, need all-inclusive packages",
        "Business trip to London next month, need hotels near financial district"
    ]
    
    print(f"\n  Analyzing {len(sample_prompts)} sample prompts...")
    analysis = analyzer.analyze_prompts(sample_prompts)
    
    print(f"✓ Analysis complete")
    print(f"\n  EXTRACTED CHARACTERISTICS:")
    print(f"  - Interests: {analysis.get('interests', [])}")
    print(f"  - Travel Preferences: {analysis.get('travel_preferences', {})}")
    print(f"  - Budget Profile: {analysis.get('budget_profile', {})}")
    print(f"  - Personality Traits: {analysis.get('personality_traits', [])}")
    print(f"  - Pain Points: {analysis.get('pain_points', [])}")
    print(f"  - Motivation Drivers: {analysis.get('motivation_drivers', [])}")
    print(f"  - Decision Style: {analysis.get('decision_style', 'N/A')}")
    print(f"  - Tone Preference: {analysis.get('tone_preference', 'N/A')}")
    print(f"  - Communication Style: {analysis.get('communication_style', 'N/A')}")
    
    # Test detailed summary
    summary = analysis.get('detailed_summary', '')
    print(f"\n  DETAILED SUMMARY (for LLM):")
    print(f"  {summary[:200]}..." if len(summary) > 200 else f"  {summary}")
    
    # Test confidence score
    confidence = analysis.get('confidence_score', 0.0)
    print(f"\n  Confidence Score: {confidence} (Range: 0.0-1.0)")
    if confidence >= 0.7:
        print(f"  ✓ High confidence - sufficient data for personalization")
    elif confidence >= 0.3:
        print(f"  ⚠ Medium confidence - reasonable personalization possible")
    else:
        print(f"  ⚠ Low confidence - needs more prompts")
    
    TEST_3_PASS = True
except Exception as e:
    print(f"✗ ML Analyzer FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    TEST_3_PASS = False

# ============================================================================
# TEST 4: FEATURE EXTRACTION METHODS
# ============================================================================
print("\n[TEST 4] ML Analyzer - Individual Feature Extraction")
print("-" * 80)
try:
    from app.ml.analyzer import PromptAnalyzer
    
    analyzer = PromptAnalyzer()
    test_prompts = [
        "Luxury hotels in Paris for honeymoon",
        "Budget travel in Southeast Asia",
        "Adventure trekking in Nepal"
    ]
    
    print(f"✓ Testing extraction methods with {len(test_prompts)} prompts:\n")
    
    # Travel preferences
    prefs = analyzer._extract_travel_preferences(test_prompts)
    print(f"  Travel Preferences: {prefs}")
    
    # Budget profile
    budget = analyzer._extract_budget_profile(test_prompts)
    print(f"  Budget Profile: {budget}")
    
    # Interests
    interests = analyzer._extract_interests(test_prompts)
    print(f"  Interests: {interests}")
    
    # Personality traits
    traits = analyzer._extract_personality_traits(test_prompts)
    print(f"  Personality Traits: {traits}")
    
    # Pain points
    pain_points = analyzer._extract_pain_points(test_prompts)
    print(f"  Pain Points: {pain_points}")
    
    # Decision style
    decision_style = analyzer._extract_decision_style(test_prompts)
    print(f"  Decision Style: {decision_style}")
    
    # Sentiment
    sentiment = analyzer._calculate_avg_sentiment(test_prompts)
    print(f"  Average Sentiment: {sentiment}")
    
    TEST_4_PASS = True
except Exception as e:
    print(f"✗ Feature Extraction FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    TEST_4_PASS = False

# ============================================================================
# TEST 5: PRISMA SCHEMA VALIDATION
# ============================================================================
print("\n[TEST 5] Database Schema Validation")
print("-" * 80)
try:
    schema_path = Path(__file__).parent / "app" / "prisma" / "schema.prisma"
    
    if schema_path.exists():
        with open(schema_path, 'r') as f:
            schema_content = f.read()
        
        print(f"✓ Schema file found and readable")
        
        # Check for required tables
        required_models = [
            "user_profile",
            "prompt_history",
            "user_characteristics",
            "analysis_logs"
        ]
        
        found_models = []
        for model in required_models:
            if f"model {model}" in schema_content:
                found_models.append(model)
                print(f"  ✓ {model} table defined")
        
        if len(found_models) == len(required_models):
            print(f"\n✓ All required tables found in schema")
            TEST_5_PASS = True
        else:
            print(f"✗ Missing tables: {set(required_models) - set(found_models)}")
            TEST_5_PASS = False
    else:
        print(f"✗ Schema file not found at {schema_path}")
        TEST_5_PASS = False
        
except Exception as e:
    print(f"✗ Schema validation FAILED: {str(e)}")
    TEST_5_PASS = False

# ============================================================================
# TEST 6: REQUIREMENTS.TXT VALIDATION
# ============================================================================
print("\n[TEST 6] Dependencies Validation")
print("-" * 80)
try:
    req_path = Path(__file__).parent / "requirements.txt"
    
    if req_path.exists():
        with open(req_path, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"✓ requirements.txt found with {len(requirements)} packages")
        
        required_packages = ['fastapi', 'uvicorn', 'pydantic', 'prisma', 'scikit-learn']
        found_packages = []
        
        for req in requirements:
            for pkg in required_packages:
                if pkg in req.lower():
                    found_packages.append(pkg)
                    break
        
        print(f"\n  Required packages found:")
        for pkg in required_packages:
            status = "✓" if pkg in found_packages else "✗"
            print(f"    {status} {pkg}")
        
        if len(found_packages) == len(required_packages):
            TEST_6_PASS = True
            print(f"\n✓ All required packages listed")
        else:
            TEST_6_PASS = False
            print(f"\n✗ Missing packages: {set(required_packages) - set(found_packages)}")
    else:
        print(f"✗ requirements.txt not found")
        TEST_6_PASS = False
        
except Exception as e:
    print(f"✗ Requirements validation FAILED: {str(e)}")
    TEST_6_PASS = False

# ============================================================================
# TEST 7: LLM CONTEXT GENERATION
# ============================================================================
print("\n[TEST 7] LLM Context Generation")
print("-" * 80)
try:
    from app.ml.analyzer import PromptAnalyzer
    
    analyzer = PromptAnalyzer()
    
    # Simulate real user prompts
    user_prompts = [
        "I want to book a 5-star luxury hotel in Paris for my honeymoon",
        "Budget is around $500-600 per night",
        "Looking for places with spa and fine dining restaurants",
        "Prefer organized tours but also some free time to explore",
        "Need travel insurance and flexible cancellation policy"
    ]
    
    analysis = analyzer.analyze_prompts(user_prompts)
    detailed_summary = analysis.get('detailed_summary', '')
    interests = analysis.get('interests', [])
    decision_style = analysis.get('decision_style', 'balanced')
    tone_pref = analysis.get('tone_preference', 'helpful')
    
    # Build sample LLM system context
    llm_context = f"""You are assisting a user with the following profile:

## User Characteristics
{detailed_summary}

## Key Preferences
- Interests: {', '.join(interests) if interests else 'Not specified'}
- Budget Tier: luxury
- Decision Style: {decision_style}
- Tone Preference: {tone_pref}

Use this context to provide personalized responses aligned with their preferences."""
    
    print(f"✓ LLM Context generated successfully\n")
    print(f"  Context Length: {len(llm_context)} characters")
    print(f"  Ready for: OpenAI GPT-4, Claude, Llama, etc.")
    print(f"\n  SAMPLE CONTEXT (first 500 chars):")
    print(f"  {llm_context[:500]}...")
    
    TEST_7_PASS = True
except Exception as e:
    print(f"✗ LLM Context Generation FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    TEST_7_PASS = False

# ============================================================================
# TEST 8: FASTAPI APPLICATION
# ============================================================================
print("\n[TEST 8] FastAPI Application Structure")
print("-" * 80)
try:
    import inspect
    from app.main import app
    
    print(f"✓ FastAPI app imported successfully")
    print(f"  - App Title: {app.title}")
    print(f"  - App Version: {app.version}")
    
    # Check routes
    routes = [route.path for route in app.routes]
    print(f"\n  Available Routes ({len(app.routes)} total):")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', ['GET'])
            print(f"    • {route.path} [{', '.join(methods)}]")
    
    # Check required endpoints
    required_endpoints = ['/health', '/api/v1/analyze', '/api/v1/context']
    found_endpoints = [r.path for r in app.routes if hasattr(r, 'path') and any(req in r.path for req in required_endpoints)]
    
    print(f"\n  Required Endpoints Status:")
    for endpoint in required_endpoints:
        found = any(endpoint in r.path for r in app.routes if hasattr(r, 'path'))
        status = "✓" if found else "✗"
        print(f"    {status} {endpoint}")
    
    TEST_8_PASS = all(endpoint in str(found_endpoints) or any(endpoint in r.path for r in app.routes if hasattr(r, 'path')) for endpoint in ['/health', 'analyze', 'context'])
    
    if TEST_8_PASS:
        print(f"\n✓ All required endpoints present")
    else:
        print(f"\n✗ Some endpoints missing")
        
except Exception as e:
    print(f"✗ FastAPI Application FAILED: {str(e)}")
    import traceback
    traceback.print_exc()
    TEST_8_PASS = False

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

results = {
    "Configuration Import": TEST_1_PASS,
    "Pydantic Models": TEST_2_PASS,
    "ML Analyzer": TEST_3_PASS,
    "Feature Extraction": TEST_4_PASS,
    "Database Schema": TEST_5_PASS,
    "Dependencies": TEST_6_PASS,
    "LLM Context Generation": TEST_7_PASS,
    "FastAPI Application": TEST_8_PASS,
}

passed = sum(1 for v in results.values() if v)
total = len(results)

print(f"\n{'Test Name':<30} {'Status':<10}")
print("-" * 40)
for test_name, passed_flag in results.items():
    status = "✓ PASS" if passed_flag else "✗ FAIL"
    print(f"{test_name:<30} {status:<10}")

print("\n" + "=" * 80)
print(f"TOTAL: {passed}/{total} tests passed")
print("=" * 80)

if passed == total:
    print("\n✓✓✓ ALL TESTS PASSED! Service is ready for deployment. ✓✓✓\n")
    sys.exit(0)
else:
    print(f"\n⚠ {total - passed} test(s) failed. See details above.\n")
    sys.exit(1)
