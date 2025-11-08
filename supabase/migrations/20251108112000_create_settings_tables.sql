-- Create comprehensive settings tables for the platform

-- 1. Business Profile
CREATE TABLE IF NOT EXISTS business_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default',
    company_name TEXT,
    industry TEXT,
    description TEXT,
    products_services TEXT,
    value_proposition TEXT,
    typical_deal_size TEXT,
    sales_cycle_length TEXT,
    key_differentiators TEXT,
    case_studies TEXT,
    website TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id)
);

-- 2. ICP (Ideal Customer Profile) Configuration
CREATE TABLE IF NOT EXISTS icp_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default',
    profile_name TEXT NOT NULL DEFAULT 'Default ICP',
    is_active BOOLEAN NOT NULL DEFAULT true,

    -- Company Demographics
    employee_count_min INTEGER,
    employee_count_max INTEGER,
    annual_revenue_min BIGINT,
    annual_revenue_max BIGINT,
    company_age_min INTEGER,
    company_age_max INTEGER,
    company_types JSONB DEFAULT '[]'::jsonb,

    -- Industry Targeting
    industries JSONB DEFAULT '[]'::jsonb,
    sub_industries JSONB DEFAULT '[]'::jsonb,
    industry_keywords JSONB DEFAULT '[]'::jsonb,
    excluded_industries JSONB DEFAULT '[]'::jsonb,

    -- Geographic Criteria
    target_countries JSONB DEFAULT '["US"]'::jsonb,
    target_states JSONB DEFAULT '["HI"]'::jsonb,
    target_cities JSONB DEFAULT '[]'::jsonb,
    target_zip_codes JSONB DEFAULT '[]'::jsonb,

    -- Decision Maker Profile
    decision_maker_titles JSONB DEFAULT '[]'::jsonb,
    decision_maker_seniority JSONB DEFAULT '[]'::jsonb,
    decision_maker_departments JSONB DEFAULT '[]'::jsonb,
    multiple_decision_makers BOOLEAN DEFAULT false,

    -- Behavioral Signals
    recently_funded BOOLEAN DEFAULT false,
    actively_hiring BOOLEAN DEFAULT false,
    recent_tech_adoption BOOLEAN DEFAULT false,
    expanding_locations BOOLEAN DEFAULT false,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id, profile_name)
);

-- 3. Lead Generation Preferences
CREATE TABLE IF NOT EXISTS lead_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default',
    leads_per_batch INTEGER DEFAULT 50,
    min_lead_score INTEGER DEFAULT 70,
    refresh_frequency TEXT DEFAULT 'weekly',
    quality_vs_quantity INTEGER DEFAULT 70,
    excluded_companies JSONB DEFAULT '[]'::jsonb,
    excluded_domains JSONB DEFAULT '[]'::jsonb,
    include_competitors BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id)
);

-- 4. Search & Discovery Settings
CREATE TABLE IF NOT EXISTS search_discovery_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default',
    priority_keywords JSONB DEFAULT '[]'::jsonb,
    priority_websites JSONB DEFAULT '["pacificbusinessnews.com", "hawaiibusiness.com"]'::jsonb,
    search_territories JSONB DEFAULT '["Hawaii"]'::jsonb,
    social_platforms JSONB DEFAULT '["linkedin"]'::jsonb,
    news_sources JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id)
);

-- 5. Notification Settings
CREATE TABLE IF NOT EXISTS notification_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default',
    email_enabled BOOLEAN DEFAULT true,
    email_address TEXT,
    new_lead_alerts BOOLEAN DEFAULT true,
    lead_score_threshold INTEGER DEFAULT 80,
    digest_frequency TEXT DEFAULT 'daily',
    slack_webhook TEXT,
    teams_webhook TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id)
);

-- 6. Integration Settings
CREATE TABLE IF NOT EXISTS integration_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default',
    crm_type TEXT DEFAULT 'none',
    crm_auto_sync BOOLEAN DEFAULT false,
    export_format TEXT DEFAULT 'csv',
    webhook_url TEXT,
    calendar_integration BOOLEAN DEFAULT false,
    calendar_type TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id)
);

-- 7. AI Personalization Settings
CREATE TABLE IF NOT EXISTS ai_personalization_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id TEXT NOT NULL DEFAULT 'default',
    tone TEXT DEFAULT 'professional',
    research_depth TEXT DEFAULT 'standard',
    preferred_model TEXT DEFAULT 'claude-sonnet',
    custom_prompt_template TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(organization_id)
);

-- Create RLS policies for all tables
ALTER TABLE business_profile ENABLE ROW LEVEL SECURITY;
ALTER TABLE icp_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_discovery_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_personalization_settings ENABLE ROW LEVEL SECURITY;

-- RLS Policies for default organization
CREATE POLICY business_profile_default_org_policy ON business_profile
    FOR ALL USING (organization_id = 'default') WITH CHECK (organization_id = 'default');

CREATE POLICY icp_config_default_org_policy ON icp_config
    FOR ALL USING (organization_id = 'default') WITH CHECK (organization_id = 'default');

CREATE POLICY lead_preferences_default_org_policy ON lead_preferences
    FOR ALL USING (organization_id = 'default') WITH CHECK (organization_id = 'default');

CREATE POLICY search_discovery_default_org_policy ON search_discovery_settings
    FOR ALL USING (organization_id = 'default') WITH CHECK (organization_id = 'default');

CREATE POLICY notification_settings_default_org_policy ON notification_settings
    FOR ALL USING (organization_id = 'default') WITH CHECK (organization_id = 'default');

CREATE POLICY integration_settings_default_org_policy ON integration_settings
    FOR ALL USING (organization_id = 'default') WITH CHECK (organization_id = 'default');

CREATE POLICY ai_personalization_default_org_policy ON ai_personalization_settings
    FOR ALL USING (organization_id = 'default') WITH CHECK (organization_id = 'default');

-- Create updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
CREATE TRIGGER update_business_profile_updated_at BEFORE UPDATE ON business_profile
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_icp_config_updated_at BEFORE UPDATE ON icp_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lead_preferences_updated_at BEFORE UPDATE ON lead_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_search_discovery_updated_at BEFORE UPDATE ON search_discovery_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_notification_settings_updated_at BEFORE UPDATE ON notification_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integration_settings_updated_at BEFORE UPDATE ON integration_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ai_personalization_updated_at BEFORE UPDATE ON ai_personalization_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
