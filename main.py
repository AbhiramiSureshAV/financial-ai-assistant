import os
import logging
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import httpx
import uvicorn

from dotenv import load_dotenv

# Load environment variables from .env file (optional in production)
try:
    load_dotenv()
except:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Session memory storage
session_memory: Dict[str, List[Dict[str, str]]] = {}

class QueryRequest(BaseModel):
    session_id: str = "default"
    message: str

class SimpleQueryRequest(BaseModel):
    message: str

class QueryResponse(BaseModel):
    response: str

app = FastAPI(
    title="Financial AI Assistant MCP Server",
    description="MCP-compatible FastAPI server for financial market queries",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting FastAPI MCP server")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down FastAPI MCP server")

async def call_groq_api(messages: List[Dict[str, str]]) -> str:
    """Call Groq API with conversation history"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in environment")
    
    # Add system prompt for financial context
    system_message = {
        "role": "system",
        "content": "You are a financial AI assistant. Provide accurate, helpful information about stock markets, investments, and financial news. Keep responses concise and relevant."
    }
    
    full_messages = [system_message] + messages
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "messages": full_messages,
                    "model": "llama-3.1-8b-instant",
                    "temperature": 0.7,
                    "max_tokens": 500
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(status_code=500, detail="Failed to connect to Groq API")
    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        logger.error(f"HTTP error: {e.response.status_code} - {error_text}")
        raise HTTPException(status_code=500, detail=f"Groq API error: {error_text}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_query(session_id: str, message: str):
    """Process query with session management"""
    try:
        # Initialize session if not exists
        if session_id not in session_memory:
            session_memory[session_id] = []
        
        # Add user message to session history
        session_memory[session_id].append({
            "role": "user",
            "content": message
        })
        
        # Get AI response
        ai_response = await call_groq_api(session_memory[session_id])
        
        # Add AI response to session history
        session_memory[session_id].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Keep only last 10 messages to prevent memory overflow
        if len(session_memory[session_id]) > 10:
            session_memory[session_id] = session_memory[session_id][-10:]
        
        logger.info(f"Processed query for session {session_id}")
        return QueryResponse(response=ai_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Main query endpoint - supports both formats"""
    return await process_query(request.session_id, request.message)

@app.post("/simple-query", response_model=QueryResponse)
async def simple_query_endpoint(request: SimpleQueryRequest):
    """Simple query endpoint matching exact requirement format"""
    return await process_query("default", request.message)

@app.get("/")
async def root():
    """Simple test interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Financial AI Assistant</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
            input, textarea, button { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #007bff; color: white; cursor: pointer; }
            button:hover { background: #0056b3; }
            .response { background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Financial AI Assistant</h1>
            <input type="text" id="sessionId" placeholder="Session ID (e.g., user123)" value="test123">
            <textarea id="message" placeholder="Ask about stocks, markets, investments..." rows="3">What is the latest on the stock market?</textarea>
            <button onclick="sendQuery()">Ask AI</button>
            <div id="response"></div>
        </div>
        
        <script>
        async function sendQuery() {
            const sessionId = document.getElementById('sessionId').value;
            const message = document.getElementById('message').value;
            const responseDiv = document.getElementById('response');
            
            if (!sessionId || !message) {
                alert('Please fill in both fields');
                return;
            }
            
            responseDiv.innerHTML = '<div class="response">Thinking...</div>';
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, message: message})
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    responseDiv.innerHTML = `<div class="response"><strong>AI:</strong> ${data.response}</div>`;
                } else {
                    responseDiv.innerHTML = `<div class="response" style="border-left-color: red;"><strong>Error:</strong> ${data.detail}</div>`;
                }
            } catch (error) {
                responseDiv.innerHTML = `<div class="response" style="border-left-color: red;"><strong>Error:</strong> ${error.message}</div>`;
            }
        }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Financial AI Assistant MCP Server"}

@app.get("/sessions")
async def get_sessions():
    """Get active sessions count (for debugging)"""
    return {"active_sessions": len(session_memory)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)