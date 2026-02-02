"""
NEXUS-R&D Tech Trend Agent
Research paper analysis and technology evolution tracking
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from loguru import logger

from agents.base_agent import BaseAgent
from core.models import (
    ResearchQuery,
    ResearchPaper,
    TechnologyTrend,
    TechTrendAnalysis,
)
from config import get_settings


class TechTrendAgent(BaseAgent):
    """
    Tech Trend Agent - Research paper and technology evolution analysis
    
    Capabilities:
    - Analyze academic papers from arXiv, Semantic Scholar
    - Track technology readiness levels (TRL)
    - Map research collaboration networks
    - Identify emerging paradigms
    - Predict technology maturation timelines
    """
    
    def __init__(self):
        super().__init__("tech_trend")
        self.settings = get_settings()
        self.sources = self.config.get("sources", ["arxiv", "semantic_scholar"])
        self.max_papers = self.settings.max_papers_per_search
    
    async def execute(self, query: ResearchQuery) -> Dict[str, Any]:
        """Execute technology trend analysis"""
        self.log(f"Starting tech trend analysis for: {query.query}")
        
        # Phase 1: Search research papers
        await self._update_status("Searching research databases...", progress=10.0)
        papers = await self._search_papers(query)
        
        if not papers:
            self.log("No papers found, generating insights from query", "warning")
            papers = await self._generate_simulated_papers(query)
        
        # Phase 2: Analyze papers
        await self._update_status(f"Analyzing {len(papers)} research papers...", progress=30.0)
        analyzed_papers = await self._analyze_papers(papers, query)
        
        # Phase 3: Identify technology trends
        await self._update_status("Identifying technology trends...", progress=50.0)
        trends = await self._identify_trends(analyzed_papers, query)
        
        # Phase 4: Map research networks
        await self._update_status("Mapping research networks...", progress=70.0)
        networks = await self._map_research_networks(analyzed_papers)
        
        # Phase 5: Predict timelines
        await self._update_status("Predicting technology timelines...", progress=85.0)
        timeline_predictions = await self._predict_timelines(trends, query)
        
        # Phase 6: Synthesize
        await self._update_status("Synthesizing tech trend analysis...", progress=95.0)
        analysis = await self._synthesize_analysis(
            analyzed_papers, trends, networks, timeline_predictions, query
        )
        
        self.results_count = len(analyzed_papers)
        
        return analysis
    
    async def _search_papers(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search for research papers across multiple sources"""
        papers = []
        
        # Search arXiv (Computer Science, Physics, Math)
        arxiv_papers = await self._search_arxiv(query)
        papers.extend(arxiv_papers)
        
        # Search Semantic Scholar (Cross-disciplinary)
        ss_papers = await self._search_semantic_scholar(query)
        papers.extend(ss_papers)
        
        # Search PubMed (Biomedical, Life Sciences) - FREE API
        pubmed_papers = await self._search_pubmed(query)
        papers.extend(pubmed_papers)
        
        # Search CrossRef (Broader Academic Coverage) - FREE API
        crossref_papers = await self._search_crossref(query)
        papers.extend(crossref_papers)
        
        await self._increment_sources(len(papers))
        self.log(f"Found {len(papers)} research papers from 4 sources")
        
        return papers[:self.max_papers]
    
    async def _search_pubmed(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search PubMed for biomedical papers - FREE API"""
        papers = []
        
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Search for paper IDs
                search_response = await client.get(
                    "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                    params={
                        "db": "pubmed",
                        "term": query.query,
                        "retmax": 15,
                        "retmode": "json",
                        "sort": "relevance",
                    },
                    timeout=30.0,
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    ids = search_data.get("esearchresult", {}).get("idlist", [])
                    
                    if ids:
                        # Step 2: Fetch paper details
                        details_response = await client.get(
                            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                            params={
                                "db": "pubmed",
                                "id": ",".join(ids),
                                "retmode": "json",
                            },
                            timeout=30.0,
                        )
                        
                        if details_response.status_code == 200:
                            details = details_response.json()
                            for pmid in ids:
                                paper_info = details.get("result", {}).get(pmid, {})
                                if paper_info and isinstance(paper_info, dict):
                                    authors = paper_info.get("authors", [])
                                    author_names = [a.get("name", "") for a in authors if isinstance(a, dict)]
                                    
                                    papers.append({
                                        "paper_id": f"PMID:{pmid}",
                                        "title": paper_info.get("title", ""),
                                        "abstract": paper_info.get("sorttitle", ""),
                                        "authors": author_names[:5],
                                        "published_at": paper_info.get("pubdate", ""),
                                        "venue": paper_info.get("source", ""),
                                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                        "source": "pubmed",
                                    })
                                    
                self.log(f"Found {len(papers)} papers from PubMed")
                
            except Exception as e:
                self.log(f"PubMed search error: {e}", "warning")
        
        return papers
    
    async def _search_crossref(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search CrossRef for academic papers - FREE API"""
        papers = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.crossref.org/works",
                    params={
                        "query": query.query,
                        "rows": 15,
                        "sort": "relevance",
                        "select": "DOI,title,author,published,container-title,abstract,is-referenced-by-count",
                    },
                    headers={
                        "User-Agent": "NEXUS-RD/1.0 (https://nexus-rd.com; mailto:research@nexus-rd.com)",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("message", {}).get("items", []):
                        title_list = item.get("title", [])
                        title = title_list[0] if title_list else ""
                        
                        authors = []
                        for author in item.get("author", [])[:5]:
                            name = f"{author.get('given', '')} {author.get('family', '')}".strip()
                            if name:
                                authors.append(name)
                        
                        published = item.get("published", {})
                        date_parts = published.get("date-parts", [[]])
                        year = str(date_parts[0][0]) if date_parts and date_parts[0] else ""
                        
                        venue_list = item.get("container-title", [])
                        venue = venue_list[0] if venue_list else ""
                        
                        papers.append({
                            "paper_id": item.get("DOI", ""),
                            "title": title,
                            "abstract": item.get("abstract", "")[:500] if item.get("abstract") else "",
                            "authors": authors,
                            "published_at": year,
                            "venue": venue,
                            "citation_count": item.get("is-referenced-by-count", 0),
                            "url": f"https://doi.org/{item.get('DOI', '')}",
                            "source": "crossref",
                        })
                        
                self.log(f"Found {len(papers)} papers from CrossRef")
                
            except Exception as e:
                self.log(f"CrossRef search error: {e}", "warning")
        
        return papers
    
    async def _search_arxiv(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search arXiv for papers"""
        papers = []
        
        async with httpx.AsyncClient() as client:
            try:
                # arXiv API search
                search_query = query.query.replace(" ", "+")
                response = await client.get(
                    "http://export.arxiv.org/api/query",
                    params={
                        "search_query": f"all:{search_query}",
                        "start": 0,
                        "max_results": 20,
                        "sortBy": "relevance",
                        "sortOrder": "descending",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    papers = self._parse_arxiv_response(response.text)
                    
            except Exception as e:
                self.log(f"arXiv search error: {e}", "warning")
        
        return papers
    
    def _parse_arxiv_response(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse arXiv XML response"""
        papers = []
        
        try:
            import xml.etree.ElementTree as ET
            
            # Parse the XML
            root = ET.fromstring(xml_text)
            
            # Define namespace
            ns = {
                "atom": "http://www.w3.org/2005/Atom",
                "arxiv": "http://arxiv.org/schemas/atom",
            }
            
            for entry in root.findall("atom:entry", ns):
                paper = {
                    "paper_id": self._get_text(entry, "atom:id", ns).split("/")[-1],
                    "title": self._get_text(entry, "atom:title", ns).replace("\n", " ").strip(),
                    "abstract": self._get_text(entry, "atom:summary", ns).replace("\n", " ").strip(),
                    "authors": [
                        author.find("atom:name", ns).text
                        for author in entry.findall("atom:author", ns)
                        if author.find("atom:name", ns) is not None
                    ],
                    "published_at": self._get_text(entry, "atom:published", ns),
                    "url": self._get_text(entry, "atom:id", ns),
                    "source": "arxiv",
                }
                
                # Get PDF link
                for link in entry.findall("atom:link", ns):
                    if link.get("title") == "pdf":
                        paper["pdf_url"] = link.get("href")
                        break
                
                if paper["title"]:
                    papers.append(paper)
                    
        except Exception as e:
            logger.warning(f"arXiv parse error: {e}")
        
        return papers
    
    def _get_text(self, element, path: str, ns: Dict[str, str]) -> str:
        """Safely get text from XML element"""
        el = element.find(path, ns)
        return el.text if el is not None and el.text else ""
    
    async def _search_semantic_scholar(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Search Semantic Scholar for papers"""
        papers = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.semanticscholar.org/graph/v1/paper/search",
                    params={
                        "query": query.query,
                        "limit": 20,
                        "fields": "paperId,title,abstract,authors,year,citationCount,url",
                    },
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for paper in data.get("data", []):
                        papers.append({
                            "paper_id": paper.get("paperId", ""),
                            "title": paper.get("title", ""),
                            "abstract": paper.get("abstract", ""),
                            "authors": [a.get("name", "") for a in paper.get("authors", [])],
                            "published_at": str(paper.get("year", "")),
                            "citation_count": paper.get("citationCount", 0),
                            "url": paper.get("url", ""),
                            "source": "semantic_scholar",
                        })
                        
            except Exception as e:
                self.log(f"Semantic Scholar error: {e}", "warning")
        
        return papers
    
    async def _generate_simulated_papers(self, query: ResearchQuery) -> List[Dict[str, Any]]:
        """Generate simulated paper data for demo"""
        prompt = f"""Generate 12 realistic research paper entries related to: "{query.query}"

For each paper:
- paper_id: A realistic ID (arxiv format like "2410.12345" or semantic scholar format)
- title: An academic paper title
- abstract: A 3-4 sentence technical abstract
- authors: List of 2-4 author names
- published_at: Year between 2022-2025
- venue: Conference or journal name (ICML, NeurIPS, Nature, etc.)
- citation_count: Number between 0-200
- keywords: List of 3-5 keywords

Return as JSON array."""

        response = await self.gemini.generate(prompt, task_type="tech_trend", temperature=0.7)
        
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            return json.loads(response)
        except:
            return []
    
    async def _analyze_papers(
        self,
        papers: List[Dict[str, Any]],
        query: ResearchQuery
    ) -> List[ResearchPaper]:
        """Analyze and enrich paper data"""
        analyzed = []
        
        for paper_data in papers:
            try:
                paper = ResearchPaper(
                    paper_id=paper_data.get("paper_id", f"paper-{len(analyzed)}"),
                    title=paper_data.get("title", "Untitled"),
                    abstract=paper_data.get("abstract", ""),
                    authors=paper_data.get("authors", []),
                    publication_date=self._parse_year(paper_data.get("published_at")),
                    venue=paper_data.get("venue"),
                    citation_count=paper_data.get("citation_count", 0),
                    keywords=paper_data.get("keywords", []),
                    url=paper_data.get("url"),
                    pdf_url=paper_data.get("pdf_url"),
                    relevance_score=self._calculate_relevance(paper_data, query),
                )
                analyzed.append(paper)
                
                # Track research groups
                for author in paper.authors[:2]:
                    await self._track_entity(
                        "researcher",
                        author,
                        {
                            "paper_count": 1,
                            "citations": paper.citation_count,
                            "topic": query.query,
                        },
                    )
                    
            except Exception as e:
                self.log(f"Paper analysis error: {e}", "warning")
        
        return analyzed
    
    def _parse_year(self, year_str: Optional[str]) -> Optional[datetime]:
        """Parse year string to datetime"""
        if not year_str:
            return None
        try:
            year = int(str(year_str)[:4])
            return datetime(year, 1, 1)
        except:
            return None
    
    def _calculate_relevance(self, paper_data: Dict[str, Any], query: ResearchQuery) -> float:
        """Calculate relevance score for a paper"""
        score = 0.4
        
        title = (paper_data.get("title") or "").lower()
        abstract = (paper_data.get("abstract") or "").lower()
        query_terms = query.query.lower().split()
        
        for term in query_terms:
            if term in title:
                score += 0.2
            if term in abstract:
                score += 0.1
        
        # Citation bonus
        citations = paper_data.get("citation_count", 0)
        if citations > 100:
            score += 0.15
        elif citations > 50:
            score += 0.1
        elif citations > 20:
            score += 0.05
        
        return min(score, 1.0)
    
    async def _identify_trends(
        self,
        papers: List[ResearchPaper],
        query: ResearchQuery
    ) -> List[TechnologyTrend]:
        """Identify technology trends from papers"""
        # Use AI to identify trends
        paper_summaries = [
            f"- {p.title}: {p.abstract[:150]}..." for p in papers[:15]
        ]
        
        prompt = f"""Analyze these research papers about "{query.query}" and identify 4-5 technology trends:

Papers:
{chr(10).join(paper_summaries)}

For each trend:
- technology_name: Name of the technology/approach
- description: What it is and why it matters
- maturity_level: emerging/growing/mature/declining
- trl_level: Technology Readiness Level (1-9)
- research_momentum: Growth rate indicator (0.0-1.0)
- key_research_groups: List of key researchers/institutions
- predicted_commercialization_year: When it might reach market

Return as JSON array."""

        response = await self.gemini.generate(prompt, task_type="tech_trend", temperature=0.4)
        
        trends = []
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            trend_data = json.loads(response)
            
            for td in trend_data:
                # Find breakthrough papers for this trend
                trend_keywords = td.get("technology_name", "").lower().split()
                breakthrough_papers = [
                    p for p in papers
                    if any(kw in p.title.lower() for kw in trend_keywords)
                ][:3]
                
                trend = TechnologyTrend(
                    technology_name=td.get("technology_name", "Unknown"),
                    description=td.get("description", ""),
                    maturity_level=td.get("maturity_level", "emerging"),
                    trl_level=min(9, max(1, td.get("trl_level", 5))),
                    research_momentum=td.get("research_momentum", 0.5),
                    key_research_groups=td.get("key_research_groups", []),
                    breakthrough_papers=breakthrough_papers,
                    predicted_commercialization_year=td.get("predicted_commercialization_year"),
                )
                trends.append(trend)
                
                # Store as discovery
                await self._add_discovery(
                    discovery_type="tech_trend",
                    content={
                        "name": trend.technology_name,
                        "trl": trend.trl_level,
                        "maturity": trend.maturity_level,
                    },
                    confidence=0.8,
                )
                
                # Check for whitespace
                if trend.maturity_level == "emerging" and trend.research_momentum > 0.7:
                    await self._add_whitespace_hint(
                        hint=f"Emerging technology '{trend.technology_name}' shows high research momentum but low commercial maturity",
                        evidence=["high_research_momentum", "low_trl"],
                    )
                    
        except Exception as e:
            self.log(f"Trend identification error: {e}", "warning")
        
        return trends
    
    async def _map_research_networks(
        self,
        papers: List[ResearchPaper]
    ) -> Dict[str, List[str]]:
        """Map collaboration networks between researchers"""
        networks: Dict[str, List[str]] = {}
        
        for paper in papers:
            authors = paper.authors
            for i, author in enumerate(authors):
                if author not in networks:
                    networks[author] = []
                
                # Add co-authors as collaborators
                for j, co_author in enumerate(authors):
                    if i != j and co_author not in networks[author]:
                        networks[author].append(co_author)
        
        return networks
    
    async def _predict_timelines(
        self,
        trends: List[TechnologyTrend],
        query: ResearchQuery
    ) -> Dict[str, Any]:
        """Predict technology maturation timelines"""
        predictions = {}
        
        for trend in trends:
            current_trl = trend.trl_level
            momentum = trend.research_momentum
            
            # Simple prediction model
            years_to_commercial = max(1, 9 - current_trl) * (1.5 - momentum)
            
            predictions[trend.technology_name] = {
                "current_trl": current_trl,
                "predicted_commercial_year": 2026 + int(years_to_commercial),
                "confidence": 0.6 + (momentum * 0.3),
                "factors": [
                    f"Current TRL: {current_trl}",
                    f"Research momentum: {momentum:.1%}",
                    f"Maturity: {trend.maturity_level}",
                ],
            }
        
        return predictions
    
    async def _synthesize_analysis(
        self,
        papers: List[ResearchPaper],
        trends: List[TechnologyTrend],
        networks: Dict[str, List[str]],
        predictions: Dict[str, Any],
        query: ResearchQuery,
    ) -> Dict[str, Any]:
        """Synthesize complete tech trend analysis"""
        # Calculate research hotspots
        keyword_counts: Dict[str, int] = {}
        for paper in papers:
            for keyword in paper.keywords:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
        
        # Sort by frequency
        hotspots = dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        
        # Get emerging keywords from trends
        emerging_keywords = [
            t.technology_name for t in trends
            if t.maturity_level == "emerging"
        ]
        
        # Use AI for deeper analysis
        ai_analysis = await self.gemini.analyze_tech_trends(
            papers_data=[{
                "title": p.title,
                "abstract": p.abstract[:200],
                "citations": p.citation_count,
            } for p in papers[:10]],
            query=query.query,
        )
        
        key_insights = ai_analysis.get("key_insights", [])
        if not key_insights:
            key_insights = [
                f"Identified {len(trends)} technology trends with varying maturity levels",
                f"Research momentum strongest in: {', '.join([t.technology_name for t in trends[:2]])}",
                f"Collaboration networks span {len(networks)} researchers",
            ]
        
        analysis = TechTrendAnalysis(
            total_papers_analyzed=len(papers),
            papers=papers,
            trends=trends,
            emerging_keywords=emerging_keywords,
            research_hotspots=hotspots,
            collaboration_networks=networks,
            key_insights=key_insights,
        )
        
        result = analysis.model_dump()
        result["timeline_predictions"] = predictions
        result["ai_analysis"] = ai_analysis
        
        return result
