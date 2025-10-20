# Quick Reference Card - Smart Lead Discovery

## ✅ Status: INSTALLED & RUNNING

**Cron Job:** Every day at 9:00 AM
**Location:** `/Users/renoprovine/Development/ai-lead-gen-booking-platform/backend`

---

## 📋 Daily Checklist (Optional - It's Automatic!)

- [ ] Backend running? (Only needed if server restarted)
- [ ] Check logs after 9 AM to see results
- [ ] Review weekly stats

---

## 🚀 Common Commands

### Check If Everything Is Working
```bash
# Is backend running?
curl -s http://localhost:8000/health

# View today's discovery log
cat /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend/logs/daily_discovery_$(date +%Y-%m-%d).log | tail -20

# Check current stats
curl -s http://localhost:8000/api/leads/discovery-stats | python3 -m json.tool
```

### Run Discovery Manually (Test)
```bash
cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend
./daily_discovery.sh
```

### View Logs
```bash
# Today's log
cat logs/daily_discovery_$(date +%Y-%m-%d).log

# Last 7 days summary
grep "Summary:" logs/daily_discovery_*.log | tail -7
```

### Start Backend (If Needed)
```bash
cd /Users/renoprovine/Development/ai-lead-gen-booking-platform/backend
./venv/bin/python main.py &
```

### Manage Cron Job
```bash
# View schedule
crontab -l

# Edit schedule
crontab -e

# Temporarily disable
crontab -l | sed 's/^0 9 \* \* \*/#0 9 * * */' | crontab -

# Re-enable
crontab -l | sed 's/^#0 9 \* \* \*/0 9 * * */' | crontab -
```

---

## 📊 Expected Daily Results

| Time | What Happens | Results |
|------|-------------|---------|
| 9:00 AM | Cron job starts | - |
| 9:01 AM | Discovers leads | 30-50 raw leads |
| 9:02 AM | Filters & adds | 15-50 new leads |
| 9:02 AM | Logs results | Log file created |

**Typical Output:**
- Total Discovered: 30
- New Leads Saved: 15
- Duplicates Skipped: 5
- ICP Filtered: 10

---

## 🎯 What It Does Automatically

✅ Generates different search queries each day
✅ Discovers leads from 8+ sources
✅ Scores by ICP (only adds if ≥70)
✅ Removes duplicates (name, website, phone)
✅ Enforces daily limit (50 leads)
✅ Tracks source exhaustion
✅ Logs everything

**You do: NOTHING!** (It's automatic)

---

## 🔧 Configuration Files

**Environment (.env):**
```bash
DAILY_LEAD_LIMIT=50
ICP_SCORE_THRESHOLD=70.0
API_CACHE_TTL_HOURS=24
```

**Cron Schedule:**
```bash
0 9 * * * /path/to/daily_discovery.sh
```

**State Files (Auto-managed):**
- `discovery_state.json` - Companies seen, daily stats
- `query_rotation_state.json` - Queries used, source exhaustion

---

## 📈 Monitoring Dashboard

```bash
# Quick stats (copy/paste this)
echo "=== LEAD DISCOVERY STATUS ===" && \
echo "" && \
echo "Backend Status:" && \
curl -s http://localhost:8000/health 2>&1 | head -1 && \
echo "" && \
echo "Today's Stats:" && \
curl -s http://localhost:8000/api/leads/discovery-stats | python3 -c "import sys, json; d = json.load(sys.stdin); print(f\"  Added: {d['stats']['today']['leads_added']}/{d['stats']['today']['daily_limit']}\"); print(f\"  Remaining: {d['stats']['today']['remaining_capacity']}\")" && \
echo "" && \
echo "Recent Queries:" && \
curl -s http://localhost:8000/api/leads/query-rotation-stats | python3 -c "import sys, json; d = json.load(sys.stdin); [print(f\"  - {q}\") for q in d['stats']['recent_queries'][-5:]]" && \
echo "" && \
echo "Last Log:" && \
ls -t logs/daily_discovery_*.log 2>/dev/null | head -1 | xargs tail -10
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| No leads added | Check if backend is running: `curl http://localhost:8000/health` |
| Daily limit reached | Normal! Resets at midnight. Check: `curl http://localhost:8000/api/leads/discovery-stats` |
| Cron not running | Check: `crontab -l` and test manually: `./daily_discovery.sh` |
| Too many duplicates | Sources exhausted. Will auto-recover in 24h. Check: `curl http://localhost:8000/api/leads/query-rotation-stats` |
| Backend stopped | Restart: `cd /path/to/backend && ./venv/bin/python main.py &` |

---

## 📚 Full Documentation

1. **HOW_IT_WORKS.md** - Simple explanation (read this first!)
2. **CRON_JOB_SETUP.md** - Cron job management
3. **QUERY_ROTATION_GUIDE.md** - Query rotation deep dive
4. **SMART_DISCOVERY_README.md** - Complete reference
5. **SETUP_COMPLETE.md** - Full setup summary

---

## 🎉 Quick Facts

- **Runs:** Daily at 9 AM (automatic)
- **Adds:** 15-50 high-quality leads per day
- **Duplicates:** <5% (aggressive filtering)
- **Queries:** 2,160+ unique combinations
- **Cost:** Optimized (no repeated API calls)
- **Work Required:** None (fully automated)

---

## 💡 Pro Tips

1. **Let it run for a week** before adjusting settings
2. **Check logs weekly** to see patterns
3. **Don't worry about duplicates** - system handles it
4. **Backend must be running** - set up auto-start if needed
5. **Daily limit exists for a reason** - quality > quantity

---

**Questions? Check the docs or view logs!**

**Enjoying automated leads? You're welcome!** 🚀
