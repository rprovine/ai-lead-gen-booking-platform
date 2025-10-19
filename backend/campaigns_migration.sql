-- Campaigns Migration - Run this in Supabase SQL Editor
-- This adds campaigns functionality to your existing database

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,

    -- Target filters (JSONB for flexibility)
    target_filters JSONB DEFAULT '{}', -- {industry: "Tourism", min_score: 75, max_score: 100}

    -- Campaign settings
    channels TEXT[] DEFAULT ARRAY['email'], -- ['email', 'sms', 'linkedin']
    status TEXT DEFAULT 'draft', -- 'draft', 'active', 'paused', 'completed'

    -- Statistics
    total_leads INTEGER DEFAULT 0,
    contacted_leads INTEGER DEFAULT 0,
    opened_count INTEGER DEFAULT 0,
    replied_count INTEGER DEFAULT 0,
    converted_count INTEGER DEFAULT 0,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Campaign-Lead relationship (many-to-many)
CREATE TABLE IF NOT EXISTS campaign_leads (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    lead_id TEXT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

    -- Status tracking
    status TEXT DEFAULT 'pending', -- 'pending', 'contacted', 'opened', 'replied', 'converted', 'skipped'

    -- Timing
    contacted_at TIMESTAMP WITH TIME ZONE,
    opened_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,
    converted_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Unique constraint: one entry per campaign-lead pair
    UNIQUE(campaign_id, lead_id)
);

-- Campaign sequences (email/SMS/LinkedIn templates and timing)
CREATE TABLE IF NOT EXISTS campaign_sequences (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,

    -- Sequence settings
    sequence_number INTEGER NOT NULL, -- 1 = initial, 2 = first follow-up, etc.
    channel TEXT NOT NULL, -- 'email', 'sms', 'linkedin'
    delay_days INTEGER DEFAULT 0, -- Days after previous step (0 for initial)

    -- Template content
    subject TEXT, -- For email
    content TEXT NOT NULL,
    template_style TEXT DEFAULT 'professional', -- 'professional', 'casual', 'consultative'

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure sequences are ordered
    UNIQUE(campaign_id, sequence_number, channel)
);

-- Create indexes for campaigns
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_campaign_leads_campaign_id ON campaign_leads(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_leads_lead_id ON campaign_leads(lead_id);
CREATE INDEX IF NOT EXISTS idx_campaign_leads_status ON campaign_leads(status);
CREATE INDEX IF NOT EXISTS idx_campaign_sequences_campaign_id ON campaign_sequences(campaign_id);

-- Apply triggers to campaigns tables
DROP TRIGGER IF EXISTS update_campaigns_updated_at ON campaigns;
CREATE TRIGGER update_campaigns_updated_at
    BEFORE UPDATE ON campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_campaign_leads_updated_at ON campaign_leads;
CREATE TRIGGER update_campaign_leads_updated_at
    BEFORE UPDATE ON campaign_leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS for campaigns tables
ALTER TABLE campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE campaign_sequences ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Allow all operations on campaigns" ON campaigns FOR ALL USING (true);
CREATE POLICY "Allow all operations on campaign_leads" ON campaign_leads FOR ALL USING (true);
CREATE POLICY "Allow all operations on campaign_sequences" ON campaign_sequences FOR ALL USING (true);
