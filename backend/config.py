"""
NEXUS-R&D Configuration
Global settings and environment variable management
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    elevenlabs_api_key: Optional[str] = Field(None, env="ELEVENLABS_API_KEY")
    elevenlabs_voice_id: str = Field("21m00Tcm4TlvDq8ikWAM", env="ELEVENLABS_VOICE_ID")
    serper_api_key: Optional[str] = Field(None, env="SERPER_API_KEY")
    news_api_key: Optional[str] = Field(None, env="NEWS_API_KEY")
    
    # Database
    supabase_url: Optional[str] = Field(None, env="SUPABASE_URL")
    supabase_key: Optional[str] = Field(None, env="SUPABASE_KEY")
    
    # Redis
    redis_url: str = Field("redis://localhost:6379", env="REDIS_URL")
    
    # Application Settings
    debug: bool = Field(True, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # Research Settings
    max_recursion_depth: int = Field(4, env="MAX_RECURSION_DEPTH")
    min_verification_sources: int = Field(5, env="MIN_VERIFICATION_SOURCES")
    confidence_threshold: float = Field(0.85, env="CONFIDENCE_THRESHOLD")
    max_patents_per_search: int = Field(100, env="MAX_PATENTS_PER_SEARCH")
    max_papers_per_search: int = Field(50, env="MAX_PAPERS_PER_SEARCH")
    
    # Gemini Settings
    gemini_model: str = Field("gemini-2.0-flash", env="GEMINI_MODEL")
    gemini_thinking_model: str = Field("gemini-2.0-flash", env="GEMINI_THINKING_MODEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Agent Configuration
AGENT_CONFIG = {
    "patent_scout": {
        "name": "Patent Scout",
        "emoji": "🔍",
        "description": "Deep patent landscape analysis across global databases",
        "max_results": 100,
        "recursion_enabled": True,
    },
    "market_analyst": {
        "name": "Market Analyst",
        "emoji": "📊",
        "description": "Market intelligence and commercial viability assessment",
        "data_sources": ["crunchbase", "newsapi", "sec_edgar"],
    },
    "tech_trend": {
        "name": "Tech Trend",
        "emoji": "🔬",
        "description": "Research paper analysis and technology evolution tracking",
        "sources": ["arxiv", "semantic_scholar", "google_scholar"],
    },
    "verifier": {
        "name": "Verifier",
        "emoji": "✅",
        "description": "Adversarial verification and cross-reference validation",
        "min_sources": 5,
        "confidence_methods": ["bayesian", "consensus", "source_authority"],
    },
    "synthesizer": {
        "name": "Synthesizer",
        "emoji": "🧠",
        "description": "Intelligence synthesis and report generation",
        "output_formats": ["json", "markdown", "audio"],
    },
}

# Report Templates
REPORT_SECTIONS = [
    "executive_summary",
    "whitespace_opportunities",
    "patent_landscape",
    "market_intelligence",
    "temporal_forecast",
    "verification_chain",
    "strategic_recommendations",
]
