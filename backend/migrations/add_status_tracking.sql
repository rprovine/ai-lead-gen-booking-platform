-- Migration: Add Simple Status Tracking
-- Description: Track lead lifecycle status (NEW, RESEARCHED, IN_HUBSPOT)
-- Date: 2025-10-19

-- Note: 'status' column may already exist in leads table (defaulting to 'new')
-- This migration updates it to use proper status values

-- Update status column to use proper enum-style values
-- Convert any existing 'new' values to 'NEW' for consistency
UPDATE leads
SET status = 'NEW'
WHERE status = 'new' OR status IS NULL;

-- Add last_activity_date for sorting/filtering
ALTER TABLE leads
ADD COLUMN IF NOT EXISTS last_activity_date TIMESTAMP DEFAULT NOW();

-- Create index for faster filtering by status
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

-- Create index for last activity date (for sorting)
CREATE INDEX IF NOT EXISTS idx_leads_last_activity ON leads(last_activity_date DESC);

-- Set last_activity_date to created_at for existing leads if null
UPDATE leads
SET last_activity_date = created_at
WHERE last_activity_date IS NULL;

-- Update existing leads with intelligence to RESEARCHED status
UPDATE leads
SET status = 'RESEARCHED',
    last_activity_date = updated_at
WHERE status = 'NEW'
  AND (lead_score IS NOT NULL OR hot_buttons IS NOT NULL);

-- Update existing leads that have been sent to HubSpot
UPDATE leads
SET status = 'IN_HUBSPOT',
    last_activity_date = hubspot_synced_at
WHERE hubspot_company_id IS NOT NULL
  AND status IN ('NEW', 'RESEARCHED');

-- Add comment to status column explaining valid values
COMMENT ON COLUMN leads.status IS 'Lead lifecycle status: NEW (just discovered), RESEARCHED (intelligence generated), IN_HUBSPOT (synced to HubSpot CRM)';
