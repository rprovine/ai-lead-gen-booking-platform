"""
Predictive Analytics Engine
Uses AI to generate predictions and insights for leads
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import google.generativeai as genai

# Initialize Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_AI_API_KEY')
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


class PredictiveAnalytics:
    """AI-powered predictive analytics for lead scoring and insights"""

    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash') if GOOGLE_API_KEY else None

    async def calculate_conversion_probability(self, lead: Dict, historical_data: Optional[List[Dict]] = None) -> Dict:
        """
        Predict probability of lead converting based on characteristics

        Args:
            lead: Lead data dictionary
            historical_data: Optional historical conversion data for context

        Returns:
            Dict with probability, confidence, and factors
        """
        if not self.model:
            # Fallback to rule-based scoring
            return self._rule_based_conversion_score(lead)

        try:
            prompt = f"""
Analyze this lead and predict their conversion probability (0-100):

Lead Information:
- Company: {lead.get('company_name')}
- Industry: {lead.get('industry')}
- Location: {lead.get('location')}
- Employee Count: {lead.get('employee_count', 'Unknown')}
- Current Score: {lead.get('score', 0)}
- Status: {lead.get('status', 'NEW')}
- Tech Stack: {', '.join(lead.get('tech_stack', []))}
- Pain Points: {', '.join(lead.get('pain_points', []))}
- Source: {lead.get('source', 'Unknown')}

Based on these factors, provide:
1. Conversion probability (0-100)
2. Confidence level (0-100)
3. Top 3 positive factors (reasons they might convert)
4. Top 3 risk factors (reasons they might not convert)

Respond ONLY with valid JSON in this exact format:
{{
    "probability": 75,
    "confidence": 85,
    "positive_factors": ["High score", "Strong tech stack fit", "Clear pain points"],
    "risk_factors": ["New lead", "Unknown budget", "Competitive industry"]
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))

            return {
                'probability': float(result.get('probability', 50)),
                'confidence': float(result.get('confidence', 50)),
                'factors': {
                    'positive': result.get('positive_factors', []),
                    'negative': result.get('risk_factors', [])
                }
            }
        except Exception as e:
            print(f"Error in AI conversion prediction: {e}")
            return self._rule_based_conversion_score(lead)

    def _rule_based_conversion_score(self, lead: Dict) -> Dict:
        """Fallback rule-based conversion scoring"""
        probability = 50  # Base probability
        factors = {'positive': [], 'negative': []}

        # Score factor
        score = lead.get('score', 0)
        if score >= 80:
            probability += 25
            factors['positive'].append('High lead score (80+)')
        elif score >= 60:
            probability += 15
            factors['positive'].append('Good lead score (60+)')
        elif score < 40:
            probability -= 15
            factors['negative'].append('Low lead score')

        # Status factor
        status = lead.get('status', 'NEW')
        status_boost = {
            'OPPORTUNITY': 30,
            'QUALIFIED': 20,
            'CONTACTED': 10,
            'NEW': 0,
            'LOST': -40
        }
        probability += status_boost.get(status, 0)
        if status == 'OPPORTUNITY':
            factors['positive'].append('Active opportunity in pipeline')
        elif status == 'LOST':
            factors['negative'].append('Previously marked as lost')

        # Pain points factor
        pain_points = len(lead.get('pain_points', []))
        if pain_points >= 3:
            probability += 10
            factors['positive'].append('Multiple identified pain points')
        elif pain_points == 0:
            probability -= 10
            factors['negative'].append('No identified pain points')

        # Tech stack factor
        tech_stack = len(lead.get('tech_stack', []))
        if tech_stack >= 3:
            probability += 5
            factors['positive'].append('Established tech stack')

        # Company size factor
        employee_count = lead.get('employee_count', 0)
        if employee_count >= 50:
            probability += 10
            factors['positive'].append('Substantial company size')
        elif employee_count > 0 and employee_count < 10:
            probability -= 5
            factors['negative'].append('Very small company')

        return {
            'probability': max(0, min(100, probability)),
            'confidence': 60,  # Medium confidence for rule-based
            'factors': factors
        }

    async def calculate_icp_match_score(self, lead: Dict, icp_criteria: Optional[Dict] = None) -> Dict:
        """
        Calculate how well lead matches ideal customer profile

        Args:
            lead: Lead data
            icp_criteria: Optional ICP criteria from settings

        Returns:
            Dict with match score and matching/missing factors
        """
        if not icp_criteria:
            # Default ICP for Hawaii tech consulting
            icp_criteria = {
                'industries': ['Technology', 'Healthcare', 'Finance', 'Retail', 'Professional Services'],
                'min_employees': 20,
                'max_employees': 500,
                'locations': ['Hawaii', 'Honolulu', 'Maui', 'Oahu'],
                'tech_indicators': ['Salesforce', 'HubSpot', 'AWS', 'Cloud', 'API']
            }

        score = 0
        max_score = 100
        matching = []
        missing = []

        # Industry match (25 points)
        industry = lead.get('industry', '')
        if industry in icp_criteria.get('industries', []):
            score += 25
            matching.append(f"Target industry: {industry}")
        else:
            missing.append(f"Not in target industries")

        # Company size (25 points)
        employee_count = lead.get('employee_count', 0)
        min_emp = icp_criteria.get('min_employees', 0)
        max_emp = icp_criteria.get('max_employees', 1000000)

        if employee_count >= min_emp and employee_count <= max_emp:
            score += 25
            matching.append(f"Ideal company size: {employee_count} employees")
        elif employee_count > 0:
            # Partial credit if close
            if employee_count < min_emp:
                partial = max(0, 15 - (min_emp - employee_count) / min_emp * 15)
                score += partial
                missing.append(f"Smaller than ideal ({employee_count} vs {min_emp}+)")
            else:
                partial = max(0, 15 - (employee_count - max_emp) / max_emp * 15)
                score += partial
                missing.append(f"Larger than ideal ({employee_count} vs {max_emp} max)")
        else:
            missing.append("Company size unknown")

        # Location match (20 points)
        location = lead.get('location', '')
        location_match = any(loc.lower() in location.lower() for loc in icp_criteria.get('locations', []))
        if location_match:
            score += 20
            matching.append(f"Target location: {location}")
        else:
            missing.append(f"Outside target locations")

        # Tech stack match (15 points)
        tech_stack = lead.get('tech_stack', [])
        tech_indicators = icp_criteria.get('tech_indicators', [])
        tech_matches = [tech for tech in tech_stack if any(indicator.lower() in tech.lower() for indicator in tech_indicators)]

        if tech_matches:
            tech_score = min(15, len(tech_matches) * 5)
            score += tech_score
            matching.append(f"Relevant tech stack: {', '.join(tech_matches)}")
        else:
            missing.append("No matching tech indicators")

        # Lead score factor (15 points)
        lead_score = lead.get('score', 0)
        if lead_score >= 70:
            score += 15
            matching.append("High quality lead score")
        elif lead_score >= 50:
            score += 10
            matching.append("Good lead score")
        else:
            missing.append("Below-average lead score")

        return {
            'score': round(score, 2),
            'matching_factors': matching,
            'missing_factors': missing
        }

    async def calculate_lead_velocity(self, lead: Dict, status_history: Optional[List[Dict]] = None) -> Dict:
        """
        Calculate lead velocity score based on pipeline movement speed

        Args:
            lead: Lead data
            status_history: Optional status change history

        Returns:
            Dict with velocity score and insights
        """
        if not status_history or len(status_history) < 2:
            # New lead or insufficient data
            return {
                'score': 50,
                'days_in_pipeline': 0,
                'average_time_per_stage': 0,
                'status': 'insufficient_data',
                'insight': 'New lead - velocity tracking begins after first status change'
            }

        # Calculate time in pipeline
        created_at = datetime.fromisoformat(lead.get('created_at', datetime.now().isoformat()))
        days_in_pipeline = (datetime.now() - created_at).days

        # Calculate velocity score (faster movement = higher score)
        # Ideal: 7-14 days per stage
        # Fast: < 7 days per stage (might be too rushed)
        # Slow: > 30 days per stage (stalled)

        num_stages = len(status_history)
        avg_days_per_stage = days_in_pipeline / max(1, num_stages - 1)

        if avg_days_per_stage < 3:
            score = 60  # Too fast, might not be properly qualified
            status = 'very_fast'
            insight = 'Moving very quickly - ensure proper qualification'
        elif avg_days_per_stage <= 7:
            score = 90  # Excellent velocity
            status = 'fast'
            insight = 'Excellent pipeline velocity'
        elif avg_days_per_stage <= 14:
            score = 80  # Good velocity
            status = 'good'
            insight = 'Healthy pipeline progression'
        elif avg_days_per_stage <= 30:
            score = 50  # Moderate velocity
            status = 'moderate'
            insight = 'Moderate pace - consider follow-up'
        else:
            score = 25  # Slow, possibly stalled
            status = 'slow'
            insight = 'Pipeline stalled - immediate action needed'

        return {
            'score': score,
            'days_in_pipeline': days_in_pipeline,
            'average_time_per_stage': round(avg_days_per_stage, 1),
            'num_stage_changes': num_stages - 1,
            'status': status,
            'insight': insight
        }

    async def generate_recommended_action(self, lead: Dict, predictions: Dict) -> Dict:
        """
        Generate AI-powered recommended next action

        Args:
            lead: Lead data
            predictions: Dict containing conversion probability, ICP score, etc.

        Returns:
            Dict with recommended action and reasoning
        """
        if not self.model:
            return self._rule_based_recommendation(lead, predictions)

        try:
            prompt = f"""
Based on this lead analysis, recommend the single best next action:

Lead: {lead.get('company_name')} ({lead.get('industry')})
Current Status: {lead.get('status', 'NEW')}
Lead Score: {lead.get('score', 0)}
Conversion Probability: {predictions.get('conversion_probability', 50)}%
ICP Match: {predictions.get('icp_match_score', 50)}%

Recommend ONE specific action from these options:
- "Send personalized email" - When lead needs initial outreach
- "Schedule discovery call" - When lead is qualified and ready
- "Send follow-up" - When lead has been contacted but not responded
- "Request demo" - When lead shows high interest
- "Update qualification" - When lead needs more research
- "Move to nurture" - When timing isn't right but lead is good
- "Mark as lost" - When lead clearly won't convert

Respond with ONLY valid JSON:
{{
    "action": "Send personalized email",
    "reasoning": "High ICP match but new lead - personalized outreach is best first step",
    "priority": "high",
    "timing": "within 24 hours"
}}
"""

            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip().replace('```json', '').replace('```', ''))

            return {
                'action': result.get('action', 'Review lead details'),
                'reasoning': result.get('reasoning', ''),
                'priority': result.get('priority', 'medium'),
                'timing': result.get('timing', 'this week')
            }
        except Exception as e:
            print(f"Error generating recommendation: {e}")
            return self._rule_based_recommendation(lead, predictions)

    def _rule_based_recommendation(self, lead: Dict, predictions: Dict) -> Dict:
        """Fallback rule-based recommendations"""
        status = lead.get('status', 'NEW')
        conversion_prob = predictions.get('conversion_probability', 50)
        icp_score = predictions.get('icp_match_score', 50)

        # High value, not contacted
        if status == 'NEW' and conversion_prob >= 70 and icp_score >= 70:
            return {
                'action': 'Send personalized email',
                'reasoning': 'High-value lead matching ICP - prioritize outreach',
                'priority': 'high',
                'timing': 'within 24 hours'
            }

        # Contacted, waiting for response
        elif status == 'CONTACTED' and conversion_prob >= 60:
            return {
                'action': 'Send follow-up',
                'reasoning': 'Qualified lead needs follow-up to maintain momentum',
                'priority': 'medium',
                'timing': 'within 3 days'
            }

        # Qualified, ready for next step
        elif status == 'QUALIFIED' and conversion_prob >= 70:
            return {
                'action': 'Schedule discovery call',
                'reasoning': 'Qualified lead ready for deeper conversation',
                'priority': 'high',
                'timing': 'this week'
            }

        # Opportunity, push forward
        elif status == 'OPPORTUNITY':
            return {
                'action': 'Request demo',
                'reasoning': 'Active opportunity - demonstrate value',
                'priority': 'critical',
                'timing': 'immediately'
            }

        # Low probability, needs work
        elif conversion_prob < 40:
            return {
                'action': 'Update qualification',
                'reasoning': 'Low conversion probability - gather more information',
                'priority': 'low',
                'timing': 'this month'
            }

        # Default
        else:
            return {
                'action': 'Review lead details',
                'reasoning': 'Standard follow-up needed',
                'priority': 'medium',
                'timing': 'this week'
            }

    async def predict_best_contact_time(self, lead: Dict) -> str:
        """
        Predict best time to contact based on industry and location

        Args:
            lead: Lead data

        Returns:
            String describing best contact time
        """
        industry = lead.get('industry', '').lower()
        location = lead.get('location', '').lower()

        # Hawaii timezone considerations
        if 'hawaii' in location or 'honolulu' in location:
            timezone_note = "HST"
        else:
            timezone_note = "their local time"

        # Industry-based timing
        if 'healthcare' in industry or 'medical' in industry:
            return f"Tue-Thu 10am-12pm {timezone_note} (avoid Mondays and late afternoons)"
        elif 'retail' in industry or 'restaurant' in industry:
            return f"Tue-Wed 2-4pm {timezone_note} (avoid weekends and meal times)"
        elif 'tech' in industry or 'software' in industry:
            return f"Tue-Thu 9-11am or 2-4pm {timezone_note} (avoid Monday mornings)"
        elif 'finance' in industry or 'accounting' in industry:
            return f"Wed-Thu 10am-3pm {timezone_note} (avoid month-end/quarter-end)"
        else:
            return f"Tue-Thu 10am-2pm {timezone_note} (standard business hours)"
