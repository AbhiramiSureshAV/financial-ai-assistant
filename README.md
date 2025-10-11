# Financial AI Assistant MCP Server

A FastAPI-based MCP (Model Context Protocol) server that provides AI-powered financial market insights using the Grok API.

## Features

- **Session-based Context**: Maintains conversation history per session
- **Grok API Integration**: Uses Grok for AI-powered financial responses
- **MCP Compatible**: Runs as an MCP server for integration with compatible clients
- **Error Handling**: Comprehensive error handling and logging

## Tech Stack

- **FastAPI**: Modern Python web framework
- **Grok API**: AI model for financial insights
- **uvicorn**: ASGI server for deployment
- **httpx**: Async HTTP client for API calls

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable:
```bash
export GROK_API_KEY="your-grok-api-key-here"
```

3. Run locally:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Context Memory

The service preserves conversation context using in-memory session storage:
- Each session_id maintains its own conversation history
- Last 10 messages are kept per session to prevent memory overflow
- Context allows follow-up questions like "How about tech stocks?" after asking about general market news

## MCP Server Configuration

The service runs as an MCP server with:
- Lifespan management for startup/shutdown
- Health check endpoint at `/health`
- Session monitoring at `/sessions`

## API Usage

### Test Command
```bash
curl -X POST http://localhost:8000/query \
-H "Content-Type: application/json" \
-d '{"session_id": "user123", "message": "Give me the latest news on the stock market."}'
```

### Example Conversation
```bash
# First query
curl -X POST http://localhost:8000/query \
-H "Content-Type: application/json" \
-d '{"session_id": "user123", "message": "What is the latest on the stock market today?"}'

# Follow-up query (maintains context)
curl -X POST http://localhost:8000/query \
-H "Content-Type: application/json" \
-d '{"session_id": "user123", "message": "How about tech stocks?"}'
```

## Deployment

### Render
1. Connect your GitHub repository
2. Set environment variable `GROK_API_KEY`
3. Use build command: `pip install -r requirements.txt`
4. Use start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Railway
1. Connect your GitHub repository
2. Set environment variable `GROK_API_KEY`
3. Railway will auto-detect and deploy the FastAPI app

## Endpoints

- `POST /query` - Main query endpoint
- `GET /health` - Health check
- `GET /sessions` - Active sessions count