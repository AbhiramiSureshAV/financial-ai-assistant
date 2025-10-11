# Backend AI Market Intelligence Service

**Internship Task**: MCP Server-based Financial AI Assistant

## 🚀 Live Service

**URL**: https://financial-ai-backend-fu6p.onrender.com

## 📋 How to Test

### Curl Commands for Testing (As Requested)

**Basic Query (Exact Format Required):**
```bash
curl -X POST https://financial-ai-backend-fu6p.onrender.com/simple-query \
-H "Content-Type: application/json" \
-d '{"message": "Give me the latest news on the stock market."}'
```

**Advanced Query (With Session Support):**
```bash
curl -X POST https://financial-ai-backend-fu6p.onrender.com/query \
-H "Content-Type: application/json" \
-d '{"session_id": "user123", "message": "What are the top tech stocks to watch?"}'
```

**Follow-up Query (Shows Context Memory):**
```bash
curl -X POST https://financial-ai-backend-fu6p.onrender.com/query \
-H "Content-Type: application/json" \
-d '{"session_id": "user123", "message": "How about their recent performance?"}'
```

**Health Check:**
```bash
curl https://financial-ai-backend-fu6p.onrender.com/health
```

### Web Interface (Bonus)
Visit: **https://financial-ai-backend-fu6p.onrender.com**
- Modern, interactive web interface
- Real-time chat experience
- Visual feedback and animations

### API Documentation
Visit: **https://financial-ai-backend-fu6p.onrender.com/docs**
- Interactive API testing
- Complete endpoint documentation
- Built-in request/response examples

### Alternative Testing Methods

#### PowerShell (Windows)
```powershell
# Basic Query (Exact Format Required)
Invoke-RestMethod -Uri "https://financial-ai-backend-fu6p.onrender.com/simple-query" -Method POST -ContentType "application/json" -Body '{"message": "Give me the latest news on the stock market."}'

# Advanced Query (With Session Support)
Invoke-RestMethod -Uri "https://financial-ai-backend-fu6p.onrender.com/query" -Method POST -ContentType "application/json" -Body '{"session_id": "user123", "message": "What are the top tech stocks to watch?"}'

# Follow-up Query (Shows Context Memory)
Invoke-RestMethod -Uri "https://financial-ai-backend-fu6p.onrender.com/query" -Method POST -ContentType "application/json" -Body '{"session_id": "user123", "message": "How about their recent performance?"}'
```

#### For Windows Users (PowerShell Alternative)
```powershell
# If curl doesn't work on Windows, use PowerShell:
Invoke-RestMethod -Uri "https://financial-ai-backend-fu6p.onrender.com/simple-query" -Method POST -ContentType "application/json" -Body '{"message": "Give me the latest news on the stock market."}'
```

## 🏗️ How the Service Functions

### Architecture
- **MCP Server**: FastAPI-based server running on Render cloud platform
- **AI Integration**: Grok API (xAI) for intelligent financial responses
- **Context Management**: In-memory session storage for conversation continuity
- **API Design**: RESTful endpoints with JSON request/response format

### Request Flow
1. Client sends POST request to `/query` or `/simple-query`
2. Server extracts message and session ID (if provided)
3. Message added to session conversation history
4. Complete conversation context sent to Grok AI
5. AI generates contextual financial response
6. Response stored in session memory and returned to client

## 🛠️ Tools, Libraries & Models Used

### Core Stack
- **FastAPI**: Modern Python web framework for API development
- **Uvicorn**: ASGI server for production deployment
- **Pydantic**: Data validation and serialization
- **httpx**: Async HTTP client for AI API calls

### AI Model
- **Grok API (xAI)**: Advanced language model specialized for real-time information
- **Model**: `llama-3.1-8b-instant` for fast, accurate financial responses
- **System Prompt**: Configured specifically for financial market expertise

### Deployment
- **Render**: Cloud platform for hosting and auto-deployment
- **Environment Variables**: Secure API key management
- **Health Monitoring**: Built-in health check endpoints

## 🧠 Context Preservation

### Session-Based Memory
- **Session Storage**: Each `session_id` maintains independent conversation history
- **Message Limit**: Last 10 messages per session to prevent memory overflow
- **Context Window**: Full conversation history sent to AI for contextual responses
- **Memory Structure**:
  ```python
  session_memory = {
      "user123": [
          {"role": "user", "content": "What are tech stocks?"},
          {"role": "assistant", "content": "Tech stocks are..."},
          {"role": "user", "content": "How about their performance?"},
          {"role": "assistant", "content": "Based on our previous discussion..."}
      ]
  }
  ```

### Context Benefits
- **Follow-up Questions**: AI remembers previous topics
- **Clarifications**: Can reference earlier parts of conversation
- **Personalization**: Maintains user-specific conversation flow

## ⚙️ MCP Server Configuration

### Server Setup
- **Framework**: FastAPI with lifespan management
- **Host**: `0.0.0.0` (accepts all connections)
- **Port**: Dynamic port assignment via `$PORT` environment variable
- **Runtime**: Python 3.11 for optimal compatibility

### Deployment Configuration (`render.yaml`)
```yaml
services:
  - type: web
    name: financial-ai-backend
    runtime: python
    pythonVersion: "3.11"
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GROQ_API_KEY
        sync: false
```

### Environment Variables
- `GROQ_API_KEY`: Secure API key for Grok AI service
- `PORT`: Dynamic port assignment by hosting platform

## 📊 API Endpoints

### GET `/`
**Purpose**: Modern web interface for interactive testing
**Features**: Real-time chat, visual feedback, responsive design

### POST `/simple-query`
**Format**: `{"message": "your question"}`
**Purpose**: Matches exact internship requirement format

### POST `/query` 
**Format**: `{"session_id": "user123", "message": "your question"}`
**Purpose**: Advanced endpoint with session management

### GET `/health`
**Purpose**: Service health monitoring

### GET `/sessions`
**Purpose**: Active session count (debugging)

### GET `/docs`
**Purpose**: Interactive API documentation

## 🎯 Financial Intelligence Features

### Market Expertise
- Real-time stock market analysis
- Investment recommendations
- Financial news interpretation
- Economic trend analysis
- Risk assessment guidance

### Conversation Capabilities
- Contextual follow-up questions
- Multi-turn financial discussions
- Personalized investment advice
- Historical market references

### User Interface
- **Modern Web Interface**: Professional financial theme with gradient design
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Feedback**: Loading animations and visual status indicators
- **Interactive Elements**: Smooth transitions and hover effects
- **Accessibility**: Keyboard shortcuts (Enter to send) and focus management

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GROQ_API_KEY="your-api-key"

# Run locally
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📈 Performance & Scalability

- **Async Architecture**: Non-blocking request handling
- **Memory Management**: Automatic session cleanup
- **Error Handling**: Comprehensive exception management
- **Logging**: Structured logging for monitoring
- **Health Checks**: Built-in service monitoring

---

**Developed for**: Backend AI Market Intelligence Internship Task  
**Deployment**: Production-ready MCP server on Render  
**Testing**: Fully functional with curl commands provided above