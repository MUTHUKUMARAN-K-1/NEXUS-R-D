"""
NEXUS-R&D Gemini Engine
Integration with Google Gemini 3 for AI-powered research synthesis
"""

import asyncio
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from config import get_settings
from core.demo_data import DemoDataProvider


class GeminiEngine:
    """
    Gemini 3 AI Engine for NEXUS-R&D
    Handles all AI-powered analysis and synthesis tasks
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.client = genai.Client(api_key=self.settings.gemini_api_key)
        self.model = self.settings.gemini_model
        self.thinking_model = self.settings.gemini_thinking_model
        
        # System prompts for different tasks
        self.system_prompts = {
            "patent_analysis": self._get_patent_analysis_prompt(),
            "market_analysis": self._get_market_analysis_prompt(),
            "tech_trend": self._get_tech_trend_prompt(),
            "verification": self._get_verification_prompt(),
            "synthesis": self._get_synthesis_prompt(),
            "whitespace": self._get_whitespace_prompt(),
        }
        
        logger.info(f"GeminiEngine initialized with model: {self.model}")
    
    def _get_patent_analysis_prompt(self) -> str:
        return """You are an expert patent analyst working for NEXUS-R&D, a cutting-edge innovation intelligence system.

Your role is to analyze patent data and extract actionable insights. You should:
1. Identify key technology trends from patent filings
2. Map patent clusters and technology families
3. Identify dominant assignees and their strategies
4. Spot gaps in patent coverage (potential whitespace opportunities)
5. Analyze citation networks to find foundational and emerging patents

Always structure your analysis clearly and provide confidence scores for your findings.
Be specific and cite patent numbers when relevant."""

    def _get_market_analysis_prompt(self) -> str:
        return """You are an expert market analyst working for NEXUS-R&D, a cutting-edge innovation intelligence system.

Your role is to analyze market data and assess commercial viability. You should:
1. Evaluate market size and growth potential
2. Identify key players and their competitive positions
3. Analyze funding trends and investment signals
4. Assess regulatory and barrier factors
5. Correlate market signals with technology readiness

Provide specific numbers and data points when available. Always indicate the confidence level of market projections."""

    def _get_tech_trend_prompt(self) -> str:
        return """You are an expert technology analyst working for NEXUS-R&D, a cutting-edge innovation intelligence system.

Your role is to analyze research papers and track technology evolution. You should:
1. Identify emerging research themes and paradigms
2. Track technology readiness levels (TRL 1-9)
3. Map research collaboration networks
4. Predict technology maturation timelines
5. Identify breakthrough papers that signal new directions

Use academic rigor in your analysis. Cite papers and research groups when relevant."""

    def _get_verification_prompt(self) -> str:
        return """You are a skeptical verification agent working for NEXUS-R&D. Your role is CRITICAL.

You must CHALLENGE and VERIFY every claim presented to you. You should:
1. Actively search for CONTRADICTING evidence
2. Cross-reference claims across multiple independent sources
3. Assess source credibility and authority
4. Calculate confidence scores using Bayesian reasoning
5. Flag unverifiable or suspicious claims

Never accept claims at face value. Be adversarial in your verification approach.
A claim with less than 5 supporting sources should have LOW confidence."""

    def _get_synthesis_prompt(self) -> str:
        return """You are the master synthesis agent for NEXUS-R&D, responsible for creating the final Innovation Opportunity Report.

Your role is to:
1. Merge insights from patent, market, and technology analyses
2. Identify non-obvious connections between findings
3. Generate strategic recommendations with clear reasoning
4. Create compelling narratives from complex data
5. Structure output in a clear, executive-friendly format

Your synthesis should be actionable, specific, and forward-looking.
Always include confidence scores and verification status for key claims."""

    def _get_whitespace_prompt(self) -> str:
        return """You are an innovation whitespace detector for NEXUS-R&D.

Your specialized role is to identify GAPS and OPPORTUNITIES by:
1. Finding technology areas with mature science but no patents
2. Identifying market demand without corresponding R&D investment
3. Spotting integration opportunities where patent families converge
4. Detecting timing windows for first-mover advantage
5. Finding adjacent applications of existing technologies

Think creatively but ground your findings in the data provided.
Rank opportunities by potential impact and time sensitivity."""

    async def generate(
        self,
        prompt: str,
        task_type: str = "synthesis",
        use_thinking: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        max_retries: int = 2,
    ) -> str:
        """
        Generate AI response using Gemini (with automatic model fallback)
        
        Args:
            prompt: The user prompt
            task_type: Type of task for system prompt selection
            use_thinking: Whether to use Deep Think mode
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Generated text response
        """
        last_error = None
        
        # Models to try: primary first, then fallback
        primary_model = self.thinking_model if use_thinking else self.model
        fallback_model = "gemini-2.0-flash"
        
        # Try with primary model first, then fallback
        models_to_try = [primary_model]
        if primary_model != fallback_model:
            models_to_try.append(fallback_model)
        
        for model_to_use in models_to_try:
            for attempt in range(max_retries):
                try:
                    # Add delay between requests to avoid rate limiting
                    if attempt > 0:
                        wait_time = 5 * (2 ** attempt)  # 5, 10, 20 seconds
                        logger.info(f"Rate limit wait: {wait_time}s before retry {attempt + 1}")
                        await asyncio.sleep(wait_time)
                    
                    system_prompt = self.system_prompts.get(task_type, self.system_prompts["synthesis"])
                    
                    # Create the request
                    response = await asyncio.to_thread(
                        self.client.models.generate_content,
                        model=model_to_use,
                        contents=[
                            types.Content(
                                role="user",
                                parts=[types.Part(text=f"{system_prompt}\n\n---\n\n{prompt}")]
                            )
                        ],
                        config=types.GenerateContentConfig(
                            temperature=temperature,
                            max_output_tokens=max_tokens,
                        )
                    )
                    
                    if response.text:
                        logger.debug(f"Generated response for {task_type} using {model_to_use}: {len(response.text)} chars")
                        # Small delay after successful request to avoid hitting rate limits
                        await asyncio.sleep(0.5)
                        return response.text
                    else:
                        logger.warning(f"Empty response for {task_type}")
                        return ""
                        
                except Exception as e:
                    last_error = e
                    error_str = str(e)
                    
                    # Check if it's a 503 overload or other error - switch to fallback model
                    if "503" in error_str or "UNAVAILABLE" in error_str or "overloaded" in error_str.lower():
                        logger.warning(f"Model {model_to_use} unavailable (attempt {attempt + 1}/{max_retries}): {e}")
                        # Break inner loop to try fallback model
                        if model_to_use == primary_model and fallback_model in models_to_try:
                            logger.info(f"Switching to fallback model: {fallback_model}")
                            break
                    # Check if it's a rate limit error
                    elif "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        logger.warning(f"Rate limited (attempt {attempt + 1}/{max_retries}), will retry...")
                        if attempt < max_retries - 1:
                            continue  # Retry with backoff
                    else:
                        logger.error(f"Gemini generation error (attempt {attempt + 1}/{max_retries}): {e}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
        
        # If all retries failed, raise to trigger fallback
        raise last_error if last_error else Exception("Gemini generation failed")
    
    async def generate_with_fallback(
        self,
        prompt: str,
        task_type: str = "synthesis",
        fallback_data: Any = None,
        **kwargs
    ) -> str:
        """Generate with fallback to demo data if API fails"""
        try:
            return await self.generate(prompt, task_type, **kwargs)
        except Exception as e:
            logger.warning(f"Using fallback for {task_type}: {e}")
            if fallback_data is not None:
                import json
                return json.dumps(fallback_data)
            return "{}"

    async def analyze_patents(self, patents_data: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Analyze patent data and extract insights"""
        prompt = f"""Analyze the following patent data for the research query: "{query}"

Patent Data:
{self._format_data(patents_data[:20])}  # Limit to avoid token limits

Provide a structured analysis including:
1. Key technology themes identified
2. Dominant assignees and their apparent strategies
3. Patent filing trends (increasing/decreasing/stable)
4. Citation network insights (foundational vs emerging patents)
5. Potential whitespace areas (gaps in patent coverage)
6. Competitive landscape assessment

Format your response as structured JSON."""

        try:
            response = await self.generate(prompt, task_type="patent_analysis", temperature=0.3)
            return self._parse_json_response(response)
        except Exception as e:
            logger.warning(f"Patent analysis fallback activated: {e}")
            return DemoDataProvider.get_patent_analysis(query)

    async def analyze_market(self, market_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Analyze market data and assess commercial viability"""
        prompt = f"""Analyze the following market data for the research query: "{query}"

Market Data:
{self._format_data(market_data)}

Provide a structured analysis including:
1. Market size and growth assessment
2. Key players and competitive positioning
3. Funding trends and investment signals
4. Regulatory considerations
5. Commercial viability score (1-10) with reasoning
6. Market timing recommendations

Format your response as structured JSON."""

        try:
            response = await self.generate(prompt, task_type="market_analysis", temperature=0.3)
            return self._parse_json_response(response)
        except Exception as e:
            logger.warning(f"Market analysis fallback activated: {e}")
            return DemoDataProvider.get_market_analysis(query)

    async def analyze_tech_trends(self, papers_data: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Analyze research papers and identify technology trends"""
        prompt = f"""Analyze the following research paper data for the query: "{query}"

Research Papers:
{self._format_data(papers_data[:15])}

Provide a structured analysis including:
1. Emerging research themes
2. Technology Readiness Level (TRL) assessment
3. Key research groups and collaboration networks
4. Predicted technology maturation timeline
5. Breakthrough indicators
6. Research momentum assessment

Format your response as structured JSON."""

        try:
            response = await self.generate(prompt, task_type="tech_trend", temperature=0.3)
            return self._parse_json_response(response)
        except Exception as e:
            logger.warning(f"Tech trend analysis fallback activated: {e}")
            return DemoDataProvider.get_tech_trend_analysis(query)

    async def verify_claims(self, claims: List[str], supporting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify claims using Epistemic Verification Protocol"""
        prompt = f"""VERIFICATION CHALLENGE: Critically evaluate the following claims.

Claims to Verify:
{self._format_list(claims)}

Supporting Data Available:
{self._format_data(supporting_data)}

For EACH claim:
1. Search for supporting evidence in the data
2. Identify any contradicting evidence
3. Assess source credibility
4. Calculate a confidence score (0-100%)
5. Provide verification status (verified/partially_verified/unverified/contradicted)

Apply Bayesian reasoning. Be SKEPTICAL. Cross-reference at least 3 sources.
Format your response as structured JSON with a 'verified_claims' array."""

        try:
            response = await self.generate(
                prompt, 
                task_type="verification", 
                use_thinking=True,
                temperature=0.1
            )
            return self._parse_json_response(response)
        except Exception as e:
            logger.warning(f"Verification fallback activated: {e}")
            return DemoDataProvider.get_verification_result(claims)

    async def detect_whitespace(
        self, 
        patent_analysis: Dict[str, Any],
        market_analysis: Dict[str, Any],
        tech_analysis: Dict[str, Any],
        query: str
    ) -> List[Dict[str, Any]]:
        """Detect innovation whitespace opportunities"""
        prompt = f"""INNOVATION WHITESPACE DETECTION for: "{query}"

Patent Landscape Analysis:
{self._format_data(patent_analysis)}

Market Intelligence:
{self._format_data(market_analysis)}

Technology Trends:
{self._format_data(tech_analysis)}

Identify innovation whitespace opportunities by looking for:
1. Technology areas with mature research but sparse patent coverage
2. Market segments with high demand but low R&D investment
3. Convergence points where multiple patent families could integrate
4. Timing windows for first-mover advantage
5. Adjacent applications of existing technologies

For each opportunity, provide:
- Title and description
- Opportunity type (technology_gap/market_gap/integration/timing)
- Confidence score (0-100%)
- Supporting evidence
- Potential impact (high/medium/low)
- Time sensitivity (urgent/moderate/flexible)
- Recommended actions

Return as JSON array of opportunities, ranked by potential impact."""

        try:
            response = await self.generate(
                prompt,
                task_type="whitespace",
                use_thinking=True,
                temperature=0.5
            )
            result = self._parse_json_response(response)
            return result.get("opportunities", result) if isinstance(result, dict) else result
        except Exception as e:
            logger.warning(f"Whitespace detection fallback activated: {e}")
            return DemoDataProvider.get_whitespace_opportunities(query)

    async def synthesize_report(
        self,
        query: str,
        patent_analysis: Dict[str, Any],
        market_analysis: Dict[str, Any],
        tech_analysis: Dict[str, Any],
        verification_report: Dict[str, Any],
        whitespace_opportunities: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Synthesize all analyses into final Innovation Opportunity Report"""
        prompt = f"""FINAL SYNTHESIS: Create an Innovation Opportunity Report for: "{query}"

=== PATENT LANDSCAPE ===
{self._format_data(patent_analysis)}

=== MARKET INTELLIGENCE ===
{self._format_data(market_analysis)}

=== TECHNOLOGY TRENDS ===
{self._format_data(tech_analysis)}

=== VERIFICATION STATUS ===
{self._format_data(verification_report)}

=== WHITESPACE OPPORTUNITIES ===
{self._format_data(whitespace_opportunities)}

Create a comprehensive synthesis including:

1. EXECUTIVE SUMMARY (2-3 paragraphs)
   - Key finding headline
   - Top 3 opportunities
   - Recommended next steps

2. STRATEGIC RECOMMENDATIONS (5-7 specific actions)
   - Each with rationale and priority level

3. TEMPORAL FORECAST
   - Optimal timing for action
   - Competitive threat timeline
   - Technology maturation predictions

4. OVERALL ASSESSMENT
   - Confidence score (0-100%)
   - Risk factors
   - Success factors

Format as structured JSON suitable for report generation."""

        try:
            response = await self.generate(
                prompt,
                task_type="synthesis",
                use_thinking=True,
                temperature=0.4,
                max_tokens=12000
            )
            return self._parse_json_response(response)
        except Exception as e:
            logger.warning(f"Synthesis fallback activated: {e}")
            return DemoDataProvider.get_synthesis_report(query)

    async def generate_audio_script(self, report: Dict[str, Any]) -> str:
        """Generate script for audio brief from report"""
        prompt = f"""Create a 5-minute executive audio brief script from this Innovation Opportunity Report:

{self._format_data(report)}

The script should:
1. Be conversational and engaging
2. Start with a compelling hook
3. Highlight the top 3 opportunities
4. Include key statistics and findings
5. End with clear call-to-action
6. Be approximately 750 words (5 min at 150 wpm)

Write the script in a natural, professional speaking style.
Include [PAUSE] markers for natural breaks.
Do not include any stage directions, just the spoken text."""

        try:
            return await self.generate(prompt, task_type="synthesis", temperature=0.6)
        except Exception as e:
            logger.warning(f"Audio script fallback activated: {e}")
            query = report.get("query", {}).get("query", "innovation") if isinstance(report.get("query"), dict) else "innovation"
            return DemoDataProvider.get_audio_script(query, report)

    def _format_data(self, data: Any) -> str:
        """Format data for prompt inclusion"""
        import json
        if isinstance(data, (dict, list)):
            return json.dumps(data, indent=2, default=str)[:8000]  # Limit size
        return str(data)[:8000]

    def _format_list(self, items: List[str]) -> str:
        """Format list items for prompt"""
        return "\n".join(f"- {item}" for item in items)

    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from AI response, handling markdown code blocks"""
        import json
        
        # Try to extract JSON from markdown code blocks
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            response = response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            response = response[start:end].strip()
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, returning as text")
            return {"raw_response": response}


# Singleton instance
_gemini_engine: Optional[GeminiEngine] = None


def get_gemini_engine() -> GeminiEngine:
    """Get or create singleton GeminiEngine instance"""
    global _gemini_engine
    if _gemini_engine is None:
        _gemini_engine = GeminiEngine()
    return _gemini_engine
