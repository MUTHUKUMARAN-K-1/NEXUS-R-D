"""
NEXUS-R&D TTS Generator
Text-to-Speech Audio Brief generation using ElevenLabs AI Voices
"""

import os
from typing import Dict, Any, Optional
from loguru import logger

try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("ElevenLabs not installed. Install with: pip install elevenlabs")


class TTSGenerator:
    """
    Text-to-Speech Generator for Audio Briefs
    
    Uses ElevenLabs AI for high-quality voice synthesis
    of research report summaries.
    """
    
    def __init__(self, output_dir: str = "static/audio"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize ElevenLabs client
        self.client = None
        if ELEVENLABS_AVAILABLE:
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if api_key:
                self.client = ElevenLabs(api_key=api_key)
            else:
                logger.warning("ELEVENLABS_API_KEY not set in environment")
        
        # Default voice settings - use env var or fallback to Rachel
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
        self.model_id = "eleven_monolingual_v1"
        
    def generate_audio_brief(
        self,
        session_id: str,
        report: Dict[str, Any],
        voice_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate an audio brief from a research report
        
        Args:
            session_id: The research session ID
            report: The complete research report
            voice_id: Optional custom voice ID
            
        Returns:
            Path to the generated audio file, or None if failed
        """
        if not ELEVENLABS_AVAILABLE or not self.client:
            logger.error("ElevenLabs not available or API key not set")
            return None
            
        try:
            # Generate the script for TTS
            script = self._generate_script(report)
            
            if not script:
                logger.error("Failed to generate TTS script")
                return None
            
            # Output file path
            output_path = os.path.join(
                self.output_dir, 
                f"brief_{session_id}.mp3"
            )
            
            logger.info(f"Generating ElevenLabs audio brief for session {session_id}")
            
            # Generate audio using ElevenLabs
            audio = self.client.text_to_speech.convert(
                text=script,
                voice_id=voice_id or self.voice_id,
                model_id=self.model_id,
                output_format="mp3_44100_128"
            )
            
            # Save audio to file
            with open(output_path, "wb") as f:
                for chunk in audio:
                    f.write(chunk)
            
            logger.info(f"Audio brief saved to {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"ElevenLabs TTS generation error: {e}")
            return None
    
    def _generate_script(self, report: Dict[str, Any]) -> str:
        """Generate a spoken script from the research report"""
        
        parts = []
        
        # Introduction
        query = report.get("query", "the research topic")
        parts.append(f"NEXUS R&D Innovation Brief for: {query}.")
        parts.append("Here is your executive summary.")
        
        # Executive Summary
        executive_summary = report.get("executive_summary", "")
        if executive_summary:
            # Clean up for speech
            summary = executive_summary.replace("**", "").replace("*", "")
            summary = summary.replace("\n", " ").strip()
            if len(summary) > 600:
                summary = summary[:600] + "..."
            parts.append(summary)
        
        # Key Statistics
        parts.append("Key findings from our analysis.")
        
        patent_count = report.get("patent_analysis", {}).get("total_patents_found", 0)
        if patent_count:
            parts.append(f"We analyzed {patent_count} patents in this domain.")
        
        papers_count = report.get("tech_analysis", {}).get("total_papers_analyzed", 0)
        if papers_count:
            parts.append(f"We reviewed {papers_count} research papers.")
        
        sources = report.get("sources_analyzed", 0)
        if sources:
            parts.append(f"Total sources analyzed: {sources}.")
        
        # Innovation Whitespace
        whitespace = report.get("innovation_whitespace", [])
        if whitespace:
            parts.append(f"We identified {len(whitespace)} innovation opportunities.")
            
            # Top opportunity
            if len(whitespace) > 0:
                top = whitespace[0]
                area = top.get("opportunity_area", "")
                if area:
                    parts.append(f"The top opportunity is: {area}.")
                    
                description = top.get("description", "")
                if description:
                    desc_clean = description.replace("**", "").replace("*", "")[:250]
                    parts.append(desc_clean)
        
        # Technology Trends
        trends = report.get("tech_analysis", {}).get("trends", [])
        if trends:
            parts.append(f"We identified {len(trends)} technology trends.")
            
            # Mention top trends
            for trend in trends[:2]:
                name = trend.get("technology_name", "")
                if name:
                    maturity = trend.get("maturity_level", "emerging")
                    parts.append(f"{name} is currently {maturity}.")
        
        # Competitive Threats
        threats = report.get("competitive_threats", [])
        if threats:
            parts.append(f"We detected {len(threats)} competitive threats to monitor.")
        
        # Conclusion
        confidence = report.get("confidence_score", 0.8)
        confidence_pct = int(confidence * 100)
        parts.append(f"Overall analysis confidence: {confidence_pct} percent.")
        
        parts.append("This concludes your NEXUS R&D innovation brief. For the full report, please refer to the dashboard or export the PDF.")
        
        # Join with natural pauses
        script = " ".join(parts)
        
        return script
    
    def get_audio_duration_estimate(self, report: Dict[str, Any]) -> int:
        """Estimate audio duration in seconds"""
        script = self._generate_script(report)
        # Average speaking rate: ~150 words per minute
        word_count = len(script.split())
        duration_seconds = int((word_count / 150) * 60)
        return max(30, min(180, duration_seconds))  # 30s to 3min
    
    def list_available_voices(self) -> list:
        """List available ElevenLabs voices"""
        if not self.client:
            return []
        
        try:
            voices = self.client.voices.get_all()
            return [{"id": v.voice_id, "name": v.name} for v in voices.voices]
        except Exception as e:
            logger.error(f"Failed to list voices: {e}")
            return []


# Singleton instance
_tts_generator: Optional[TTSGenerator] = None


def get_tts_generator() -> TTSGenerator:
    """Get or create TTS generator instance"""
    global _tts_generator
    if _tts_generator is None:
        _tts_generator = TTSGenerator()
    return _tts_generator
