"""
NEXUS-R&D Core Models
Pydantic models for research states, results, and reports
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class AgentStatus(str, Enum):
    """Status of an agent's execution"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


class ResearchPhase(str, Enum):
    """Current phase of the research process"""
    INITIALIZING = "initializing"
    PATENT_SEARCH = "patent_search"
    MARKET_ANALYSIS = "market_analysis"
    TECH_TRENDS = "tech_trends"
    VERIFICATION = "verification"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """Confidence level for verified claims"""
    VERY_HIGH = "very_high"  # > 95%
    HIGH = "high"            # 85-95%
    MEDIUM = "medium"        # 70-85%
    LOW = "low"              # 50-70%
    UNVERIFIED = "unverified"  # < 50%


# ============================================
# Research Request & Response Models
# ============================================

class ResearchQuery(BaseModel):
    """Initial research query from user"""
    query: str = Field(..., description="The research question or topic")
    domain: Optional[str] = Field(None, description="Specific domain/industry focus")
    geographic_scope: List[str] = Field(default=["US", "EU", "CN", "JP"], description="Patent jurisdictions")
    time_range_years: int = Field(default=5, description="How many years back to search")
    max_recursion_depth: int = Field(default=4, description="How deep to recurse in research")
    priority_areas: List[str] = Field(default=[], description="Specific focus areas")


class ResearchSession(BaseModel):
    """Active research session tracking"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    query: ResearchQuery
    phase: ResearchPhase = ResearchPhase.INITIALIZING
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    agent_statuses: Dict[str, AgentStatus] = Field(default_factory=dict)
    current_recursion_depth: int = 0
    total_sources_analyzed: int = 0
    error_message: Optional[str] = None


# ============================================
# Patent Models
# ============================================

class Patent(BaseModel):
    """Individual patent record"""
    patent_id: str
    title: str
    abstract: str
    claims: List[str] = Field(default=[])
    inventors: List[str] = Field(default=[])
    assignee: Optional[str] = None
    filing_date: Optional[datetime] = None
    publication_date: Optional[datetime] = None
    jurisdiction: str = "US"
    classification_codes: List[str] = Field(default=[])
    citation_count: int = 0
    cited_patents: List[str] = Field(default=[])
    citing_patents: List[str] = Field(default=[])
    url: Optional[str] = None
    relevance_score: float = 0.0


class PatentCluster(BaseModel):
    """Group of related patents"""
    cluster_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    patents: List[Patent]
    dominant_assignees: List[str] = Field(default=[])
    technology_themes: List[str] = Field(default=[])
    average_age_years: float = 0.0
    growth_trend: str = "stable"  # growing, stable, declining


class PatentLandscape(BaseModel):
    """Complete patent landscape analysis"""
    total_patents: int
    patents: List[Patent]
    clusters: List[PatentCluster]
    top_assignees: Dict[str, int] = Field(default_factory=dict)
    filing_trend: Dict[str, int] = Field(default_factory=dict)  # year -> count
    technology_distribution: Dict[str, int] = Field(default_factory=dict)
    key_inventors: List[str] = Field(default=[])
    whitespace_indicators: List[str] = Field(default=[])


# ============================================
# Market Intelligence Models
# ============================================

class Startup(BaseModel):
    """Startup/company information"""
    name: str
    description: str
    founded_year: Optional[int] = None
    funding_total: Optional[float] = None
    latest_round: Optional[str] = None
    latest_round_amount: Optional[float] = None
    investors: List[str] = Field(default=[])
    headquarters: Optional[str] = None
    employee_count: Optional[str] = None
    website: Optional[str] = None
    relevance_score: float = 0.0


class MarketSegment(BaseModel):
    """Market segment analysis"""
    name: str
    market_size_usd: Optional[float] = None
    cagr_percent: Optional[float] = None
    key_players: List[str] = Field(default=[])
    growth_drivers: List[str] = Field(default=[])
    challenges: List[str] = Field(default=[])


class MergersAcquisition(BaseModel):
    """M&A transaction"""
    acquirer: str
    target: str
    deal_value_usd: Optional[float] = None
    announced_date: Optional[datetime] = None
    rationale: Optional[str] = None


class MarketIntelligence(BaseModel):
    """Complete market intelligence report"""
    total_market_size_usd: Optional[float] = None
    market_cagr_percent: Optional[float] = None
    segments: List[MarketSegment]
    relevant_startups: List[Startup]
    funding_total_usd: float = 0.0
    funding_trend: Dict[str, float] = Field(default_factory=dict)  # year -> amount
    ma_activity: List[MergersAcquisition] = Field(default=[])
    regulatory_factors: List[str] = Field(default=[])
    key_insights: List[str] = Field(default=[])


# ============================================
# Research & Technology Models
# ============================================

class ResearchPaper(BaseModel):
    """Academic research paper"""
    paper_id: str
    title: str
    abstract: str
    authors: List[str] = Field(default=[])
    publication_date: Optional[datetime] = None
    venue: Optional[str] = None  # journal/conference
    citation_count: int = 0
    keywords: List[str] = Field(default=[])
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    relevance_score: float = 0.0


class TechnologyTrend(BaseModel):
    """Technology trend analysis"""
    technology_name: str
    description: str
    maturity_level: str  # emerging, growing, mature, declining
    trl_level: int = Field(ge=1, le=9)  # Technology Readiness Level
    research_momentum: float = 0.0  # papers/year growth rate
    patent_momentum: float = 0.0  # patents/year growth rate
    key_research_groups: List[str] = Field(default=[])
    breakthrough_papers: List[ResearchPaper] = Field(default=[])
    predicted_commercialization_year: Optional[int] = None


class TechTrendAnalysis(BaseModel):
    """Complete technology trend analysis"""
    total_papers_analyzed: int
    papers: List[ResearchPaper]
    trends: List[TechnologyTrend]
    emerging_keywords: List[str] = Field(default=[])
    research_hotspots: Dict[str, int] = Field(default_factory=dict)
    collaboration_networks: Dict[str, List[str]] = Field(default_factory=dict)
    key_insights: List[str] = Field(default=[])


# ============================================
# Verification Models
# ============================================

class VerificationSource(BaseModel):
    """Individual source used for verification"""
    source_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_type: str  # patent, paper, news, report, database
    source_name: str
    url: Optional[str] = None
    authority_score: float = Field(ge=0, le=1)  # 0-1 credibility score
    access_date: datetime = Field(default_factory=datetime.now)
    relevant_excerpt: Optional[str] = None


class VerifiedClaim(BaseModel):
    """A verified claim with supporting evidence"""
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim_text: str
    confidence_score: float = Field(ge=0, le=1)
    confidence_level: ConfidenceLevel
    supporting_sources: List[VerificationSource]
    contradicting_sources: List[VerificationSource] = Field(default=[])
    verification_notes: Optional[str] = None
    verified_at: datetime = Field(default_factory=datetime.now)


class VerificationReport(BaseModel):
    """Complete verification report"""
    total_claims_analyzed: int
    verified_claims: List[VerifiedClaim]
    unverified_claims: List[str] = Field(default=[])
    total_sources_used: int
    source_distribution: Dict[str, int] = Field(default_factory=dict)
    average_confidence: float = 0.0
    verification_coverage: float = 0.0  # % of claims verified


# ============================================
# Whitespace & Opportunity Models
# ============================================

class InnovationWhitespace(BaseModel):
    """Identified innovation opportunity/gap"""
    whitespace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    opportunity_type: str  # technology_gap, market_gap, integration, timing
    confidence_score: float = Field(ge=0, le=1)
    supporting_evidence: List[str] = Field(default=[])
    potential_impact: str  # high, medium, low
    time_sensitivity: str  # urgent, moderate, flexible
    competitive_landscape: str
    recommended_actions: List[str] = Field(default=[])
    estimated_market_size_usd: Optional[float] = None
    investment_score: float = Field(default=0.0, ge=0, le=100)  # 0-100 investment attractiveness


class CompetitiveThreat(BaseModel):
    """Competitive threat analysis"""
    company_name: str
    threat_level: str  # high, medium, low
    patent_count: int = 0
    key_technologies: List[str] = Field(default=[])
    recent_filings: int = 0  # Patents filed in last 2 years
    market_overlap: float = Field(default=0.0, ge=0, le=1)  # 0-1 overlap score
    threat_summary: str = ""


class TemporalForecast(BaseModel):
    """Time-based predictions"""
    technology: str
    current_trl: int
    predicted_trl_timeline: Dict[int, int] = Field(default_factory=dict)  # year -> TRL
    optimal_patent_window: Optional[str] = None
    competitive_threat_timeline: Optional[str] = None
    market_entry_recommendation: Optional[str] = None
    confidence_score: float = 0.0


# ============================================
# Final Report Models
# ============================================

class ExecutiveSummary(BaseModel):
    """Executive summary section"""
    headline: str
    key_finding: str
    top_opportunities: List[str]
    recommended_next_steps: List[str]
    overall_confidence: float


class InnovationOpportunityReport(BaseModel):
    """Complete Innovation Opportunity Report (IOR)"""
    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    generated_at: datetime = Field(default_factory=datetime.now)
    query: ResearchQuery
    
    # Core Sections
    executive_summary: ExecutiveSummary
    whitespace_opportunities: List[InnovationWhitespace]
    patent_landscape: PatentLandscape
    market_intelligence: MarketIntelligence
    tech_trends: TechTrendAnalysis
    temporal_forecasts: List[TemporalForecast]
    verification_report: VerificationReport
    
    # Metadata
    total_sources_analyzed: int
    total_patents_analyzed: int
    total_papers_analyzed: int
    processing_time_seconds: float
    overall_confidence_score: float
    
    # Audio Brief (optional)
    audio_brief_url: Optional[str] = None
    audio_brief_transcript: Optional[str] = None


# ============================================
# Agent Communication Models
# ============================================

class AgentMessage(BaseModel):
    """Message passed between agents"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str
    to_agent: str
    message_type: str  # query, response, verification_request, challenge
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    requires_response: bool = False


class AgentState(BaseModel):
    """Current state of an agent"""
    agent_id: str
    agent_type: str
    status: AgentStatus
    current_task: Optional[str] = None
    progress_percent: float = 0.0
    results_count: int = 0
    error_message: Optional[str] = None
    last_updated: datetime = Field(default_factory=datetime.now)
