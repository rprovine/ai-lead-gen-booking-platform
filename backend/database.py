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
    # ============= DATA SOURCES CONFIGURATION =============

    async def get_data_sources(self, organization_id: str = 'default') -> List[Dict]:
        """Get all data source configurations for an organization"""
        if not self.client:
            return []

        try:
            response = self.client.table('data_sources_config').select('*').eq('organization_id', organization_id).order('source_name').execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting data sources: {e}")
            return []

    async def get_data_source(self, source_type: str, organization_id: str = 'default') -> Optional[Dict]:
        """Get a specific data source configuration"""
        if not self.client:
            return None

        try:
            response = self.client.table('data_sources_config').select('*').eq('organization_id', organization_id).eq('source_type', source_type).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting data source: {e}")
            return None

    async def update_data_source(self, source_type: str, update_data: Dict, organization_id: str = 'default') -> Optional[Dict]:
        """Update a data source configuration"""
        if not self.client:
            return None

        try:
            response = self.client.table('data_sources_config').update(update_data).eq('organization_id', organization_id).eq('source_type', source_type).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating data source: {e}")
            return None

    async def toggle_data_source(self, source_type: str, is_enabled: bool, organization_id: str = 'default') -> Optional[Dict]:
        """Enable or disable a data source"""
        if not self.client:
            return None

        try:
            response = self.client.table('data_sources_config').update({
                'is_enabled': is_enabled
            }).eq('organization_id', organization_id).eq('source_type', source_type).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error toggling data source: {e}")
            return None

    async def upsert_data_source(self, source_data: Dict) -> Optional[Dict]:
        """Insert or update a data source configuration"""
        if not self.client:
            return None

        try:
            response = self.client.table('data_sources_config').upsert(source_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting data source: {e}")
            return None

    async def test_data_source_connection(self, source_type: str, organization_id: str = 'default') -> Dict:
        """Test a data source connection and update test status"""
        if not self.client:
            return {'success': False, 'message': 'Database not connected'}

        try:
            # Update test timestamp and status
            await self.update_data_source(source_type, {
                'last_tested_at': datetime.now().isoformat(),
                'test_status': 'testing'
            }, organization_id)

            # The actual connection test will be done in the API endpoint
            # This method just updates the database record
            return {'success': True, 'message': 'Test initiated'}
        except Exception as e:
            print(f"Error testing data source: {e}")
            return {'success': False, 'message': str(e)}

    # ============= SETTINGS: BUSINESS PROFILE =============

    async def get_business_profile(self, organization_id: str = 'default') -> Optional[Dict]:
        """Get business profile for an organization"""
        if not self.client:
            return None

        try:
            response = self.client.table('business_profile').select('*').eq('organization_id', organization_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting business profile: {e}")
            return None

    async def upsert_business_profile(self, profile_data: Dict) -> Optional[Dict]:
        """Insert or update business profile"""
        if not self.client:
            return None

        try:
            response = self.client.table('business_profile').upsert(profile_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting business profile: {e}")
            return None

    # ============= SETTINGS: ICP CONFIG =============

    async def get_icp_configs(self, organization_id: str = 'default') -> List[Dict]:
        """Get all ICP configurations for an organization"""
        if not self.client:
            return []

        try:
            response = self.client.table('icp_config').select('*').eq('organization_id', organization_id).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error getting ICP configs: {e}")
            return []

    async def get_icp_config(self, icp_id: str) -> Optional[Dict]:
        """Get a specific ICP configuration by ID"""
        if not self.client:
            return None

        try:
            response = self.client.table('icp_config').select('*').eq('id', icp_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting ICP config: {e}")
            return None

    async def create_icp_config(self, icp_data: Dict) -> Optional[Dict]:
        """Create a new ICP configuration"""
        if not self.client:
            return None

        try:
            response = self.client.table('icp_config').insert(icp_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating ICP config: {e}")
            return None

    async def update_icp_config(self, icp_id: str, icp_data: Dict) -> Optional[Dict]:
        """Update an ICP configuration"""
        if not self.client:
            return None

        try:
            response = self.client.table('icp_config').update(icp_data).eq('id', icp_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating ICP config: {e}")
            return None

    async def delete_icp_config(self, icp_id: str) -> bool:
        """Delete an ICP configuration"""
        if not self.client:
            return False

        try:
            self.client.table('icp_config').delete().eq('id', icp_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting ICP config: {e}")
            return False

    # ============= SETTINGS: LEAD PREFERENCES =============

    async def get_lead_preferences(self, organization_id: str = 'default') -> Optional[Dict]:
        """Get lead generation preferences for an organization"""
        if not self.client:
            return None

        try:
            response = self.client.table('lead_preferences').select('*').eq('organization_id', organization_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting lead preferences: {e}")
            return None

    async def upsert_lead_preferences(self, preferences_data: Dict) -> Optional[Dict]:
        """Insert or update lead preferences"""
        if not self.client:
            return None

        try:
            response = self.client.table('lead_preferences').upsert(preferences_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting lead preferences: {e}")
            return None

    # ============= SETTINGS: SEARCH & DISCOVERY =============

    async def get_search_discovery_settings(self, organization_id: str = 'default') -> Optional[Dict]:
        """Get search & discovery settings for an organization"""
        if not self.client:
            return None

        try:
            response = self.client.table('search_discovery_settings').select('*').eq('organization_id', organization_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting search discovery settings: {e}")
            return None

    async def upsert_search_discovery_settings(self, settings_data: Dict) -> Optional[Dict]:
        """Insert or update search & discovery settings"""
        if not self.client:
            return None

        try:
            response = self.client.table('search_discovery_settings').upsert(settings_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting search discovery settings: {e}")
            return None

    # ============= SETTINGS: NOTIFICATIONS =============

    async def get_notification_settings(self, organization_id: str = 'default') -> Optional[Dict]:
        """Get notification settings for an organization"""
        if not self.client:
            return None

        try:
            response = self.client.table('notification_settings').select('*').eq('organization_id', organization_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting notification settings: {e}")
            return None

    async def upsert_notification_settings(self, settings_data: Dict) -> Optional[Dict]:
        """Insert or update notification settings"""
        if not self.client:
            return None

        try:
            response = self.client.table('notification_settings').upsert(settings_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting notification settings: {e}")
            return None

    # ============= SETTINGS: INTEGRATIONS =============

    async def get_integration_settings(self, organization_id: str = 'default') -> Optional[Dict]:
        """Get integration settings for an organization"""
        if not self.client:
            return None

        try:
            response = self.client.table('integration_settings').select('*').eq('organization_id', organization_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting integration settings: {e}")
            return None

    async def upsert_integration_settings(self, settings_data: Dict) -> Optional[Dict]:
        """Insert or update integration settings"""
        if not self.client:
            return None

        try:
            response = self.client.table('integration_settings').upsert(settings_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting integration settings: {e}")
            return None

    # ============= SETTINGS: AI PERSONALIZATION =============

    async def get_ai_personalization_settings(self, organization_id: str = 'default') -> Optional[Dict]:
        """Get AI personalization settings for an organization"""
        if not self.client:
            return None

        try:
            response = self.client.table('ai_personalization_settings').select('*').eq('organization_id', organization_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting AI personalization settings: {e}")
            return None

    async def upsert_ai_personalization_settings(self, settings_data: Dict) -> Optional[Dict]:
        """Insert or update AI personalization settings"""
        if not self.client:
            return None

        try:
            response = self.client.table('ai_personalization_settings').upsert(settings_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error upserting AI personalization settings: {e}")
            return None

    # ============= LEAD STATUS MANAGEMENT =============

    async def update_lead_status(self, lead_id: str, new_status: str, status_notes: str = None) -> Optional[Dict]:
        """Update the status of a lead with optional notes"""
        if not self.client:
            return None

        try:
            update_data = {
                'status': new_status,
                'status_updated_at': 'now()'
            }
            if status_notes:
                update_data['status_notes'] = status_notes

            response = self.client.table('leads').update(update_data).eq('id', lead_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating lead status: {e}")
            return None

    async def save_lead_prediction(self, lead_id: str, predictions: Dict) -> bool:
        """Save predictive analytics for a lead"""
        if not self.client:
            return False

        try:
            # Update lead with predictions
            lead_update = {
                'conversion_probability': predictions.get('conversion_probability'),
                'icp_match_score': predictions.get('icp_match_score'),
                'lead_velocity_score': predictions.get('lead_velocity_score'),
                'recommended_action': predictions.get('recommended_action'),
                'best_contact_time': predictions.get('best_contact_time'),
                'last_prediction_at': 'now()'
            }

            self.client.table('leads').update(lead_update).eq('id', lead_id).execute()

            # Save prediction record
            prediction_record = {
                'lead_id': lead_id,
                'prediction_type': 'conversion',
                'prediction_value': predictions.get('conversion_probability', 0),
                'confidence': predictions.get('confidence', 50),
                'factors': predictions.get('factors', {})
            }

            self.client.table('lead_predictions').insert(prediction_record).execute()
            return True
        except Exception as e:
            print(f"Error saving predictions: {e}")
            return False

    async def save_lead_insight(self, lead_id: str, insight_type: str, insight_text: str, priority: str = 'medium') -> bool:
        """Save an AI-generated insight for a lead"""
        if not self.client:
            return False

        try:
            insight_record = {
                'lead_id': lead_id,
                'insight_type': insight_type,
                'insight_text': insight_text,
                'priority': priority,
                'is_read': False
            }

            self.client.table('lead_insights').insert(insight_record).execute()
            return True
        except Exception as e:
            print(f"Error saving insight: {e}")
            return False

    async def get_lead_insights(self, lead_id: str, unread_only: bool = False) -> List[Dict]:
        """Get insights for a lead"""
        if not self.client:
            return []

        try:
            query = self.client.table('lead_insights').select('*').eq('lead_id', lead_id)

            if unread_only:
                query = query.eq('is_read', False)

            response = query.order('created_at', desc=True).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching insights: {e}")
            return []

    async def track_velocity_change(self, lead_id: str, from_status: str, to_status: str, time_in_hours: float) -> bool:
        """Track lead velocity when status changes"""
        if not self.client:
            return False

        try:
            velocity_record = {
                'lead_id': lead_id,
                'from_status': from_status,
                'to_status': to_status,
                'time_in_status_hours': time_in_hours
            }

            self.client.table('lead_velocity_tracking').insert(velocity_record).execute()
            return True
        except Exception as e:
            print(f"Error tracking velocity: {e}")
            return False

    async def get_lead_velocity_history(self, lead_id: str) -> List[Dict]:
        """Get velocity history for a lead"""
        if not self.client:
            return []

        try:
            response = self.client.table('lead_velocity_tracking')\
                .select('*')\
                .eq('lead_id', lead_id)\
                .order('created_at', desc=False)\
                .execute()

            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching velocity history: {e}")
            return []


# Global instance
db = SupabaseDB()
