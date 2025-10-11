import os
import logging
from typing import Dict, List
from fastapi import FastAPI, HTTPException
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
    session_id: str
    message: str

class QueryResponse(BaseModel):
    response: str

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI MCP server")
    yield
    logger.info("Shutting down FastAPI MCP server")

app = FastAPI(
    title="Financial AI Assistant MCP Server",
    description="MCP-compatible FastAPI server for financial market queries",
    version="1.0.0",
    lifespan=lifespan
)

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

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Main query endpoint for financial AI assistant"""
    try:
        # Initialize session if not exists
        if request.session_id not in session_memory:
            session_memory[request.session_id] = []
        
        # Add user message to session history
        session_memory[request.session_id].append({
            "role": "user",
            "content": request.message
        })
        
        # Get AI response
        ai_response = await call_groq_api(session_memory[request.session_id])
        
        # Add AI response to session history
        session_memory[request.session_id].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Keep only last 10 messages to prevent memory overflow
        if len(session_memory[request.session_id]) > 10:
            session_memory[request.session_id] = session_memory[request.session_id][-10:]
        
        logger.info(f"Processed query for session {request.session_id}")
        return QueryResponse(response=ai_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")

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