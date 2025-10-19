-- LeniLani Lead Generation Platform - Supabase Schema
-- Run this SQL in your Supabase SQL Editor

-- Leads table
CREATE TABLE IF NOT EXISTS leads (
    id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    industry TEXT,
    location TEXT,
    employee_count INTEGER,
    website TEXT,
    phone TEXT,
    email TEXT,
    description TEXT,
    pain_points TEXT[], -- Array of pain points
    score INTEGER DEFAULT 0,
    score_explanation TEXT[],
    source TEXT, -- 'linkedin', 'google', 'pacific_business_news', etc.

    -- Contact information (JSONB for flexibility)
    contact_info JSONB DEFAULT '{}',

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Intelligence table (stores generated intelligence for each lead)
CREATE TABLE IF NOT EXISTS lead_intelligence (
    id SERIAL PRIMARY KEY,
    lead_id TEXT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

    -- Intelligence data (stored as JSONB for flexibility)
    intelligence JSONB NOT NULL,

    -- Metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Only one intelligence record per lead (most recent)
    UNIQUE(lead_id)
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    lead_id TEXT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

    -- Appointment details
    date_time TIMESTAMP WITH TIME ZONE NOT NULL,
    location TEXT DEFAULT '1050 Queen Street, Suite 100, Honolulu, HI 96814',
    format TEXT DEFAULT 'in-person', -- 'in-person', 'virtual', 'phone'
    status TEXT DEFAULT 'scheduled', -- 'scheduled', 'completed', 'cancelled', 'no-show'
    notes TEXT,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Outreach history table
CREATE TABLE IF NOT EXISTS outreach (
    id SERIAL PRIMARY KEY,
    lead_id TEXT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,

    -- Outreach details
    channel TEXT NOT NULL, -- 'email', 'sms', 'linkedin', 'phone'
    template_style TEXT, -- 'professional', 'casual', 'consultative'
    subject TEXT,
    content TEXT NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE,

    -- Response tracking
    opened_at TIMESTAMP WITH TIME ZONE,
    replied_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'draft', -- 'draft', 'sent', 'opened', 'replied', 'bounced'

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC);
CREATE INDEX IF NOT EXISTS idx_leads_industry ON leads(industry);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_appointments_date_time ON appointments(date_time);
CREATE INDEX IF NOT EXISTS idx_appointments_lead_id ON appointments(lead_id);
CREATE INDEX IF NOT EXISTS idx_outreach_lead_id ON outreach(lead_id);
CREATE INDEX IF NOT EXISTS idx_outreach_sent_at ON outreach(sent_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to leads table
DROP TRIGGER IF EXISTS update_leads_updated_at ON leads;
CREATE TRIGGER update_leads_updated_at
    BEFORE UPDATE ON leads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to appointments table
DROP TRIGGER IF EXISTS update_appointments_updated_at ON appointments;
CREATE TRIGGER update_appointments_updated_at
    BEFORE UPDATE ON appointments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS)
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_intelligence ENABLE ROW LEVEL SECURITY;
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach ENABLE ROW LEVEL SECURITY;

-- Create policies (allow all operations for now - you can restrict later)
CREATE POLICY "Allow all operations on leads" ON leads FOR ALL USING (true);
CREATE POLICY "Allow all operations on lead_intelligence" ON lead_intelligence FOR ALL USING (true);
CREATE POLICY "Allow all operations on appointments" ON appointments FOR ALL USING (true);
CREATE POLICY "Allow all operations on outreach" ON outreach FOR ALL USING (true);

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

-- Sample query to verify setup
-- SELECT * FROM leads ORDER BY created_at DESC LIMIT 10;
-- SELECT * FROM campaigns ORDER BY created_at DESC;
