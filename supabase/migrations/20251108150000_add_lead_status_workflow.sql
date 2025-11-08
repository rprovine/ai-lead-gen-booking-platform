-- Add new status workflow to leads table
-- This migration adds support for a 5-stage sales pipeline

-- First, let's check if the leads table exists and add status_updated_at column
DO $$
BEGIN
    -- Add status_updated_at column if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'leads' AND column_name = 'status_updated_at') THEN
        ALTER TABLE leads ADD COLUMN status_updated_at TIMESTAMPTZ DEFAULT NOW();
    END IF;

    -- Add status_notes column if it doesn't exist (optional notes for status changes)
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                   WHERE table_name = 'leads' AND column_name = 'status_notes') THEN
        ALTER TABLE leads ADD COLUMN status_notes TEXT;
    END IF;
END $$;

-- Create an index on status for faster filtering
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

-- Create an index on status_updated_at for sorting
CREATE INDEX IF NOT EXISTS idx_leads_status_updated_at ON leads(status_updated_at DESC);

-- Update existing leads with proper status values
-- Map old statuses to new workflow:
-- NEW stays as NEW
-- RESEARCHED becomes CONTACTED (they've been researched/prepared for contact)
-- IN_HUBSPOT becomes QUALIFIED (they're in CRM, so they're qualified)
UPDATE leads
SET status = CASE
    WHEN status = 'RESEARCHED' THEN 'CONTACTED'
    WHEN status = 'IN_HUBSPOT' THEN 'QUALIFIED'
    ELSE status
END
WHERE status IN ('RESEARCHED', 'IN_HUBSPOT');

-- Add comment to document the new status workflow
COMMENT ON COLUMN leads.status IS 'Lead pipeline status: NEW, CONTACTED, QUALIFIED, OPPORTUNITY, WON, LOST';
