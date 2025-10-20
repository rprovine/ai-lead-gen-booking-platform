# How Smart Discovery Works - Simple Explanation

## Your Request

> "I need to get new leads daily based on my ICP without duplicates and without rerunning the same parameters every single time"

## The Solution: Automatic Query Rotation + Smart Deduplication

### BEFORE (Old System)

**Day 1:**
```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```
→ Searches: "Hawaii hospitality"
→ Finds: 30 companies
→ Adds: 15 new leads ✅

**Day 2:** (You run the SAME command)
```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```
→ Searches: "Hawaii hospitality" (SAME QUERY!) ❌
→ Finds: 30 companies (SAME COMPANIES!) ❌
→ Adds: 2 new leads (28 duplicates skipped)
→ **WASTED API CALLS** ❌

**Day 3:** (You run the SAME command again)
```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```
→ Searches: "Hawaii hospitality" (SAME QUERY AGAIN!) ❌
→ Finds: 30 companies (ALL DUPLICATES!) ❌
→ Adds: 0 new leads
→ **MORE WASTED API CALLS** ❌

**Problem:** Running same searches repeatedly = mostly duplicates + wasted money

---

### AFTER (New Smart System)

**Day 1:**
```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```
→ System auto-generates: `["Honolulu hotel", "Maui resort"]`
→ Finds: 30 companies
→ Adds: 15 new leads ✅
→ Tracks: "Used query: Honolulu hotel, Maui resort"

**Day 2:** (You run the EXACT SAME command)
```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```
→ System sees previous queries were used
→ System auto-generates NEW queries: `["Waikiki vacation rental", "Lahaina bed and breakfast"]` ✅
→ Finds: 25 DIFFERENT companies ✅
→ Adds: 12 new leads ✅
→ Tracks: "Used query: Waikiki vacation rental, Lahaina bed and breakfast"

**Day 3:** (You run the EXACT SAME command again)
```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```
→ System sees both previous sets of queries
→ System auto-generates MORE NEW queries: `["Kailua-Kona inn", "Hilo boutique hotel"]` ✅
→ Finds: 20 DIFFERENT companies ✅
→ Adds: 10 new leads ✅
→ Tracks: "Used query: Kailua-Kona inn, Hilo boutique hotel"

**Result:** Same command, different searches every day = always fresh leads! ✅

---

## What You Need to Do

### NOTHING DIFFERENT!

Just run your discovery like normal:

```bash
# Run this EVERY DAY - system handles the rest!
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality&max_leads=30"
```

**The system automatically:**
1. ✅ Generates different search queries each day
2. ✅ Avoids repeating queries used in last 7 days
3. ✅ Rotates through 200+ query variations
4. ✅ Filters out companies already in your database
5. ✅ Filters out companies seen in previous discoveries
6. ✅ Skips companies that didn't meet ICP criteria before
7. ✅ Enforces daily lead limits
8. ✅ Tracks source exhaustion (skips sources with >80% duplicates)

---

## Example: 7-Day Discovery Schedule

**You run the SAME command every day:**

```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```

**Behind the scenes, system uses DIFFERENT queries:**

| Day | Your Command | System Auto-Uses | Results |
|-----|-------------|------------------|---------|
| Mon | `industry=hospitality` | "Honolulu hotel" | 15 new leads |
| Tue | `industry=hospitality` | "Maui resort" | 12 new leads |
| Wed | `industry=hospitality` | "Waikiki vacation rental" | 10 new leads |
| Thu | `industry=hospitality` | "Lahaina bed and breakfast" | 13 new leads |
| Fri | `industry=hospitality` | "Kailua-Kona inn" | 11 new leads |
| Sat | `industry=hospitality` | "Hilo boutique hotel" | 9 new leads |
| Sun | `industry=hospitality` | "Oahu luxury resort" | 12 new leads |

**Total: 82 NEW leads from 7 days using the SAME command** ✅

---

## How Deduplication Works (3 Levels)

### Level 1: Database Deduplication
Checks against your existing leads before adding:
- Company name (normalized)
- Website URL (normalized)
- Phone number (last 10 digits)

**Example:**
```
New: "Apple Inc" → Normalized: "apple"
Existing: "Apple" → Normalized: "apple"
→ DUPLICATE - SKIP ✅
```

### Level 2: Session Memory
Remembers companies discovered in previous sessions:

**Day 1:**
- Discovers: "Aloha Hotel"
- Saves to: `seen_companies`

**Day 2:**
- Discovers: "Aloha Hotel" again
- Checks: `seen_companies` → Found!
- → SKIP (already discovered before) ✅

### Level 3: ICP Filtering Memory
Remembers companies that didn't meet ICP criteria:

**Day 1:**
- Discovers: "Small Laundromat" (ICP score: 45)
- Below threshold (70)
- Saves to: `filtered_companies`

**Day 2:**
- Discovers: "Small Laundromat" again
- Checks: `filtered_companies` → Found!
- → SKIP (didn't qualify before) ✅

---

## Query Rotation Details

### What Gets Rotated

**Industry Keywords:** 12 variations per industry
```
hospitality: hotel → resort → vacation rental → bed and breakfast → inn → lodge → hostel → accommodation → boutique hotel → luxury resort → beachfront hotel → timeshare
```

**Locations:** 18 Hawaii locations
```
Honolulu → Oahu → Maui → Kauai → Big Island → Waikiki → Lahaina → Kailua-Kona → Hilo → Kihei → Waipahu → Pearl City → Kaneohe → Kapolei → Aiea → Mililani → Kahului → Hawaii Island
```

**Modifiers:** 10 modifiers
```
business → company → service → provider → professional → local → island → hawaiian → best → top rated
```

**Total Possible Queries:** 18 × 12 × 10 = **2,160 unique queries** per industry!

### Rotation Logic

1. **First Run:** Uses location #1 + keyword #1
2. **Second Run:** Uses location #2 + keyword #2
3. **Third Run:** Uses location #3 + keyword #3
4. Continues rotating through all combinations
5. **Won't repeat same query for 7 days**
6. **Prioritizes less-used combinations**

---

## Checking It's Working

### View Query Rotation Stats

```bash
curl http://localhost:8000/api/leads/query-rotation-stats
```

**Response shows:**
```json
{
  "stats": {
    "total_queries_used": 15,
    "recent_queries": [
      "Honolulu hotel",
      "Maui resort",
      "Waikiki vacation rental",
      "Lahaina bed and breakfast",
      "Kailua-Kona inn"
    ],
    "source_exhaustion": {
      "discovery_service": 25.5
    }
  }
}
```

**What to look for:**
- ✅ `total_queries_used` should INCREASE each day
- ✅ `recent_queries` should show DIFFERENT queries
- ✅ `source_exhaustion` should stay below 80%

### Discovery Response Shows Rotation

Every discovery response includes:

```json
{
  "new_leads_saved": 12,
  "query_rotation": {
    "queries_used": ["Honolulu hotel", "Maui resort"],
    "total_unique_queries": 15
  }
}
```

**Shows you exactly which queries were used this time!**

---

## Source Exhaustion Protection

System tracks how many duplicates each source returns:

**Example:**
```
Google Maps:
  - Day 1: 30 results, 5 duplicates = 17% exhaustion ✅
  - Day 2: 30 results, 15 duplicates = 50% exhaustion ⚠️
  - Day 3: 30 results, 25 duplicates = 83% exhaustion ❌

→ Day 4: System SKIPS Google Maps (too exhausted)
→ Day 5: After 24 hours, exhaustion resets to 41.5%
→ Day 5: System uses Google Maps again ✅
```

**This prevents wasting API calls on sources that keep returning the same companies!**

---

## Cost Savings Example

### Before (Without Query Rotation)

**30 Days of Discovery:**
```
Day 1:  SerpAPI call: "Hawaii hotel" → $0.05 → 30 results (15 new)
Day 2:  SerpAPI call: "Hawaii hotel" → $0.05 → 30 results (2 new) ❌
Day 3:  SerpAPI call: "Hawaii hotel" → $0.05 → 30 results (0 new) ❌
Day 4:  SerpAPI call: "Hawaii hotel" → $0.05 → 30 results (0 new) ❌
...
Day 30: SerpAPI call: "Hawaii hotel" → $0.05 → 30 results (0 new) ❌

Total Cost: 30 × $0.05 = $1.50
Total New Leads: ~20 leads
Cost Per Lead: $0.075
```

### After (With Query Rotation)

**30 Days of Discovery:**
```
Day 1:  SerpAPI call: "Honolulu hotel" → $0.05 → 30 results (15 new) ✅
Day 2:  SerpAPI call: "Maui resort" → $0.05 → 25 results (12 new) ✅
Day 3:  SerpAPI call: "Waikiki vacation rental" → $0.05 → 20 results (10 new) ✅
Day 4:  SerpAPI call: "Lahaina bed and breakfast" → $0.05 → 18 results (9 new) ✅
...
Day 30: SerpAPI call: "Hilo boutique hotel" → $0.05 → 15 results (8 new) ✅

Total Cost: 30 × $0.05 = $1.50
Total New Leads: ~300 leads
Cost Per Lead: $0.005
```

**15x more efficient!** ✅

---

## Summary

### What Changed

| Feature | Before | After |
|---------|--------|-------|
| **Daily Queries** | Same query every day | Auto-rotated queries |
| **Duplicate Rate** | 80-90% after Day 2 | <10% every day |
| **New Leads/Day** | 15 → 2 → 0 → 0... | 15 → 12 → 10 → 13... |
| **API Efficiency** | Very low | Very high |
| **Manual Work** | Change params daily | None - fully automatic |

### Your Workflow

**BEFORE:**
```
Day 1: Discover hospitality
Day 2: Manually change to restaurants
Day 3: Manually change to healthcare
Day 4: Manually change to retail
...
```

**AFTER:**
```
Every Day: Run same command
           System handles rotation automatically
```

### The Result

✅ **Run the same discovery command every day**
✅ **Get different results every day**
✅ **No duplicates**
✅ **No repeated API calls**
✅ **No manual parameter changes**
✅ **Complete automation**

---

## Quick Start

**Just run this every day:**

```bash
# For hospitality leads
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality&max_leads=30"

# For healthcare leads
curl -X POST "http://localhost:8000/api/leads/discover?industry=healthcare&max_leads=30"

# For all industries (maximum variety)
curl -X POST "http://localhost:8000/api/leads/discover?max_leads=50"
```

**The system does everything else automatically!**

Check your results:
```bash
curl http://localhost:8000/api/leads/query-rotation-stats
```

That's it! 🎉
