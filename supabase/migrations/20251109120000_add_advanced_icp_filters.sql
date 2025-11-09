-- Add advanced filtering capabilities to ICP configuration
-- This includes NAICS codes, SIC codes, technographic data, and firmographic enhancements

-- Add new columns to icp_config table
ALTER TABLE icp_config
ADD COLUMN IF NOT EXISTS naics_codes JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS sic_codes JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS business_models JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS tech_stack JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS required_technologies JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS excluded_technologies JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS ecommerce_platforms JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS crm_systems JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS marketing_automation JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS payment_processors JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS uses_social_media BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS has_mobile_app BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS has_blog BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS is_saas_company BOOLEAN DEFAULT NULL,
ADD COLUMN IF NOT EXISTS funding_stage JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS certifications JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS partnerships JSONB DEFAULT '[]'::jsonb;

-- Add comment to describe the new fields
COMMENT ON COLUMN icp_config.naics_codes IS 'North American Industry Classification System codes for precise industry targeting';
COMMENT ON COLUMN icp_config.sic_codes IS 'Standard Industrial Classification codes for legacy industry targeting';
COMMENT ON COLUMN icp_config.business_models IS 'Business models: B2B, B2C, B2B2C, Marketplace, etc.';
COMMENT ON COLUMN icp_config.tech_stack IS 'Technologies the company uses (programming languages, frameworks, tools)';
COMMENT ON COLUMN icp_config.required_technologies IS 'Technologies that must be present';
COMMENT ON COLUMN icp_config.excluded_technologies IS 'Technologies that should not be present';
COMMENT ON COLUMN icp_config.ecommerce_platforms IS 'Ecommerce platforms: Shopify, WooCommerce, Magento, etc.';
COMMENT ON COLUMN icp_config.crm_systems IS 'CRM systems: Salesforce, HubSpot, Pipedrive, etc.';
COMMENT ON COLUMN icp_config.marketing_automation IS 'Marketing automation tools: Marketo, Pardot, ActiveCampaign, etc.';
COMMENT ON COLUMN icp_config.payment_processors IS 'Payment processors: Stripe, PayPal, Square, etc.';
COMMENT ON COLUMN icp_config.uses_social_media IS 'Filter by social media presence';
COMMENT ON COLUMN icp_config.has_mobile_app IS 'Filter by mobile app availability';
COMMENT ON COLUMN icp_config.has_blog IS 'Filter by blog presence';
COMMENT ON COLUMN icp_config.is_saas_company IS 'Filter for SaaS companies';
COMMENT ON COLUMN icp_config.funding_stage IS 'Funding stages: Seed, Series A, Series B, etc.';
COMMENT ON COLUMN icp_config.certifications IS 'Company certifications: ISO, SOC2, etc.';
COMMENT ON COLUMN icp_config.partnerships IS 'Strategic partnerships or vendor relationships';
