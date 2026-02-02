"""
NEXUS-R&D Demo Fallback Data Provider
Provides realistic demo data when Gemini API is unavailable
"""

from typing import Dict, Any, List
from datetime import datetime
import random


class DemoDataProvider:
    """
    Provides realistic demo data for all NEXUS-R&D analysis types.
    Used when Gemini API quota is exceeded or unavailable.
    """
    
    @staticmethod
    def get_patent_analysis(query: str) -> Dict[str, Any]:
        """Generate demo patent analysis data"""
        return {
            "key_technology_themes": [
                f"Advanced {query} system architecture",
                f"Machine learning applications in {query}",
                f"Distributed {query} protocols",
                f"Security mechanisms for {query}",
            ],
            "dominant_assignees": [
                {"name": "TechCorp Industries", "patent_count": 145, "strategy": "Broad portfolio coverage"},
                {"name": "Innovation Labs Inc", "patent_count": 89, "strategy": "Deep specialization"},
                {"name": "Global Research AG", "patent_count": 67, "strategy": "Defensive positioning"},
            ],
            "filing_trends": {
                "trend": "increasing",
                "growth_rate": "23% YoY",
                "peak_year": 2025,
            },
            "citation_insights": {
                "foundational_patents": ["US10234567", "US10345678", "EP3456789"],
                "emerging_patents": ["US11234567", "US11345678"],
            },
            "whitespace_areas": [
                f"Integration of {query} with edge computing",
                f"Privacy-preserving {query} implementations",
                f"Cross-platform {query} interoperability",
            ],
            "competitive_landscape": {
                "concentration": "moderate",
                "top_3_share": "42%",
                "barriers_to_entry": "medium",
            },
        }
    
    @staticmethod
    def get_market_analysis(query: str) -> Dict[str, Any]:
        """Generate demo market analysis data"""
        base_size = random.randint(50, 200) * 1000000000  # $50B-$200B
        return {
            "market_size_assessment": {
                "current_size_usd": base_size,
                "projected_2028_usd": base_size * 2.5,
                "cagr": "18.5%",
            },
            "key_players": [
                {"name": "MarketLeader Corp", "market_share": "28%", "position": "Leader"},
                {"name": "Innovate Partners", "market_share": "19%", "position": "Challenger"},
                {"name": "Emerging Tech Inc", "market_share": "12%", "position": "Fast Follower"},
            ],
            "funding_trends": {
                "total_2024_funding_usd": 4500000000,
                "deal_count": 156,
                "average_deal_size_usd": 28800000,
                "trend": "accelerating",
            },
            "regulatory_considerations": [
                "Increasing regulatory scrutiny expected",
                "New compliance frameworks emerging",
                "International standardization efforts underway",
            ],
            "commercial_viability": {
                "score": 8.2,
                "reasoning": f"Strong market fundamentals for {query} with proven business models",
            },
            "market_timing": {
                "recommendation": "favorable",
                "window": "18-24 months",
                "rationale": "Technology maturity aligning with market demand",
            },
        }
    
    @staticmethod
    def get_tech_trend_analysis(query: str) -> Dict[str, Any]:
        """Generate demo technology trend analysis data"""
        return {
            "emerging_themes": [
                f"Neural architectures for {query}",
                f"Federated approaches to {query}",
                f"Quantum-resistant {query} methods",
                f"Sustainable {query} implementations",
            ],
            "trl_assessment": {
                "current_trl": 6,
                "expected_trl_2026": 8,
                "gap_areas": ["Scale validation", "Production hardening"],
            },
            "key_research_groups": [
                {"name": "MIT AI Lab", "focus": "Foundational algorithms", "citations": 12500},
                {"name": "Stanford NLP Group", "focus": "Applied systems", "citations": 9800},
                {"name": "DeepMind Research", "focus": "Advanced architectures", "citations": 8900},
            ],
            "maturation_timeline": {
                "lab_prototype": "2023",
                "pilot_deployment": "2025",
                "commercial_scale": "2027",
                "market_saturation": "2030",
            },
            "breakthrough_indicators": [
                "Recent papers show 40% efficiency improvements",
                "Major tech companies increasing R&D investment",
                "Open source ecosystem maturing rapidly",
            ],
            "research_momentum": {
                "score": 0.85,
                "trend": "accelerating",
                "publication_growth": "35% YoY",
            },
            "key_insights": [
                f"Research in {query} is accelerating with 35% YoY publication growth",
                f"Major breakthrough expected in hybrid {query} architectures",
                "Industry-academia collaboration strengthening",
            ],
        }
    
    @staticmethod
    def get_verification_result(claims: List[str]) -> Dict[str, Any]:
        """Generate demo verification results"""
        verified_claims = []
        for i, claim in enumerate(claims[:10]):
            confidence = random.uniform(0.65, 0.95)
            status = "verified" if confidence > 0.8 else "partially_verified"
            verified_claims.append({
                "claim_id": i + 1,
                "original_claim": claim[:200],
                "verification_status": status,
                "confidence_score": round(confidence, 2),
                "supporting_sources": random.randint(2, 5),
                "contradicting_evidence": "none" if confidence > 0.85 else "minor discrepancies",
            })
        
        avg_confidence = sum(c["confidence_score"] for c in verified_claims) / len(verified_claims) if verified_claims else 0.75
        
        return {
            "verified_claims": verified_claims,
            "summary": {
                "total_claims_checked": len(verified_claims),
                "verified_count": sum(1 for c in verified_claims if c["verification_status"] == "verified"),
                "partially_verified_count": sum(1 for c in verified_claims if c["verification_status"] == "partially_verified"),
                "average_confidence": round(avg_confidence, 2),
            },
            "methodology": "Epistemic Verification Protocol (EVP) with multi-source validation",
        }
    
    @staticmethod
    def get_whitespace_opportunities(query: str) -> List[Dict[str, Any]]:
        """Generate demo whitespace opportunities"""
        opportunities = [
            {
                "title": f"AI-Enhanced {query} Automation Platform",
                "description": f"Gap identified between current {query} capabilities and market demand for intelligent automation. No dominant player has captured this intersection.",
                "opportunity_type": "technology_gap",
                "confidence_score": 0.87,
                "supporting_evidence": [
                    "Patent landscape shows limited coverage",
                    "Market research indicates high demand",
                    "Technical feasibility validated by recent papers",
                ],
                "potential_impact": "high",
                "time_sensitivity": "urgent",
                "competitive_landscape": "3-5 startups attempting, no clear leader",
                "recommended_actions": [
                    "File provisional patents in key areas",
                    "Build proof of concept within 6 months",
                    "Establish partnerships with key players",
                ],
                "estimated_market_size_usd": 2500000000,
            },
            {
                "title": f"Enterprise-Grade {query} Security Suite",
                "description": f"Security requirements for {query} implementations significantly outpace current solutions. Regulatory pressure creating urgency.",
                "opportunity_type": "market_gap",
                "confidence_score": 0.82,
                "supporting_evidence": [
                    "Regulatory mandates pending",
                    "Enterprise survey data shows pain point",
                    "Limited IP coverage in security layer",
                ],
                "potential_impact": "high",
                "time_sensitivity": "moderate",
                "competitive_landscape": "Legacy players slow to adapt",
                "recommended_actions": [
                    "Develop compliance-first architecture",
                    "Target financial services vertical first",
                    "Build certification partnerships",
                ],
                "estimated_market_size_usd": 1800000000,
            },
            {
                "title": f"Open-Source {query} Development Framework",
                "description": f"Developer ecosystem lacks comprehensive tooling for {query} applications. Community appetite for standardized frameworks.",
                "opportunity_type": "ecosystem_gap",
                "confidence_score": 0.78,
                "supporting_evidence": [
                    "GitHub activity analysis shows fragmentation",
                    "Developer surveys indicate tooling pain",
                    "No dominant open-source standard emerged",
                ],
                "potential_impact": "medium",
                "time_sensitivity": "moderate",
                "competitive_landscape": "Multiple fragmented projects",
                "recommended_actions": [
                    "Launch open-source initiative",
                    "Build enterprise support model",
                    "Establish developer community",
                ],
                "estimated_market_size_usd": 500000000,
            },
            {
                "title": f"Cross-Platform {query} Interoperability Layer",
                "description": f"Lack of standardized protocols preventing {query} adoption in heterogeneous environments.",
                "opportunity_type": "standards_gap",
                "confidence_score": 0.75,
                "supporting_evidence": [
                    "Industry consortia forming",
                    "Patent filings show interest",
                    "Technical specifications lacking",
                ],
                "potential_impact": "high",
                "time_sensitivity": "low",
                "competitive_landscape": "Early stage opportunity",
                "recommended_actions": [
                    "Join standards bodies",
                    "Publish reference implementations",
                    "Build industry alliance",
                ],
                "estimated_market_size_usd": 1200000000,
            },
        ]
        return opportunities
    
    @staticmethod
    def get_synthesis_report(query: str) -> Dict[str, Any]:
        """Generate demo synthesis report data"""
        return {
            "headline": f"Significant Innovation Opportunities Identified in {query} Landscape",
            "key_finding": f"Analysis reveals 4 major whitespace opportunities in the {query} sector with combined addressable market exceeding $6 billion. Immediate action recommended on AI automation and security verticals.",
            "executive_summary": f"Our multi-agent analysis of the {query} landscape has uncovered significant innovation opportunities that align strong technical feasibility with proven market demand. The convergence of maturing technology (TRL 6-7), favorable regulatory environment, and fragmented competitive landscape creates an optimal entry window for strategic investments.",
            "recommended_next_steps": [
                "Commission detailed technical feasibility study for top 2 opportunities",
                "Engage IP counsel for provisional patent strategy",
                "Initiate partnership discussions with identified potential collaborators",
                "Develop 90-day proof of concept roadmap",
            ],
            "confidence_score": 0.84,
            "risk_factors": [
                "Regulatory uncertainty in key jurisdictions",
                "Talent acquisition challenges in specialized areas",
                "Potential incumbent response acceleration",
            ],
            "success_factors": [
                "First-mover advantage in whitespace areas",
                "Strong technical foundations available",
                "Market timing favorable",
            ],
        }
    
    @staticmethod
    def get_audio_script(query: str, report: Dict[str, Any]) -> str:
        """Generate demo audio brief script"""
        return f"""Welcome to your NEXUS-R&D Innovation Opportunity Brief for {query}.

[PAUSE]

Today's analysis has uncovered significant opportunities that demand your attention. Let me walk you through the key findings.

[PAUSE]

Our multi-agent research system analyzed over 500 patents, 200 research papers, and extensive market data to identify four major whitespace opportunities with a combined addressable market exceeding six billion dollars.

[PAUSE]

The most urgent opportunity is in AI-enhanced automation platforms. We've identified a critical gap between current capabilities and market demand. No dominant player has captured this intersection yet, but the window is narrowing. I recommend filing provisional patents within the next 90 days.

[PAUSE]

The second major opportunity lies in enterprise-grade security solutions. Regulatory pressure is creating urgency here, and legacy players are slow to adapt. This represents an eighteen hundred million dollar opportunity with high impact potential.

[PAUSE]

From a technology readiness perspective, the core technologies are at TRL 6, with expected maturation to TRL 8 by 2026. The research momentum is accelerating, with 35% year-over-year growth in relevant publications.

[PAUSE]

My recommended next steps are as follows: First, commission a detailed technical feasibility study for the top two opportunities. Second, engage intellectual property counsel to develop a provisional patent strategy. Third, initiate partnership discussions with the key players we've identified. Finally, develop a 90-day proof of concept roadmap.

[PAUSE]

The overall confidence score for this analysis is 84 percent, based on verification from multiple independent sources through our Epistemic Verification Protocol.

[PAUSE]

Time is critical. The optimal patent filing window is within the next six to twelve months. I strongly recommend scheduling a strategy session within the next two weeks to capitalize on these opportunities.

This concludes your NEXUS-R&D Innovation Opportunity Brief. Full report details are available in your dashboard.
"""
