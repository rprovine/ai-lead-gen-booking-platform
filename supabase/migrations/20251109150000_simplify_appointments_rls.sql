-- Simplify RLS for appointments - just disable it since we're using single tenant for now
ALTER TABLE appointments DISABLE ROW LEVEL SECURITY;

-- Drop the policy
DROP POLICY IF EXISTS "Allow all for default organization" ON appointments;

-- Update any NULL organization_ids to 'default' for consistency
UPDATE appointments
SET organization_id = 'default'
WHERE organization_id IS NULL;
