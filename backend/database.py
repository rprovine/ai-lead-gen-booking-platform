"""
Database integration layer for Supabase
Handles all database operations for leads, intelligence, appointments, and outreach
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from supabase import create_client, Client

class SupabaseDB:
    """Supabase database client for LeniLani Lead Generation Platform"""

    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')

        if not self.url or not self.key or self.key == 'your_anon_key_here':
            print("⚠️  Supabase not configured - using in-memory storage")
            self.client = None
        else:
            try:
                self.client: Client = create_client(self.url, self.key)
                print("✅ Supabase connected successfully")
            except Exception as e:
                print(f"❌ Supabase connection failed: {e}")
                self.client = None

    # ============= LEADS =============

    async def create_lead(self, lead_data: Dict) -> Optional[Dict]:
        """Create a new lead in database"""
        if not self.client:
            return None

        try:
            response = self.client.table('leads').insert(lead_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating lead: {e}")
            return None

    async def get_leads(self, limit: int = 100, status: str = None, min_score: int = None) -> List[Dict]:
        """Get all leads, optionally filtered by status and min_score"""
        if not self.client:
            return []

        try:
            query = self.client.table('leads').select('*')

            # Filter by status if provided
            if status:
                query = query.eq('status', status)

            # Filter by minimum score if provided
            if min_score is not None:
                query = query.gte('score', min_score)

            response = query.order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting leads: {e}")
            return []

    async def get_lead_by_id(self, lead_id: str) -> Optional[Dict]:
        """Get a specific lead by ID"""
        if not self.client:
            return None

        try:
            response = self.client.table('leads').select('*').eq('id', lead_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting lead: {e}")
            return None

    async def update_lead(self, lead_id: str, update_data: Dict) -> Optional[Dict]:
        """Update a lead"""
        if not self.client:
            return None

        try:
            response = self.client.table('leads').update(update_data).eq('id', lead_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating lead: {e}")
            return None

    async def upsert_lead(self, lead_data: Dict) -> Optional[Dict]:
        """Insert or update a lead (by id)"""
        if not self.client:
            return None

        try:
            response = self.client.table('leads').upsert(lead_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting lead: {e}")
            return None

    # ============= INTELLIGENCE =============

    async def save_intelligence(self, lead_id: str, intelligence_data: Dict) -> Optional[Dict]:
        """Save AI-generated intelligence for a lead"""
        if not self.client:
            return None

        try:
            data = {
                'lead_id': lead_id,
                'intelligence': intelligence_data
            }
            response = self.client.table('lead_intelligence').upsert(data, on_conflict='lead_id').execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error saving intelligence: {e}")
            return None

    async def get_intelligence(self, lead_id: str) -> Optional[Dict]:
        """Get intelligence for a lead"""
        if not self.client:
            return None

        try:
            response = self.client.table('lead_intelligence').select('intelligence').eq('lead_id', lead_id).execute()
            return response.data[0]['intelligence'] if response.data else None
        except Exception as e:
            print(f"Error getting intelligence: {e}")
            return None

    # ============= APPOINTMENTS =============

    async def create_appointment(self, appointment_data: Dict) -> Optional[Dict]:
        """Create a new appointment"""
        if not self.client:
            return None

        try:
            response = self.client.table('appointments').insert(appointment_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating appointment: {e}")
            return None

    async def get_appointments(self, lead_id: Optional[str] = None) -> List[Dict]:
        """Get appointments, optionally filtered by lead_id"""
        if not self.client:
            return []

        try:
            query = self.client.table('appointments').select('*')
            if lead_id:
                query = query.eq('lead_id', lead_id)
            response = query.order('date_time').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting appointments: {e}")
            return []

    # ============= OUTREACH =============

    async def create_outreach(self, outreach_data: Dict) -> Optional[Dict]:
        """Create outreach record"""
        if not self.client:
            return None

        try:
            response = self.client.table('outreach').insert(outreach_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating outreach: {e}")
            return None

    async def get_outreach_history(self, lead_id: str) -> List[Dict]:
        """Get outreach history for a lead"""
        if not self.client:
            return []

        try:
            response = self.client.table('outreach').select('*').eq('lead_id', lead_id).order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting outreach history: {e}")
            return []

    # ============= ANALYTICS =============

    async def get_analytics(self) -> Dict:
        """Get dashboard analytics"""
        if not self.client:
            return {
                'total_leads': 0,
                'qualified_leads': 0,
                'total_appointments': 0,
                'avg_lead_score': 0
            }

        try:
            # Get lead counts
            all_leads = self.client.table('leads').select('score', count='exact').execute()
            qualified = self.client.table('leads').select('*', count='exact').gte('score', 70).execute()
            appointments = self.client.table('appointments').select('*', count='exact').execute()

            # Calculate avg score
            avg_score = 0
            if all_leads.data:
                scores = [lead.get('score', 0) for lead in all_leads.data]
                avg_score = sum(scores) / len(scores) if scores else 0

            return {
                'total_leads': all_leads.count or 0,
                'qualified_leads': qualified.count or 0,
                'total_appointments': appointments.count or 0,
                'avg_lead_score': round(avg_score, 1)
            }
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {
                'total_leads': 0,
                'qualified_leads': 0,
                'total_appointments': 0,
                'avg_lead_score': 0
            }
    # ============= CAMPAIGNS =============

    async def create_campaign(self, campaign_data: Dict) -> Optional[Dict]:
        """Create a new campaign"""
        if not self.client:
            return None

        try:
            response = self.client.table('campaigns').insert(campaign_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating campaign: {e}")
            return None

    async def get_campaigns(self, status: Optional[str] = None) -> List[Dict]:
        """Get all campaigns, optionally filtered by status"""
        if not self.client:
            return []

        try:
            query = self.client.table('campaigns').select('*').order('created_at', desc=True)

            if status:
                query = query.eq('status', status)

            response = query.execute()
            return response.data or []
        except Exception as e:
            print(f"Error getting campaigns: {e}")
            return []

    async def get_campaign_by_id(self, campaign_id: int) -> Optional[Dict]:
        """Get a specific campaign by ID"""
        if not self.client:
            return None

        try:
            response = self.client.table('campaigns').select('*').eq('id', campaign_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting campaign: {e}")
            return None

    async def update_campaign(self, campaign_id: int, update_data: Dict) -> Optional[Dict]:
        """Update a campaign"""
        if not self.client:
            return None

        try:
            response = self.client.table('campaigns').update(update_data).eq('id', campaign_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating campaign: {e}")
            return None

    async def delete_campaign(self, campaign_id: int) -> bool:
        """Delete a campaign"""
        if not self.client:
            return False

        try:
            self.client.table('campaigns').delete().eq('id', campaign_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting campaign: {e}")
            return False

    async def add_leads_to_campaign(self, campaign_id: int, lead_ids: List[str]) -> bool:
        """Add multiple leads to a campaign"""
        if not self.client:
            return False

        try:
            campaign_leads = [
                {'campaign_id': campaign_id, 'lead_id': lead_id, 'status': 'pending'}
                for lead_id in lead_ids
            ]

            self.client.table('campaign_leads').insert(campaign_leads).execute()

            # Update campaign total_leads count
            current_count = len(lead_ids)
            campaign = await self.get_campaign_by_id(campaign_id)
            if campaign:
                new_count = campaign.get('total_leads', 0) + current_count
                await self.update_campaign(campaign_id, {'total_leads': new_count})

            return True
        except Exception as e:
            print(f"Error adding leads to campaign: {e}")
            return False

    async def get_campaign_leads(self, campaign_id: int) -> List[Dict]:
        """Get all leads in a campaign with their status"""
        if not self.client:
            return []

        try:
            # Join campaign_leads with leads table
            response = self.client.table('campaign_leads').select(
                '*, leads(*)'
            ).eq('campaign_id', campaign_id).execute()

            return response.data or []
        except Exception as e:
            print(f"Error getting campaign leads: {e}")
            return []

    async def update_campaign_lead_status(self, campaign_id: int, lead_id: str, status: str, timestamp_field: Optional[str] = None) -> bool:
        """Update the status of a lead in a campaign"""
        if not self.client:
            return False

        try:
            update_data = {'status': status}

            # Add timestamp if specified
            if timestamp_field:
                update_data[timestamp_field] = datetime.utcnow().isoformat()

            self.client.table('campaign_leads').update(update_data).eq(
                'campaign_id', campaign_id
            ).eq('lead_id', lead_id).execute()

            # Update campaign statistics
            if status == 'contacted':
                campaign = await self.get_campaign_by_id(campaign_id)
                if campaign:
                    await self.update_campaign(campaign_id, {
                        'contacted_leads': campaign.get('contacted_leads', 0) + 1
                    })
            elif status == 'replied':
                campaign = await self.get_campaign_by_id(campaign_id)
                if campaign:
                    await self.update_campaign(campaign_id, {
                        'replied_count': campaign.get('replied_count', 0) + 1
                    })
            elif status == 'converted':
                campaign = await self.get_campaign_by_id(campaign_id)
                if campaign:
                    await self.update_campaign(campaign_id, {
                        'converted_count': campaign.get('converted_count', 0) + 1
                    })

            return True
        except Exception as e:
            print(f"Error updating campaign lead status: {e}")
            return False

    async def create_campaign_sequence(self, sequence_data: Dict) -> Optional[Dict]:
        """Create a campaign sequence step"""
        if not self.client:
            return None

        try:
            response = self.client.table('campaign_sequences').insert(sequence_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating campaign sequence: {e}")
            return None

    async def get_campaign_sequences(self, campaign_id: int) -> List[Dict]:
        """Get all sequence steps for a campaign"""
        if not self.client:
            return []

        try:
            response = self.client.table('campaign_sequences').select('*').eq(
                'campaign_id', campaign_id
            ).order('sequence_number').execute()

            return response.data or []
        except Exception as e:
            print(f"Error getting campaign sequences: {e}")
            return []

    async def get_campaign_analytics(self, campaign_id: int) -> Dict:
        """Get analytics for a specific campaign"""
        if not self.client:
            return {}

        try:
            campaign = await self.get_campaign_by_id(campaign_id)
            if not campaign:
                return {}

            leads = await self.get_campaign_leads(campaign_id)

            # Calculate progress percentage
            total = campaign.get('total_leads', 0)
            contacted = campaign.get('contacted_leads', 0)
            progress = round((contacted / total * 100) if total > 0 else 0)

            # Calculate conversion rate
            converted = campaign.get('converted_count', 0)
            conversion_rate = round((converted / contacted * 100) if contacted > 0 else 0, 1)

            return {
                'total_leads': total,
                'contacted_leads': contacted,
                'opened_count': campaign.get('opened_count', 0),
                'replied_count': campaign.get('replied_count', 0),
                'converted_count': converted,
                'progress': progress,
                'conversion_rate': conversion_rate,
                'status': campaign.get('status', 'draft')
            }
        except Exception as e:
            print(f"Error getting campaign analytics: {e}")
            return {}


# Global instance
db = SupabaseDB()
