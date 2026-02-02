# NEXUS-R&D Architecture

> **Clean, modular, and architectural design for maintainability and extensibility**

## 📁 Project Structure

```
nexus-rd/
├── backend/                    # Python FastAPI Backend
│   ├── main.py                 # Application entry point & API endpoints
│   ├── orchestrator.py         # Master workflow coordinator
│   ├── config.py               # Centralized configuration management
│   ├── requirements.txt        # Python dependencies
│   │
│   ├── agents/                 # Multi-Agent System (5 Specialized Agents)
│   │   ├── __init__.py         # Agent exports
│   │   ├── base_agent.py       # Abstract base class for all agents
│   │   ├── patent_scout.py     # Patent landscape analysis agent
│   │   ├── market_analyst.py   # Market intelligence agent
│   │   ├── tech_trend.py       # Research paper analysis agent
│   │   ├── verifier.py         # Adversarial verification agent
│   │   └── synthesizer.py      # Report synthesis agent
│   │
│   ├── core/                   # Core Services
│   │   ├── __init__.py         # Core exports
│   │   ├── gemini_engine.py    # Gemini 3 AI integration
│   │   ├── models.py           # Pydantic data models
│   │   ├── state_manager.py    # Session & state management
│   │   ├── pdf_generator.py    # PDF report generation
│   │   ├── tts_generator.py    # ElevenLabs TTS integration
│   │   └── demo_data.py        # Demo mode data generation
│   │
│   └── static/                 # Generated files (audio, PDFs)
│
└── frontend/                   # Next.js 15 Frontend
    ├── app/                    # App Router
    │   ├── page.tsx            # Landing page
    │   ├── research/           # Research dashboard
    │   ├── layout.tsx          # Root layout
    │   └── globals.css         # Global styles
    │
    └── components/             # React Components
        ├── ResearchDashboard.tsx
        ├── ThemeToggle.tsx
        └── CitationGraph.tsx
```

---

## 🏗️ Design Patterns Used

### 1. **Abstract Factory Pattern** (Agents)
```python
class BaseAgent(ABC):
    """Abstract base class - all agents inherit from this"""
    
    @abstractmethod
    async def execute(self, query: ResearchQuery) -> Dict[str, Any]:
        """Must be implemented by each specialized agent"""
        pass
```

### 2. **Singleton Pattern** (Configuration & Services)
```python
@lru_cache()
def get_settings() -> Settings:
    """Cached singleton for configuration"""
    return Settings()

def get_orchestrator() -> Orchestrator:
    """Singleton orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator
```

### 3. **Dependency Injection** (State Management)
```python
class BaseAgent:
    def __init__(self, agent_id: str):
        # Services injected at initialization
        self.state_manager = get_state_manager()
        self.memory = get_recursive_memory()
        self.gemini = get_gemini_engine()
```

### 4. **Observer Pattern** (WebSocket Updates)
```python
# Real-time status broadcasting to connected clients
async def broadcast_update(session_id: str, update: dict):
    if session_id in connected_clients:
        for ws in connected_clients[session_id]:
            await ws.send_json(update)
```

---

## 🔄 Data Flow Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend   │────▶│   FastAPI API    │────▶│   Orchestrator  │
│  (Next.js)   │◀────│   (main.py)      │◀────│                 │
└──────────────┘     └──────────────────┘     └────────┬────────┘
                              │                        │
                              │                        ▼
                     ┌────────┴────────┐     ┌─────────────────┐
                     │  State Manager  │◀────│   Agent Layer   │
                     │  (WebSocket)    │     │  (5 Scholars)   │
                     └─────────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
                                             ┌─────────────────┐
                                             │  Gemini 3 +     │
                                             │  External APIs  │
                                             └─────────────────┘
```

---

## 🧠 Agent Responsibilities

| Agent | Single Responsibility | Input | Output |
|-------|----------------------|-------|--------|
| **Patent Scout** | Patent landscape analysis | Query | Patents, citations, claims |
| **Market Analyst** | Market intelligence | Query | Market signals, funding data |
| **Tech Trend** | Research paper analysis | Query | Papers, trends, TRL levels |
| **Verifier** | Adversarial fact-checking | Claims | Verification score, contradictions |
| **Synthesizer** | Report generation | All data | Final IOR report |

---

## 📊 Type Safety (Pydantic Models)

All data structures are type-safe using Pydantic:

```python
class ResearchQuery(BaseModel):
    query: str
    domain: Optional[str] = None
    geographic_scope: List[str] = ["US", "EU", "CN"]
    time_range_years: int = 5
    max_recursion_depth: int = 4

class Patent(BaseModel):
    patent_id: str
    title: str
    abstract: str
    claims: List[str]
    assignee: Optional[str]
    filing_date: Optional[datetime]
    relevance_score: float = 0.0
```

---

## ⚙️ Configuration Management

All settings are loaded from environment variables with Pydantic validation:

```python
class Settings(BaseSettings):
    # Type-validated from .env
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    max_recursion_depth: int = Field(4, env="MAX_RECURSION_DEPTH")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

---

## 🧪 Error Handling Strategy

Every async operation is wrapped with proper error handling:

```python
async def _run_agent(self, agent, session_id, query):
    try:
        result = await agent.execute(query)
        return result
    except Exception as e:
        logger.error(f"{agent.name} failed: {e}")
        # Graceful degradation - return empty instead of crash
        return {}
```

---

## 📈 Extensibility

To add a new agent:

1. Create `agents/new_agent.py`
2. Inherit from `BaseAgent`
3. Implement `execute()` method
4. Register in `agents/__init__.py`
5. Add to orchestrator workflow

```python
class NewAgent(BaseAgent):
    def __init__(self):
        super().__init__("new_agent")
    
    async def execute(self, query: ResearchQuery) -> Dict[str, Any]:
        # Your implementation
        pass
```

---

*Built with ❤️ for the VETROX AGENTIC 3.0 Hackathon*
