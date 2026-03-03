# Persona-Adaptive Customer Support Agent

A sophisticated AI-powered customer support agent that adapts its communication style based on detected user persona. The agent analyzes user intent, retrieves relevant knowledge, and escalates to humans when needed.
.
## Features

- 🔍 **Persona Detection**: Classifies users as Technical, Frustrated, Business, or General
- 🎯 **Intent Classification**: Understands user needs and intent
- 📚 **Knowledge Retrieval**: Uses FAISS vector search for relevant documentation
- 🗣️ **Adaptive Response Tone**: Tailors responses to match user persona
- ⚠️ **Escalation Management**: Routes to humans when needed
- 💬 **Streamlit Frontend**: Interactive web interface
- ⚡ **FastAPI Backend**: High-performance REST API

## Architecture

```
┌─────────────────────────────────────────────┐
│    Streamlit Web Frontend  (Port 8501)      │
│    - User Interface                         │
│    - Real-time Chat                         │
│    - Context Visualization                  │
└─────────────┬───────────────────────────────┘
              │
              │ HTTP Requests
              │
┌─────────────▼───────────────────────────────┐
│    FastAPI Backend  (Port 8000)             │
│    - Persona Detection                      │
│    - Intent Classification                  │
│    - Knowledge Retrieval                    │
│    - Response Generation                    │
│    - Escalation Logic                       │
└─────────────┬───────────────────────────────┘
              │
        ┌─────┴("▼──────────────────┐
        │                          │
   ┌────▼─────────┐    ┌─────────▼──────┐
   │  Ollama LLM  │    │ FAISS Vector   │
   │ (tinyllama)  │    │   Store        │
   │              │    │                │
   └──────────────┘    └────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.8+
- Ollama (for local LLM)

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd persona_adaptive_agent
```

2. Create a virtual environment:
```bash
python -m venv personaa
personaa\Scripts\activate  # Windows
source personaa/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Local Development

1. **Start Ollama** (if not already running):
```bash
ollama serve
```

2. **Start the FastAPI backend**:
```bash
python -m uvicorn app.main:app --reload
```

3. **Start Streamlit** (in another terminal):
```bash
streamlit run demo/streamlit_app.py
```

The app will be available at `http://localhost:8501`

## Deployment

### Deploy to Streamlit Cloud

1. Deploy your FastAPI backend to a cloud service (Railway, Render, Heroku, etc.)
2. Update `API_URL` in [Streamlit Cloud secrets](#streamlit-cloud-secrets)
3. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions

### Streamlit Cloud Secrets

In your Streamlit Cloud app settings, add:

```toml
API_URL = "https://your-deployed-api-url.com"
```

## Project Structure

```
persona_adaptive_agent/
├── app/
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration management
│   ├── models/
│   │   ├── embeddings.py        # Embedding functions
│   │   └── vector_store.py      # FAISS vector store
│   ├── services/
│   │   ├── persona.py           # Persona detection
│   │   ├── intent.py            # Intent classification
│   │   ├── retriever.py         # Knowledge retrieval
│   │   ├── generator.py         # Response generation
│   │   ├── escalation.py        # Escalation logic
│   │   └── __pycache__/
│   └── utils/
│       ├── helpers.py           # Utility functions
│       ├── logger.py            # Logging setup
│       └── __pycache__/
├── demo/
│   └── streamlit_app.py         # Streamlit interface
├── kb/
│   ├── api_guide.txt
│   ├── billing_policy.txt
│   ├── login_troubleshooting.txt
│   └── sla_info.txt
├── vector_store/
│   └── index.faiss              # FAISS index
├── logs/                        # Application logs
├── .streamlit/
│   ├── config.toml              # Streamlit configuration
│   └── secrets.toml             # Streamlit secrets (Cloud)
├── .env                         # Local environment variables
├── requirements.txt             # Python dependencies
├── Procfile                     # Cloud deployment config
├── DEPLOYMENT.md                # Deployment guide
└── README.md                    # This file
```

## Configuration

### Environment Variables (.env)

```env
# App settings
APP_NAME=Persona Adaptive Agent
DEBUG=True
LOG_LEVEL=INFO

# API Configuration
API_URL=http://localhost:8000

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=tinyllama

# Model settings
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Paths
FAISS_INDEX_PATH=./vector_store/index.faiss
KB_DOCUMENTS_PATH=./kb/

# Escalation
ESCALATION_CONFIDENCE_THRESHOLD=0.5
MAX_HISTORY_LENGTH=5
```

## API Endpoints

### FastAPI Backend

- `GET /health` - Health check
- `POST /chat` - Process user message
  - Request:
    ```json
    {
      "message": "User message",
      "conversation_id": "unique-id",
      "history": ["previous messages"]
    }
    ```
  - Response:
    ```json
    {
      "response": "Agent response",
      "persona": {"persona": "technical", "confidence": 0.95},
      "intent": {"intent": "technical_support", "confidence": 0.88},
      "escalated": false,
      "context_summary": "..."
    }
    ```

## Troubleshooting

### "Cannot reach API at http://localhost:8000"

**Local Development:**
- Ensure FastAPI is running: `python -m uvicorn app.main:app --reload`

**Streamlit Cloud:**
- Your API must be deployed to a cloud service
- Check that `API_URL` is set correctly in Streamlit Cloud secrets
- Verify the API endpoint is accessible from the internet

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

## Technologies Used

- **Frontend**: Streamlit
- **Backend**: FastAPI, Uvicorn
- **LLM**: Ollama (Local)
- **Vector Store**: FAISS
- **Embeddings**: Sentence Transformers (BAAI/bge-small-en-v1.5)
- **NLP**: Transformers
- **ML Framework**: PyTorch

repository and links:

-GitHub repo: https://github.com/Abhishek-2027/PERSONA_ADAPTIVE_AGENT
-Streamlit application: https://personaadaptiveagent-tt6sa9ianwdkv4abduk4sr.streamlit.app/


full UI:
-<img width="940" height="427" alt="image" src="https://github.com/user-attachments/assets/fd85f9ae-bebc-4388-88df-8f84ece542b4" />


## License

MIT

## Support

For issues and questions, please open an issue on GitHub or refer to [DEPLOYMENT.md](DEPLOYMENT.md) for deployment-related help.
