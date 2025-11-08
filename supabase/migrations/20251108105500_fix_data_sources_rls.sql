-- Fix RLS policy for data_sources_config to allow default organization access

-- Drop the existing restrictive policy
DROP POLICY IF EXISTS data_sources_org_policy ON data_sources_config;

-- Create a more permissive policy for the default organization
-- This allows all operations for organization_id = 'default'
CREATE POLICY data_sources_default_org_policy ON data_sources_config
    FOR ALL
    USING (organization_id = 'default')
    WITH CHECK (organization_id = 'default');
