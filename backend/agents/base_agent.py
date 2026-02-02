"""
NEXUS-R&D Base Agent
Abstract base class for all research agents
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from loguru import logger

from core.models import (
    AgentStatus,
    AgentState,
    AgentMessage,
    ResearchQuery,
)
from core.state_manager import get_state_manager, get_recursive_memory
from core.gemini_engine import get_gemini_engine
from config import AGENT_CONFIG


class BaseAgent(ABC):
    """
    Abstract base class for all NEXUS-R&D research agents
    
    Each agent is responsible for a specific aspect of research:
    - Patent Scout: Patent landscape analysis
    - Market Analyst: Market intelligence
    - Tech Trend: Research paper analysis
    - Verifier: Cross-reference verification
    - Synthesizer: Final report generation
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.config = AGENT_CONFIG.get(agent_id, {})
        self.name = self.config.get("name", agent_id)
        self.emoji = self.config.get("emoji", "🤖")
        self.description = self.config.get("description", "")
        
        # Get shared services
        self.state_manager = get_state_manager()
        self.memory = get_recursive_memory()
        self.gemini = get_gemini_engine()
        
        # Agent state
        self.current_session_id: Optional[str] = None
        self.status = AgentStatus.IDLE
        self.current_task: Optional[str] = None
        self.progress = 0.0
        self.results_count = 0
        
        logger.info(f"{self.emoji} {self.name} agent initialized")
    
    async def start(self, session_id: str, query: ResearchQuery) -> Dict[str, Any]:
        """
        Start the agent's research task
        
        Args:
            session_id: The research session ID
            query: The research query
            
        Returns:
            Dictionary containing the agent's results
        """
        self.current_session_id = session_id
        self.status = AgentStatus.RUNNING
        self.progress = 0.0
        self.results_count = 0
        
        await self._update_status("Starting analysis...")
        
        try:
            # Execute the main research task
            results = await self.execute(query)
            
            # Store discoveries in memory
            await self._store_discoveries(results)
            
            self.status = AgentStatus.COMPLETED
            await self._update_status("Analysis complete", progress=100.0)
            
            logger.info(f"{self.emoji} {self.name} completed with {self.results_count} results")
            
            return results
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            await self._update_status(f"Error: {str(e)}", progress=self.progress, error=str(e))
            logger.error(f"{self.emoji} {self.name} error: {e}")
            raise
    
    @abstractmethod
    async def execute(self, query: ResearchQuery) -> Dict[str, Any]:
        """
        Execute the agent's main research task
        Must be implemented by each specialized agent
        
        Args:
            query: The research query
            
        Returns:
            Dictionary containing the agent's results
        """
        pass
    
    async def _update_status(
        self,
        task: str,
        progress: Optional[float] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update agent status in state manager"""
        self.current_task = task
        if progress is not None:
            self.progress = progress
            
        await self.state_manager.update_agent_status(
            session_id=self.current_session_id,
            agent_id=self.agent_id,
            status=self.status,
            current_task=task,
            progress=self.progress,
            results_count=self.results_count,
            error=error,
        )
    
    async def _store_discoveries(self, results: Dict[str, Any]) -> None:
        """Store important discoveries in recursive memory"""
        # Override in subclasses to store agent-specific discoveries
        pass
    
    async def _increment_sources(self, count: int = 1) -> None:
        """Increment the sources analyzed counter"""
        await self.state_manager.increment_sources(self.current_session_id, count)
    
    async def _add_discovery(
        self,
        discovery_type: str,
        content: Any,
        confidence: float = 1.0,
        recursion_level: int = 0,
    ) -> None:
        """Add a discovery to memory"""
        await self.memory.add_discovery(
            session_id=self.current_session_id,
            discovery_type=discovery_type,
            content=content,
            source=self.agent_id,
            confidence=confidence,
            recursion_level=recursion_level,
        )
        self.results_count += 1
    
    async def _add_whitespace_hint(self, hint: str, evidence: List[str]) -> None:
        """Add a whitespace opportunity hint"""
        await self.memory.add_whitespace_hint(
            session_id=self.current_session_id,
            hint=hint,
            evidence=evidence,
            agent_source=self.agent_id,
        )
    
    async def _track_entity(
        self,
        entity_type: str,
        entity_name: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Track an important entity"""
        await self.memory.track_entity(
            session_id=self.current_session_id,
            entity_type=entity_type,
            entity_name=entity_name,
            metadata=metadata,
        )
    
    async def _record_research_path(
        self,
        from_query: str,
        to_query: str,
        reason: str,
        recursion_level: int,
    ) -> None:
        """Record a recursive research path"""
        await self.memory.record_research_path(
            session_id=self.current_session_id,
            from_query=from_query,
            to_query=to_query,
            reason=reason,
            recursion_level=recursion_level,
        )
    
    async def send_message(
        self,
        to_agent: str,
        message_type: str,
        payload: Dict[str, Any],
        requires_response: bool = False,
    ) -> None:
        """Send a message to another agent"""
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            requires_response=requires_response,
        )
        await self.state_manager.send_message(self.current_session_id, message)
    
    async def receive_message(self, timeout: float = 30.0) -> Optional[AgentMessage]:
        """Receive a message from another agent"""
        return await self.state_manager.receive_message(
            session_id=self.current_session_id,
            agent_id=self.agent_id,
            timeout=timeout,
        )
    
    def log(self, message: str, level: str = "info") -> None:
        """Log a message with agent context"""
        log_message = f"{self.emoji} [{self.name}] {message}"
        getattr(logger, level)(log_message)
