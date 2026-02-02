"""
NEXUS-R&D State Manager
Manages research session state and agent coordination
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from loguru import logger

from core.models import (
    ResearchSession,
    ResearchQuery,
    ResearchPhase,
    AgentStatus,
    AgentState,
    AgentMessage,
    InnovationOpportunityReport,
)


class StateManager:
    """
    Central state manager for NEXUS-R&D research sessions
    Coordinates agents and tracks progress through research phases
    """
    
    def __init__(self):
        self.sessions: Dict[str, ResearchSession] = {}
        self.agent_states: Dict[str, Dict[str, AgentState]] = {}  # session_id -> {agent_id -> state}
        self.message_queue: Dict[str, asyncio.Queue] = {}  # session_id -> message queue
        self.event_callbacks: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        
        logger.info("StateManager initialized")
    
    async def create_session(self, query: ResearchQuery) -> ResearchSession:
        """Create a new research session"""
        async with self._lock:
            session = ResearchSession(query=query)
            self.sessions[session.session_id] = session
            self.agent_states[session.session_id] = {}
            self.message_queue[session.session_id] = asyncio.Queue()
            
            # Initialize agent states
            for agent_id in ["patent_scout", "market_analyst", "tech_trend", "verifier", "synthesizer"]:
                self.agent_states[session.session_id][agent_id] = AgentState(
                    agent_id=agent_id,
                    agent_type=agent_id,
                    status=AgentStatus.IDLE,
                )
            
            logger.info(f"Created research session: {session.session_id}")
            await self._emit_event("session_created", session.session_id, {"session": session.model_dump()})
            
            return session
    
    async def get_session(self, session_id: str) -> Optional[ResearchSession]:
        """Get a research session by ID"""
        return self.sessions.get(session_id)
    
    async def update_phase(self, session_id: str, phase: ResearchPhase) -> None:
        """Update the current research phase"""
        async with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].phase = phase
                logger.info(f"Session {session_id} phase updated to: {phase.value}")
                await self._emit_event("phase_updated", session_id, {"phase": phase.value})
    
    async def update_agent_status(
        self,
        session_id: str,
        agent_id: str,
        status: AgentStatus,
        current_task: Optional[str] = None,
        progress: float = 0.0,
        results_count: int = 0,
        error: Optional[str] = None,
    ) -> None:
        """Update an agent's status"""
        async with self._lock:
            if session_id in self.agent_states:
                if agent_id not in self.agent_states[session_id]:
                    self.agent_states[session_id][agent_id] = AgentState(
                        agent_id=agent_id,
                        agent_type=agent_id,
                        status=status,
                    )
                
                state = self.agent_states[session_id][agent_id]
                state.status = status
                state.current_task = current_task
                state.progress_percent = progress
                state.results_count = results_count
                state.error_message = error
                state.last_updated = datetime.now()
                
                # Also update session's agent status map
                self.sessions[session_id].agent_statuses[agent_id] = status
                
                logger.debug(f"Agent {agent_id} status: {status.value} ({progress:.0f}%)")
                await self._emit_event("agent_status_updated", session_id, {
                    "agent_id": agent_id,
                    "status": status.value,
                    "current_task": current_task,
                    "progress": progress,
                    "results_count": results_count,
                })
    
    async def get_agent_states(self, session_id: str) -> Dict[str, AgentState]:
        """Get all agent states for a session"""
        return self.agent_states.get(session_id, {})
    
    async def increment_sources(self, session_id: str, count: int = 1) -> None:
        """Increment the total sources analyzed counter"""
        async with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].total_sources_analyzed += count
    
    async def increment_recursion_depth(self, session_id: str) -> int:
        """Increment and return the current recursion depth"""
        async with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].current_recursion_depth += 1
                return self.sessions[session_id].current_recursion_depth
            return 0
    
    async def send_message(self, session_id: str, message: AgentMessage) -> None:
        """Send a message to the session's message queue"""
        if session_id in self.message_queue:
            await self.message_queue[session_id].put(message)
            logger.debug(f"Message sent: {message.from_agent} -> {message.to_agent}")
    
    async def receive_message(
        self,
        session_id: str,
        agent_id: str,
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        """Receive a message for a specific agent"""
        if session_id not in self.message_queue:
            return None
        
        try:
            # This is a simplified implementation - in production, 
            # you'd have per-agent queues
            message = await asyncio.wait_for(
                self.message_queue[session_id].get(),
                timeout=timeout
            )
            if message.to_agent == agent_id:
                return message
            else:
                # Put it back if not for this agent
                await self.message_queue[session_id].put(message)
                return None
        except asyncio.TimeoutError:
            return None
    
    async def complete_session(
        self,
        session_id: str,
        report: Optional[InnovationOpportunityReport] = None,
        error: Optional[str] = None
    ) -> None:
        """Mark a session as completed"""
        async with self._lock:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.completed_at = datetime.now()
                
                if error:
                    session.phase = ResearchPhase.FAILED
                    session.error_message = error
                else:
                    session.phase = ResearchPhase.COMPLETED
                
                logger.info(f"Session {session_id} completed. Phase: {session.phase.value}")
                await self._emit_event("session_completed", session_id, {
                    "phase": session.phase.value,
                    "error": error,
                    "report_id": report.report_id if report else None,
                })
    
    def on_event(self, event_type: str, callback: Callable) -> None:
        """Register an event callback"""
        if event_type not in self.event_callbacks:
            self.event_callbacks[event_type] = []
        self.event_callbacks[event_type].append(callback)
    
    async def _emit_event(self, event_type: str, session_id: str, data: Dict[str, Any]) -> None:
        """Emit an event to all registered callbacks"""
        if event_type in self.event_callbacks:
            for callback in self.event_callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(session_id, data)
                    else:
                        callback(session_id, data)
                except Exception as e:
                    logger.error(f"Error in event callback: {e}")
    
    async def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the current session state"""
        session = await self.get_session(session_id)
        if not session:
            return {}
        
        agent_states = await self.get_agent_states(session_id)
        
        return {
            "session_id": session_id,
            "query": session.query.query,
            "phase": session.phase.value,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "recursion_depth": session.current_recursion_depth,
            "sources_analyzed": session.total_sources_analyzed,
            "agents": {
                agent_id: {
                    "status": state.status.value,
                    "task": state.current_task,
                    "progress": state.progress_percent,
                    "results": state.results_count,
                }
                for agent_id, state in agent_states.items()
            },
            "error": session.error_message,
        }


class RecursiveMemory:
    """
    Recursive memory system for tracking research paths and discoveries
    Enables agents to build on previous findings
    """
    
    def __init__(self):
        self.memory: Dict[str, Dict[str, Any]] = {}  # session_id -> memory
        self.research_paths: Dict[str, List[Dict[str, Any]]] = {}  # session_id -> paths
        self._lock = asyncio.Lock()
    
    async def initialize_session(self, session_id: str) -> None:
        """Initialize memory for a new session"""
        async with self._lock:
            self.memory[session_id] = {
                "discoveries": [],
                "verified_facts": [],
                "whitespace_hints": [],
                "key_entities": {},
                "citation_network": {},
            }
            self.research_paths[session_id] = []
    
    async def add_discovery(
        self,
        session_id: str,
        discovery_type: str,
        content: Any,
        source: str,
        confidence: float = 1.0,
        recursion_level: int = 0,
    ) -> None:
        """Add a discovery to memory"""
        async with self._lock:
            if session_id in self.memory:
                self.memory[session_id]["discoveries"].append({
                    "type": discovery_type,
                    "content": content,
                    "source": source,
                    "confidence": confidence,
                    "recursion_level": recursion_level,
                    "timestamp": datetime.now().isoformat(),
                })
    
    async def add_verified_fact(
        self,
        session_id: str,
        fact: str,
        sources: List[str],
        confidence: float,
    ) -> None:
        """Add a verified fact to memory"""
        async with self._lock:
            if session_id in self.memory:
                self.memory[session_id]["verified_facts"].append({
                    "fact": fact,
                    "sources": sources,
                    "confidence": confidence,
                    "verified_at": datetime.now().isoformat(),
                })
    
    async def add_whitespace_hint(
        self,
        session_id: str,
        hint: str,
        evidence: List[str],
        agent_source: str,
    ) -> None:
        """Add a whitespace opportunity hint"""
        async with self._lock:
            if session_id in self.memory:
                self.memory[session_id]["whitespace_hints"].append({
                    "hint": hint,
                    "evidence": evidence,
                    "agent_source": agent_source,
                    "timestamp": datetime.now().isoformat(),
                })
    
    async def track_entity(
        self,
        session_id: str,
        entity_type: str,
        entity_name: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Track an important entity (company, inventor, technology, etc.)"""
        async with self._lock:
            if session_id in self.memory:
                key = f"{entity_type}:{entity_name}"
                if key not in self.memory[session_id]["key_entities"]:
                    self.memory[session_id]["key_entities"][key] = {
                        "type": entity_type,
                        "name": entity_name,
                        "metadata": metadata,
                        "mentions": 1,
                    }
                else:
                    self.memory[session_id]["key_entities"][key]["mentions"] += 1
                    self.memory[session_id]["key_entities"][key]["metadata"].update(metadata)
    
    async def add_citation_link(
        self,
        session_id: str,
        source_id: str,
        target_id: str,
        link_type: str = "cites",
    ) -> None:
        """Add a citation link to the network"""
        async with self._lock:
            if session_id in self.memory:
                network = self.memory[session_id]["citation_network"]
                if source_id not in network:
                    network[source_id] = []
                network[source_id].append({
                    "target": target_id,
                    "type": link_type,
                })
    
    async def record_research_path(
        self,
        session_id: str,
        from_query: str,
        to_query: str,
        reason: str,
        recursion_level: int,
    ) -> None:
        """Record a recursive research path"""
        async with self._lock:
            if session_id in self.research_paths:
                self.research_paths[session_id].append({
                    "from": from_query,
                    "to": to_query,
                    "reason": reason,
                    "level": recursion_level,
                    "timestamp": datetime.now().isoformat(),
                })
    
    async def get_discoveries(
        self,
        session_id: str,
        discovery_type: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """Get discoveries from memory, optionally filtered"""
        if session_id not in self.memory:
            return []
        
        discoveries = self.memory[session_id]["discoveries"]
        
        if discovery_type:
            discoveries = [d for d in discoveries if d["type"] == discovery_type]
        
        if min_confidence > 0:
            discoveries = [d for d in discoveries if d["confidence"] >= min_confidence]
        
        return discoveries
    
    async def get_verified_facts(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all verified facts"""
        if session_id not in self.memory:
            return []
        return self.memory[session_id]["verified_facts"]
    
    async def get_whitespace_hints(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all whitespace hints"""
        if session_id not in self.memory:
            return []
        return self.memory[session_id]["whitespace_hints"]
    
    async def get_top_entities(
        self,
        session_id: str,
        entity_type: Optional[str] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get top mentioned entities"""
        if session_id not in self.memory:
            return []
        
        entities = list(self.memory[session_id]["key_entities"].values())
        
        if entity_type:
            entities = [e for e in entities if e["type"] == entity_type]
        
        entities.sort(key=lambda x: x["mentions"], reverse=True)
        return entities[:limit]
    
    async def get_research_paths(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all research paths taken"""
        return self.research_paths.get(session_id, [])
    
    async def get_full_memory(self, session_id: str) -> Dict[str, Any]:
        """Get the complete memory for a session"""
        if session_id not in self.memory:
            return {}
        
        return {
            "memory": self.memory[session_id],
            "research_paths": self.research_paths.get(session_id, []),
        }


# Singleton instances
_state_manager: Optional[StateManager] = None
_recursive_memory: Optional[RecursiveMemory] = None


def get_state_manager() -> StateManager:
    """Get or create singleton StateManager"""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager


def get_recursive_memory() -> RecursiveMemory:
    """Get or create singleton RecursiveMemory"""
    global _recursive_memory
    if _recursive_memory is None:
        _recursive_memory = RecursiveMemory()
    return _recursive_memory
