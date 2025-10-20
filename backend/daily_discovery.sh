#!/bin/bash

# Daily Lead Discovery Script
# Automatically discovers new leads based on ICP with query rotation
# Runs daily via cron job

# Configuration
API_URL="http://localhost:8000"
LOG_DIR="/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs"
LOG_FILE="${LOG_DIR}/daily_discovery_$(date +%Y-%m-%d).log"
MAX_LEADS=50

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Start logging
echo "================================================================" >> "$LOG_FILE"
echo "Daily Lead Discovery - $(date)" >> "$LOG_FILE"
echo "================================================================" >> "$LOG_FILE"

# Function to log and display
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Check if backend is running
log "Checking if backend is running..."
if ! curl -s "${API_URL}/health" > /dev/null 2>&1; then
    log "❌ Backend is not running! Please start the backend server."
    log "   Run: cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend && ./venv/bin/python main.py &"
    exit 1
fi

log "✅ Backend is running"
log ""

# Check current discovery stats
log "📊 Checking current stats..."
STATS=$(curl -s "${API_URL}/api/leads/discovery-stats")
REMAINING=$(echo "$STATS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['stats']['today']['remaining_capacity'])" 2>/dev/null || echo "50")
DAILY_LIMIT=$(echo "$STATS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['stats']['today']['daily_limit'])" 2>/dev/null || echo "50")
LEADS_ADDED=$(echo "$STATS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['stats']['today']['leads_added'])" 2>/dev/null || echo "0")

log "   Daily Limit: ${DAILY_LIMIT}"
log "   Already Added Today: ${LEADS_ADDED}"
log "   Remaining Capacity: ${REMAINING}"
log ""

# Check if we have capacity
if [ "$REMAINING" -le 0 ]; then
    log "⚠️  Daily limit already reached (${LEADS_ADDED}/${DAILY_LIMIT})"
    log "   No discovery will be performed today."
    log "   Limit will reset tomorrow."
    exit 0
fi

# Run discovery
log "🔍 Starting lead discovery..."
log "   Discovering up to ${REMAINING} leads..."
log ""

# Make the API call and capture response
RESPONSE=$(curl -s -X POST "${API_URL}/api/leads/discover?max_leads=${REMAINING}")

# Parse discovery results
NEW_SAVED=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('new_leads_saved', 0))" 2>/dev/null || echo "0")

# Run enrichment if we got new leads
if [ "$NEW_SAVED" -gt 0 ]; then
    log ""
    log "💡 Enriching ${NEW_SAVED} new leads with contacts and AI research..."
    log ""

    # Call enrichment API
    ENRICH_RESPONSE=$(curl -s -X POST "${API_URL}/api/leads/enrich-new")

    # Parse enrichment results
    ENRICHED=$(echo "$ENRICH_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('successful', 0))" 2>/dev/null || echo "0")
    ENRICH_FAILED=$(echo "$ENRICH_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('failed', 0))" 2>/dev/null || echo "0")

    log "✅ Enrichment completed!"
    log "   Successfully Enriched: ${ENRICHED}"
    log "   Failed: ${ENRICH_FAILED}"
    log ""
else
    log "⏭️  No new leads to enrich"
    log ""
fi

# Parse response
TOTAL_DISCOVERED=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('total_discovered', 0))" 2>/dev/null || echo "0")
NEW_SAVED=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('new_leads_saved', 0))" 2>/dev/null || echo "0")
DUPLICATES=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('duplicates_skipped', 0))" 2>/dev/null || echo "0")
ICP_FILTERED=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data.get('icp_filtered', 0))" 2>/dev/null || echo "0")

# Get query rotation info
QUERIES_USED=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(', '.join(data.get('query_rotation', {}).get('queries_used', [])))" 2>/dev/null || echo "N/A")

# Display results
log "✅ Discovery completed!"
log ""
log "📊 Results:"
log "   Total Discovered: ${TOTAL_DISCOVERED}"
log "   New Leads Saved: ${NEW_SAVED}"
log "   Duplicates Skipped: ${DUPLICATES}"
log "   ICP Filtered: ${ICP_FILTERED}"
log ""
log "🎯 Queries Used:"
log "   ${QUERIES_USED}"
log ""

# Get updated stats
log "📈 Updated Stats:"
FINAL_STATS=$(curl -s "${API_URL}/api/leads/discovery-stats")
FINAL_ADDED=$(echo "$FINAL_STATS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['stats']['today']['leads_added'])" 2>/dev/null || echo "0")
FINAL_REMAINING=$(echo "$FINAL_STATS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['stats']['today']['remaining_capacity'])" 2>/dev/null || echo "0")

log "   Total Added Today: ${FINAL_ADDED}/${DAILY_LIMIT}"
log "   Remaining Capacity: ${FINAL_REMAINING}"
log ""

# Get query rotation stats
log "🔄 Query Rotation Stats:"
ROTATION_STATS=$(curl -s "${API_URL}/api/leads/query-rotation-stats")
TOTAL_QUERIES=$(echo "$ROTATION_STATS" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['stats']['total_queries_used'])" 2>/dev/null || echo "0")
log "   Total Unique Queries Used: ${TOTAL_QUERIES}"
log ""

# Summary
log "================================================================"
log "Summary: Added ${NEW_SAVED} new high-quality leads"
log "Next run: $(date -v+1d +"%Y-%m-%d at %I:%M %p")"
log "================================================================"

# Keep only last 30 days of logs
find "$LOG_DIR" -name "daily_discovery_*.log" -mtime +30 -delete

exit 0
