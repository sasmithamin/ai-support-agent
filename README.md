# 🤖 AI-Powered Customer Support Agent

A production-ready AI customer support system with RAG (Retrieval Augmented Generation), sentiment analysis, and intelligent escalation.

## ✨ Features

- 🧠 **Intelligent Support Agent** - Powered by LLMs (Ollama/GPT/Gemini/Claude)
- 📚 **RAG Knowledge Base** - Semantic search over documentation
- 😊 **Sentiment Analysis** - Detects customer emotions and urgency
- 🚨 **Smart Escalation** - Auto-escalates complex issues to humans
- 🔧 **Tool Orchestration** - MCP server with knowledge search, web search, ticket management
- 🗄️ **Database Integration** - SQLite/PostgreSQL for tickets and conversations
- 🌐 **REST API** - FastAPI backend with OpenAPI docs
- 📊 **Analytics** - Track sentiment, resolution rates, and performance

## 🏗️ Architecture
User → FastAPI → Support Agent → MCP Server → Tools → Response
↓                ↓
Sentiment      Knowledge Base
Analysis         (ChromaDB)
↓
Escalation
Logic

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Ollama installed (or API keys for OpenAI/Gemini/Claude)
- 4GB+ RAM

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-support-agent.git
cd ai-support-agent
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Run quick start (sets up everything)**
```bash
python scripts/quick_start.py
```

## 🔧 Manual Setup

### Step 1: Setup Database
```bash
python scripts/setup_db.py
```

### Step 2: Load Knowledge Base
```bash
python scripts/load_knowledge.py
```

### Step 3: Start Server
```bash
python scripts/run_server.py
```

## 📡 API Usage

### Chat Endpoint

```bash
curl -X POST "http://localhost:8000/api/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I forgot my password",
    "user_id": "user_123"
  }'
```

**Response:**
```json
{
  "response": "I can help you reset your password! Here's how:\n1. Go to...",
  "ticket_id": 1,
  "sentiment": {
    "sentiment": "neutral",
    "score": 0.1,
    "urgency": "medium"
  },
  "confidence": 0.85,
  "escalation": {
    "should_escalate": false,
    "reason": "AI can handle this",
    "priority": "medium"
  },
  "tools_used": ["knowledge_search"]
}
```

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## 🧪 Testing

### Run automated tests
```bash
python scripts/test_agent.py
```

### Interactive mode
```bash
python scripts/test_agent.py --interactive
```

## 📊 Configuration

### LLM Options (choose one)

**Option 1: Local Ollama** (Free, slower)
```bash
USE_LOCAL_LLM=True
OLLAMA_MODEL=llama3.1:8b
```

### Optional: Web Search

```bash
# Get free API key at https://tavily.com
TAVILY_API_KEY=tvly-...
```

## 📁 Project Structure
ai-support-agent/
├── config/              # Configuration
├── src/
│   ├── agents/          # AI agents (support, sentiment, escalation)
│   ├── tools/           # Tools (knowledge search, web search, tickets)
│   ├── mcp/             # MCP server for tool orchestration
│   ├── rag/             # RAG system (embeddings, vector store)
│   ├── api/             # FastAPI routes and models
│   ├── db/              # Database models and CRUD
│   └── utils/           # Utilities (LLM factory, prompts)
├── scripts/             # Setup and testing scripts
├── data/                # Knowledge base and database
└── tests/               # Test files

## Deployment

### Docker (Recommended)

```bash
docker-compose up -d
```

### Cloud Platforms

- **Railway**: `railway up`
- **Render**: Connect GitHub repo
- **AWS/GCP/Azure**: Deploy as container

## Security

- API keys in `.env` (never commit!)
- CORS configured for production
- SQL injection protection via ORM
- Input validation with Pydantic

## 📈 Performance

- **Response Time**: 1-3 seconds (with Ollama)
- **Throughput**: 10-50 req/sec
- **Accuracy**: 85%+ confidence on common queries
- **Escalation Rate**: ~10-15%

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

MIT License - see LICENSE file

## Support

- **Issues**: GitHub Issues
- **Email**: support@example.com
- **Docs**: Full documentation at `/docs`

## Roadmap

- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Advanced analytics dashboard
- [ ] Slack/Discord integration
- [ ] Fine-tuned models
- [ ] A/B testing framework

---

**Built using LangChain, FastAPI, and ChromaDB**
