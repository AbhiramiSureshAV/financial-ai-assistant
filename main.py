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
    """Modern Financial AI Assistant Interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Financial AI Assistant | Market Intelligence</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container {
                max-width: 900px; margin: 0 auto;
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden; backdrop-filter: blur(10px);
            }
            .header {
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                color: white; padding: 30px; text-align: center;
            }
            .header h1 { font-size: 2.5rem; margin-bottom: 10px; font-weight: 300; }
            .header p { opacity: 0.9; font-size: 1.1rem; }
            .chat-container { padding: 30px; }
            .input-group { margin-bottom: 20px; position: relative; }
            .input-group label {
                display: block; margin-bottom: 8px; color: #333;
                font-weight: 500; font-size: 0.9rem;
            }
            .input-group input, .input-group textarea {
                width: 100%; padding: 15px 20px; border: 2px solid #e1e5e9;
                border-radius: 12px; font-size: 1rem; transition: all 0.3s ease;
                background: #f8f9fa;
            }
            .input-group input:focus, .input-group textarea:focus {
                outline: none; border-color: #667eea; background: white;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .send-btn {
                width: 100%; padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border: none; border-radius: 12px;
                font-size: 1.1rem; font-weight: 600; cursor: pointer;
                transition: all 0.3s ease; display: flex;
                align-items: center; justify-content: center; gap: 10px;
            }
            .send-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
            }
            .response {
                background: white; border: 1px solid #e1e5e9;
                border-radius: 15px; padding: 20px; margin: 15px 0;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                animation: slideIn 0.3s ease;
            }
            .response.ai {
                background: #f8f9fa; border-left: 4px solid #28a745;
            }
            .response.error {
                background: #fff5f5; border-left: 4px solid #dc3545; color: #721c24;
            }
            @keyframes slideIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1><i class="fas fa-chart-line"></i> Financial AI Assistant</h1>
                <p>Intelligent Market Analysis & Investment Insights</p>
            </div>
            <div class="chat-container">
                <div class="input-group">
                    <label for="sessionId"><i class="fas fa-user"></i> Session ID</label>
                    <input type="text" id="sessionId" placeholder="Enter session ID" value="demo-user">
                </div>
                <div class="input-group">
                    <label for="message"><i class="fas fa-comments"></i> Your Question</label>
                    <textarea id="message" rows="3" placeholder="Ask about stocks, market trends, investments...">What are the top tech stocks to watch?</textarea>
                </div>
                <button class="send-btn" onclick="sendQuery()">
                    <i class="fas fa-paper-plane"></i> Ask AI Assistant
                </button>
                <div id="response"></div>
            </div>
        </div>
        <script>
        async function sendQuery() {
            const sessionId = document.getElementById('sessionId').value;
            const message = document.getElementById('message').value;
            const responseDiv = document.getElementById('response');
            if (!sessionId || !message) {
                alert('Please fill in both fields'); return;
            }
            responseDiv.innerHTML = '<div class="response"><i class="fas fa-spinner fa-spin"></i> AI is thinking...</div>';
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, message: message})
                });
                const data = await response.json();
                if (response.ok) {
                    responseDiv.innerHTML = `<div class="response ai"><i class="fas fa-robot"></i> <strong>AI Assistant:</strong><br><br>${data.response}</div>`;
                } else {
                    responseDiv.innerHTML = `<div class="response error"><i class="fas fa-exclamation-triangle"></i> <strong>Error:</strong> ${data.detail}</div>`;
                }
            } catch (error) {
                responseDiv.innerHTML = `<div class="response error"><i class="fas fa-exclamation-triangle"></i> <strong>Error:</strong> ${error.message}</div>`;
            }
        }
        document.getElementById('message').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQuery(); }
        });
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