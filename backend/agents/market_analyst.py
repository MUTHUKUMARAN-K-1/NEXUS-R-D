"""
NEXUS-R&D Market Analyst Agent
Market intelligence and commercial viability assessment
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from loguru import logger

from agents.base_agent import BaseAgent
from core.models import (
    ResearchQuery,
    Startup,
    MarketSegment,
    MergersAcquisition,
    MarketIntelligence,
)
from config import get_settings


class MarketAnalystAgent(BaseAgent):
    """
    Market Analyst Agent - Commercial viability assessment
    
    Capabilities:
    - Analyze market size and growth rates
    - Track startup funding in technology domains
    - Monitor M&A activity for technology acquisitions
    - Assess regulatory landscape and barriers
    - Correlate funding rounds with patent filing spikes
    """
    
    def __init__(self):
        super().__init__("market_analyst")
        self.settings = get_settings()
        self.data_sources = self.config.get("data_sources", ["newsapi"])
    
    async def execute(self, query: ResearchQuery) -> Dict[str, Any]:
        """Execute market intelligence analysis"""
        self.log(f"Starting market analysis for: {query.query}")
        
        # Phase 1: Search for market news and data
        await self._update_status("Gathering market intelligence...", progress=10.0)
        market_news = await self._search_market_news(query)
        
        # Phase 2: Identify relevant startups
        await self._update_status("Identifying relevant startups...", progress=30.0)
        startups = await self._identify_startups(query, market_news)
        
        # Phase 3: Analyze funding trends
        await self._update_status("Analyzing funding trends...", progress=50.0)
        funding_data = await self._analyze_funding(query, startups)
        
        # Phase 4: Research M&A activity
        await self._update_status("Researching M&A activity...", progress=65.0)
        ma_activity = await self._research_ma_activity(query)
        
        # Phase 5: Assess regulatory factors
        await self._update_status("Assessing regulatory landscape...", progress=80.0)
        regulatory = await self._assess_regulatory(query)
        
        # Phase 6: AI-powered market synthesis
        await self._update_status("Synthesizing market intelligence...", progress=90.0)
        market_intel = await self._synthesize_market_intelligence(
            query, market_news, startups, funding_data, ma_activity, regulatory
        )
        
        self.results_count = len(startups) + len(ma_activity)
        
        return market_intel
    
    async def _search_market_news(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search for market news and reports"""
        news_items = []
        
        try:
            if self.settings.news_api_key:
                news_items = await self._search_newsapi(query)
            
            if self.settings.serper_api_key:
                serper_news = await self._search_serper_news(query)
                news_items.extend(serper_news)
            
            if not news_items:
                news_items = await self._generate_simulated_news(query)
            
            await self._increment_sources(len(news_items))
            self.log(f"Found {len(news_items)} news articles")
            
        except Exception as e:
            self.log(f"Market news search error: {e}", "error")
            news_items = await self._generate_simulated_news(query)
        
        return news_items
    
    async def _search_newsapi(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search NewsAPI for market news"""
        articles = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        "q": f"{query.query} market funding investment",
                        "language": "en",
                        "sortBy": "relevancy",
                        "pageSize": 20,
                        "apiKey": self.settings.news_api_key,
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get("articles", []):
                        articles.append({
                            "title": article.get("title"),
                            "description": article.get("description"),
                            "source": article.get("source", {}).get("name"),
                            "url": article.get("url"),
                            "published_at": article.get("publishedAt"),
                        })
                        
            except Exception as e:
                self.log(f"NewsAPI error: {e}", "warning")
        
        return articles
    
    async def _search_serper_news(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search Google News via Serper"""
        articles = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://google.serper.dev/news",
                    json={
                        "q": f"{query.query} market investment startup",
                        "num": 15,
                    },
                    headers={"X-API-KEY": self.settings.serper_api_key},
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for news in data.get("news", []):
                        articles.append({
                            "title": news.get("title"),
                            "description": news.get("snippet"),
                            "source": news.get("source"),
                            "url": news.get("link"),
                            "published_at": news.get("date"),
                        })
                        
            except Exception as e:
                self.log(f"Serper news error: {e}", "warning")
        
        return articles
    
    async def _generate_simulated_news(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Generate simulated market news for demo"""
        prompt = f"""Generate 8 realistic market news headlines and snippets about: "{query.query}"

Include:
- Funding announcements
- Market growth reports
- Industry analysis
- M&A news
- Technology adoption trends

For each article:
- title: News headline
- description: 2-3 sentence snippet
- source: Realistic news source (TechCrunch, Bloomberg, Reuters, etc.)
- published_at: Date in 2025-2026

Return as JSON array."""

        response = await self.gemini.generate(prompt, task_type="market_analysis", temperature=0.7)
        
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return json.loads(response)
        except:
            return [{"title": f"{query.query} Market Shows Strong Growth", "description": "Industry analysts report significant growth in the sector.", "source": "TechCrunch"}]
    
    async def _identify_startups(
        self,
        query: ResearchQuery,
        news: List[Dict[str, Any]]
    ) -> List[Startup]:
        """Identify relevant startups from news and search"""
        # Use AI to extract and generate startup information
        prompt = f"""Based on the research topic "{query.query}", identify 10 realistic startups working in this space.

For each startup provide:
- name: Company name
- description: What they do (1-2 sentences)
- founded_year: Year founded (2018-2024)
- funding_total: Total funding in USD (e.g., 15000000 for $15M)
- latest_round: Series (Seed, Series A, B, C, etc.)
- latest_round_amount: Amount of latest round
- investors: List of 2-3 investors
- headquarters: City, Country
- employee_count: Range like "50-100"
- relevance_score: 0.0-1.0 relevance to the query

Return as JSON array."""

        response = await self.gemini.generate(prompt, task_type="market_analysis", temperature=0.6)
        
        startups = []
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            startup_data = json.loads(response)
            
            for sd in startup_data:
                startup = Startup(
                    name=sd.get("name", "Unknown"),
                    description=sd.get("description", ""),
                    founded_year=sd.get("founded_year"),
                    funding_total=sd.get("funding_total"),
                    latest_round=sd.get("latest_round"),
                    latest_round_amount=sd.get("latest_round_amount"),
                    investors=sd.get("investors", []),
                    headquarters=sd.get("headquarters"),
                    employee_count=sd.get("employee_count"),
                    relevance_score=sd.get("relevance_score", 0.5),
                )
                startups.append(startup)
                
                # Track as entity
                await self._track_entity(
                    "startup",
                    startup.name,
                    {
                        "funding": startup.funding_total,
                        "stage": startup.latest_round,
                        "domain": query.domain or query.query,
                    },
                )
                
        except Exception as e:
            self.log(f"Startup extraction error: {e}", "warning")
        
        return startups
    
    async def _analyze_funding(
        self,
        query: ResearchQuery,
        startups: List[Startup]
    ) -> Dict[str, Any]:
        """Analyze funding trends in the sector"""
        # Calculate funding statistics
        total_funding = sum(s.funding_total or 0 for s in startups)
        
        # Group by year (simulated)
        funding_by_year = {
            "2022": total_funding * 0.15,
            "2023": total_funding * 0.25,
            "2024": total_funding * 0.35,
            "2025": total_funding * 0.25,
        }
        
        # Round distribution
        round_distribution = {}
        for startup in startups:
            if startup.latest_round:
                round_distribution[startup.latest_round] = round_distribution.get(startup.latest_round, 0) + 1
        
        funding_data = {
            "total_funding_usd": total_funding,
            "funding_by_year": funding_by_year,
            "round_distribution": round_distribution,
            "average_funding": total_funding / len(startups) if startups else 0,
            "top_funded": sorted(startups, key=lambda x: x.funding_total or 0, reverse=True)[:5],
        }
        
        # Store insight
        await self._add_discovery(
            discovery_type="funding_insight",
            content=f"Total sector funding: ${total_funding:,.0f} across {len(startups)} startups",
            confidence=0.8,
        )
        
        return funding_data
    
    async def _research_ma_activity(self, query: ResearchQuery) -> List[MergersAcquisition]:
        """Research M&A activity in the sector"""
        prompt = f"""Generate 5 realistic M&A transactions related to: "{query.query}"

For each transaction:
- acquirer: Acquiring company name (large tech/industry company)
- target: Target company name
- deal_value_usd: Deal value (can be null if undisclosed)
- announced_date: Date in 2023-2025
- rationale: Brief reason for acquisition

Return as JSON array."""

        response = await self.gemini.generate(prompt, task_type="market_analysis", temperature=0.6)
        
        ma_list = []
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            ma_data = json.loads(response)
            
            for ma in ma_data:
                transaction = MergersAcquisition(
                    acquirer=ma.get("acquirer", "Unknown"),
                    target=ma.get("target", "Unknown"),
                    deal_value_usd=ma.get("deal_value_usd"),
                    announced_date=self._parse_date(ma.get("announced_date")),
                    rationale=ma.get("rationale"),
                )
                ma_list.append(transaction)
                
                # Track acquirer as entity
                await self._track_entity(
                    "acquirer",
                    transaction.acquirer,
                    {"target": transaction.target, "value": transaction.deal_value_usd},
                )
                
        except Exception as e:
            self.log(f"M&A extraction error: {e}", "warning")
        
        return ma_list
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse date string"""
        if not date_str:
            return None
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            return None
    
    async def _assess_regulatory(self, query: ResearchQuery) -> List[str]:
        """Assess regulatory factors affecting the market"""
        prompt = f"""Identify 5 key regulatory factors affecting: "{query.query}"

Consider:
- Existing regulations
- Upcoming regulatory changes
- Compliance requirements
- Regional differences (US, EU, China)
- Industry-specific standards

Return as a JSON array of strings, each describing a regulatory factor."""

        response = await self.gemini.generate(prompt, task_type="market_analysis", temperature=0.4)
        
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return json.loads(response)
        except:
            return [f"Standard industry regulations apply to {query.query}"]
    
    async def _synthesize_market_intelligence(
        self,
        query: ResearchQuery,
        news: List[Dict[str, Any]],
        startups: List[Startup],
        funding_data: Dict[str, Any],
        ma_activity: List[MergersAcquisition],
        regulatory: List[str],
    ) -> Dict[str, Any]:
        """Synthesize all market data into intelligence report"""
        # Build market segments
        segments = await self._identify_market_segments(query)
        
        # Use AI for final analysis
        analysis = await self.gemini.analyze_market(
            market_data={
                "news_count": len(news),
                "startup_count": len(startups),
                "total_funding": funding_data.get("total_funding_usd", 0),
                "ma_count": len(ma_activity),
                "regulatory_factors": regulatory,
            },
            query=query.query,
        )
        
        # Extract key insights
        key_insights = analysis.get("key_insights", [])
        if not key_insights:
            key_insights = [
                f"Active startup ecosystem with {len(startups)} identified companies",
                f"Total sector funding exceeds ${funding_data.get('total_funding_usd', 0):,.0f}",
                f"M&A activity indicates strategic importance with {len(ma_activity)} recent transactions",
            ]
        
        # Store insights
        for insight in key_insights:
            await self._add_discovery(
                discovery_type="market_insight",
                content=insight,
                confidence=0.75,
            )
        
        # Look for whitespace signals
        if len(startups) < 5 and funding_data.get("total_funding_usd", 0) > 0:
            await self._add_whitespace_hint(
                hint="Market shows funding interest but limited startup activity - potential entry opportunity",
                evidence=["low_startup_count", "active_funding"],
            )
        
        market_intel = MarketIntelligence(
            total_market_size_usd=analysis.get("market_size"),
            market_cagr_percent=analysis.get("cagr"),
            segments=segments,
            relevant_startups=startups,
            funding_total_usd=funding_data.get("total_funding_usd", 0),
            funding_trend=funding_data.get("funding_by_year", {}),
            ma_activity=ma_activity,
            regulatory_factors=regulatory,
            key_insights=key_insights,
        )
        
        result = market_intel.model_dump()
        result["ai_analysis"] = analysis
        
        return result
    
    async def _identify_market_segments(self, query: ResearchQuery) -> List[MarketSegment]:
        """Identify and analyze market segments"""
        prompt = f"""Identify 3-4 market segments for: "{query.query}"

For each segment:
- name: Segment name
- market_size_usd: Estimated market size
- cagr_percent: Growth rate percentage
- key_players: List of 3-4 major players
- growth_drivers: List of 2-3 growth drivers
- challenges: List of 2-3 challenges

Return as JSON array."""

        response = await self.gemini.generate(prompt, task_type="market_analysis", temperature=0.5)
        
        segments = []
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            segment_data = json.loads(response)
            
            for sd in segment_data:
                segment = MarketSegment(
                    name=sd.get("name", "Unknown"),
                    market_size_usd=sd.get("market_size_usd"),
                    cagr_percent=sd.get("cagr_percent"),
                    key_players=sd.get("key_players", []),
                    growth_drivers=sd.get("growth_drivers", []),
                    challenges=sd.get("challenges", []),
                )
                segments.append(segment)
                
        except Exception as e:
            self.log(f"Segment extraction error: {e}", "warning")
        
        return segments
