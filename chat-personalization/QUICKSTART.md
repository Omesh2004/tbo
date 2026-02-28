# Quick Start Guide - Chat Personalization Service

## 1. Start the Service (Docker - Recommended)

```bash
cd chat-personalization
docker-compose up -d
```

Service runs on: `http://localhost:8001`
Database: **PostgreSQL** on `localhost:5433`

## 2. Create User Profile (One-time)

Before saving prompts, create a user profile:

```bash
curl -X POST http://localhost:8001/api/v1/users/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_abc123",
    "google_email": "user@gmail.com",
    "google_id": "google_12345",
    "name": "John Doe",
    "picture_url": "https://..."
  }'
```

## 3. Save User Prompts

```bash
curl -X POST http://localhost:8001/api/v1/prompts/save \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_abc123",
    "prompt_text": "I need luxury 5-star hotels in Paris",
    "response_text": "I found these options...",
    "category": "travel",
    "tags": ["luxury", "paris"]
  }'
```

Save at least 3-5 prompts with different topics for better analysis.

## 4. Analyze User Prompts

```bash
curl -X POST http://localhost:8001/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_abc123"
  }'
```

Response includes:
- Travel preferences
- Budget profile
- Interests
- Personality traits
- Detailed summary
- Confidence score (0.0-1.0)

## 5. Get LLM Context

```bash
curl -X POST http://localhost:8001/api/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_abc123"
  }'
```

Response includes:
- `system_context`: Ready for LLM system prompt
- `user_interests`: Array of interests
- `key_characteristics`: Structured preferences
- `confidence_score`: Analysis quality metric

## 6. Use in Your LLM Chat

### Python Example:
```python
import requests
import openai

# Get personalized context
context_response = requests.post(
    'http://localhost:8001/api/v1/context',
    json={'user_id': 'user_abc123'}
)
context = context_response.json()

# Call LLM with user context
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": context['system_context']},
        {"role": "user", "content": "What hotels do you recommend?"}
    ]
)

# Save the exchange
requests.post(
    'http://localhost:8001/api/v1/prompts/save',
    json={
        'user_id': 'user_abc123',
        'prompt_text': 'What hotels do you recommend?',
        'response_text': response.choices[0].message.content
    }
)
```

### JavaScript Example:
```javascript
// Get context
const contextRes = await fetch('http://localhost:8001/api/v1/context', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ user_id: 'user_abc123' })
});
const context = await contextRes.json();

// Use in chat
const chatRes = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    system_context: context.system_context,
    user_message: "What hotels do you recommend?",
    user_id: 'user_abc123'
  })
});
```

## API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/v1/prompts/save` | POST | Save user prompt |
| `/api/v1/prompts/{user_id}` | GET | Get user's prompt history |
| `/api/v1/analyze` | POST | Analyze user prompts & generate characteristics |
| `/api/v1/context` | POST | Get LLM context for user |
| `/api/v1/characteristics/{user_id}` | GET | Get user characteristics (without full context) |

## Testing Workflow

1. **Health check:**
   ```bash
   curl http://localhost:8001/health
   ```

2. **Create user (in your database):**
   ```bash
   # Create user_profile in PostgreSQL
   ```

3. **Save 3+ prompts:**
   ```bash
   for i in {1..5}; do
     curl -X POST http://localhost:8001/api/v1/prompts/save \
       -H "Content-Type: application/json" \
       -d "{\"user_id\":\"user_test\",\"prompt_text\":\"Sample prompt $i\",\"category\":\"travel\"}"
   done
   ```

4. **Analyze:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/analyze \
     -H "Content-Type: application/json" \
     -d '{"user_id":"user_test"}'
   ```

5. **Get context:**
   ```bash
   curl -X POST http://localhost:8001/api/v1/context \
     -H "Content-Type: application/json" \
     -d '{"user_id":"user_test"}'
   ```

## Configuration

Edit `.env` to customize:
- `DATABASE_URL` - PostgreSQL connection
- `MAX_CONTEXT_LENGTH` - Max LLM context size (default: 2000 tokens)
- `MIN_PROMPTS_FOR_ANALYSIS` - Minimum prompts before analysis (default: 3)

## Stopping the Service

```bash
docker-compose down
```

## Logs

```bash
docker-compose logs -f chat-personalization-api
```

## Resetting Everything

```bash
docker-compose down -v  # Removes volumes too
docker-compose up -d    # Fresh start
```

---

**Ready!** Start saving prompts and analyzing user behavior with LLM personalization.
