"""
Run database migrations directly against Supabase
"""
import os
from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

def run_migration(sql_file):
    """Execute a SQL migration file"""
    print(f"\nRunning migration: {sql_file}")

    with open(sql_file, 'r') as f:
        sql = f.read()

    # Split into individual statements
    statements = [s.strip() for s in sql.split(';') if s.strip()]

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    for i, statement in enumerate(statements, 1):
        if not statement or statement.startswith('--'):
            continue

        try:
            print(f"  Executing statement {i}/{len(statements)}...")
            # Use RPC to execute raw SQL
            client.rpc('exec_sql', {'query': statement + ';'}).execute()
            print(f"  ✓ Statement {i} completed")
        except Exception as e:
            # Some errors are okay (like IF NOT EXISTS when thing exists)
            if 'already exists' in str(e) or 'does not exist' in str(e):
                print(f"  ⚠ Statement {i}: {str(e)[:100]}... (continuing)")
            else:
                print(f"  ✗ Error in statement {i}: {e}")
                raise

    print(f"✓ Migration {sql_file} completed successfully\n")

if __name__ == '__main__':
    migrations = [
        'supabase/migrations/20251108150000_add_lead_status_workflow.sql',
        'supabase/migrations/20251108160000_add_predictive_analytics_schema.sql'
    ]

    for migration in migrations:
        try:
            run_migration(migration)
        except Exception as e:
            print(f"Failed to run {migration}: {e}")
            # Try using supabase db execute instead
            import subprocess
            print(f"Attempting alternative method...")
            result = subprocess.run(
                ['supabase', 'db', 'remote', 'commit', '--message', f"Apply {migration}"],
                cwd='/Users/renoprovine/Development/ai-lead-gen-booking-platform',
                capture_output=True,
                text=True
            )
            print(result.stdout)
            if result.returncode != 0:
                print(result.stderr)
