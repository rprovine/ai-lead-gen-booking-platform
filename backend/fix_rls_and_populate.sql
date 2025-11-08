-- Temporarily disable RLS
ALTER TABLE data_sources_config DISABLE ROW LEVEL SECURITY;

-- Insert default data sources
INSERT INTO data_sources_config (organization_id, source_type, source_name, is_enabled, config) VALUES
    ('default', 'anthropic', 'Anthropic Claude AI', false, '{"description": "AI-powered lead intelligence and content generation", "docs_url": "https://console.anthropic.com/", "required_fields": ["api_key"]}'),
    ('default', 'openai', 'OpenAI', false, '{"description": "Embeddings and AI capabilities", "docs_url": "https://platform.openai.com/api-keys", "required_fields": ["api_key"]}'),
    ('default', 'google_ai', 'Google AI (Gemini)', false, '{"description": "Google Gemini AI models", "docs_url": "https://makersuite.google.com/app/apikey", "required_fields": ["api_key"]}'),
    ('default', 'perplexity', 'Perplexity AI', false, '{"description": "Real-time company research and intelligence", "docs_url": "https://www.perplexity.ai/", "required_fields": ["api_key"]}'),
    ('default', 'apollo', 'Apollo.io', false, '{"description": "Decision maker contact finder", "docs_url": "https://apolloio.github.io/apollo-api-docs/", "required_fields": ["api_key"]}'),
    ('default', 'hunter', 'Hunter.io', false, '{"description": "Email finder and verification", "docs_url": "https://hunter.io/api-keys", "required_fields": ["api_key"]}'),
    ('default', 'rocketreach', 'RocketReach', false, '{"description": "Executive contact data", "docs_url": "https://rocketreach.co/api", "required_fields": ["api_key"]}'),
    ('default', 'serpapi', 'SerpAPI', false, '{"description": "Google Maps and business data scraping", "docs_url": "https://serpapi.com/", "required_fields": ["api_key"]}'),
    ('default', 'linkedin', 'LinkedIn API', false, '{"description": "LinkedIn professional data access", "docs_url": "https://developer.linkedin.com/", "required_fields": ["access_token"]}'),
    ('default', 'linkedin_sales_nav', 'LinkedIn Sales Navigator', false, '{"description": "Advanced LinkedIn lead discovery", "docs_url": "https://developer.linkedin.com/", "required_fields": ["api_key"]}'),
    ('default', 'hubspot', 'HubSpot CRM', false, '{"description": "CRM integration for lead management", "docs_url": "https://developers.hubspot.com/", "required_fields": ["api_key"]}'),
    ('default', 'sendgrid', 'SendGrid Email', false, '{"description": "Email outreach automation", "docs_url": "https://sendgrid.com/", "required_fields": ["api_key"]}'),
    ('default', 'twilio', 'Twilio SMS', false, '{"description": "SMS outreach automation", "docs_url": "https://www.twilio.com/", "required_fields": ["account_sid", "auth_token", "phone_number"]}')
ON CONFLICT (organization_id, source_type) DO NOTHING;

-- Drop the existing restrictive policy
DROP POLICY IF EXISTS data_sources_org_policy ON data_sources_config;

-- Create a permissive policy for default organization
CREATE POLICY data_sources_default_org_policy ON data_sources_config
    FOR ALL
    USING (organization_id = 'default')
    WITH CHECK (organization_id = 'default');

-- Re-enable RLS
ALTER TABLE data_sources_config ENABLE ROW LEVEL SECURITY;
