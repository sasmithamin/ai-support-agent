# 📘 Usage Guide

## Basic Usage

### 1. Start the Server

```bash
python scripts/run_server.py
```

Server will run at `http://localhost:8000`

### 2. Test with cURL

```bash
# Simple chat
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I reset my password?", "user_id": "test_user"}'

# Get ticket details
curl "http://localhost:8000/api/tickets/1"

# Search knowledge base
curl "http://localhost:8000/api/knowledge/search?query=password&top_k=3"

# Get statistics
curl "http://localhost:8000/api/knowledge/stats"
```

### 3. Use Interactive API Docs

Visit: `http://localhost:8000/docs`

## Advanced Usage

### Add Custom Knowledge

```python
import requests

response = requests.post(
    "http://localhost:8000/api/knowledge/upload",
    json={
        "title": "Custom Guide",
        "content": "Your content here...",
        "category": "custom"
    }
)
```

### Load from Files

```bash
# Load all .txt and .md files from a directory
python scripts/load_knowledge.py --directory ./my-docs/
```

### Integrate with Website

See the HTML/React examples in the main README.

## Testing Scenarios

### Test 1: Password Reset
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I forgot my password", "user_id": "user1"}'
```

Expected: High confidence, knowledge_search tool used, no escalation

### Test 2: Billing Issue
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "I was charged twice this month!", "user_id": "user2"}'
```

Expected: Negative sentiment, automatic escalation, urgent priority

### Test 3: General Question
```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{"message": "What plans do you offer?", "user_id": "user3"}'
```

Expected: Neutral sentiment, knowledge_search tool, no escalation

## Configuration Tips

### Adjust Escalation Sensitivity

In `.env`:
```bash
# Lower = more escalations (0.0 - 1.0)
AUTO_ESCALATION_THRESHOLD=0.3  # Default
AUTO_ESCALATION_THRESHOLD=0.5  # Less sensitive
AUTO_ESCALATION_THRESHOLD=0.2  # More sensitive
```

### Tune RAG Parameters

```bash
# Number of similar documents to retrieve
SIMILARITY_TOP_K=5

# Minimum similarity score (0.0 - 1.0)
SIMILARITY_THRESHOLD=0.7

# Chunk size for documents
CHUNK_SIZE=1000
```

### Switch LLM Provider

```bash
# Option 1: Use OpenAI
USE_LOCAL_LLM=False
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview

# Option 2: Use Gemini
USE_LOCAL_LLM=False
GOOGLE_API_KEY=...
GEMINI_MODEL=gemini-1.5-pro

# Option 3: Use Ollama (default)
USE_LOCAL_LLM=True
OLLAMA_MODEL=llama3.1:8b
```

## Monitoring

### Check System Health

```bash
curl http://localhost:8000/health
```

### View Statistics

```bash
curl http://localhost:8000/api/knowledge/stats
```

Response:
```json
{
  "total_tickets": 150,
  "open_tickets": 23,
  "resolved_tickets": 127,
  "average_sentiment": 0.15,
  "vector_store_documents": 6,
  "registered_tools": 3
}
```

### Database Queries

```python
# Connect to SQLite
import sqlite3
conn = sqlite3.connect('./data/support_agent.db')

# Get ticket stats
cursor = conn.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status")
for row in cursor:
    print(row)
```

## Troubleshooting

### Issue: "No relevant information found"

**Solution**: Load more knowledge documents
```bash
python scripts/load_knowledge.py
```

### Issue: Slow responses

**Solutions**:
1. Use cloud LLM (OpenAI/Gemini) instead of Ollama
2. Reduce `SIMILARITY_TOP_K` in .env
3. Use smaller Ollama model (llama3.1:8b instead of 70b)

### Issue: Database locked

**Solution**: Restart the server
```bash
# Kill existing process
pkill -f "run_server"

# Restart
python scripts/run_server.py
```

### Issue: Import errors

**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

## Best Practices

1. **Always test locally first** before deploying
2. **Monitor sentiment scores** to improve knowledge base
3. **Review escalated tickets** to identify gaps
4. **Update knowledge regularly** as products change
5. **Set up logging** to track performance
6. **Use HTTPS** in production
7. **Rate limit** API endpoints
8. **Backup database** regularly

## Production Checklist

- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper logging (not just console)
- [ ] Configure CORS for your domain
- [ ] Add authentication/API keys
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Enable HTTPS
- [ ] Set DEBUG=False
- [ ] Use production LLM (not Ollama)
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Add error tracking (Sentry)
- [ ] Set up CI/CD pipeline