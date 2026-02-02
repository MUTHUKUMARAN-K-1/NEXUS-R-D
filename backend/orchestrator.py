"""
NEXUS-R&D Master Orchestrator
Coordinates all agents in recursive research workflow
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from loguru import logger

from core.models import ResearchQuery, ResearchPhase
from core.state_manager import get_state_manager, get_recursive_memory
from agents import (
    PatentScoutAgent,
    MarketAnalystAgent,
    TechTrendAgent,
    VerifierAgent,
    SynthesizerAgent,
)
from config import get_settings


class Orchestrator:
    """
    Master Orchestrator for NEXUS-R&D
    
    Coordinates the multi-agent research workflow:
    1. Patent Scout → Patent landscape analysis
    2. Market Analyst → Market intelligence (parallel)
    3. Tech Trend → Research paper analysis (parallel)
    4. Verifier → Cross-reference verification
    5. Synthesizer → Final report generation
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.state_manager = get_state_manager()
        self.memory = get_recursive_memory()
        
        # Initialize agents
        self.patent_scout = PatentScoutAgent()
        self.market_analyst = MarketAnalystAgent()
        self.tech_trend = TechTrendAgent()
        self.verifier = VerifierAgent()
        self.synthesizer = SynthesizerAgent()
        
        logger.info("Orchestrator initialized with all agents")
    
    async def run(self, session_id: str, query: ResearchQuery) -> Dict[str, Any]:
        """
        Execute the full research workflow
        
        Args:
            session_id: Existing session ID
            query: The research query
            
        Returns:
            Complete Innovation Opportunity Report
        """
        start_time = datetime.now()
        logger.info(f"Starting research workflow for: {query.query} (Session: {session_id})")
        
        # Session is already created by main.py
        # check if it exists just in case
        session = await self.state_manager.get_session(session_id)
        if not session:
             logger.warning(f"Session {session_id} not found, creating new one")
             session = await self.state_manager.create_session(query)
             session_id = session.session_id
        
        # Initialize memory for session
        await self.memory.initialize_session(session_id)
        
        try:
            # Phase 1: Parallel research execution
            await self.state_manager.update_phase(session_id, ResearchPhase.PATENT_SEARCH)
            
            logger.info("Phase 1: Executing research agents...")
            
            # Run agents SEQUENTIALLY to avoid rate limiting
            # (Gemini free tier has strict per-minute limits)
            
            logger.info("Running Patent Scout...")
            try:
                patent_result = await self._run_agent(self.patent_scout, session_id, query)
            except Exception as e:
                logger.error(f"Patent Scout failed: {e}")
                patent_result = {}
            
            await asyncio.sleep(1)  # Rate limit buffer
            
            logger.info("Running Market Analyst...")
            try:
                market_result = await self._run_agent(self.market_analyst, session_id, query)
            except Exception as e:
                logger.error(f"Market Analyst failed: {e}")
                market_result = {}
            
            await asyncio.sleep(1)  # Rate limit buffer
            
            logger.info("Running Tech Trend...")
            try:
                tech_result = await self._run_agent(self.tech_trend, session_id, query)
            except Exception as e:
                logger.error(f"Tech Trend failed: {e}")
                tech_result = {}
            
            # Phase 2: Verification
            await self.state_manager.update_phase(session_id, ResearchPhase.VERIFICATION)
            
            logger.info("Phase 2: Running verification agent...")
            
            # Combine results for verification
            combined_results = {
                "patent_landscape": patent_result,
                "market_intelligence": market_result,
                "tech_trends": tech_result,
            }
            
            verification_result = await self._run_verifier(
                session_id, query, combined_results
            )
            
            # Phase 3: Synthesis
            await self.state_manager.update_phase(session_id, ResearchPhase.SYNTHESIS)
            
            logger.info("Phase 3: Running synthesis agent...")
            
            # Add verification to combined results
            combined_results["verification_report"] = verification_result
            
            final_report = await self._run_synthesizer(
                session_id, query, combined_results
            )
            
            # Complete session
            await self.state_manager.update_phase(session_id, ResearchPhase.COMPLETED)
            
            # Add metadata
            processing_time = (datetime.now() - start_time).total_seconds()
            final_report["session_id"] = session_id
            final_report["processing_time_seconds"] = processing_time
            
            logger.info(f"Research completed in {processing_time:.1f}s")
            
            # Mark session complete
            await self.state_manager.complete_session(session_id)
            
            return final_report
            
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            await self.state_manager.complete_session(session_id, error=str(e))
            raise
    
    async def _run_agent(
        self,
        agent,
        session_id: str,
        query: ResearchQuery,
    ) -> Dict[str, Any]:
        """Run an agent with proper session context"""
        agent.current_session_id = session_id
        return await agent.start(session_id, query)
    
    async def _run_verifier(
        self,
        session_id: str,
        query: ResearchQuery,
        combined_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run the verifier agent with all collected claims"""
        self.verifier.current_session_id = session_id
        return await self.verifier.execute(query, claims_data=combined_results)
    
    async def _run_synthesizer(
        self,
        session_id: str,
        query: ResearchQuery,
        all_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run the synthesizer agent to create final report"""
        self.synthesizer.current_session_id = session_id
        return await self.synthesizer.execute(query, all_results)
    
    async def get_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a research session"""
        return await self.state_manager.get_session_summary(session_id)


# Singleton instance
_orchestrator: Optional[Orchestrator] = None


def get_orchestrator() -> Orchestrator:
    """Get or create singleton Orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
