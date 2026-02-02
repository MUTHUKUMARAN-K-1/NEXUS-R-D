"""
NEXUS-R&D Synthesizer Agent
Final intelligence synthesis and report generation
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger

from agents.base_agent import BaseAgent
from core.models import (
    ResearchQuery,
    ResearchSession,
    ExecutiveSummary,
    InnovationWhitespace,
    TemporalForecast,
    InnovationOpportunityReport,
    PatentLandscape,
    MarketIntelligence,
    TechTrendAnalysis,
    VerificationReport,
    CompetitiveThreat,
)
from config import get_settings


class SynthesizerAgent(BaseAgent):
    """
    Synthesizer Agent - Master intelligence synthesis
    
    The FINAL agent that brings everything together.
    
    Capabilities:
    - Merge insights from all other agents
    - Identify non-obvious connections
    - Generate strategic recommendations
    - Create compelling Innovation Opportunity Reports
    - Generate audio briefs via ElevenLabs
    """
    
    def __init__(self):
        super().__init__("synthesizer")
        self.settings = get_settings()
        self.output_formats = self.config.get("output_formats", ["json", "markdown", "audio"])
    
    async def execute(
        self,
        query: ResearchQuery,
        all_results: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute final synthesis to create Innovation Opportunity Report"""
        self.log(f"Starting final synthesis for: {query.query}")
        
        # Extract component results
        patent_landscape = all_results.get("patent_landscape", {})
        market_intelligence = all_results.get("market_intelligence", {})
        tech_trends = all_results.get("tech_trends", {})
        verification_report = all_results.get("verification_report", {})
        
        # Phase 1: Identify whitespace opportunities
        await self._update_status("Detecting innovation whitespace...", progress=15.0)
        whitespace = await self._detect_whitespace(
            patent_landscape, market_intelligence, tech_trends, query
        )
        
        # Phase 2: Generate temporal forecasts
        await self._update_status("Generating temporal forecasts...", progress=35.0)
        forecasts = await self._generate_forecasts(tech_trends, patent_landscape, query)
        
        # Phase 3: Create executive summary
        await self._update_status("Creating executive summary...", progress=55.0)
        executive_summary = await self._create_executive_summary(
            whitespace, forecasts, market_intelligence, verification_report, query
        )
        
        # Phase 4: Generate strategic recommendations
        await self._update_status("Generating strategic recommendations...", progress=70.0)
        recommendations = await self._generate_recommendations(
            whitespace, forecasts, market_intelligence, query
        )
        
        # Phase 5: Analyze competitive threats
        await self._update_status("Analyzing competitive threats...", progress=80.0)
        competitive_threats = await self._analyze_competitive_threats(patent_landscape, market_intelligence)
        
        # Phase 6: Build final report
        await self._update_status("Building Innovation Opportunity Report...", progress=90.0)
        report = await self._build_report(
            query,
            executive_summary,
            whitespace,
            patent_landscape,
            market_intelligence,
            tech_trends,
            forecasts,
            verification_report,
            recommendations,
            competitive_threats,
        )
        
        # Phase 6: Generate audio brief (optional)
        if self.settings.elevenlabs_api_key:
            await self._update_status("Generating audio brief...", progress=95.0)
            audio_url, transcript = await self._generate_audio_brief(report)
            report["audio_brief_url"] = audio_url
            report["audio_brief_transcript"] = transcript
        
        self.results_count = len(whitespace)
        
        return report
    
    async def _detect_whitespace(
        self,
        patent_landscape: Dict[str, Any],
        market_intelligence: Dict[str, Any],
        tech_trends: Dict[str, Any],
        query: ResearchQuery,
    ) -> List[InnovationWhitespace]:
        """Detect innovation whitespace opportunities"""
        # Get hints from memory
        memory_hints = await self.memory.get_whitespace_hints(self.current_session_id)
        
        # Use AI for comprehensive whitespace detection
        whitespace_data = await self.gemini.detect_whitespace(
            patent_analysis=patent_landscape,
            market_analysis=market_intelligence,
            tech_analysis=tech_trends,
            query=query.query,
        )
        
        whitespace_opportunities = []
        
        for ws in whitespace_data:
            if not isinstance(ws, dict):
                continue
            
            # Ensure supporting_evidence is a list
            evidence = ws.get("supporting_evidence", [])
            if isinstance(evidence, str):
                evidence = [evidence] if evidence else []
            elif not isinstance(evidence, list):
                evidence = []
            
            # Ensure recommended_actions is a list
            actions = ws.get("recommended_actions", [])
            if isinstance(actions, str):
                actions = [actions] if actions else []
            elif not isinstance(actions, list):
                actions = []
            
            # Normalize confidence score
            conf_score = ws.get("confidence_score", 0.7)
            if isinstance(conf_score, (int, float)) and conf_score > 1:
                conf_score = conf_score / 100
                
            # Calculate investment score (0-100)
            impact_weights = {"high": 30, "medium": 20, "low": 10}
            time_weights = {"urgent": 20, "moderate": 15, "flexible": 10}
            
            investment_score = (
                (conf_score * 35) +  # Confidence: 35%
                impact_weights.get(ws.get("potential_impact", "medium"), 20) +  # Impact: 30%
                time_weights.get(ws.get("time_sensitivity", "moderate"), 15) +  # Timing: 20%
                (15 if ws.get("estimated_market_size_usd") else 5)  # Market size: 15%
            )
            investment_score = min(100, max(0, investment_score))
                
            opportunity = InnovationWhitespace(
                title=ws.get("title", "Untitled Opportunity"),
                description=ws.get("description", ""),
                opportunity_type=ws.get("opportunity_type", "technology_gap"),
                confidence_score=conf_score,
                supporting_evidence=evidence,
                potential_impact=ws.get("potential_impact", "medium"),
                time_sensitivity=ws.get("time_sensitivity", "moderate"),
                competitive_landscape=ws.get("competitive_landscape", "Not analyzed"),
                recommended_actions=actions,
                estimated_market_size_usd=ws.get("estimated_market_size_usd"),
                investment_score=investment_score,
            )
            whitespace_opportunities.append(opportunity)
            
            # Store as discovery
            await self._add_discovery(
                discovery_type="whitespace_opportunity",
                content={
                    "title": opportunity.title,
                    "type": opportunity.opportunity_type,
                    "confidence": opportunity.confidence_score,
                },
                confidence=opportunity.confidence_score,
            )
        
        # Add opportunities from memory hints
        for hint in memory_hints:
            if not any(ws.title == hint.get("hint", "")[:50] for ws in whitespace_opportunities):
                opportunity = InnovationWhitespace(
                    title=hint.get("hint", "")[:100],
                    description=hint.get("hint", ""),
                    opportunity_type="identified_gap",
                    confidence_score=0.6,
                    supporting_evidence=hint.get("evidence", []),
                    potential_impact="medium",
                    time_sensitivity="moderate",
                    competitive_landscape="Requires validation",
                    recommended_actions=["Conduct detailed feasibility study"],
                )
                whitespace_opportunities.append(opportunity)
        
        # Sort by confidence
        whitespace_opportunities.sort(key=lambda x: x.confidence_score, reverse=True)
        
        self.log(f"Identified {len(whitespace_opportunities)} whitespace opportunities")
        
        return whitespace_opportunities[:10]  # Return top 10
    
    async def _generate_forecasts(
        self,
        tech_trends: Dict[str, Any],
        patent_landscape: Dict[str, Any],
        query: ResearchQuery,
    ) -> List[TemporalForecast]:
        """Generate temporal forecasts for technologies"""
        forecasts = []
        
        # Get trends from tech analysis
        trends = tech_trends.get("trends", [])
        timeline_predictions = tech_trends.get("timeline_predictions", {})
        
        for trend in trends:
            if isinstance(trend, dict):
                tech_name = trend.get("technology_name", "Unknown")
                current_trl = trend.get("trl_level", 5)
            else:
                tech_name = getattr(trend, "technology_name", "Unknown")
                current_trl = getattr(trend, "trl_level", 5)
            
            prediction = timeline_predictions.get(tech_name, {})
            
            # Generate TRL timeline
            predicted_timeline = {}
            years_to_go = 9 - current_trl
            current_year = datetime.now().year
            
            for i in range(min(years_to_go + 1, 5)):
                year = current_year + i
                predicted_trl = min(9, current_trl + i)
                predicted_timeline[year] = predicted_trl
            
            forecast = TemporalForecast(
                technology=tech_name,
                current_trl=current_trl,
                predicted_trl_timeline=predicted_timeline,
                optimal_patent_window=self._calculate_patent_window(current_trl),
                competitive_threat_timeline=self._calculate_threat_timeline(current_trl),
                market_entry_recommendation=self._calculate_entry_recommendation(current_trl),
                confidence_score=prediction.get("confidence", 0.7),
            )
            forecasts.append(forecast)
        
        return forecasts
    
    def _calculate_patent_window(self, current_trl: int) -> str:
        """Calculate optimal patent filing window"""
        if current_trl <= 3:
            return "12-24 months - File provisional patents early"
        elif current_trl <= 5:
            return "6-12 months - File utility patents now"
        elif current_trl <= 7:
            return "URGENT: 0-6 months - Risk of prior art"
        else:
            return "Late window - Focus on improvement patents"
    
    def _calculate_threat_timeline(self, current_trl: int) -> str:
        """Calculate competitive threat timeline"""
        if current_trl <= 3:
            return "Low threat for 2-3 years"
        elif current_trl <= 5:
            return "Moderate threat in 12-18 months"
        elif current_trl <= 7:
            return "High threat - Competitors likely active"
        else:
            return "Immediate threat - Market entry imminent"
    
    def _calculate_entry_recommendation(self, current_trl: int) -> str:
        """Calculate market entry recommendation"""
        if current_trl <= 3:
            return "R&D investment phase - Build capabilities"
        elif current_trl <= 5:
            return "Pilot phase - Start proof of concepts"
        elif current_trl <= 7:
            return "Scale-up phase - Accelerate development"
        else:
            return "Commercial phase - Launch or acquire"
    
    async def _create_executive_summary(
        self,
        whitespace: List[InnovationWhitespace],
        forecasts: List[TemporalForecast],
        market_intelligence: Dict[str, Any],
        verification_report: Dict[str, Any],
        query: ResearchQuery,
    ) -> ExecutiveSummary:
        """Create executive summary using AI synthesis"""
        # Prepare data for AI
        synthesis_data = {
            "whitespace_opportunities": [ws.model_dump() for ws in whitespace[:5]],
            "forecasts": [f.model_dump() for f in forecasts[:5]],
            "market_highlights": {
                "total_funding": market_intelligence.get("funding_total_usd"),
                "startup_count": len(market_intelligence.get("relevant_startups", [])),
                "ma_count": len(market_intelligence.get("ma_activity", [])),
            },
            "verification_stats": {
                "average_confidence": verification_report.get("average_confidence"),
                "sources_used": verification_report.get("total_sources_used"),
            },
        }
        
        # Use Gemini for synthesis
        synthesis_result = await self.gemini.synthesize_report(
            query=query.query,
            patent_analysis={},  # Simplified for summary
            market_analysis=synthesis_data["market_highlights"],
            tech_analysis={},
            verification_report=synthesis_data["verification_stats"],
            whitespace_opportunities=synthesis_data["whitespace_opportunities"],
        )
        
        # Extract summary components
        headline = synthesis_result.get("headline", f"Innovation Opportunities in {query.query}")
        key_finding = synthesis_result.get("key_finding", 
            f"Identified {len(whitespace)} whitespace opportunities with strong market potential.")
        
        top_opportunities = [
            ws.title for ws in whitespace[:3]
        ]
        
        recommended_steps = synthesis_result.get("recommended_next_steps", [
            "Review top whitespace opportunities in detail",
            "Initiate patent landscape due diligence",
            "Evaluate strategic partnerships",
            "Develop proof of concept roadmap",
        ])[:4]
        
        overall_confidence = sum(ws.confidence_score for ws in whitespace) / len(whitespace) if whitespace else 0.7
        
        return ExecutiveSummary(
            headline=headline,
            key_finding=key_finding,
            top_opportunities=top_opportunities,
            recommended_next_steps=recommended_steps,
            overall_confidence=overall_confidence,
        )
    
    async def _generate_recommendations(
        self,
        whitespace: List[InnovationWhitespace],
        forecasts: List[TemporalForecast],
        market_intelligence: Dict[str, Any],
        query: ResearchQuery,
    ) -> List[Dict[str, Any]]:
        """Generate strategic recommendations"""
        recommendations = []
        
        # Based on whitespace opportunities
        for i, ws in enumerate(whitespace[:3]):
            recommendations.append({
                "priority": i + 1,
                "recommendation": f"Pursue '{ws.title}' opportunity",
                "rationale": ws.description[:200],
                "actions": ws.recommended_actions[:3],
                "time_sensitivity": ws.time_sensitivity,
            })
        
        # Based on temporal forecasts
        urgent_forecasts = [f for f in forecasts if "URGENT" in (f.optimal_patent_window or "")]
        if urgent_forecasts:
            recommendations.append({
                "priority": len(recommendations) + 1,
                "recommendation": "File provisional patents immediately",
                "rationale": f"Technology '{urgent_forecasts[0].technology}' is approaching critical patent window",
                "actions": ["Engage IP counsel", "Document innovations", "File provisional applications"],
                "time_sensitivity": "urgent",
            })
        
        # Based on market intelligence
        if market_intelligence.get("ma_activity"):
            recommendations.append({
                "priority": len(recommendations) + 1,
                "recommendation": "Monitor M&A landscape for partnership opportunities",
                "rationale": "Active M&A indicates strategic value in the sector",
                "actions": ["Identify potential targets", "Assess partnership fit", "Prepare acquisition thesis"],
                "time_sensitivity": "moderate",
            })
        
        return recommendations
    
    async def _analyze_competitive_threats(
        self,
        patent_landscape: Dict[str, Any],
        market_intelligence: Dict[str, Any],
    ) -> List[CompetitiveThreat]:
        """Analyze competitive threats from patent and market data"""
        threats = []
        
        # Get top patent assignees as potential competitors
        top_assignees = patent_landscape.get("top_assignees", {})
        
        for company, patent_count in list(top_assignees.items())[:5]:
            if not company or company == "Unknown":
                continue
            
            # Calculate threat level based on patent count
            if patent_count >= 20:
                threat_level = "high"
            elif patent_count >= 10:
                threat_level = "medium"
            else:
                threat_level = "low"
            
            # Estimate market overlap based on patent concentration
            total_patents = patent_landscape.get("total_patents", 1)
            market_overlap = min(1.0, patent_count / (total_patents * 0.3))
            
            threat = CompetitiveThreat(
                company_name=company,
                threat_level=threat_level,
                patent_count=patent_count,
                key_technologies=patent_landscape.get("whitespace_indicators", [])[:3],
                recent_filings=int(patent_count * 0.4),  # Estimate
                market_overlap=round(market_overlap, 2),
                threat_summary=f"{company} holds {patent_count} patents in this space with {threat_level} competitive threat.",
            )
            threats.append(threat)
        
        # Add startup threats from market intelligence
        startups = market_intelligence.get("relevant_startups", [])
        for startup in startups[:3]:
            if isinstance(startup, dict):
                name = startup.get("name", "Unknown")
                funding = startup.get("funding_total", 0) or 0
                
                # High funding = higher threat
                if funding >= 50_000_000:
                    threat_level = "high"
                elif funding >= 20_000_000:
                    threat_level = "medium"
                else:
                    threat_level = "low"
                
                threat = CompetitiveThreat(
                    company_name=name,
                    threat_level=threat_level,
                    patent_count=0,
                    key_technologies=[],
                    recent_filings=0,
                    market_overlap=0.5,
                    threat_summary=f"Startup {name} with ${funding/1_000_000:.0f}M funding represents {threat_level} competitive threat.",
                )
                threats.append(threat)
        
        self.log(f"Identified {len(threats)} competitive threats")
        return threats
    
    async def _build_report(
        self,
        query: ResearchQuery,
        executive_summary: ExecutiveSummary,
        whitespace: List[InnovationWhitespace],
        patent_landscape: Dict[str, Any],
        market_intelligence: Dict[str, Any],
        tech_trends: Dict[str, Any],
        forecasts: List[TemporalForecast],
        verification_report: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        competitive_threats: List[CompetitiveThreat] = None,
    ) -> Dict[str, Any]:
        """Build the final Innovation Opportunity Report"""
        # Get session info for timing
        session = await self.state_manager.get_session(self.current_session_id)
        processing_time = 0.0
        if session:
            processing_time = (datetime.now() - session.started_at).total_seconds()
        
        # Calculate totals
        total_patents = patent_landscape.get("total_patents", 0)
        total_papers = tech_trends.get("total_papers_analyzed", 0)
        total_sources = verification_report.get("total_sources_used", 0)
        
        # Build report object
        report = {
            "report_id": f"IOR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "query": query.model_dump(),
            "executive_summary": executive_summary.model_dump(),
            "whitespace_opportunities": [ws.model_dump() for ws in whitespace],
            "patent_landscape": patent_landscape,
            "market_intelligence": market_intelligence,
            "tech_trends": tech_trends,
            "temporal_forecasts": [f.model_dump() for f in forecasts],
            "verification_report": verification_report,
            "strategic_recommendations": recommendations,
            "competitive_threats": [t.model_dump() for t in (competitive_threats or [])],
            "metadata": {
                "total_sources_analyzed": total_sources + total_patents + total_papers,
                "total_patents_analyzed": total_patents,
                "total_papers_analyzed": total_papers,
                "processing_time_seconds": processing_time,
                "overall_confidence_score": executive_summary.overall_confidence,
            },
        }
        
        self.log(f"Built report: {report['report_id']} in {processing_time:.1f}s")
        
        return report
    
    async def _generate_audio_brief(
        self,
        report: Dict[str, Any],
    ) -> tuple[Optional[str], Optional[str]]:
        """Generate audio brief using ElevenLabs"""
        try:
            # Generate script from report
            script = await self.gemini.generate_audio_script(report)
            
            if not script:
                return None, None
            
            # Clean up script
            script = script.replace("[PAUSE]", "...")
            
            # Call ElevenLabs API
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{self.settings.elevenlabs_voice_id}",
                    json={
                        "text": script[:5000],  # Limit length
                        "model_id": "eleven_multilingual_v2",
                        "voice_settings": {
                            "stability": 0.5,
                            "similarity_boost": 0.75,
                        },
                    },
                    headers={
                        "xi-api-key": self.settings.elevenlabs_api_key,
                        "Content-Type": "application/json",
                    },
                    timeout=60.0,
                )
                
                if response.status_code == 200:
                    # Save to static file
                    filename = f"static/{self.current_session_id}.mp3"
                    with open(filename, "wb") as f:
                        f.write(response.content)
                        
                    audio_url = f"http://localhost:8000/{filename}"
                    self.log(f"Audio brief saved to {filename}")
                    return audio_url, script
                else:
                    self.log(f"ElevenLabs error: {response.status_code} - {response.text}", "warning")
                    return None, script
                    
        except Exception as e:
            self.log(f"Audio generation error: {e}", "error")
            return None, None
