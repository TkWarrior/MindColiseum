# MindColiseum TTS Microservice

Standalone text-to-speech service for AI debate arguments.

## Setup

```powershell
# Create separate virtual environment
cd tts-miniservice
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```powershell
# Start on port 8001 (separate from main backend on 8000)
uvicorn main:app --reload --port 8001
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /stream?text={text}&agent={agent}` | Stream TTS audio |
| `POST /generate?text={text}&agent={agent}` | Download audio file |

**Agent options**: `pro`, `con`, `judge`, `summary`

## Integration with Main Backend

Call this service from the main backend or frontend:
```python
import httpx

response = httpx.get("http://localhost:8001/stream", params={"text": "Hello", "agent": "pro"})
```
