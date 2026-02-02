"""
NEXUS-R&D Core Package
Central components for the research system
"""

from core.models import (
    ResearchQuery,
    ResearchSession,
    ResearchPhase,
    AgentStatus,
    Patent,
    PatentLandscape,
    MarketIntelligence,
    TechTrendAnalysis,
    VerificationReport,
    InnovationWhitespace,
    InnovationOpportunityReport,
)

from core.state_manager import (
    StateManager,
    RecursiveMemory,
    get_state_manager,
    get_recursive_memory,
)

from core.gemini_engine import (
    GeminiEngine,
    get_gemini_engine,
)

from core.demo_data import DemoDataProvider

__all__ = [
    # Models
    "ResearchQuery",
    "ResearchSession",
    "ResearchPhase",
    "AgentStatus",
    "Patent",
    "PatentLandscape",
    "MarketIntelligence",
    "TechTrendAnalysis",
    "VerificationReport",
    "InnovationWhitespace",
    "InnovationOpportunityReport",
    # State Management
    "StateManager",
    "RecursiveMemory",
    "get_state_manager",
    "get_recursive_memory",
    # AI Engine
    "GeminiEngine",
    "get_gemini_engine",
    # Demo Data
    "DemoDataProvider",
]
