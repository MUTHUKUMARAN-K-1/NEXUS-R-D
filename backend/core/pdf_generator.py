"""
NEXUS-R&D PDF Report Generator
Professional Innovation Opportunity Report export
"""

import io
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from loguru import logger


class PDFReportGenerator:
    """Generate professional PDF reports from research data"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Define custom styles for the report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            textColor=colors.HexColor('#6366f1'),
            alignment=TA_CENTER,
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#64748b'),
            alignment=TA_CENTER,
            spaceAfter=20,
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=20,
            spaceAfter=12,
        ))
        
        # Subsection header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#475569'),
            spaceBefore=15,
            spaceAfter=8,
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='ReportBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#334155'),
            spaceBefore=6,
            spaceAfter=6,
            leading=16,
        ))
        
        # Highlight text
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6366f1'),
            spaceBefore=4,
            spaceAfter=4,
        ))
        
        # Small text
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#94a3b8'),
        ))
    
    def generate_report(self, report_data: Dict[str, Any]) -> bytes:
        """Generate PDF report from research data"""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )
        
        story = []
        
        # Cover page
        story.extend(self._build_cover_page(report_data))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._build_executive_summary(report_data))
        story.append(Spacer(1, 20))
        
        # Innovation Whitespace
        story.extend(self._build_whitespace_section(report_data))
        story.append(PageBreak())
        
        # Competitive Threats
        story.extend(self._build_threats_section(report_data))
        story.append(Spacer(1, 20))
        
        # Patent Landscape
        story.extend(self._build_patent_section(report_data))
        story.append(PageBreak())
        
        # Market Intelligence
        story.extend(self._build_market_section(report_data))
        story.append(Spacer(1, 20))
        
        # Tech Trends
        story.extend(self._build_trends_section(report_data))
        
        # Build PDF
        doc.build(story)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def _build_cover_page(self, report_data: Dict[str, Any]) -> list:
        """Build cover page"""
        elements = []
        
        # Spacer for top margin
        elements.append(Spacer(1, 2*inch))
        
        # Title
        elements.append(Paragraph(
            "NEXUS-R&D",
            self.styles['ReportTitle']
        ))
        
        elements.append(Paragraph(
            "Innovation Opportunity Report",
            self.styles['ReportSubtitle']
        ))
        
        elements.append(Spacer(1, 30))
        
        # Query
        query = report_data.get("query", {})
        query_text = query.get("query", "Research Analysis") if isinstance(query, dict) else str(query)
        elements.append(Paragraph(
            f"<b>Research Topic:</b> {query_text}",
            self.styles['ReportBody']
        ))
        
        elements.append(Spacer(1, 20))
        
        # Report metadata
        report_id = report_data.get("report_id", "N/A")
        generated_at = report_data.get("generated_at", datetime.now().isoformat())
        
        elements.append(Paragraph(
            f"Report ID: {report_id}",
            self.styles['SmallText']
        ))
        elements.append(Paragraph(
            f"Generated: {generated_at[:19].replace('T', ' ')}",
            self.styles['SmallText']
        ))
        
        # Key stats
        elements.append(Spacer(1, 40))
        
        metadata = report_data.get("metadata", {})
        stats_data = [
            ["Patents Analyzed", "Papers Reviewed", "Sources Used", "Processing Time"],
            [
                str(metadata.get("total_patents_analyzed", 0)),
                str(metadata.get("total_papers_analyzed", 0)),
                str(metadata.get("total_sources_analyzed", 0)),
                f"{metadata.get('processing_time_seconds', 0):.0f}s",
            ]
        ]
        
        stats_table = Table(stats_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#475569')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#6366f1')),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 1), (-1, 1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
        ]))
        elements.append(stats_table)
        
        return elements
    
    def _build_executive_summary(self, report_data: Dict[str, Any]) -> list:
        """Build executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#6366f1')))
        elements.append(Spacer(1, 10))
        
        summary = report_data.get("executive_summary", {})
        
        # Headline
        headline = summary.get("headline", "Research Analysis Complete")
        elements.append(Paragraph(f"<b>{headline}</b>", self.styles['SubsectionHeader']))
        
        # Key finding
        key_finding = summary.get("key_finding", "")
        if key_finding:
            elements.append(Paragraph(key_finding, self.styles['ReportBody']))
        
        # Confidence score
        confidence = summary.get("overall_confidence", 0)
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(
            f"<b>Overall Confidence Score:</b> {confidence*100:.0f}%",
            self.styles['Highlight']
        ))
        
        # Top opportunities
        top_opps = summary.get("top_opportunities", [])
        if top_opps:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Top Opportunities:</b>", self.styles['ReportBody']))
            for i, opp in enumerate(top_opps[:5], 1):
                elements.append(Paragraph(f"  {i}. {opp}", self.styles['ReportBody']))
        
        return elements
    
    def _build_whitespace_section(self, report_data: Dict[str, Any]) -> list:
        """Build whitespace opportunities section"""
        elements = []
        
        elements.append(Paragraph("Innovation Whitespace Opportunities", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#6366f1')))
        elements.append(Spacer(1, 10))
        
        opportunities = report_data.get("whitespace_opportunities", [])
        
        for i, opp in enumerate(opportunities[:6], 1):
            title = opp.get("title", "Opportunity")
            desc = opp.get("description", "")
            impact = opp.get("potential_impact", "medium")
            confidence = opp.get("confidence_score", 0)
            investment = opp.get("investment_score", 0)
            
            elements.append(Paragraph(
                f"<b>{i}. {title}</b> ({impact.upper()} IMPACT)",
                self.styles['SubsectionHeader']
            ))
            elements.append(Paragraph(desc, self.styles['ReportBody']))
            elements.append(Paragraph(
                f"Confidence: {confidence*100:.0f}% | Investment Score: {investment:.0f}/100",
                self.styles['SmallText']
            ))
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _build_threats_section(self, report_data: Dict[str, Any]) -> list:
        """Build competitive threats section"""
        elements = []
        
        elements.append(Paragraph("Competitive Threat Radar", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#ef4444')))
        elements.append(Spacer(1, 10))
        
        threats = report_data.get("competitive_threats", [])
        
        if not threats:
            elements.append(Paragraph("No significant competitive threats identified.", self.styles['ReportBody']))
            return elements
        
        # Threats table
        table_data = [["Company", "Threat Level", "Patents", "Market Overlap"]]
        
        threat_colors = {
            "high": colors.HexColor('#ef4444'),
            "medium": colors.HexColor('#f59e0b'),
            "low": colors.HexColor('#22c55e'),
        }
        
        for threat in threats[:8]:
            table_data.append([
                threat.get("company_name", "Unknown"),
                threat.get("threat_level", "low").upper(),
                str(threat.get("patent_count", 0)),
                f"{threat.get('market_overlap', 0)*100:.0f}%",
            ])
        
        threats_table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 1*inch, 1.3*inch])
        threats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        elements.append(threats_table)
        
        return elements
    
    def _build_patent_section(self, report_data: Dict[str, Any]) -> list:
        """Build patent landscape section"""
        elements = []
        
        elements.append(Paragraph("Patent Landscape", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#06b6d4')))
        elements.append(Spacer(1, 10))
        
        patent_data = report_data.get("patent_landscape", {})
        total = patent_data.get("total_patents", 0)
        
        elements.append(Paragraph(
            f"<b>Total Patents Analyzed:</b> {total}",
            self.styles['ReportBody']
        ))
        
        # Top assignees
        assignees = patent_data.get("top_assignees", {})
        if assignees:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Top Patent Holders:</b>", self.styles['SubsectionHeader']))
            
            table_data = [["Company", "Patent Count"]]
            for company, count in list(assignees.items())[:10]:
                table_data.append([company, str(count)])
            
            assignee_table = Table(table_data, colWidths=[4*inch, 1.5*inch])
            assignee_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0891b2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
            ]))
            elements.append(assignee_table)
        
        return elements
    
    def _build_market_section(self, report_data: Dict[str, Any]) -> list:
        """Build market intelligence section"""
        elements = []
        
        elements.append(Paragraph("Market Intelligence", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#8b5cf6')))
        elements.append(Spacer(1, 10))
        
        market_data = report_data.get("market_intelligence", {})
        
        funding = market_data.get("funding_total_usd", 0)
        elements.append(Paragraph(
            f"<b>Total Funding Tracked:</b> ${funding/1_000_000:.1f}M",
            self.styles['ReportBody']
        ))
        
        # Startups
        startups = market_data.get("relevant_startups", [])
        if startups:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Key Startups:</b>", self.styles['SubsectionHeader']))
            
            for startup in startups[:5]:
                if isinstance(startup, dict):
                    name = startup.get("name", "Unknown")
                    desc = startup.get("description", "")
                    funding_amt = startup.get("funding_total", 0) or 0
                    elements.append(Paragraph(
                        f"• <b>{name}</b> (${funding_amt/1_000_000:.1f}M): {desc}",
                        self.styles['ReportBody']
                    ))
        
        return elements
    
    def _build_trends_section(self, report_data: Dict[str, Any]) -> list:
        """Build tech trends section"""
        elements = []
        
        elements.append(Paragraph("Technology Trends", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#ec4899')))
        elements.append(Spacer(1, 10))
        
        tech_data = report_data.get("tech_trends", {})
        total_papers = tech_data.get("total_papers_analyzed", 0)
        
        elements.append(Paragraph(
            f"<b>Research Papers Analyzed:</b> {total_papers}",
            self.styles['ReportBody']
        ))
        
        trends = tech_data.get("trends", [])
        if trends:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Emerging Technologies:</b>", self.styles['SubsectionHeader']))
            
            table_data = [["Technology", "Maturity", "TRL", "Momentum"]]
            for trend in trends[:8]:
                if isinstance(trend, dict):
                    table_data.append([
                        trend.get("technology_name", "Unknown"),
                        trend.get("maturity_level", "N/A"),
                        str(trend.get("trl_level", 0)),
                        f"{trend.get('research_momentum', 0)*100:.0f}%",
                    ])
            
            if len(table_data) > 1:
                trends_table = Table(table_data, colWidths=[2.5*inch, 1.2*inch, 0.8*inch, 1*inch])
                trends_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#db2777')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                elements.append(trends_table)
        
        return elements


# Singleton instance
_pdf_generator: Optional[PDFReportGenerator] = None


def get_pdf_generator() -> PDFReportGenerator:
    """Get PDF generator singleton"""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFReportGenerator()
    return _pdf_generator
