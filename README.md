# Avivo - AI Image Description Bot 🤖

A Telegram bot with REST API that uses Qwen Vision Model to provide detailed descriptions of images.

## Features

- 📸 Image analysis using Qwen Vision Model
- 🔄 Automatic image processing
- 📝 Detailed image descriptions
- 🛡️ Error handling and logging
- ⚙️ Environment-based configuration
- 🌐 REST API with FastAPI
- 🤖 Telegram Bot integration

## Project Structure

```
Avivo/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   └── logger.py          # Logging setup
│   ├── services/
│   │   ├── __init__.py
│   │   └── vision_service.py  # Vision model integration
│   ├── handlers/
│   │   ├── __init__.py
│   │   └── telegram_handlers.py  # Bot command handlers
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # FastAPI routes
│   ├── __init__.py
│   ├── bot.py                 # Main bot class
│   └── app.py                 # FastAPI application
├── temp/                      # Temporary image storage
├── logs/                      # Application logs
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .env.example               # Example environment file
└── README.md                  # This file
```

## Installation

1. Clone the repository

2. Create virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate virtual environment:
   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On Linux/Mac
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. **Pull Ollama models:**
   ```bash
   # Vision model
   ollama pull qwen3-vl:4b
   
   # Embedding model (optional)
   ollama pull all-minilm:l6-v2
   ```

7. **Start Redis using Docker:**
   ```bash
   docker run -d --name redis-server -p 6379:6379 redis:latest
   ```

## Configuration

Required environment variables in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=qwen3-vl:4b
IMAGE_QUALITY=95
MAX_IMAGE_SIZE=10485760
API_HOST=0.0.0.0
API_PORT=8000
```

## Usage

### Running with Uvicorn

1. Start Ollama with Qwen model:
   ```bash
   ollama run qwen3-vl:4b
   ```

2. Run the application:
   ```bash
   python main.py
   ```
   
   Or directly with uvicorn:
   ```bash
   uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
   ```

3. Access the API:
   - Root: `http://localhost:8000/`
   - Health check: `http://localhost:8000/health`
   - API docs (Swagger): `http://localhost:8000/docs`
   - Alternative docs (ReDoc): `http://localhost:8000/redoc`

### Telegram Bot

1. Open Telegram and search for your bot
2. Send `/start` to begin
3. Send any image to get a detailed description

### REST API Endpoints

#### `GET /`
Root endpoint with basic information

**Response:**
```json
{
  "message": "Avivo - AI Image Description Bot",
  "version": "1.0.0",
  "status": "running"
}
```

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "model": "qwen3-vl:4b",
  "ollama_url": "http://localhost:11434/api/generate"
}
```

#### `POST /api/describe`
Upload an image to get AI-generated description

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Response:**
```json
{
  "success": true,
  "filename": "example.jpg",
  "description": "A detailed description of the image..."
}
```

#### `GET /api/stats`
Get bot statistics and configuration

**Response:**
```json
{
  "model": "qwen3-vl:4b",
  "image_quality": 95,
  "max_image_size": 10485760
}
```

#### `POST /api/embed`
Generate text embedding vector

**Request:**
- Method: `POST`
- Query param: `text` (string)

**Response:**
```json
{
  "success": true,
  "text_length": 25,
  "embedding_dimension": 384,
  "embedding": [0.123, -0.456, ...]
}
```

#### `POST /api/similarity`
Calculate similarity between two texts

**Request:**
- Method: `POST`
- Query params: `text1` (string), `text2` (string)

**Response:**
```json
{
  "success": true,
  "text1_length": 20,
  "text2_length": 25,
  "similarity": 0.85,
  "similarity_percentage": 85.0
}
```

#### `GET /api/embedding/health`
Check embedding service health

**Response:**
```json
{
  "status": "healthy",
  "model": "all-minilm:l6-v2",
  "url": "http://localhost:11434/api/embeddings",
  "dimension": 384
}
```

## API Usage Examples

### Using cURL

```bash
curl -X POST "http://localhost:8000/api/describe" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

### Using Python requests

```python
import requests

# Describe an image
with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/describe",
        files={"file": f}
    )
    
if response.status_code == 200:
    result = response.json()
    print(f"Description: {result['description']}")
else:
    print(f"Error: {response.status_code}")
```

### Using JavaScript fetch

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/api/describe', {
  method: 'POST',
  body: formData
})
  .then(response => response.json())
  .then(data => console.log(data.description))
  .catch(error => console.error('Error:', error));
```

## Telegram Bot Commands

### Image Analysis
- Send any image - Get AI-powered description

### RAG Q&A
- `/ask <question>` - Ask questions from knowledge base
- `/addtext <text>` - Add text to knowledge base
- `/clearrag` - Clear RAG knowledge base

### Other Commands
- `/start` - Start the bot and see welcome message
- `/help` - Get help information and usage instructions
- `/stats` - Show system statistics

### Example Usage

```
# Add knowledge to bot
/addtext Python is a high-level programming language

# Ask questions
/ask What is Python?

# Get system stats
/stats

# Clear knowledge base
/clearrag
```

## Development

### Project Architecture

- **core/**: Core functionality (configuration, logging)
- **services/**: Business logic (vision model processing)
- **handlers/**: Telegram bot event handlers
- **api/**: REST API endpoints and routes
- **app.py**: FastAPI application with lifespan management
- **bot.py**: Telegram bot orchestration

### Adding New Features

1. Create new service in `src/services/`
2. Add routes in `src/api/routes.py`
3. Update handlers in `src/handlers/`

### Logging

- Logs are stored in `logs/` directory
- Daily log rotation with timestamp
- Log level: INFO
- Format: `YYYY-MM-DD HH:MM:SS - name - LEVEL - message`

### Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test with sample image
curl -X POST http://localhost:8000/api/describe \
  -F "file=@test_image.jpg"
```

## Troubleshooting

### Bot not responding
- Check if Ollama is running: `ollama list`
- Verify bot token in `.env` file
- Check logs in `logs/` directory

### API errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify Ollama is accessible at configured URL

### Image processing fails
- Check image format (JPG, PNG supported)
- Verify image size is under MAX_IMAGE_SIZE
- Ensure sufficient disk space in `temp/` directory

## Requirements

- Python 3.8+
- Ollama with Qwen Vision Model
- Telegram Bot Token
- 2GB+ RAM recommended

## License

MIT License

## Author

Anish

## Contributing

Pull requests are welcome! For major changes, please open an issue first.

## Support

For issues and questions, please open an issue on GitHub.


