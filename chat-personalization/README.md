# Chat Personalization Service

A production-ready FastAPI service that analyzes user chat prompt history from Google OAuth authenticated users and generates detailed user characteristics for LLM context personalization.

---

## Features

- **Google OAuth Integration** — Ready for frontend Google OAuth integration
- **Prompt History Storage** — Stores all user prompts in PostgreSQL
- **Intelligent Analysis** — ML-based analysis of prompt patterns
- **User Characteristics** — Generates detailed summaries of user preferences and behavior
- **LLM Context Generation** — Provides formatted context for LLM system prompts
- **Confidence Scoring** — Includes confidence metrics for analysis reliability
- **Real-time Updates** — Updates characteristics as new prompts arrive
- **Caching Support** — Optimized for fast context retrieval

---

## Architecture

```
chat-personalization/
├── app/
│   ├── ml/
│   │   ├── __init__.py
│   │   └── analyzer.py          # Prompt analysis engine
│   ├── prisma/
│   │   └── schema.prisma        # Database schema
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── db.py                    # Database connection
│   ├── main.py                  # FastAPI application & routes
│   └── models.py                # Pydantic models
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Database Schema

### Tables

1. **user_profile** — User information from Google OAuth
   - Fields: user_id, google_email, google_id, name, picture_url, locale, timestamps

2. **prompt_history** — All user chat prompts
   - Fields: id, user_id, prompt_text, response_text, category, tags, timestamp
   - Indexes: (user_id, timestamp), (user_id, domain)

3. **user_characteristics** — Analyzed user profile
   - Fields: 
     - travel_preferences (JSON)
     - budget_profile (JSON)
     - booking_patterns (JSON)
     - interests, personality_traits, pain_points, motivation_drivers (arrays)
     - decision_style, tone_preference, communication_style
     - detailed_summary (text)
     - confidence_score, last_analyzed_at

4. **analysis_logs** — Audit trail of analyses
   - Fields: id, user_id, analysis_type, prompts_analyzed, confidence, key_insights

---

## Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone and navigate:**
   ```bash
   cd chat-personalization
   ```

2. **Create and activate virtual environment:**
   ```bash
   # Windows
   python -m venv .venv
   .\.venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials
   ```

5. **Setup database:**
   ```bash
   # Generate and run Prisma migrations
   prisma migrate dev --name init
   ```

6. **Run the service:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8001
   ```

### Docker Setup

1. **Build and start:**
   ```bash
   docker-compose up -d
   ```

2. **Check status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f chat-personalization-api
   ```

---

## API Endpoints

### Health Check
```
GET /health
```
Returns: `{ status, service, version, timestamp }`

### Prompt Management

**Save Prompt:**
```
POST /api/v1/prompts/save
Body: {
  "user_id": "user123",
  "prompt_text": "I need luxury 5-star hotels in Paris for a business trip",
  "response_text": "Optional response text",
  "category": "travel",
  "tags": ["business", "paris", "luxury"]
}
```

**Get User Prompts:**
```
GET /api/v1/prompts/{user_id}?limit=50&offset=0
```

### Analysis

**Analyze User Prompts:**
```
POST /api/v1/analyze
Body: {
  "user_id": "user123",
  "force_reanalyze": false
}
```

Returns: Analyzed characteristics with confidence score

### LLM Context

**Get Full LLM Context:**
```
POST /api/v1/context
Body: {
  "user_id": "user123",
  "include_full_history": false,
  "max_context_tokens": 2000
}
```

Returns: System context ready for LLM, with formatted summary

**Get Characteristics Only:**
```
GET /api/v1/characteristics/{user_id}
```

Returns: Structured characteristics without full context

---

## User Characteristics Output

Generated characteristics include:

```json
{
  "user_id": "user123",
  "travel_preferences": {
    "preferred_destinations": ["Paris", "London", "Dubai"],
    "travel_frequency": "regular",
    "accommodation_style": "hotel",
    "trip_duration_preference": "medium"
  },
  "budget_profile": {
    "budget_tier": "luxury",
    "price_sensitivity": "low",
    "willing_to_splurge": true
  },
  "interests": ["luxury", "cultural", "business"],
  "personality_traits": ["organized", "detail_oriented", "social"],
  "pain_points": ["high_costs", "booking_risk"],
  "motivation_drivers": ["quality_excellence", "memorable_experiences"],
  "decision_style": "analytical",
  "tone_preference": "professional",
  "communication_style": "detailed",
  "detailed_summary": "This user is interested in luxury, cultural, and business travel...",
  "confidence_score": 0.85
}
```

---

## LLM Context Example

When `GET /api/v1/context` is called, the response includes a `system_context` field formatted like:

```
You are assisting a user with the following profile:

Name: John Doe

## User Characteristics
This user is interested in luxury, cultural, and business travel experiences. 
Preferred destinations include Paris, London, Dubai. User has a luxury travel 
budget and is willing to spending on premium experiences...

## Key Preferences
- Travel Style: luxury, cultural, business
- Budget Tier: luxury
- Decision Style: analytical
- Communication Preference: professional

## Personality Traits
organized, detail_oriented, social

## Pain Points
high_costs, booking_risk

## What Motivates Them
quality_excellence, memorable_experiences

Use this context to provide personalized responses that align with their preferences 
and communication style.
```

---

## Integration with Frontend

### Step 1: User Signup/Login
```javascript
// Frontend: Google OAuth login
const googleUser = handleGoogleLogin();

// Frontend: Save user to your backend
await fetch('/api/users/google-auth', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    google_id: googleUser.id,
    google_email: googleUser.email,
    name: googleUser.name,
    picture_url: googleUser.picture
  })
});
```

### Step 2: Save Prompts
```javascript
// Frontend: After user sends a chat prompt
await fetch('http://localhost:8001/api/v1/prompts/save', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: currentUser.id,
    prompt_text: userMessage,
    response_text: aiResponse,
    category: "travel"
  })
});
```

### Step 3: Get LLM Context
```python
# Backend: Before calling LLM
import requests

context_response = requests.post(
    'http://localhost:8001/api/v1/context',
    json={'user_id': user_id}
)

context = context_response.json()
system_context = context['system_context']

# Use in LLM call:
# messages = [
#   {"role": "system", "content": system_context},
#   {"role": "user", "content": user_prompt}
# ]
```

---

## Configuration

Edit `.env` to customize:

- `DATABASE_URL` — PostgreSQL connection string
- `MAX_CONTEXT_LENGTH` — Max tokens for LLM context
- `MIN_PROMPTS_FOR_ANALYSIS` — Minimum prompts before analysis
- `ENABLE_SENTIMENT_ANALYSIS` — Enable sentiment scoring
- `ENABLE_CONTEXT_CACHING` — Cache characteristics

---

## Troubleshooting

**Error: "No characteristics found"**
- Solution: Run analysis endpoint first with at least 3 prompts

**Error: "User not found"**
- Ensure user_profile is created before saving prompts

**Database connection error**
- Check DATABASE_URL in .env
- Verify PostgreSQL is running
- Test: `psql -U user -d chat_personalization`

---

## Performance Considerations

- Analysis runs on first request or can be scheduled
- Characteristics are cached for 24 hours
- Prompt history queries use database indexes
- LLM context generation is sub-100ms

---

## Security Notes

- All API endpoints should require authentication in production
- User IDs should be validated against auth tokens
- DATABASE_URL should use environment variables
- Never commit .env to version control

---

## Support & Documentation

- API Docs (Swagger): `http://localhost:8001/docs`
- ReDoc: `http://localhost:8001/redoc`
- Health Check: `curl http://localhost:8001/health`

---

## License

Built for TBO Hackathon
