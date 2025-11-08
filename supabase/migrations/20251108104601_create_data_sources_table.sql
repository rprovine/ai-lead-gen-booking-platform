-- Create data_sources_config table to store user/organization data source configurations
-- This allows users to configure which data sources they want to use and provide their own API keys

CREATE TABLE IF NOT EXISTS data_sources_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default', -- For multi-tenant support
    source_type TEXT NOT NULL, -- e.g., 'apollo', 'hunter', 'perplexity', etc.
    source_name TEXT NOT NULL, -- Display name
    is_enabled BOOLEAN NOT NULL DEFAULT false,
    api_key TEXT, -- Encrypted API key (we'll encrypt in app layer)
    api_secret TEXT, -- For sources that need secret
    config JSONB DEFAULT '{}', -- Additional config like account_sid for Twilio
    last_tested_at TIMESTAMPTZ,
    test_status TEXT, -- 'success', 'failed', 'not_tested'
    test_message TEXT, -- Result message from last test
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id, source_type)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_data_sources_org ON data_sources_config(organization_id);
CREATE INDEX IF NOT EXISTS idx_data_sources_enabled ON data_sources_config(organization_id, is_enabled);

-- Add RLS (Row Level Security) for multi-tenant support
ALTER TABLE data_sources_config ENABLE ROW LEVEL SECURITY;

-- Create policy to allow users to manage their own organization's data sources
CREATE POLICY data_sources_org_policy ON data_sources_config
    FOR ALL
    USING (organization_id = current_setting('app.current_org_id', true)::text);

-- Insert default data source definitions for reference
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

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_data_sources_updated_at BEFORE UPDATE ON data_sources_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
