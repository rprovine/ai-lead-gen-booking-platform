-- Disable RLS temporarily to update all appointments
ALTER TABLE appointments DISABLE ROW LEVEL SECURITY;

-- Update ALL existing appointments to have organization_id = 'default'
UPDATE appointments
SET organization_id = 'default'
WHERE organization_id IS NULL;

-- Re-enable RLS
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Verify the policy exists
DROP POLICY IF EXISTS "Allow all for default organization" ON appointments;
CREATE POLICY "Allow all for default organization" ON appointments
    FOR ALL
    USING (organization_id = 'default');
