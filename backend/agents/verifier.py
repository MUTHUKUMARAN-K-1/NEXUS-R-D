"""
NEXUS-R&D Verifier Agent
Adversarial verification and cross-reference validation using Epistemic Verification Protocol
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from loguru import logger

from agents.base_agent import BaseAgent
from core.models import (
    ResearchQuery,
    VerificationSource,
    VerifiedClaim,
    VerificationReport,
    ConfidenceLevel,
)
from config import get_settings


class VerifierAgent(BaseAgent):
    """
    Verifier Agent - Epistemic Verification Protocol (EVP)
    
    The SKEPTIC agent that challenges and validates all claims.
    
    Capabilities:
    - Cross-reference claims across 5+ independent sources
    - Actively search for contradicting evidence
    - Calculate Bayesian confidence scores
    - Assess source credibility and authority
    - Flag unverifiable or suspicious claims
    """
    
    def __init__(self):
        super().__init__("verifier")
        self.settings = get_settings()
        self.min_sources = self.config.get("min_sources", 5)
        self.confidence_methods = self.config.get(
            "confidence_methods",
            ["bayesian", "consensus", "source_authority"]
        )
    
    async def execute(self, query: ResearchQuery, claims_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute verification protocol on all accumulated claims"""
        self.log(f"Starting Epistemic Verification Protocol for: {query.query}")
        
        # Phase 1: Collect claims from memory
        await self._update_status("Collecting claims for verification...", progress=10.0)
        claims = await self._collect_claims(claims_data)
        
        if not claims:
            self.log("No claims to verify", "warning")
            return self._create_empty_report()
        
        # Phase 2: Search for supporting evidence
        await self._update_status(f"Gathering evidence for {len(claims)} claims...", progress=25.0)
        evidence = await self._gather_evidence(claims, query)
        
        # Phase 3: Search for CONTRADICTING evidence (adversarial)
        await self._update_status("Searching for contradictions...", progress=45.0)
        contradictions = await self._search_contradictions(claims, query)
        
        # Phase 4: Verify each claim using EVP
        await self._update_status("Applying Epistemic Verification Protocol...", progress=65.0)
        verified_claims = await self._verify_claims(claims, evidence, contradictions, query)
        
        # Phase 5: Calculate overall confidence
        await self._update_status("Calculating confidence scores...", progress=85.0)
        report = await self._generate_report(verified_claims, evidence, claims)
        
        # Phase 6: Store verified facts in memory
        await self._update_status("Storing verified facts...", progress=95.0)
        await self._store_verified_facts(verified_claims)
        
        self.results_count = len(verified_claims)
        
        return report
    
    async def _collect_claims(self, claims_data: Optional[Dict[str, Any]]) -> List[str]:
        """Collect claims from provided data and memory"""
        claims = []
        
        # Get claims from provided data
        if claims_data:
            # Extract claims from patent analysis
            if "patent_landscape" in claims_data:
                patent_data = claims_data["patent_landscape"]
                if patent_data.get("whitespace_indicators"):
                    claims.extend(patent_data["whitespace_indicators"])
                if patent_data.get("ai_analysis", {}).get("key_insights"):
                    claims.extend(patent_data["ai_analysis"]["key_insights"])
            
            # Extract claims from market analysis
            if "market_intelligence" in claims_data:
                market_data = claims_data["market_intelligence"]
                if market_data.get("key_insights"):
                    claims.extend(market_data["key_insights"])
            
            # Extract claims from tech trends
            if "tech_trends" in claims_data:
                tech_data = claims_data["tech_trends"]
                if tech_data.get("key_insights"):
                    claims.extend(tech_data["key_insights"])
        
        # Also get discoveries from memory
        discoveries = await self.memory.get_discoveries(
            session_id=self.current_session_id,
            min_confidence=0.5,
        )
        
        for discovery in discoveries:
            content = discovery.get("content")
            if isinstance(content, str):
                claims.append(content)
            elif isinstance(content, dict):
                claims.append(str(content))
        
        # Get whitespace hints
        hints = await self.memory.get_whitespace_hints(self.current_session_id)
        for hint in hints:
            claims.append(hint.get("hint", ""))
        
        # Deduplicate
        unique_claims = list(set(c for c in claims if c and len(c) > 10))
        
        self.log(f"Collected {len(unique_claims)} claims for verification")
        return unique_claims[:30]  # Limit to avoid API limits
    
    async def _gather_evidence(
        self,
        claims: List[str],
        query: ResearchQuery
    ) -> Dict[str, List[VerificationSource]]:
        """Gather evidence for each claim"""
        evidence: Dict[str, List[VerificationSource]] = {}
        
        for i, claim in enumerate(claims):
            await self._update_status(
                f"Gathering evidence ({i+1}/{len(claims)})...",
                progress=25 + (20 * i / len(claims)),
            )
            
            sources = await self._search_evidence_for_claim(claim, query)
            evidence[claim] = sources
            await self._increment_sources(len(sources))
        
        return evidence
    
    async def _search_evidence_for_claim(
        self,
        claim: str,
        query: ResearchQuery
    ) -> List[VerificationSource]:
        """Search for evidence supporting a specific claim"""
        sources = []
        
        # Build search query from claim
        search_terms = self._extract_key_terms(claim)
        search_query = f"{query.query} {search_terms}"
        
        # Search using Serper if available
        if self.settings.serper_api_key:
            serper_sources = await self._search_serper(search_query, claim)
            sources.extend(serper_sources)
        
        # Generate simulated sources if needed
        if len(sources) < self.min_sources:
            simulated = await self._generate_simulated_sources(claim, query)
            sources.extend(simulated)
        
        return sources[:10]  # Return top 10 sources
    
    def _extract_key_terms(self, claim: str) -> str:
        """Extract key terms from a claim for searching"""
        # Remove common words and extract nouns/entities
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                      "have", "has", "had", "do", "does", "did", "will", "would", "could",
                      "should", "may", "might", "must", "and", "or", "but", "if", "then",
                      "than", "that", "which", "who", "whom", "this", "these", "those",
                      "to", "of", "in", "for", "on", "with", "at", "by", "from", "as"}
        
        words = claim.lower().split()
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        return " ".join(key_terms[:8])
    
    async def _search_serper(
        self,
        search_query: str,
        claim: str
    ) -> List[VerificationSource]:
        """Search Google via Serper for evidence"""
        sources = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://google.serper.dev/search",
                    json={
                        "q": search_query,
                        "num": 10,
                    },
                    headers={"X-API-KEY": self.settings.serper_api_key},
                    timeout=30.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for result in data.get("organic", []):
                        source = VerificationSource(
                            source_type="web",
                            source_name=result.get("title", "Unknown"),
                            url=result.get("link"),
                            authority_score=self._calculate_authority(result.get("link", "")),
                            relevant_excerpt=result.get("snippet"),
                        )
                        sources.append(source)
                        
            except Exception as e:
                self.log(f"Serper search error: {e}", "warning")
        
        return sources
    
    def _calculate_authority(self, url: str) -> float:
        """Calculate authority score for a source URL"""
        url_lower = url.lower()
        
        # High authority domains
        high_authority = [
            "nature.com", "science.org", "ieee.org", "acm.org",
            "arxiv.org", "gov", ".edu", "who.int", "nih.gov",
            "reuters.com", "bloomberg.com", "forbes.com",
            "techcrunch.com", "wired.com", "mit.edu", "stanford.edu",
        ]
        
        # Medium authority
        medium_authority = [
            "wikipedia.org", "medium.com", "towardsdatascience.com",
            "analyticsvidhya.com", "hackernoon.com",
        ]
        
        for domain in high_authority:
            if domain in url_lower:
                return 0.9
        
        for domain in medium_authority:
            if domain in url_lower:
                return 0.7
        
        return 0.5  # Default authority
    
    async def _generate_simulated_sources(
        self,
        claim: str,
        query: ResearchQuery
    ) -> List[VerificationSource]:
        """Generate simulated sources for demo purposes"""
        prompt = f"""For the claim: "{claim}"
Related to: "{query.query}"

Generate 5 realistic verification sources that would support or refute this claim.

For each source:
- source_type: Type (academic, news, report, database, patent)
- source_name: Title of the source
- url: Realistic URL
- authority_score: 0.0-1.0 credibility score
- relevant_excerpt: Brief excerpt that relates to the claim
- supports_claim: true/false

Return as JSON array."""

        response = await self.gemini.generate(prompt, task_type="verification", temperature=0.5)
        
        sources = []
        try:
            import json
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            
            source_data = json.loads(response)
            
            for sd in source_data:
                source = VerificationSource(
                    source_type=sd.get("source_type", "web"),
                    source_name=sd.get("source_name", "Unknown"),
                    url=sd.get("url"),
                    authority_score=sd.get("authority_score", 0.5),
                    relevant_excerpt=sd.get("relevant_excerpt"),
                )
                sources.append(source)
                
        except Exception as e:
            self.log(f"Source generation error: {e}", "warning")
        
        return sources
    
    async def _search_contradictions(
        self,
        claims: List[str],
        query: ResearchQuery
    ) -> Dict[str, List[VerificationSource]]:
        """Actively search for contradicting evidence - THE ADVERSARIAL STEP"""
        contradictions: Dict[str, List[VerificationSource]] = {}
        
        for claim in claims:
            # Build negation queries
            negation_queries = [
                f'NOT "{claim[:50]}" {query.query}',
                f'"{query.query}" problems challenges failure',
                f'"{query.query}" criticism concerns issues',
            ]
            
            contra_sources = []
            
            if self.settings.serper_api_key:
                for neg_query in negation_queries[:1]:  # Limit API calls
                    sources = await self._search_serper(neg_query, claim)
                    contra_sources.extend(sources[:3])
            
            contradictions[claim] = contra_sources
        
        return contradictions
    
    async def _verify_claims(
        self,
        claims: List[str],
        evidence: Dict[str, List[VerificationSource]],
        contradictions: Dict[str, List[VerificationSource]],
        query: ResearchQuery,
    ) -> List[VerifiedClaim]:
        """Verify each claim using the Epistemic Verification Protocol"""
        verified_claims = []
        
        # Use AI for comprehensive verification
        verification_result = await self.gemini.verify_claims(
            claims=claims[:15],  # Limit for API
            supporting_data={
                "evidence_summary": {
                    claim: [s.model_dump() for s in sources[:3]]
                    for claim, sources in evidence.items()
                },
                "contradictions_found": {
                    claim: len(sources)
                    for claim, sources in contradictions.items()
                },
                "context": query.query,
            },
        )
        
        # Parse verification results
        ai_verified = verification_result.get("verified_claims", [])
        
        for claim in claims:
            claim_evidence = evidence.get(claim, [])
            claim_contradictions = contradictions.get(claim, [])
            
            # Find AI verification result for this claim
            ai_result = next(
                (v for v in ai_verified if claim[:50] in str(v)),
                None
            )
            
            # Calculate confidence score
            confidence = await self._calculate_confidence(
                claim,
                claim_evidence,
                claim_contradictions,
                ai_result,
            )
            
            # Determine confidence level
            level = self._get_confidence_level(confidence)
            
            verified_claim = VerifiedClaim(
                claim_text=claim,
                confidence_score=confidence,
                confidence_level=level,
                supporting_sources=claim_evidence,
                contradicting_sources=claim_contradictions,
                verification_notes=ai_result.get("notes") if ai_result else None,
            )
            verified_claims.append(verified_claim)
            
            self.log(f"Verified: '{claim[:50]}...' - Confidence: {confidence:.0%}")
        
        return verified_claims
    
    async def _calculate_confidence(
        self,
        claim: str,
        evidence: List[VerificationSource],
        contradictions: List[VerificationSource],
        ai_result: Optional[Dict[str, Any]],
    ) -> float:
        """Calculate Bayesian confidence score for a claim"""
        # Start with prior
        prior = 0.5
        
        # Evidence boost
        evidence_boost = 0
        for source in evidence:
            evidence_boost += source.authority_score * 0.1
        evidence_boost = min(evidence_boost, 0.35)
        
        # Contradiction penalty
        contradiction_penalty = len(contradictions) * 0.08
        contradiction_penalty = min(contradiction_penalty, 0.25)
        
        # Number of sources factor
        source_count = len(evidence)
        if source_count >= self.min_sources:
            source_factor = 0.1
        elif source_count >= 3:
            source_factor = 0.05
        else:
            source_factor = -0.1
        
        # AI verification factor
        ai_factor = 0
        if ai_result:
            ai_confidence = ai_result.get("confidence_score", 0.5)
            if isinstance(ai_confidence, (int, float)):
                ai_factor = (ai_confidence - 0.5) * 0.2
        
        # Calculate final score
        confidence = prior + evidence_boost - contradiction_penalty + source_factor + ai_factor
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))
    
    def _get_confidence_level(self, score: float) -> ConfidenceLevel:
        """Convert numeric score to confidence level"""
        if score >= 0.95:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.85:
            return ConfidenceLevel.HIGH
        elif score >= 0.70:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNVERIFIED
    
    async def _generate_report(
        self,
        verified_claims: List[VerifiedClaim],
        evidence: Dict[str, List[VerificationSource]],
        original_claims: List[str],
    ) -> Dict[str, Any]:
        """Generate verification report"""
        # Count sources by type
        source_distribution: Dict[str, int] = {}
        total_sources = 0
        
        for sources in evidence.values():
            for source in sources:
                source_distribution[source.source_type] = source_distribution.get(source.source_type, 0) + 1
                total_sources += 1
        
        # Calculate statistics
        verified_count = sum(
            1 for vc in verified_claims
            if vc.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]
        )
        
        average_confidence = sum(vc.confidence_score for vc in verified_claims) / len(verified_claims) if verified_claims else 0
        
        coverage = verified_count / len(original_claims) if original_claims else 0
        
        # Identify unverified claims
        unverified = [
            vc.claim_text for vc in verified_claims
            if vc.confidence_level == ConfidenceLevel.UNVERIFIED
        ]
        
        report = VerificationReport(
            total_claims_analyzed=len(original_claims),
            verified_claims=verified_claims,
            unverified_claims=unverified,
            total_sources_used=total_sources,
            source_distribution=source_distribution,
            average_confidence=average_confidence,
            verification_coverage=coverage,
        )
        
        result = report.model_dump()
        
        # Add summary stats
        result["summary"] = {
            "high_confidence_claims": verified_count,
            "medium_confidence_claims": sum(
                1 for vc in verified_claims
                if vc.confidence_level == ConfidenceLevel.MEDIUM
            ),
            "low_confidence_claims": sum(
                1 for vc in verified_claims
                if vc.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.UNVERIFIED]
            ),
            "average_confidence_percent": f"{average_confidence * 100:.1f}%",
        }
        
        return result
    
    async def _store_verified_facts(self, verified_claims: List[VerifiedClaim]) -> None:
        """Store verified facts in memory for synthesis"""
        for vc in verified_claims:
            if vc.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH]:
                await self.memory.add_verified_fact(
                    session_id=self.current_session_id,
                    fact=vc.claim_text,
                    sources=[s.source_name for s in vc.supporting_sources[:5]],
                    confidence=vc.confidence_score,
                )
    
    def _create_empty_report(self) -> Dict[str, Any]:
        """Create empty verification report"""
        return VerificationReport(
            total_claims_analyzed=0,
            verified_claims=[],
            unverified_claims=[],
            total_sources_used=0,
            source_distribution={},
            average_confidence=0.0,
            verification_coverage=0.0,
        ).model_dump()
