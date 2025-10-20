#!/bin/bash

echo "=================================="
echo "HubSpot Integration Setup"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    exit 1
fi

# Check current HubSpot API key
CURRENT_KEY=$(grep "HUBSPOT_API_KEY=" .env | cut -d '=' -f2)

if [ "$CURRENT_KEY" = "your_key_here" ] || [ -z "$CURRENT_KEY" ]; then
    echo "⚠️  HubSpot API key not configured yet"
    echo ""
    echo "Please enter your HubSpot API key"
    echo "(You can use the same key from your tourism bot or business intelligence tool)"
    echo ""
    read -p "HubSpot API Key: " HUBSPOT_KEY

    if [ -z "$HUBSPOT_KEY" ]; then
        echo "❌ No key provided. Exiting."
        exit 1
    fi

    # Update .env file
    sed -i.bak "s/HUBSPOT_API_KEY=.*/HUBSPOT_API_KEY=$HUBSPOT_KEY/" .env
    echo "✓ Updated .env file with HubSpot API key"
else
    echo "✓ HubSpot API key already configured: ${CURRENT_KEY:0:20}..."
fi

echo ""
echo "=================================="
echo "Step 1: Database Migration"
echo "=================================="
echo ""
echo "Please run the following SQL in your Supabase dashboard:"
echo ""
echo "URL: https://supabase.com/dashboard/project/gxooanjnjiharjnnkqvm/sql"
echo ""
echo "------- Copy the SQL below -------"
cat migrations/add_hubspot_fields.sql
echo "-----------------------------------"
echo ""
read -p "Press Enter after you've run the SQL migration in Supabase..."

echo ""
echo "=================================="
echo "Step 2: Testing Integration"
echo "=================================="
echo ""

# Test HubSpot API key
echo "Testing HubSpot API connection..."
HUBSPOT_KEY=$(grep "HUBSPOT_API_KEY=" .env | cut -d '=' -f2)

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X GET \
  "https://api.hubapi.com/crm/v3/objects/companies?limit=1" \
  -H "Authorization: Bearer $HUBSPOT_KEY")

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ HubSpot API key is valid!"
else
    echo "❌ HubSpot API key test failed (HTTP $HTTP_CODE)"
    echo "Please check your API key at: https://app.hubspot.com/settings/account/integrations/api-keys"
    exit 1
fi

echo ""
echo "=================================="
echo "Step 3: Restart Backend Server"
echo "=================================="
echo ""

# Check if backend is running
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Stopping current backend server..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
fi

echo "Starting backend server..."
./venv/bin/python main.py &
BACKEND_PID=$!
sleep 5

if ps -p $BACKEND_PID > /dev/null; then
    echo "✓ Backend server started (PID: $BACKEND_PID)"
else
    echo "❌ Failed to start backend server"
    exit 1
fi

echo ""
echo "=================================="
echo "Step 4: Running Test Script"
echo "=================================="
echo ""

# Run test script
./venv/bin/python test_hubspot_integration.py

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Your HubSpot integration is now ready to use."
echo ""
echo "Next steps:"
echo "1. Discover leads: POST /api/leads/discover"
echo "2. Generate intelligence: POST /api/leads/{lead_id}/intelligence"
echo "3. Send to HubSpot: POST /api/leads/{lead_id}/send-to-hubspot"
echo ""
echo "See HUBSPOT_SETUP_README.md for more details."
echo ""
