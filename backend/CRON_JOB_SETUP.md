# Daily Lead Discovery Cron Job

## ✅ Installed and Running!

A cron job has been set up to automatically discover new leads every day at **9:00 AM**.

## What It Does

Every day at 9 AM, the system will:
1. ✅ Check if the backend is running
2. ✅ Check remaining daily capacity
3. ✅ Generate rotated queries (different from previous days)
4. ✅ Discover new leads from multiple sources
5. ✅ Filter by ICP criteria (score ≥ 70)
6. ✅ Remove duplicates
7. ✅ Add new leads to your database
8. ✅ Log everything to a file

**You don't need to do anything - it runs automatically!**

## Cron Job Details

```bash
# Runs at 9:00 AM every day
0 9 * * * /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/daily_discovery.sh
```

**Schedule Breakdown:**
- `0` - Minute (0 = on the hour)
- `9` - Hour (9 = 9 AM)
- `*` - Day of month (every day)
- `*` - Month (every month)
- `*` - Day of week (every day of week)

## Viewing Logs

Logs are saved to:
```
/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/
```

**View today's log:**
```bash
cat /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/daily_discovery_$(date +%Y-%m-%d).log
```

**View latest log:**
```bash
ls -t /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/daily_discovery_*.log | head -1 | xargs cat
```

**View all recent logs:**
```bash
ls -t /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/daily_discovery_*.log | head -5
```

**Example log output:**
```
================================================================
Daily Lead Discovery - 2025-10-19 09:00:01
================================================================
Checking if backend is running...
✅ Backend is running

📊 Checking current stats...
   Daily Limit: 50
   Already Added Today: 0
   Remaining Capacity: 50

🔍 Starting lead discovery...
   Discovering up to 50 leads...

✅ Discovery completed!

📊 Results:
   Total Discovered: 30
   New Leads Saved: 15
   Duplicates Skipped: 3
   ICP Filtered: 12

🎯 Queries Used:
   Honolulu hotel, Maui resort, Waikiki vacation rental

📈 Updated Stats:
   Total Added Today: 15/50
   Remaining Capacity: 35

🔄 Query Rotation Stats:
   Total Unique Queries Used: 23

================================================================
Summary: Added 15 new high-quality leads
Next run: 2025-10-20 at 09:00 AM
================================================================
```

## Testing the Script Manually

**Run it now (without waiting for 9 AM):**
```bash
cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend
./daily_discovery.sh
```

**Check the output:**
```bash
tail -f logs/daily_discovery_$(date +%Y-%m-%d).log
```

## Managing the Cron Job

### View Current Cron Jobs
```bash
crontab -l
```

### Edit Cron Schedule
```bash
crontab -e
```

**Common schedules:**
```bash
# Every day at 9:00 AM (current)
0 9 * * *

# Every day at 6:00 AM (early morning)
0 6 * * *

# Every day at 9:00 AM and 3:00 PM (twice daily)
0 9,15 * * *

# Every Monday at 9:00 AM (weekly)
0 9 * * 1

# Every 6 hours
0 */6 * * *
```

### Disable the Cron Job (Temporarily)
```bash
crontab -l | sed 's/^0 9 \* \* \*/#0 9 * * */' | crontab -
```
(Adds `#` to comment out the line)

### Enable the Cron Job (Re-enable)
```bash
crontab -l | sed 's/^#0 9 \* \* \*/0 9 * * */' | crontab -
```

### Remove the Cron Job Completely
```bash
crontab -l | grep -v "daily_discovery.sh" | crontab -
```

## Requirements

### 1. Backend Must Be Running

The backend server must be running for the cron job to work:

**Start the backend:**
```bash
cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend
./venv/bin/python main.py &
```

**Check if it's running:**
```bash
curl -s http://localhost:8000/health
```

**Auto-start backend on system boot (optional):**

Create a LaunchAgent (macOS):
```bash
# Create the plist file
cat > ~/Library/LaunchAgents/com.lenilani.backend.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.lenilani.backend</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/venv/bin/python</string>
        <string>/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/main.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/backend.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/backend_error.log</string>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.lenilani.backend.plist
```

### 2. Environment Variables

Make sure your `.env` file is configured:
```bash
cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend
cat .env | grep -E "DAILY_LEAD_LIMIT|ICP_SCORE_THRESHOLD|API_CACHE_TTL_HOURS"
```

Should show:
```
DAILY_LEAD_LIMIT=50
ICP_SCORE_THRESHOLD=70.0
API_CACHE_TTL_HOURS=24
```

## Monitoring

### Quick Status Check
```bash
# Check last run
ls -lt /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/daily_discovery_*.log | head -1

# Check today's results
grep "Summary:" /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/daily_discovery_$(date +%Y-%m-%d).log
```

### Dashboard Commands
```bash
# Check current stats
curl -s http://localhost:8000/api/leads/discovery-stats | python3 -m json.tool

# Check query rotation
curl -s http://localhost:8000/api/leads/query-rotation-stats | python3 -m json.tool

# Check recent leads
curl -s http://localhost:8000/api/leads | python3 -c "import sys, json; leads = json.load(sys.stdin); [print(f\"{l.get('company_name')} - Score: {l.get('score')}\") for l in sorted(leads, key=lambda x: x.get('last_activity_date', ''), reverse=True)[:10]]"
```

### Email Notifications (Optional)

To get email notifications of daily results, modify the script:

```bash
# Add to the end of daily_discovery.sh (before exit 0)

# Email notification (requires mail command)
if command -v mail &> /dev/null; then
    echo "Daily Discovery: Added ${NEW_SAVED} new leads" | mail -s "LeniLani Lead Discovery - $(date +%Y-%m-%d)" your@email.com
fi
```

Or use macOS notifications:
```bash
# Add to the end of daily_discovery.sh (before exit 0)

# macOS notification
osascript -e "display notification \"Added ${NEW_SAVED} new leads\" with title \"LeniLani Lead Discovery\""
```

## Troubleshooting

### Cron job not running

**1. Check if cron is enabled (macOS):**
```bash
sudo launchctl list | grep cron
```

**2. Check cron logs (macOS):**
```bash
log show --predicate 'process == "cron"' --info --last 1h
```

**3. Check script permissions:**
```bash
ls -l /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/daily_discovery.sh
```
Should show: `-rwxr-xr-x` (executable)

**4. Test script manually:**
```bash
/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/daily_discovery.sh
```

### No leads being added

**Check the logs:**
```bash
tail -50 /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/daily_discovery_$(date +%Y-%m-%d).log
```

**Common issues:**
- Daily limit reached (check "Remaining Capacity")
- Backend not running (check "Backend is running" message)
- All sources exhausted (check query rotation stats)
- ICP threshold too high (check filtered count)

### Backend keeps stopping

If the backend keeps stopping, use the LaunchAgent setup above to auto-restart it.

Or use a process manager like `supervisor`:
```bash
# Install supervisor
pip install supervisor

# Create config
cat > supervisord.conf << 'EOF'
[program:lenilani-backend]
command=/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/venv/bin/python main.py
directory=/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend
autostart=true
autorestart=true
stderr_logfile=/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/backend_error.log
stdout_logfile=/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/backend.log
EOF

# Start supervisor
supervisord -c supervisord.conf
```

## Daily Workflow Example

**Set it and forget it:**

1. **Initial Setup** (one time):
   ```bash
   # Start backend
   cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend
   ./venv/bin/python main.py &

   # Verify cron job
   crontab -l
   ```

2. **Daily (automatic)**:
   - 9:00 AM: Cron job runs
   - Script discovers 15-50 new leads
   - Logs saved to `logs/daily_discovery_YYYY-MM-DD.log`

3. **Weekly Review** (manual):
   ```bash
   # Check this week's stats
   for day in {0..6}; do
       date=$(date -v-${day}d +%Y-%m-%d)
       if [ -f logs/daily_discovery_${date}.log ]; then
           echo "=== $date ==="
           grep "Summary:" logs/daily_discovery_${date}.log
       fi
   done
   ```

4. **Monthly Cleanup**:
   - Old logs auto-deleted after 30 days
   - No manual cleanup needed

## Summary

✅ **Installed:** Cron job runs at 9 AM daily
✅ **Automatic:** No manual intervention needed
✅ **Smart:** Uses query rotation to find new leads
✅ **Logged:** All runs saved to log files
✅ **Resilient:** Checks backend status before running

**Next Steps:**
1. Make sure backend is running (or set up auto-start)
2. Check logs tomorrow after 9 AM
3. Review weekly to see your lead pipeline growing!

**Questions?**
- View logs: `cat logs/daily_discovery_$(date +%Y-%m-%d).log`
- Test manually: `./daily_discovery.sh`
- Check cron: `crontab -l`
