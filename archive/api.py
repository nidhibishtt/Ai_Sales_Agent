"""
FastAPI application for AI Sales Agent REST API
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import os
from dotenv import load_dotenv
from main import EnhancedAISalesAgent

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Enhanced AI Sales Agent API",
    description="REST API for Enhanced AI-powered Sales Agent with Premium LLM Providers",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[EnhancedAISalesAgent] = None

# Request/Response Models
class MessageRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ConversationStartRequest(BaseModel):
    initial_message: Optional[str] = None

class HealthResponse(BaseModel):
    system: str
    services: Dict[str, str]
    agents: Dict[str, Any]
    database: str
    success: bool

class MessageResponse(BaseModel):
    response: str
    session_id: str
    stage: str
    success: bool
    agent: Optional[str] = None
    next_actions: Optional[List[str]] = None

class ConversationHistoryResponse(BaseModel):
    session_id: str
    history: List[Dict[str, Any]]
    current_stage: str
    client_inquiry: Optional[Dict[str, Any]]
    recommended_packages: List[Dict[str, Any]]
    success: bool

class SessionSummaryResponse(BaseModel):
    session_id: str
    current_stage: str
    created_at: str
    updated_at: str
    message_count: int
    client_info: Dict[str, Any]
    recommended_packages: int
    next_actions: List[str]
    success: bool

class AnalyticsResponse(BaseModel):
    analytics: Dict[str, Any]
    success: bool

class ServicePackagesResponse(BaseModel):
    packages: List[Dict[str, Any]]
    count: int
    success: bool

@app.on_event("startup")
async def startup_event():
    """Initialize the AI Sales Agent on startup"""
    global agent
    try:
        agent = EnhancedAISalesAgent()
        print("✅ AI Sales Agent initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI Sales Agent: {str(e)}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global agent
    if agent:
        # Perform any necessary cleanup
        print("🔄 Shutting down AI Sales Agent")

@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint with basic information"""
    return {
        "name": "AI Sales Agent API",
        "version": "1.0.0",
        "description": "REST API for AI-powered Sales Agent for Recruiting Agency",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check():
    """Perform system health check"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        health_result = agent.health_check()
        if not health_result.get('success'):
            raise HTTPException(status_code=503, detail="System health check failed")
        
        return HealthResponse(**health_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check error: {str(e)}")

@app.post("/conversations/start", response_model=MessageResponse, summary="Start new conversation")
async def start_conversation(request: ConversationStartRequest):
    """Start a new conversation session"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.start_conversation(request.initial_message)
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to start conversation'))
        
        return MessageResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting conversation: {str(e)}")

@app.post("/conversations/{session_id}/messages", response_model=MessageResponse, summary="Send message")
async def send_message(session_id: str, request: MessageRequest):
    """Send a message in an existing conversation"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.process_message(session_id, request.message, request.context)
        if not result.get('success'):
            error_msg = result.get('error', 'Failed to process message')
            if 'Session not found' in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        return MessageResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/conversations/{session_id}/history", response_model=ConversationHistoryResponse, summary="Get conversation history")
async def get_conversation_history(session_id: str, limit: Optional[int] = None):
    """Get conversation history for a session"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.get_conversation_history(session_id, limit)
        if not result.get('success'):
            error_msg = result.get('error', 'Failed to get conversation history')
            if 'Session not found' in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        return ConversationHistoryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversation history: {str(e)}")

@app.get("/conversations/{session_id}/summary", response_model=SessionSummaryResponse, summary="Get session summary")
async def get_session_summary(session_id: str):
    """Get summary of a conversation session"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.get_session_summary(session_id)
        if not result.get('success'):
            error_msg = result.get('error', 'Failed to get session summary')
            if 'Session not found' in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        return SessionSummaryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session summary: {str(e)}")

@app.post("/conversations/{session_id}/reset", summary="Reset conversation")
async def reset_conversation(session_id: str):
    """Reset a conversation to initial state"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.reset_conversation(session_id)
        if not result.get('success'):
            error_msg = result.get('error', 'Failed to reset conversation')
            if 'Session not found' in error_msg:
                raise HTTPException(status_code=404, detail=error_msg)
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        
        return {"message": "Conversation reset successfully", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting conversation: {str(e)}")

@app.get("/analytics", response_model=AnalyticsResponse, summary="Get analytics")
async def get_analytics(days: int = 7):
    """Get analytics summary"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.get_analytics(days)
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to get analytics'))
        
        return AnalyticsResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting analytics: {str(e)}")

@app.get("/service-packages", response_model=ServicePackagesResponse, summary="Get service packages")
async def get_service_packages():
    """Get all available service packages"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.get_service_packages()
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to get service packages'))
        
        return ServicePackagesResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting service packages: {str(e)}")

@app.delete("/cleanup", summary="Cleanup old sessions")
async def cleanup_old_sessions(days: int = 30):
    """Clean up old session data"""
    if not agent:
        raise HTTPException(status_code=503, detail="AI Sales Agent not initialized")
    
    try:
        result = agent.cleanup_old_sessions(days)
        if not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to cleanup sessions'))
        
        return {
            "message": f"Cleaned up {result['deleted_sessions']} sessions older than {days} days",
            "deleted_sessions": result['deleted_sessions'],
            "days": days
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up sessions: {str(e)}")

# Custom error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": "An unexpected error occurred"}

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server"""
    uvicorn.run("api:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Sales Agent API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    print("🚀 Starting AI Sales Agent API Server...")
    print(f"📍 Server will be available at: http://{args.host}:{args.port}")
    print(f"📚 API Documentation: http://{args.host}:{args.port}/docs")
    
    run_server(host=args.host, port=args.port, reload=args.reload)
