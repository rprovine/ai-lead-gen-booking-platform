"""
PDF Sales Playbook Generator
Creates professional sales playbooks from AI intelligence data
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import io
from typing import Dict


class SalesPlaybookPDFGenerator:
    """Generate professional PDF sales playbooks"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e3a8a'),  # Dark blue
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2563eb'),  # Blue
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold',
            borderPadding=5,
            leftIndent=0
        ))

        # Bullet style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=8,
            bulletIndent=10
        ))

    def _safe_get_dict(self, intelligence: Dict, key: str, default=None) -> Dict:
        """Safely get a nested dict field, parsing from JSON string if needed"""
        import json

        value = intelligence.get(key, default or {})

        # If it's already a dict, return it
        if isinstance(value, dict):
            return value

        # If it's a string, try to parse it as JSON
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                pass

        # Fallback to default
        return default or {}

    def generate_playbook(self, lead_data: Dict, intelligence: Dict) -> bytes:
        """Generate complete sales playbook PDF"""

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=50
        )

        # Container for PDF elements
        story = []

        # Add content sections
        self._add_cover_page(story, lead_data, intelligence)
        self._add_executive_summary(story, intelligence)
        self._add_perplexity_research(story, intelligence)
        self._add_hot_buttons(story, intelligence)
        self._add_recommended_approach(story, intelligence)
        self._add_talking_points(story, intelligence)
        self._add_decision_maker(story, intelligence)
        self._add_budget_analysis(story, intelligence)
        self._add_competitive_positioning(story, intelligence)
        self._add_appointment_strategy(story, intelligence)
        self._add_next_steps(story, intelligence)

        # Build PDF
        doc.build(story)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def _add_cover_page(self, story, lead_data: Dict, intelligence: Dict):
        """Add cover page"""
        # Company name as title
        title = Paragraph(
            f"<b>Sales Playbook</b><br/>{lead_data.get('company_name', 'Prospect')}",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))

        # Lead info table
        budget_data = self._safe_get_dict(intelligence, 'budget')
        lead_info = [
            ['Industry:', lead_data.get('industry', 'N/A')],
            ['Location:', lead_data.get('location', 'N/A')],
            ['Employees:', str(lead_data.get('employee_count', 'Unknown'))],
            ['Lead Score:', f"{intelligence.get('confidence', 0)}/100"],
            ['Investment Likelihood:', budget_data.get('investment_likelihood', 'Unknown')]
        ]

        table = Table(lead_info, colWidths=[2*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#2563eb')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#eff6ff')])
        ]))

        story.append(table)
        story.append(Spacer(1, 0.5 * inch))

        # LeniLani branding
        branding = Paragraph(
            "<b>LeniLani Consulting</b><br/>1050 Queen Street, Suite 100<br/>Honolulu, HI 96814",
            self.styles['Normal']
        )
        story.append(branding)
        story.append(Spacer(1, 0.2 * inch))

        # Generation date
        date_text = Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            self.styles['Normal']
        )
        story.append(date_text)
        story.append(PageBreak())

    def _add_executive_summary(self, story, intelligence: Dict):
        """Add executive summary section"""
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        summary_text = intelligence.get('executive_summary', 'No summary available')
        story.append(Paragraph(summary_text, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

    def _add_perplexity_research(self, story, intelligence: Dict):
        """Add Perplexity AI research section"""
        # Get research data using safe helper
        perplexity_data = self._safe_get_dict(intelligence, 'perplexity_research')

        # Skip section if no research data available
        if not perplexity_data or not perplexity_data.get('has_recent_data'):
            return

        story.append(Paragraph("Recent Intelligence (Past 90 Days)", self.styles['SectionHeader']))

        # Research summary
        summary = perplexity_data.get('summary', '')
        if summary and summary != 'No significant recent news or developments found in the past 90 days.':
            story.append(Paragraph("<b>Summary:</b>", self.styles['Normal']))
            story.append(Paragraph(summary, self.styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

        # Recent news
        recent_news = perplexity_data.get('recent_news', '')
        if recent_news:
            story.append(Paragraph("<b>Recent News & Announcements:</b>", self.styles['Normal']))
            story.append(Paragraph(recent_news, self.styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

        # Leadership updates
        leadership = perplexity_data.get('leadership', '')
        if leadership:
            story.append(Paragraph("<b>Leadership Updates:</b>", self.styles['Normal']))
            story.append(Paragraph(leadership, self.styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

        # Business developments
        biz_dev = perplexity_data.get('business_developments', '')
        if biz_dev:
            story.append(Paragraph("<b>Business Developments:</b>", self.styles['Normal']))
            story.append(Paragraph(biz_dev, self.styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

        # Market position
        market_pos = perplexity_data.get('market_position', '')
        if market_pos:
            story.append(Paragraph("<b>Market Position:</b>", self.styles['Normal']))
            story.append(Paragraph(market_pos, self.styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

        # Challenges & opportunities
        challenges = perplexity_data.get('challenges_opportunities', '')
        if challenges:
            story.append(Paragraph("<b>Challenges & Opportunities:</b>", self.styles['Normal']))
            story.append(Paragraph(challenges, self.styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))

        story.append(Spacer(1, 0.2 * inch))

    def _add_hot_buttons(self, story, intelligence: Dict):
        """Add hot buttons section"""
        story.append(Paragraph("Hot Buttons & Pain Points", self.styles['SectionHeader']))

        hot_buttons = intelligence.get('hot_buttons', [])
        for button in hot_buttons:
            bullet = Paragraph(f"• {button}", self.styles['BulletPoint'])
            story.append(bullet)

        story.append(Spacer(1, 0.3 * inch))

    def _add_recommended_approach(self, story, intelligence: Dict):
        """Add recommended approach section"""
        story.append(Paragraph("Recommended Approach", self.styles['SectionHeader']))

        approach = intelligence.get('recommended_approach', 'No approach defined')
        story.append(Paragraph(approach, self.styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

    def _add_talking_points(self, story, intelligence: Dict):
        """Add key talking points"""
        story.append(Paragraph("Key Talking Points", self.styles['SectionHeader']))

        points = intelligence.get('talking_points', [])
        for point in points:
            bullet = Paragraph(f"• {point}", self.styles['BulletPoint'])
            story.append(bullet)

        story.append(Spacer(1, 0.3 * inch))

    def _add_decision_maker(self, story, intelligence: Dict):
        """Add decision maker insights"""
        story.append(Paragraph("Decision Maker Intelligence", self.styles['SectionHeader']))

        dm = self._safe_get_dict(intelligence, 'decision_maker')

        dm_data = [
            ['Target Role:', dm.get('target_role', 'Unknown')],
            ['Best Contact:', dm.get('best_contact', 'Email + LinkedIn')],
        ]

        table = Table(dm_data, colWidths=[2*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

        # Priorities
        story.append(Paragraph("<b>Their Priorities:</b>", self.styles['Normal']))
        priorities = dm.get('priorities', [])
        for priority in priorities:
            story.append(Paragraph(f"• {priority}", self.styles['BulletPoint']))

        story.append(Spacer(1, 0.3 * inch))

    def _add_budget_analysis(self, story, intelligence: Dict):
        """Add budget analysis"""
        story.append(Paragraph("Budget Analysis", self.styles['SectionHeader']))

        budget = self._safe_get_dict(intelligence, 'budget')

        budget_data = [
            ['Estimated Range:', budget.get('estimated_range', 'Unknown')],
            ['Investment Likelihood:', budget.get('investment_likelihood', 'Unknown')],
            ['Signals:', budget.get('signals', 'N/A')]
        ]

        table = Table(budget_data, colWidths=[2*inch, 3.5*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

    def _add_competitive_positioning(self, story, intelligence: Dict):
        """Add competitive positioning"""
        story.append(Paragraph("Competitive Positioning", self.styles['SectionHeader']))

        comp = self._safe_get_dict(intelligence, 'competitive_positioning')

        # Likely competitors
        story.append(Paragraph("<b>Likely Competitors:</b>", self.styles['Normal']))
        competitors = comp.get('likely_competitors', [])
        for competitor in competitors:
            story.append(Paragraph(f"• {competitor}", self.styles['BulletPoint']))

        story.append(Spacer(1, 0.15 * inch))

        # Our differentiators
        story.append(Paragraph("<b>Our Differentiators:</b>", self.styles['Normal']))
        diffs = comp.get('our_differentiators', [])
        for diff in diffs:
            story.append(Paragraph(f"• {diff}", self.styles['BulletPoint']))

        story.append(Spacer(1, 0.15 * inch))

        # Hawaii advantage
        story.append(Paragraph("<b>Hawaii Advantage:</b>", self.styles['Normal']))
        advantage = comp.get('hawaii_advantage', 'Local expertise')
        story.append(Paragraph(advantage, self.styles['Normal']))

        story.append(Spacer(1, 0.3 * inch))

    def _add_appointment_strategy(self, story, intelligence: Dict):
        """Add appointment setting strategy"""
        story.append(Paragraph("Appointment Setting Strategy", self.styles['SectionHeader']))

        appt = self._safe_get_dict(intelligence, 'appointment_strategy')

        appt_data = [
            ['Hook:', appt.get('hook', 'Free consultation')],
            ['Format:', appt.get('format', 'In-person')],
            ['Follow-up:', appt.get('follow_up_cadence', 'Weekly')]
        ]

        table = Table(appt_data, colWidths=[1.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

    def _add_next_steps(self, story, intelligence: Dict):
        """Add next steps"""
        story.append(Paragraph("Next Steps", self.styles['SectionHeader']))

        next_steps = intelligence.get('next_steps', [])
        for i, step in enumerate(next_steps, 1):
            step_para = Paragraph(f"{i}. {step}", self.styles['Normal'])
            story.append(step_para)
            story.append(Spacer(1, 0.1 * inch))


# Example usage
if __name__ == "__main__":
    generator = SalesPlaybookPDFGenerator()

    # Sample data
    lead_data = {
        "company_name": "Aloha Hotels & Resorts",
        "industry": "Tourism & Hospitality",
        "location": "Waikiki, Honolulu, HI",
        "employee_count": 250
    }

    intelligence = {
        "executive_summary": "High-value opportunity in tourism sector...",
        "hot_buttons": ["Digital transformation", "Customer experience"],
        "confidence": 85
    }

    pdf_bytes = generator.generate_playbook(lead_data, intelligence)
    with open("test_playbook.pdf", "wb") as f:
        f.write(pdf_bytes)
