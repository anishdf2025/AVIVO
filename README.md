# Avivo - AI Image Description & RAG Bot 🤖

A Telegram bot with REST API that uses **Qwen Vision Model** for image descriptions and **LangChain + FAISS** for document Q&A (RAG).

## Features

### 🖼️ Vision Service (Image Analysis)
- 📸 Image analysis using Qwen Vision Model
- 🔄 Automatic image processing with caching
- 📝 Detailed image descriptions
- 💾 Redis caching for faster responses
![alt text](Image_caption.jpeg)

### 📚 RAG Service (Document Q&A)
- 🧠 **Pure LangChain implementation** - No custom code
- 🗄️ **FAISS vector store** for semantic search
- 📄 Multi-format document support (PDF, DOCX, TXT, XLSX, PPTX)
- 🔍 Semantic similarity search with Ollama embeddings
- 💬 Natural language Q&A from uploaded documents
- 💾 Redis caching for query responses
![alt text](RAG_Telegram.jpeg)

### 🛡️ Infrastructure
- ⚙️ Environment-based configuration
- 📊 Comprehensive logging
- 🌐 REST API with FastAPI
- 🤖 Telegram Bot integration
- 🔴 Redis caching for both services

---

## Project Structure

```
Avivo/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   └── logger.py              # Logging setup
│   ├── services/
│   │   ├── __init__.py
│   │   ├── vision_service.py      # Vision model integration
│   │   ├── rag_service.py         # RAG service (LangChain)
│   │   ├── vector_store.py        # FAISS vector store (LangChain)
│   │   ├── embedding_service.py   # Ollama embeddings wrapper
│   │   ├── document_loader.py     # LangChain document loaders
│   │   └── cache_service.py       # Redis caching
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── telegram_handlers.py   # Bot command handlers
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py              # FastAPI routes
│   ├── __init__.py
│   ├── bot.py                     # Main bot class
│   └── app.py                     # FastAPI application
├── temp/                          # Temporary file storage
├── logs/                          # Application logs
├── vector_db/                     # FAISS vector store data
│   └── faiss_index/
│       ├── index.faiss            # FAISS index
│       └── index.pkl              # Document metadata
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
├── .env.example                   # Example environment file
└── README.md                      # This file
```

---

## Installation

### 1. Prerequisites
- Python 3.8+
- Ollama installed and running
- Docker (for Redis)
- 4GB+ RAM recommended

### 2. Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd Avivo

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows
.venv\Scripts\activate

# On Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Ollama Models

```bash
# Vision model (for image descriptions)
ollama pull qwen3-vl:4b

# Embedding model (for RAG)
ollama pull all-minilm:l6-v2

# LLM model (for RAG answer generation)
ollama pull qwen3:1.7b

# Verify models
ollama list
```

### 4. Redis Setup

```bash
# Start Redis using Docker
docker run -d --name redis-server -p 6379:6379 redis:latest

# Verify Redis is running
docker ps
```

### 5. Environment Configuration

Create `.env` file:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Ollama Configuration
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen3-vl:4b
OLLAMA_TIMEOUT=180

# Image Processing
IMAGE_QUALITY=95
MAX_IMAGE_SIZE=10485760

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_TIMEOUT=180

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_TTL=86400

# Embedding Model Configuration
EMBEDDING_MODEL=all-minilm:l6-v2
EMBEDDING_URL=http://localhost:11434/api/embeddings

# RAG Configuration
RAG_LLM_MODEL=qwen3:1.7b
RAG_LLM_URL=http://localhost:11434/api/generate
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.0
```

---

## Usage

### Running the Application

```bash
# Start Ollama (if not already running)
ollama serve

# Start Redis (if not already running)
docker start redis-server

# Run the application
python main.py
```

Or directly with uvicorn:

```bash
uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

### Access Points

- **Root:** `http://localhost:8000/`
- **Health:** `http://localhost:8000/health`
- **API Docs:** `http://localhost:8000/docs` (Swagger UI)
- **ReDoc:** `http://localhost:8000/redoc`

---

## Telegram Bot Commands

### 🖼️ Vision Commands
- **Send image** → Get AI-powered description

### 📚 RAG Commands
- **Send PDF/DOCX** → Auto-upload to knowledge base
- `/ask <question>` → Ask questions from knowledge base
- `/addtext <text>` → Add text to knowledge base
- `/clearrag` → Clear RAG knowledge base

### 📊 Other Commands
- `/start` → Welcome message
- `/help` → Help information
- `/stats` → System statistics



## REST API Endpoints

### Vision Service


### Key Technologies

- **LangChain** - Document loading, text splitting, embeddings, vector stores
- **FAISS** - Fast similarity search and clustering of dense vectors
- **Ollama** - Local LLM and embedding model hosting
- **FastAPI** - Modern REST API framework
- **python-telegram-bot** - Telegram Bot API wrapper
- **Redis** - In-memory caching


## Configuration

### RAG Settings

```env
# LLM for answer generation
RAG_LLM_MODEL=qwen3:1.7b

# Embedding model for semantic search
EMBEDDING_MODEL=all-minilm:l6-v2

# Chunking parameters
RAG_CHUNK_SIZE=512          # Characters per chunk
RAG_CHUNK_OVERLAP=50        # Overlap between chunks

# Search parameters
RAG_TOP_K=5                 # Number of chunks to retrieve
RAG_SIMILARITY_THRESHOLD=0.0  # Minimum similarity (0.0 = return all)
```

### Cache Settings

```env
# Redis configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_TTL=86400  # 24 hours
```

---

## Troubleshooting

### RAG Not Responding

```bash
# Check if vector store has documents
curl http://localhost:8000/api/rag/stats

# Clear and re-upload documents
curl -X DELETE http://localhost:8000/api/rag/clear
```

### Ollama Connection Issues

```bash
# Verify Ollama is running
ollama list

# Test embedding generation
curl http://localhost:11434/api/embeddings \
  -d '{"model":"all-minilm:l6-v2","prompt":"test"}'

# Test LLM generation
curl http://localhost:11434/api/generate \
  -d '{"model":"qwen3:1.7b","prompt":"Hello","stream":false}'
```

### Redis Connection Issues

```bash
# Check Redis status
docker ps | grep redis

# Test Redis connection
redis-cli ping

# Clear all cache
curl -X DELETE "http://localhost:8000/api/cache/clear?cache_type=all"
```

### FAISS Index Corruption

```bash
# Delete vector store and restart
rm -rf vector_db/faiss_index/*
python main.py
```

---

## Performance Tips

1. **Chunk Size**: Smaller chunks (256-512) = better precision, larger (1024+) = better context
2. **Top-K**: More results = better recall but slower, fewer = faster but might miss relevant info
3. **Caching**: Enable Redis for 10-100x faster repeated queries
4. **Model Choice**:
   - **all-minilm:l6-v2**: Fast, good accuracy (384 dim)
   - **llama3:8b**: Better answers but slower (use qwen3:1.7b for speed)

---

## Requirements

```txt
python-telegram-bot==20.7
fastapi==0.109.0
uvicorn[standard]==0.27.0
langchain==0.1.0
langchain-community==0.0.20
faiss-cpu==1.8.0
redis==5.0.1
requests==2.31.0
Pillow==10.2.0
python-dotenv==1.0.0
PyPDF2==3.0.1
python-docx==1.1.0
openpyxl==3.1.2
python-pptx==0.6.23
```

---

## License

MIT License

## Author

Anish Kumar Maurya


