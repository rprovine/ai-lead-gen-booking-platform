-- Migration: Add decision_makers, email_pattern, and status columns to leads table
-- Date: 2025-10-19
-- Purpose: Store contact enrichment data directly on lead records

-- Add decision_makers column (JSONB array of executive contacts)
ALTER TABLE leads ADD COLUMN IF NOT EXISTS decision_makers JSONB DEFAULT '[]';

-- Add email_pattern column (for domain email format like "{first}.{last}")
ALTER TABLE leads ADD COLUMN IF NOT EXISTS email_pattern TEXT;

-- Add status column to track lead lifecycle
ALTER TABLE leads ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'NEW';

-- Add last_activity_date to track enrichment/updates
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_activity_date TIMESTAMP WITH TIME ZONE;

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

-- Create index on last_activity_date
CREATE INDEX IF NOT EXISTS idx_leads_last_activity ON leads(last_activity_date DESC);

-- Add comment explaining decision_makers structure
COMMENT ON COLUMN leads.decision_makers IS 'JSONB array of executive contacts with structure: [{"name": "John Doe", "title": "CEO", "email": "john@company.com", "phone": "+1-808-555-1234", "linkedin": "https://linkedin.com/in/johndoe", "confidence": 0.95, "source": "hunter.io"}]';

-- Add comment explaining status values
COMMENT ON COLUMN leads.status IS 'Lead lifecycle status: NEW (discovered), RESEARCHED (enriched with contacts/AI), IN_HUBSPOT (pushed to HubSpot), ARCHIVED (not pursuing)';
