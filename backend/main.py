"""
NEXUS-R&D FastAPI Application
Main entry point for the backend API
"""

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger

from config import get_settings
from core.models import ResearchQuery, ResearchPhase
from core.state_manager import get_state_manager
from orchestrator import get_orchestrator


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)


# Store active research tasks
active_tasks: dict = {}
completed_reports: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("🚀 NEXUS-R&D Starting up...")
    settings = get_settings()
    logger.info(f"📊 Debug mode: {settings.debug}")
    logger.info(f"🤖 Gemini model: {settings.gemini_model}")
    yield
    logger.info("👋 NEXUS-R&D Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="NEXUS-R&D API",
    description="Recursive Innovation Intelligence Engine - Autonomous R&D research platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# ============================================
# Request/Response Models
# ============================================

class ResearchRequest(BaseModel):
    """Request model for starting research"""
    query: str = Field(..., description="The research question or topic")
    domain: Optional[str] = Field(None, description="Specific domain/industry focus")
    geographic_scope: list[str] = Field(
        default=["US", "EU", "CN", "JP"],
        description="Patent jurisdictions to search"
    )
    time_range_years: int = Field(default=5, description="Years of historical data")
    max_recursion_depth: int = Field(default=4, description="Research depth level")


class ResearchResponse(BaseModel):
    """Response model for research initiation"""
    session_id: str
    status: str
    message: str


class SessionStatus(BaseModel):
    """Session status response"""
    session_id: str
    phase: str
    started_at: str
    agents: dict
    total_sources_analyzed: int
    error: Optional[str] = None


# ============================================
# API Endpoints
# ============================================

@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "NEXUS-R&D API",
        "version": "1.0.0",
        "description": "Recursive Innovation Intelligence Engine",
        "tagline": "From Patents to Profits: Autonomous Discovery of Tomorrow's Innovations",
        "endpoints": {
            "POST /research": "Start a new research session",
            "GET /research/{session_id}/status": "Get research status",
            "GET /research/{session_id}/report": "Get completed report",
        },
    }


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint for Render deployment"""
    return {
        "status": "healthy",
        "service": "nexus-rd-backend",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "operational",
            "orchestrator": "ready",
            "agents": "initialized",
        },
    }


@app.post("/research", response_model=ResearchResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a new research session
    
    This initiates the autonomous research workflow:
    1. Patent Scout analyzes patent landscape
    2. Market Analyst gathers market intelligence
    3. Tech Trend tracks research evolution
    4. Verifier validates all claims
    5. Synthesizer generates final report
    """
    try:
        # Create research query
        query = ResearchQuery(
            query=request.query,
            domain=request.domain,
            geographic_scope=request.geographic_scope,
            time_range_years=request.time_range_years,
            max_recursion_depth=request.max_recursion_depth,
        )
        
        # Get orchestrator
        orchestrator = get_orchestrator()
        
        # Create session
        state_manager = get_state_manager()
        session = await state_manager.create_session(query)
        session_id = session.session_id
        
        # Start research in background
        background_tasks.add_task(
            run_research_task,
            session_id,
            query,
        )
        
        logger.info(f"Research session started: {session_id}")
        
        return ResearchResponse(
            session_id=session_id,
            status="started",
            message=f"Research initiated for: {request.query}",
        )
        
    except Exception as e:
        logger.error(f"Failed to start research: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def run_research_task(session_id: str, query: ResearchQuery):
    """Background task to run research"""
    try:
        orchestrator = get_orchestrator()
        
        # Run the full workflow
        report = await orchestrator.run(session_id, query)
        
        # Store completed report
        completed_reports[session_id] = report
        
        logger.info(f"Research completed: {session_id}")
        
    except Exception as e:
        logger.error(f"Research task error: {e}")
        state_manager = get_state_manager()
        await state_manager.complete_session(session_id, error=str(e))


@app.get("/research/{session_id}/status")
async def get_research_status(session_id: str):
    """
    Get the current status of a research session
    
    Returns real-time status of all agents and overall progress
    """
    try:
        state_manager = get_state_manager()
        status = await state_manager.get_session_summary(session_id)
        
        if not status:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research/{session_id}/report")
async def get_research_report(session_id: str):
    """
    Get the completed Innovation Opportunity Report
    
    Returns the full report once research is complete
    """
    try:
        # Check if report is ready
        if session_id in completed_reports:
            return completed_reports[session_id]
        
        # Check session status
        state_manager = get_state_manager()
        session = await state_manager.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.phase == ResearchPhase.FAILED:
            raise HTTPException(
                status_code=500,
                detail=f"Research failed: {session.error_message}"
            )
        
        if session.phase != ResearchPhase.COMPLETED:
            return JSONResponse(
                status_code=202,
                content={
                    "status": "in_progress",
                    "phase": session.phase.value,
                    "message": "Research still in progress. Please check status endpoint.",
                },
            )
        
        # If completed but not in cache, return error
        raise HTTPException(status_code=404, detail="Report not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/research/{session_id}/export/pdf")
async def export_report_pdf(session_id: str):
    """
    Export the completed report as a PDF document
    
    Returns a downloadable PDF file with the full Innovation Opportunity Report
    """
    from fastapi.responses import Response
    
    try:
        # Check if report exists
        if session_id not in completed_reports:
            raise HTTPException(status_code=404, detail="Report not found. Research may still be in progress.")
        
        report = completed_reports[session_id]
        
        # Generate PDF
        from core.pdf_generator import get_pdf_generator
        pdf_generator = get_pdf_generator()
        pdf_bytes = pdf_generator.generate_report(report)
        
        # Generate filename
        report_id = report.get("report_id", f"IOR-{session_id[:8]}")
        filename = f"{report_id}.pdf"
        
        logger.info(f"Generated PDF report: {filename}")
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF export error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")


@app.get("/research/{session_id}/export/audio")
async def export_audio_brief(session_id: str):
    """
    Generate an Audio Brief (TTS) of the research report
    
    Returns a downloadable MP3 file with a spoken summary of key findings
    """
    from fastapi.responses import FileResponse
    
    try:
        # Check if report exists
        if session_id not in completed_reports:
            raise HTTPException(status_code=404, detail="Report not found. Research may still be in progress.")
        
        report = completed_reports[session_id]
        
        # Generate Audio Brief
        from core.tts_generator import get_tts_generator
        tts_generator = get_tts_generator()
        audio_path = tts_generator.generate_audio_brief(session_id, report)
        
        if not audio_path:
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate audio. Please install gTTS: pip install gtts"
            )
        
        # Generate filename
        report_id = report.get("report_id", f"IOR-{session_id[:8]}")
        filename = f"{report_id}_brief.mp3"
        
        logger.info(f"Generated audio brief: {filename}")
        
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=filename,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio export error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate audio: {str(e)}")

@app.post("/research/demo")
async def run_demo_research(background_tasks: BackgroundTasks):
    """
    Run a demo research session with pre-configured query
    
    This is for demonstration purposes - runs the "Battery Technology" scenario
    """
    demo_query = ResearchRequest(
        query="next-generation battery technology for electric vehicles",
        domain="energy storage",
        geographic_scope=["US", "EU", "CN", "JP"],
        time_range_years=5,
        max_recursion_depth=3,
    )
    
    return await start_research(demo_query, background_tasks)


# ============================================
# WebSocket for Real-time Updates (Optional)
# ============================================

from fastapi import WebSocket, WebSocketDisconnect

connected_clients: dict[str, list[WebSocket]] = {}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time research updates"""
    await websocket.accept()
    
    if session_id not in connected_clients:
        connected_clients[session_id] = []
    connected_clients[session_id].append(websocket)
    
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            
            # Handle ping
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        connected_clients[session_id].remove(websocket)
        if not connected_clients[session_id]:
            del connected_clients[session_id]


async def broadcast_update(session_id: str, update: dict):
    """Broadcast update to all connected clients for a session"""
    if session_id in connected_clients:
        for client in connected_clients[session_id]:
            try:
                await client.send_json(update)
            except:
                pass


# Register broadcast callback with state manager
def setup_broadcast():
    """Setup broadcast callbacks"""
    state_manager = get_state_manager()
    
    async def on_status_update(session_id: str, data: dict):
        await broadcast_update(session_id, {"type": "status_update", "data": data})
    
    state_manager.on_event("agent_status_updated", on_status_update)
    state_manager.on_event("phase_updated", on_status_update)


# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    setup_broadcast()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info",
    )
