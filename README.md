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
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your credentials

## Configuration

Required environment variables in `.env`:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
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
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs
   - Root: http://localhost:8000/

### Telegram Bot

- Open Telegram and interact with your bot
- Send `/start` to begin
- Send any image to get a description

### REST API Endpoints

#### GET `/`
Root endpoint with basic info

#### GET `/health`
Health check endpoint

#### POST `/api/describe`
Upload an image to get description
- Content-Type: multipart/form-data
- Body: file (image file)

#### GET `/api/stats`
Get bot statistics and configuration

## API Usage Example

```bash
# Using curl
curl -X POST "http://localhost:8000/api/describe" \
  -F "file=@/path/to/image.jpg"

# Using Python requests
import requests

with open("image.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/describe",
        files={"file": f}
    )
    print(response.json())
```

## Commands

- `/start` - Start the bot and see welcome message
- `/help` - Get help information

## Development

### Code Structure

- **core/**: Core functionality (config, logging)
- **services/**: Business logic (vision processing)
- **handlers/**: Telegram bot handlers
- **api/**: REST API endpoints
- **app.py**: FastAPI application
- **bot.py**: Main bot orchestration

### Logging

Logs are stored in `logs/` directory with daily rotation.

## License

MIT

## Author

Your Name


