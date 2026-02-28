# Database Setup Guide - Chat Personalization Service

## Option 1: Using Docker Compose (Recommended)

Docker Compose automatically creates and initializes the PostgreSQL database.

```bash
cd chat-personalization
docker-compose up -d
```

The database will be created at `postgresql://chat_user:chat_password@localhost:5433/chat_personalization`

## Option 2: Manual PostgreSQL Setup

### Step 1: Create Database and User

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql shell:
CREATE USER chat_user WITH PASSWORD 'chat_password';
CREATE DATABASE chat_personalization OWNER chat_user;
```

### Step 2: Run Prisma Migrations

```bash
cd chat-personalization

# Generate Prisma client
prisma generate

# Run migrations
prisma migrate dev --name init
```

### Step 3: Set Environment Variable

Create `.env` file:
```
DATABASE_URL=postgresql://chat_user:chat_password@localhost:5432/chat_personalization
```

## Database Schema Overview

### user_profile Table
Stores Google OAuth user information
```sql
- user_id (STRING, PRIMARY KEY)
- google_email (STRING, UNIQUE)
- google_id (STRING, UNIQUE)
- name (STRING)
- picture_url (STRING, NULLABLE)
- locale (STRING, DEFAULT: 'en')
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- last_active_at (TIMESTAMP)
```

### prompt_history Table
Stores all user chat prompts
```sql
- id (STRING, PRIMARY KEY)
- user_id (STRING, FOREIGN KEY)
- prompt_text (TEXT)
- response_text (TEXT, NULLABLE)
- category (STRING, DEFAULT: 'general')
- intent (STRING, NULLABLE)
- domain (STRING, DEFAULT: 'travel')
- tags (STRING ARRAY)
- sentiment (STRING, DEFAULT: 'neutral')
- timestamp (TIMESTAMP, DEFAULT: NOW())

INDEXES:
- (user_id, timestamp)
- (user_id, domain)
```

### user_characteristics Table
Stores analyzed user profile data
```sql
- id (STRING, PRIMARY KEY)
- user_id (STRING, UNIQUE, FOREIGN KEY)
- travel_preferences (JSON)
- budget_profile (JSON)
- booking_patterns (JSON)
- interests (STRING ARRAY)
- risk_tolerance (STRING)
- decision_style (STRING)
- personality_traits (STRING ARRAY)
- pain_points (STRING ARRAY)
- motivation_drivers (STRING ARRAY)
- tone_preference (STRING)
- communication_style (STRING)
- preferred_features (STRING ARRAY)
- detailed_summary (TEXT)
- total_prompts (INT)
- avg_sentiment (FLOAT)
- confidence_score (FLOAT)
- last_analyzed_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### analysis_logs Table
Audit trail of user analyses
```sql
- id (STRING, PRIMARY KEY)
- user_id (STRING)
- analysis_type (STRING)
- prompts_analyzed (INT)
- confidence (FLOAT)
- key_insights (JSON)
- created_at (TIMESTAMP)

INDEXES:
- (user_id, created_at)
```

## Verifying Setup

### 1. Check Docker Status
```bash
docker-compose ps
```

Should show:
- postgres (healthy)
- chat-personalization-api (healthy)

### 2. Test Database Connection
```bash
# From docker
docker-compose exec postgres psql -U chat_user -d chat_personalization -c "SELECT 1;"

# From local psql (if installed)
psql postgresql://chat_user:chat_password@localhost:5433/chat_personalization
```

### 3. Test API Health
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "Chat Personalization Service",
  "version": "1.0.0",
  "timestamp": "2024-03-01T10:30:00"
}
```

### 4. Create Test User
```bash
curl -X POST http://localhost:8001/api/v1/users/create \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "google_email": "test@gmail.com",
    "google_id": "google_12345",
    "name": "Test User"
  }'
```

## Troubleshooting

### Database Connection Error
```
Error: connect ECONNREFUSED 127.0.0.1:5433
```

Solution:
```bash
# Ensure PostgreSQL container is running
docker-compose up -d postgres

# Check logs
docker-compose logs postgres
```

### Prisma Migration Error
```
Error: P1000 Authentication failed
```

Solution:
1. Check DATABASE_URL in .env
2. Verify PostgreSQL is running
3. Recreate database: `docker-compose down -v && docker-compose up -d`

### Port Already in Use
If port 5433 is already in use, edit `docker-compose.yml`:
```yaml
postgres:
  ports:
    - "5434:5432"  # Change 5433 to 5434

# And update DATABASE_URL in .env
DATABASE_URL=postgresql://chat_user:chat_password@localhost:5434/chat_personalization
```

## Database Backups

### Create Backup
```bash
docker-compose exec postgres pg_dump -U chat_user chat_personalization > backup.sql
```

### Restore from Backup
```bash
docker-compose exec -T postgres psql -U chat_user chat_personalization < backup.sql
```

## Monitoring Database

### Connect to Database Shell
```bash
docker-compose exec postgres psql -U chat_user -d chat_personalization
```

### Useful Commands
```sql
-- List tables
\dt

-- Check user_profile count
SELECT COUNT(*) FROM user_profile;

-- Check prompts for user
SELECT COUNT(*) FROM prompt_history WHERE user_id = 'user123';

-- Check characteristics
SELECT * FROM user_characteristics WHERE user_id = 'user123';

-- View recent prompts
SELECT prompt_text, timestamp FROM prompt_history 
ORDER BY timestamp DESC LIMIT 10;
```

## Resetting Database

### Option 1: Keep Data
```bash
docker-compose restart postgres
```

### Option 2: Delete Everything (Fresh Start)
```bash
docker-compose down -v
docker-compose up -d
```

## Advanced: Custom Database Configuration

Edit `docker-compose.yml` before starting:

```yaml
postgres:
  environment:
    POSTGRES_USER: your_user
    POSTGRES_PASSWORD: your_password
    POSTGRES_DB: your_database
  ports:
    - "your_port:5432"
```

Update `.env`:
```
DATABASE_URL=postgresql://your_user:your_password@localhost:your_port/your_database
```

## Next Steps

Once database is verified:
1. Start saving user prompts
2. Analyze at least 3-5 prompts per user
3. Test LLM context generation
4. Integrate with your chat application

See [QUICKSTART.md](./QUICKSTART.md) for API usage.
