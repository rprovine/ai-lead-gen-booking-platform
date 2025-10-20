-- Migration: Add HubSpot integration fields to leads table
-- Run this in your Supabase SQL editor: https://supabase.com/dashboard/project/gxooanjnjiharjnnkqvm/sql

-- Add HubSpot tracking columns to leads table
ALTER TABLE leads
ADD COLUMN IF NOT EXISTS hubspot_company_id TEXT,
ADD COLUMN IF NOT EXISTS hubspot_contact_id TEXT,
ADD COLUMN IF NOT EXISTS hubspot_synced_at TIMESTAMP WITH TIME ZONE;

-- Create index for faster HubSpot lookups
CREATE INDEX IF NOT EXISTS idx_leads_hubspot_company_id ON leads(hubspot_company_id);
CREATE INDEX IF NOT EXISTS idx_leads_hubspot_contact_id ON leads(hubspot_contact_id);

-- Add comment to document the fields
COMMENT ON COLUMN leads.hubspot_company_id IS 'HubSpot Company ID after syncing to CRM';
COMMENT ON COLUMN leads.hubspot_contact_id IS 'HubSpot Contact ID for decision maker';
COMMENT ON COLUMN leads.hubspot_synced_at IS 'Timestamp when lead was last synced to HubSpot';

-- Query to check existing synced leads
-- SELECT id, company_name, hubspot_company_id, hubspot_contact_id, hubspot_synced_at
-- FROM leads
-- WHERE hubspot_company_id IS NOT NULL
-- ORDER BY hubspot_synced_at DESC;
