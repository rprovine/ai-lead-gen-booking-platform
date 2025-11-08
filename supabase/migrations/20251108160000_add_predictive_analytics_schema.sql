-- Add predictive analytics and AI insights schema
-- This migration adds support for ML-based predictions and scoring

-- Add new columns to leads table for predictions
ALTER TABLE leads ADD COLUMN IF NOT EXISTS conversion_probability DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS icp_match_score DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_velocity_score DECIMAL(5,2) DEFAULT 0.0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS recommended_action TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS best_contact_time TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS last_prediction_at TIMESTAMPTZ;

-- Create lead_score_history table to track score changes over time
CREATE TABLE IF NOT EXISTS lead_score_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    score DECIMAL(5,2) NOT NULL,
    conversion_probability DECIMAL(5,2),
    icp_match_score DECIMAL(5,2),
    lead_velocity_score DECIMAL(5,2),
    factors JSONB,  -- Store contributing factors as JSON
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create lead_predictions table for tracking ML predictions
CREATE TABLE IF NOT EXISTS lead_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    prediction_type TEXT NOT NULL,  -- 'conversion', 'churn_risk', 'engagement', etc.
    prediction_value DECIMAL(5,2) NOT NULL,
    confidence DECIMAL(5,2),
    model_version TEXT,
    factors JSONB,  -- Contributing factors
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ  -- When prediction should be refreshed
);

-- Create lead_velocity_tracking table for pipeline movement analytics
CREATE TABLE IF NOT EXISTS lead_velocity_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    from_status TEXT NOT NULL,
    to_status TEXT NOT NULL,
    time_in_status_hours DECIMAL(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create lead_insights table for AI-generated recommendations
CREATE TABLE IF NOT EXISTS lead_insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lead_id UUID REFERENCES leads(id) ON DELETE CASCADE,
    insight_type TEXT NOT NULL,  -- 'next_action', 'risk_alert', 'opportunity', etc.
    insight_text TEXT NOT NULL,
    priority TEXT DEFAULT 'medium',  -- 'low', 'medium', 'high', 'critical'
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_score_history_lead_id ON lead_score_history(lead_id);
CREATE INDEX IF NOT EXISTS idx_score_history_created_at ON lead_score_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_lead_id ON lead_predictions(lead_id);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON lead_predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_expires ON lead_predictions(expires_at);
CREATE INDEX IF NOT EXISTS idx_velocity_lead_id ON lead_velocity_tracking(lead_id);
CREATE INDEX IF NOT EXISTS idx_insights_lead_id ON lead_insights(lead_id);
CREATE INDEX IF NOT EXISTS idx_insights_priority ON lead_insights(priority);
CREATE INDEX IF NOT EXISTS idx_insights_unread ON lead_insights(is_read) WHERE is_read = FALSE;

-- Add comments for documentation
COMMENT ON COLUMN leads.conversion_probability IS 'ML-predicted probability of lead converting (0-100)';
COMMENT ON COLUMN leads.icp_match_score IS 'How well lead matches ideal customer profile (0-100)';
COMMENT ON COLUMN leads.lead_velocity_score IS 'Speed of lead movement through pipeline (0-100)';
COMMENT ON COLUMN leads.recommended_action IS 'AI-recommended next action for this lead';
COMMENT ON COLUMN leads.best_contact_time IS 'Predicted best time to contact (e.g., "Tue-Thu 2-4pm")';

COMMENT ON TABLE lead_score_history IS 'Historical tracking of lead score changes and contributing factors';
COMMENT ON TABLE lead_predictions IS 'ML model predictions for various lead outcomes';
COMMENT ON TABLE lead_velocity_tracking IS 'Track time spent in each pipeline stage for velocity analytics';
COMMENT ON TABLE lead_insights IS 'AI-generated insights and recommendations for leads';
