"""
API Integration Examples and Usage Patterns
Chat Personalization Service
"""

# =============================================================================
# 1. PYTHON EXAMPLES
# =============================================================================

print("=" * 80)
print("1. PYTHON EXAMPLES")
print("=" * 80)

import requests
import json

BASE_URL = "http://localhost:8001"

# Example 1: Save a User Prompt
print("\nExample 1: Save User Prompt")
print("-" * 40)

prompt_data = {
    "user_id": "user_abc123",
    "prompt_text": "I need a luxury 5-star hotel in Paris with spa facilities for my honeymoon",
    "response_text": "I found 5 premium hotels in Paris...",
    "category": "travel",
    "tags": ["luxury", "paris", "honeymoon", "spa"]
}

response = requests.post(
    f"{BASE_URL}/api/v1/prompts/save",
    json=prompt_data
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")


# Example 2: Get User Prompts
print("\n\nExample 2: Get User Prompts")
print("-" * 40)

response = requests.get(
    f"{BASE_URL}/api/v1/prompts/user_abc123",
    params={"limit": 10, "offset": 0}
)
print(f"Status: {response.status_code}")
print(f"Prompts Found: {response.json()['total_returned']}")
if response.json()['prompts']:
    print(f"First Prompt: {response.json()['prompts'][0]['prompt_text'][:100]}...")


# Example 3: Analyze User Prompts
print("\n\nExample 3: Analyze User Prompts")
print("-" * 40)

request_data = {
    "user_id": "user_abc123",
    "force_reanalyze": False
}

response = requests.post(
    f"{BASE_URL}/api/v1/analyze",
    json=request_data
)
print(f"Status: {response.status_code}")
analysis = response.json()
print(f"Prompts Analyzed: {analysis['prompts_analyzed']}")
print(f"Confidence Score: {analysis['characteristics']['confidence_score']}")
print(f"Interests: {analysis['characteristics']['interests']}")


# Example 4: Get LLM Context (Full System Prompt)
print("\n\nExample 4: Get LLM Context for Chat")
print("-" * 40)

request_data = {
    "user_id": "user_abc123",
    "max_context_tokens": 2000
}

response = requests.post(
    f"{BASE_URL}/api/v1/context",
    json=request_data
)
print(f"Status: {response.status_code}")
context = response.json()
print(f"User Name: {context['user_name']}")
print(f"Confidence: {context['confidence_score']}")
print(f"Communication Style: {context['communication_style']}")
print(f"\nSystem Context (first 500 chars):")
print(context['system_context'][:500] + "...")


# Example 5: Get Characteristics Only
print("\n\nExample 5: Get User Characteristics")
print("-" * 40)

response = requests.get(
    f"{BASE_URL}/api/v1/characteristics/user_abc123"
)
print(f"Status: {response.status_code}")
chars = response.json()['characteristics']
print(f"Budget Tier: {chars['budget_profile'].get('budget_tier')}")
print(f"Decision Style: {chars['decision_style']}")
print(f"Pain Points: {chars['pain_points']}")


# =============================================================================
# 2. PYTHON INTEGRATION WITH LLM
# =============================================================================

print("\n\n" + "=" * 80)
print("2. PYTHON LLM INTEGRATION PATTERN")
print("=" * 80)

from typing import Optional

class ChatPersonalizationClient:
    """Client for Chat Personalization Service"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
    
    def save_prompt(self, user_id: str, prompt_text: str, response_text: Optional[str] = None):
        """Save a user prompt"""
        data = {
            "user_id": user_id,
            "prompt_text": prompt_text,
            "response_text": response_text,
            "category": "travel"
        }
        response = requests.post(f"{self.base_url}/api/v1/prompts/save", json=data)
        return response.json()
    
    def get_llm_context(self, user_id: str) -> Optional[str]:
        """Get system context for LLM"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/context",
                json={"user_id": user_id}
            )
            if response.status_code == 200:
                return response.json()['system_context']
        except Exception as e:
            print(f"Error fetching context: {e}")
        return None
    
    def analyze_user(self, user_id: str):
        """Trigger analysis of user prompts"""
        response = requests.post(
            f"{self.base_url}/api/v1/analyze",
            json={"user_id": user_id}
        )
        return response.json()


# Usage Example with LLM
print("\nUsage with LLM:")
print("-" * 40)

client = ChatPersonalizationClient()

# Step 1: Get personalized context
user_id = "user_abc123"
system_context = client.get_llm_context(user_id)

if system_context:
    # Step 2: Use in LLM call
    llm_messages = [
        {"role": "system", "content": system_context},
        {"role": "user", "content": "What hotels would you recommend?"}
    ]
    print("System context prepared for LLM:")
    print(system_context[:300] + "...")
    
    # Step 3: After getting response, save it
    response_text = "Based on your preferences for luxury travel in Paris..."
    client.save_prompt(
        user_id=user_id,
        prompt_text="What hotels would you recommend?",
        response_text=response_text
    )


# =============================================================================
# 3. CURL EXAMPLES
# =============================================================================

print("\n\n" + "=" * 80)
print("3. CURL COMMAND EXAMPLES")
print("=" * 80)

examples = [
    {
        "name": "Health Check",
        "command": 'curl -X GET http://localhost:8001/health'
    },
    {
        "name": "Save Prompt",
        "command": '''curl -X POST http://localhost:8001/api/v1/prompts/save \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":"user123","prompt_text":"Find budget hotels in Thailand","category":"travel"}'
'''
    },
    {
        "name": "Get Prompts",
        "command": 'curl -X GET "http://localhost:8001/api/v1/prompts/user123?limit=10"'
    },
    {
        "name": "Analyze User",
        "command": '''curl -X POST http://localhost:8001/api/v1/analyze \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":"user123","force_reanalyze":false}'
'''
    },
    {
        "name": "Get LLM Context",
        "command": '''curl -X POST http://localhost:8001/api/v1/context \\
  -H "Content-Type: application/json" \\
  -d '{"user_id":"user123"}'
'''
    },
]

for example in examples:
    print(f"\n{example['name']}:")
    print(f"{example['command']}")


# =============================================================================
# 4. JAVASCRIPT/FETCH EXAMPLES
# =============================================================================

print("\n\n" + "=" * 80)
print("4. JAVASCRIPT/FETCH EXAMPLES")
print("=" * 80)

javascript_code = """
// 1. Save Prompt
async function savePrompt(userId, promptText) {
  const response = await fetch('http://localhost:8001/api/v1/prompts/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      prompt_text: promptText,
      category: 'travel'
    })
  });
  return response.json();
}

// 2. Get LLM Context
async function getLLMContext(userId) {
  const response = await fetch('http://localhost:8001/api/v1/context', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  });
  const data = await response.json();
  return {
    systemContext: data.system_context,
    interests: data.user_interests,
    preferences: data.key_characteristics
  };
}

// 3. Analyze User
async function analyzeUser(userId) {
  const response = await fetch('http://localhost:8001/api/v1/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId })
  });
  return response.json();
}

// 4. Get Characteristics
async function getCharacteristics(userId) {
  const response = await fetch(
    `http://localhost:8001/api/v1/characteristics/${userId}`
  );
  return response.json();
}

// Usage in chat application
async function chatWithPersonalization(userId, userMessage) {
  // 1. Save the user's message
  await savePrompt(userId, userMessage);
  
  // 2. Get personalized context
  const context = await getLLMContext(userId);
  
  // 3. Call your LLM with context
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      system_context: context.systemContext,
      user_message: userMessage,
      user_id: userId
    })
  });
  
  return response.json();
}
"""

print(javascript_code)


# =============================================================================
# 5. CHARACTERISTIC ANALYSIS OUTPUT EXAMPLE
# =============================================================================

print("\n\n" + "=" * 80)
print("5. CHARACTERISTIC ANALYSIS OUTPUT EXAMPLE")
print("=" * 80)

example_output = """
{
  "status": "success",
  "user_id": "user123",
  "prompts_analyzed": 15,
  "characteristics": {
    "user_id": "user123",
    "travel_preferences": {
      "preferred_destinations": ["Paris", "London", "Barcelona"],
      "travel_frequency": "regular",
      "preferred_transportation": ["flight", "train"],
      "accommodation_style": "hotel",
      "trip_duration_preference": "medium"
    },
    "budget_profile": {
      "budget_tier": "luxury",
      "price_sensitivity": "moderate",
      "willing_to_splurge": true,
      "look_for_deals": false
    },
    "booking_patterns": {
      "advance_booking_tendency": "advance",
      "group_size": "couple",
      "booking_flexibility": "flexible",
      "preferred_booking_channel": "online"
    },
    "interests": ["luxury", "cultural", "food"],
    "personality_traits": ["organized", "detail_oriented", "adventurous"],
    "pain_points": ["high_costs", "quality_assurance"],
    "motivation_drivers": ["quality_excellence", "learning_exploration"],
    "decision_style": "analytical",
    "tone_preference": "professional",
    "communication_style": "detailed",
    "detailed_summary": "This user is interested in luxury, cultural, and food travel 
      experiences. Preferred destinations include Paris, London, Barcelona. User has 
      a luxury travel budget and is willing to spend on premium experiences. Adopts an 
      analytical decision-making approach, researching thoroughly before booking. 
      Personality: organized, detail_oriented, adventurous. Key concerns: high_costs, 
      quality_assurance.",
    "confidence_score": 0.87,
    "last_analyzed_at": "2024-03-01T10:30:00Z"
  }
}
"""

print(example_output)


# =============================================================================
# 6. WORKFLOW SUMMARY
# =============================================================================

print("\n\n" + "=" * 80)
print("6. COMPLETE WORKFLOW SUMMARY")
print("=" * 80)

workflow = """
1. USER SIGNUP (Frontend)
   - User logs in with Google OAuth
   - Frontend gets: { google_id, email, name, picture }
   - Frontend creates user in your database
   - Frontend stores user_id locally

2. CHAT INTERACTION (Frontend + Backend)
   - User sends message in chat
   - Frontend saves prompt: POST /api/v1/prompts/save
   - Backend calls Chat Personalization Service
   - Service stores prompt in PostgreSQL

3. ANALYSIS (Periodic or On-Demand)
   - Backend or scheduled job: POST /api/v1/analyze
   - Service analyzes all user prompts (minimum 3)
   - Generates characteristics and stores in DB
   - Returns confidence score

4. LLM CONTEXT GENERATION (Per Request)
   - Backend: POST /api/v1/context with user_id
   - Service returns formatted system context
   - Backend prepends to LLM system message
   - LLM uses context for personalized response

5. CONTINUOUS LEARNING
   - Every new prompt saved updates analysis
   - Characteristics refined over time
   - Confidence score increases with more data

DATA FLOW:
   Frontend Chat UI
        |
        v
   Save Prompt (POST /api/v1/prompts/save)
        |
        v
   PostgreSQL (prompt_history table)
        |
        v
   Analyze (POST /api/v1/analyze)
        |
        v
   ML Analysis Engine
        |
        v
   PostgreSQL (user_characteristics table)
        |
        v
   Get Context (POST /api/v1/context)
        |
        v
   Backend LLM Call (with system context)
        |
        v
   Personalized Response
"""

print(workflow)


# =============================================================================
# 7. REQUIRED POSTMAN SETUP
# =============================================================================

print("\n\n" + "=" * 80)
print("7. POSTMAN COLLECTION SETUP")
print("=" * 80)

postman_setup = """
Import this collection into Postman:

BASE URL: http://localhost:8001

REQUESTS:

1. Health Check
   GET /health

2. Save Prompt
   POST /api/v1/prompts/save
   Body (JSON):
   {
       "user_id": "user123",
       "prompt_text": "I want luxury hotels in Paris",
       "response_text": "Here are luxury options...",
       "category": "travel",
       "tags": ["luxury", "paris"]
   }

3. Get User Prompts
   GET /api/v1/prompts/{{user_id}}?limit=10&offset=0

4. Analyze User
   POST /api/v1/analyze
   Body (JSON):
   {
       "user_id": "user123",
       "force_reanalyze": false
   }

5. Get LLM Context
   POST /api/v1/context
   Body (JSON):
   {
       "user_id": "user123"
   }

6. Get Characteristics
   GET /api/v1/characteristics/{{user_id}}

VARIABLES:
   user_id = user123
   base_url = http://localhost:8001
"""

print(postman_setup)


# =============================================================================
# 8. ERROR HANDLING AND BEST PRACTICES
# =============================================================================

print("\n\n" + "=" * 80)
print("8. ERROR HANDLING AND BEST PRACTICES")
print("=" * 80)

error_handling = """
ERROR RESPONSES:

1. User Not Found (404)
   {
     "detail": "User user123 not found"
   }
   Solution: Create user in user_profile table first

2. No Characteristics Found (404)
   {
     "detail": "No characteristics found for user user123. Run analysis first."
   }
   Solution: Save at least 3 prompts, then run analyze

3. No Prompts Found (400)
   {
     "detail": "No prompts found for user user123"
   }
   Solution: Save prompts before analyzing

4. Internal Server Error (500)
   {
     "detail": "Error analyzing prompts: ..."
   }
   Solution: Check logs, verify database connection

BEST PRACTICES:

1. Save prompts after each user interaction
2. Analyze periodically (daily or weekly)
3. Cache LLM context for 1 hour per user
4. Handle 404s gracefully (no context = default behavior)
5. Monitor confidence_score (>0.7 = high quality)
6. Use tags to categorize prompts for better analysis
7. Test with at least 5-10 diverse prompts before relying on characteristics
8. Implement rate limiting on analyze endpoint
9. Log all API calls for audit trail
10. Use HTTPS in production
"""

print(error_handling)

print("\n" + "=" * 80)
print("END OF EXAMPLES")
print("=" * 80)
