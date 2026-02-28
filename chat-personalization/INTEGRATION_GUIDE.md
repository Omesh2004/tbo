# Integration Guide - Chat Personalization with Your LLM Chat System

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Your Frontend (React/Vue/etc)             │
│  - Google OAuth Login                                        │
│  - Chat Interface                                            │
│  - Save prompts to backend                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        v                                 v
┌──────────────────────┐      ┌─────────────────────────────┐
│  Your Backend/API    │      │ Chat Personalization Service │
│  (Node/Python/etc)   │      │  (Port 8001)                │
│                      │      │                             │
│ - Handle auth        │      │ - Store prompt history      │
│ - Route chat msgs    │      │ - Analyze user patterns     │
│ - Call LLM           │      │ - Generate characteristics  │
└──────────────────────┘      │ - Provide LLM context       │
        │                     └──────────┬──────────────────┘
        │                                │
        │                  ┌─────────────┴─────────────┐
        │                  │                           │
        v                  v                           v
    ┌────────────┐    ┌──────────────┐     ┌──────────────────┐
    │   OpenAI   │    │ PostgreSQL   │     │  Your Existing   │
    │   GPT-4    │    │  (Port 5433) │     │  Data Services   │
    └────────────┘    └──────────────┘     └──────────────────┘
```

## Step 1: Frontend Integration (Google OAuth)

### React Example with Google OAuth

```javascript
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import axios from 'axios';

const ChatApp = () => {
  const [user, setUser] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  // Handle Google OAuth login
  const handleGoogleLogin = async (credentialResponse) => {
    const token = credentialResponse.credential;
    
    // Decode JWT (install: npm install jwt-decode)
    const decoded = jwtDecode(token);
    const userData = {
      user_id: decoded.sub,
      google_email: decoded.email,
      google_id: decoded.sub,
      name: decoded.name,
      picture_url: decoded.picture,
      locale: navigator.language
    };

    // 1. Create user in personalization service
    await axios.post(
      'http://localhost:8001/api/v1/users/create',
      userData
    );

    setUser(userData);
    localStorage.setItem('user_id', userData.user_id);
  };

  // Handle sending chat message
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // 1. Add message to UI
    const userMsg = input;
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');

    try {
      // 2. Get personalized LLM context
      const contextRes = await axios.post(
        'http://localhost:8001/api/v1/context',
        { user_id: user.user_id }
      );
      const { system_context } = contextRes.data;

      // 3. Call your backend LLM endpoint
      const llmRes = await axios.post('/api/chat', {
        user_id: user.user_id,
        user_message: userMsg,
        system_context: system_context
      });

      const assistantMsg = llmRes.data.response;
      setMessages(prev => [...prev, { role: 'assistant', content: assistantMsg }]);

      // 4. Save prompt to personalization service
      await axios.post(
        'http://localhost:8001/api/v1/prompts/save',
        {
          user_id: user.user_id,
          prompt_text: userMsg,
          response_text: assistantMsg,
          category: 'chat'
        }
      );

    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, there was an error.' 
      }]);
    }
  };

  return (
    <div className="chat-app">
      {!user ? (
        <GoogleOAuthProvider clientId="YOUR_GOOGLE_CLIENT_ID">
          <GoogleLogin onSuccess={handleGoogleLogin} />
        </GoogleOAuthProvider>
      ) : (
        <div>
          <h1>Chat with {user.name}</h1>
          <div className="messages">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.role}`}>
                {msg.content}
              </div>
            ))}
          </div>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type your message..."
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      )}
    </div>
  );
};

export default ChatApp;
```

## Step 2: Backend Integration

### Python/FastAPI Example

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from openai import AsyncOpenAI

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clients
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
personalization_client = httpx.AsyncClient(
    base_url="http://localhost:8001"
)

@app.post("/api/chat")
async def chat_endpoint(request: dict):
    """
    Chat endpoint that uses personalization context
    """
    user_id = request.get("user_id")
    user_message = request.get("user_message")
    system_context = request.get("system_context")
    
    if not all([user_id, user_message, system_context]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    try:
        # Call OpenAI with personalized system context
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        assistant_response = response.choices[0].message.content
        
        return {
            "response": assistant_response,
            "user_id": user_id,
            "status": "success"
        }
    
    except Exception as e:
        print(f"LLM Error: {e}")
        raise HTTPException(status_code=500, detail="LLM Processing Error")


@app.post("/api/users/google-auth")
async def google_auth(user_data: dict):
    """
    Create user in both your backend and personalization service
    """
    # 1. Save to your user database
    # await your_db.users.create({...})
    
    # 2. Create in personalization service
    response = await personalization_client.post(
        "/api/v1/users/create",
        json=user_data
    )
    
    return {
        "status": "success",
        "user_id": user_data.get("user_id")
    }
```

### Node.js/Express Example

```javascript
const express = require('express');
const axios = require('axios');
const { OpenAI } = require('openai');

const app = express();
app.use(express.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const personalizationApi = axios.create({
  baseURL: 'http://localhost:8001'
});

// Chat endpoint with personalization
app.post('/api/chat', async (req, res) => {
  try {
    const { user_id, user_message, system_context } = req.body;

    // Call OpenAI with personalized context
    const completion = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        { role: 'system', content: system_context },
        { role: 'user', content: user_message }
      ],
      temperature: 0.7,
      max_tokens: 500
    });

    const assistantResponse = completion.choices[0].message.content;

    res.json({
      response: assistantResponse,
      user_id: user_id,
      status: 'success'
    });

  } catch (error) {
    console.error('LLM Error:', error);
    res.status(500).json({ error: 'LLM Processing Error' });
  }
});

// Google OAuth user creation
app.post('/api/users/google-auth', async (req, res) => {
  try {
    const userData = req.body;

    // 1. Save to your database
    // await yourDB.users.create(userData)

    // 2. Create in personalization service
    await personalizationApi.post('/api/v1/users/create', userData);

    res.json({
      status: 'success',
      user_id: userData.user_id
    });

  } catch (error) {
    console.error('Auth Error:', error);
    res.status(500).json({ error: 'Authentication failed' });
  }
});

app.listen(3001, () => {
  console.log('Backend running on port 3001');
});
```

## Step 3: Scheduled Analysis

To periodically analyze user prompts and update characteristics:

### Python Scheduled Job

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import httpx
import asyncio

scheduler = AsyncIOScheduler()

async def analyze_all_users():
    """Analyze all users daily"""
    personalization_client = httpx.AsyncClient(
        base_url="http://localhost:8001"
    )
    
    # Get all users from your database
    users = await get_all_users()  # Your DB call
    
    for user in users:
        try:
            response = await personalization_client.post(
                "/api/v1/analyze",
                json={
                    "user_id": user.id,
                    "force_reanalyze": False
                }
            )
            print(f"Analysis complete for {user.id}: {response.json()}")
        except Exception as e:
            print(f"Error analyzing {user.id}: {e}")

# Schedule daily analysis at 2 AM
scheduler.add_job(
    analyze_all_users,
    'cron',
    hour=2,
    minute=0,
    id='daily_user_analysis'
)

scheduler.start()
```

### Node.js Scheduled Job

```javascript
const cron = require('node-cron');
const axios = require('axios');

const personalizationApi = axios.create({
  baseURL: 'http://localhost:8001'
});

// Run analysis daily at 2 AM
cron.schedule('0 2 * * *', async () => {
  console.log('Starting daily user analysis...');
  
  try {
    // Get all users from your database
    const users = await getAllUsers();  // Your DB call
    
    for (const user of users) {
      try {
        const response = await personalizationApi.post('/api/v1/analyze', {
          user_id: user.id,
          force_reanalyze: false
        });
        console.log(`Analysis complete for ${user.id}`);
      } catch (error) {
        console.error(`Error analyzing ${user.id}:`, error);
      }
    }
  } catch (error) {
    console.error('Daily analysis error:', error);
  }
});
```

## Step 4: Error Handling

```python
# Python/FastAPI
from typing import Optional

async def get_llm_context(user_id: str) -> Optional[str]:
    """Get LLM context with fallback"""
    try:
        response = await personalization_client.post(
            "/api/v1/context",
            json={"user_id": user_id},
            timeout=5.0
        )
        if response.status_code == 200:
            return response.json()['system_context']
        else:
            # Fallback if user has no characteristics
            return "Be helpful and personalized based on user preferences."
    except Exception as e:
        print(f"Personalization error (using default): {e}")
        # Fallback to default system prompt
        return "You are a helpful travel assistant."
```

## Step 5: Monitoring & Analytics

```python
# Track personalization effectiveness
async def log_personalization_usage(user_id: str, confidence_score: float):
    """Log how often personalization is used"""
    await db.personalization_logs.create({
        "user_id": user_id,
        "used_at": datetime.now(),
        "confidence_score": confidence_score,
        "request_type": "llm_context"
    })

# Monitor response quality by confidence score
async def get_personalization_stats():
    """Get stats on personalization usage"""
    stats = {
        "avg_confidence": await db.personalization_logs.aggregate([
            {"$group": {"_id": None, "avg": {"$avg": "$confidence_score"}}}
        ]),
        "users_with_characteristics": await db.user_characteristics.count(),
        "total_prompts_analyzed": await db.prompt_history.count()
    }
    return stats
```

## File Structure in Your Project

```
your-chat-app/
├── frontend/               (React/Vue)
│   ├── src/
│   │   ├── components/
│   │   │   └── Chat.js     (Uses Google OAuth + personalization)
│   │   └── services/
│   │       └── api.js      (Axios config for both services)
│   └── package.json
│
├── backend/                (Your API)
│   ├── routes/
│   │   └── chat.js         (LLM endpoint with context)
│   ├── services/
│   │   └── personalization.js  (Wrapper for personalization API)
│   ├── jobs/
│   │   └── analyzeUsers.js (Scheduled analysis)
│   └── package.json
│
└── chat-personalization/   (This service)
    ├── app/
    │   ├── main.py
    │   ├── ml/
    │   └── ...
    └── docker-compose.yml
```

## Deployment Notes

### Local Development
```bash
# Terminal 1: Chat Personalization Service
cd chat-personalization
docker-compose up -d

# Terminal 2: Your Backend
npm start  # or python -m uvicorn...

# Terminal 3: Your Frontend
npm start  # React/Vue dev server
```

### Production
1. Deploy Chat Personalization Service separately
2. Update backend to use production URL (not localhost:8001)
3. Use environment variables for API URLs
4. Add authentication/API keys for personalization service
5. Use HTTPS for all endpoints

## Security Considerations

1. **Authentication**: Add API key or OAuth to personalization service
2. **User Validation**: Verify user_id in JWT before calling personalization
3. **Rate Limiting**: Implement on analysis endpoint
4. **Data Privacy**: Ensure GDPR compliance for user prompt storage
5. **HTTPS**: Use HTTPS in production
6. **Secrets**: Never commit API keys or database URLs

---

Need help? Check:
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide
- [README.md](./README.md) - Full documentation
- [DATABASE_SETUP.md](./DATABASE_SETUP.md) - Database setup
