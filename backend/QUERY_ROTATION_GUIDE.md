# Query Rotation & Anti-Duplication Guide

## The Problem You Described

> "I need to get new leads daily based around my ICP without duplicates and without rerunning the same parameters every single time"

**Before Query Rotation:**
```
Day 1: Search "Hawaii hospitality" → Get 30 companies → Add 10 new
Day 2: Search "Hawaii hospitality" → Get 30 companies → 28 duplicates, 2 new ❌
Day 3: Search "Hawaii hospitality" → Get 30 companies → 30 duplicates, 0 new ❌
```

**After Query Rotation:**
```
Day 1: Search "Honolulu hotel" → Get 30 companies → Add 10 new ✅
Day 2: Search "Maui resort" → Get 25 companies → Add 8 new ✅
Day 3: Search "Waikiki boutique hotel" → Get 20 companies → Add 6 new ✅
```

## How Query Rotation Works

### 1. Query Diversification

Instead of using the same search terms every time, the system **automatically rotates** through variations:

**Example: Hospitality Industry**

```
Run 1: "Honolulu hotel"
Run 2: "Maui resort"
Run 3: "Waikiki vacation rental"
Run 4: "Lahaina bed and breakfast"
Run 5: "Kailua-Kona inn"
Run 6: "Hilo boutique hotel"
...and so on through 100+ variations
```

**Example: Healthcare Industry**

```
Run 1: "Honolulu medical clinic"
Run 2: "Maui dental office"
Run 3: "Oahu physical therapy"
Run 4: "Kauai wellness center"
Run 5: "Big Island urgent care"
...
```

### 2. Query Tracking

The system remembers which queries have been used:

```json
{
  "queries_used": [
    {"query": "Honolulu hotel", "used_at": "2025-10-19T10:00:00"},
    {"query": "Maui resort", "used_at": "2025-10-19T15:00:00"},
    {"query": "Waikiki vacation rental", "used_at": "2025-10-20T09:00:00"}
  ]
}
```

**Won't repeat queries within 7 days** - ensures truly new searches every day.

### 3. Source Exhaustion Tracking

Tracks how many duplicates each source returns:

```json
{
  "source_exhaustion": {
    "google_maps": 45.2,    // 45% duplicates - still good
    "yelp": 78.5,           // 78% duplicates - getting exhausted
    "linkedin": 23.1        // 23% duplicates - fresh source
  }
}
```

When a source hits **80% exhaustion**, it's temporarily skipped (24 hours) to save API costs.

### 4. Industry & Location Rotation

Rotates through keywords within each industry:

**Hospitality Keywords (12 variations):**
- hotel → resort → vacation rental → bed and breakfast → inn → lodge → hostel → accommodation → boutique hotel → luxury resort → beachfront hotel → timeshare

**Rotation Example:**
```
Day 1: Use keyword #1 "hotel"
Day 2: Use keyword #2 "resort"
Day 3: Use keyword #3 "vacation rental"
...
Day 12: Use keyword #12 "timeshare"
Day 13: Back to keyword #1 "hotel" (but with different location)
```

## Daily Discovery Flow

### Day 1: First Discovery

```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality&max_leads=30"
```

**What Happens:**
1. Query Manager generates: `["Honolulu hotel", "Maui resort", "Waikiki vacation rental"]`
2. Searches Google Maps, Yelp, LinkedIn with these queries
3. Finds 30 companies
4. Filters duplicates: 0 (first run)
5. **Adds 15 new leads** (15 passed ICP threshold)
6. Tracks queries as used

**Response:**
```json
{
  "new_leads_saved": 15,
  "query_rotation": {
    "queries_used": ["Honolulu hotel", "Maui resort", "Waikiki vacation rental"],
    "total_unique_queries": 3
  }
}
```

### Day 2: Next Discovery (Same Parameters)

```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality&max_leads=30"
```

**What Happens:**
1. Query Manager sees `["Honolulu hotel", "Maui resort", "Waikiki vacation rental"]` were used
2. **Generates NEW queries:** `["Lahaina bed and breakfast", "Kailua-Kona inn", "Hilo boutique hotel"]`
3. Searches with DIFFERENT queries
4. Finds 25 companies (different from Day 1)
5. Filters duplicates: 3 (overlap with Day 1)
6. **Adds 12 new leads**

**Response:**
```json
{
  "new_leads_saved": 12,
  "query_rotation": {
    "queries_used": ["Lahaina bed and breakfast", "Kailua-Kona inn", "Hilo boutique hotel"],
    "total_unique_queries": 6
  }
}
```

### Day 3: Same Parameters Again

```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality&max_leads=30"
```

**What Happens:**
1. Query Manager rotates to: `["Oahu accommodation", "Maui luxury resort", "Kauai beachfront hotel"]`
2. Searches with COMPLETELY DIFFERENT queries
3. Finds 20 companies
4. Filters duplicates: 5
5. **Adds 10 new leads**

**Pattern:** Each day uses **different queries** even with same user parameters.

## Query Rotation Strategies

### Strategy 1: Industry Focus (User Specifies Industry)

```bash
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```

**Rotation Pattern:**
- Day 1: Honolulu hotels
- Day 2: Maui resorts
- Day 3: Waikiki vacation rentals
- Day 4: Kauai bed and breakfasts
- Day 5: Big Island inns
- Day 6: Oahu hostels
- Day 7: Lahaina lodges
- ...

**Total Combinations:** 18 locations × 12 keywords = **216 unique queries**

### Strategy 2: Location Focus (User Specifies Island)

```bash
curl -X POST "http://localhost:8000/api/leads/discover?island=Maui"
```

**Rotation Pattern:**
- Day 1: Maui hotels
- Day 2: Maui restaurants
- Day 3: Maui medical clinics
- Day 4: Maui shops
- Day 5: Maui spas
- Day 6: Maui tour operators
- ...

**Total Combinations:** 9 industries × 12 keywords = **108 unique queries** (for Maui alone)

### Strategy 3: No Filters (Maximum Diversity)

```bash
curl -X POST "http://localhost:8000/api/leads/discover?max_leads=30"
```

**Rotation Pattern:**
- Randomly selects 3 industries and 2 locations each run
- Maximum variety to discover different types of businesses
- Day 1: Honolulu hotels + Maui restaurants
- Day 2: Kauai clinics + Oahu shops
- Day 3: Waikiki spas + Hilo contractors
- ...

**Total Combinations:** 18 locations × 9 industries × 12 keywords = **1,944 unique queries**

## Preventing Repeated API Calls

### Problem: Wasted API Calls

**Before:**
```
Day 1: SerpAPI search "Hawaii hotels" → Cost: $0.05 → 30 results
Day 2: SerpAPI search "Hawaii hotels" → Cost: $0.05 → 30 results (SAME!) ❌
Day 3: SerpAPI search "Hawaii hotels" → Cost: $0.05 → 30 results (SAME!) ❌

Total Cost: $0.15 for 30 unique companies (wasted $0.10)
```

**After:**
```
Day 1: SerpAPI search "Honolulu hotel" → Cost: $0.05 → 30 results
Day 2: SerpAPI search "Maui resort" → Cost: $0.05 → 25 NEW results ✅
Day 3: SerpAPI search "Waikiki vacation rental" → Cost: $0.05 → 20 NEW results ✅

Total Cost: $0.15 for 75 unique companies (3x more efficient!)
```

### How It Works

1. **Query Deduplication:**
   - Checks if query was used in last 7 days
   - Skips if yes, generates alternative

2. **Source Exhaustion:**
   - Tracks duplicate rate per source
   - Temporarily skips exhausted sources (>80% duplicates)

3. **Company Memory:**
   - Remembers all companies seen across sessions
   - Filters at query time (before API call when possible)

4. **Intelligent Rotation:**
   - Prioritizes less-searched locations
   - Rotates through industry keywords
   - Combines for maximum variety

## Monitoring Query Rotation

### Check Current Stats

```bash
curl http://localhost:8000/api/leads/query-rotation-stats
```

**Response:**
```json
{
  "stats": {
    "total_queries_used": 23,
    "recent_queries": [
      "Honolulu hotel",
      "Maui resort",
      "Waikiki vacation rental",
      "Lahaina bed and breakfast",
      "Kailua-Kona inn"
    ],
    "source_exhaustion": {
      "discovery_service": 35.2,
      "google_maps": 45.1,
      "yelp": 52.3
    },
    "industry_rotation": {
      "hospitality": 3,
      "healthcare": 1,
      "restaurant": 2
    }
  }
}
```

**What This Means:**
- Used 23 unique queries total
- Currently on keyword #3 for hospitality
- Google Maps is 45% exhausted (still good)
- Yelp is 52% exhausted (getting tired)

### View Discovery Results

After each discovery, response includes rotation info:

```json
{
  "new_leads_saved": 12,
  "query_rotation": {
    "queries_used": ["Honolulu hotel", "Maui resort"],
    "locations_searched": ["Honolulu", "Maui"],
    "industries_searched": ["hospitality"],
    "total_unique_queries": 15
  }
}
```

## Example: 30-Day Discovery Plan

### Goal: Add 50 leads per day without duplicates

**Week 1: Hospitality Focus**
```bash
# Day 1-7: Rotate through hospitality variations
curl -X POST "http://localhost:8000/api/leads/discover?industry=hospitality"
```

**Week 2: Healthcare Focus**
```bash
# Day 8-14: Rotate through healthcare variations
curl -X POST "http://localhost:8000/api/leads/discover?industry=healthcare"
```

**Week 3: Professional Services**
```bash
# Day 15-21: Rotate through professional services
curl -X POST "http://localhost:8000/api/leads/discover?industry=professional_services"
```

**Week 4: Island-by-Island**
```bash
# Day 22-24: Oahu across all industries
curl -X POST "http://localhost:8000/api/leads/discover?island=Oahu"

# Day 25-27: Maui across all industries
curl -X POST "http://localhost:8000/api/leads/discover?island=Maui"

# Day 28-30: Kauai across all industries
curl -X POST "http://localhost:8000/api/leads/discover?island=Kauai"
```

**Result:**
- **1,500 leads** added (50/day × 30 days)
- **90+ unique queries** used
- **Minimal duplicates** (<5% due to rotation)
- **Optimized API costs** (no repeated searches)

## State Files

The system maintains two state files:

### 1. `query_rotation_state.json`

Tracks query usage and rotation:

```json
{
  "queries_used": [
    {"query": "Honolulu hotel", "used_at": "2025-10-19T10:00:00"},
    {"query": "Maui resort", "used_at": "2025-10-19T15:00:00"}
  ],
  "source_exhaustion": {
    "google_maps": 45.2,
    "yelp": 52.3
  },
  "industry_rotation": {
    "hospitality": 3,
    "healthcare": 1
  },
  "location_rotation": {
    "honolulu": 2,
    "maui": 1
  }
}
```

### 2. `discovery_state.json`

Tracks companies and daily limits:

```json
{
  "seen_companies": ["aloha hotel", "maui resort"],
  "filtered_companies": ["small shop"],
  "daily_stats": {
    "2025-10-19": {
      "leads_added": 50,
      "api_calls": 15
    }
  }
}
```

## Best Practices

### ✅ DO

1. **Run discovery daily with same parameters**
   - System auto-rotates queries
   - No need to manually vary parameters

2. **Monitor query rotation stats**
   - Check which queries are being used
   - Verify rotation is happening

3. **Let the system exhaust sources naturally**
   - Don't manually skip sources
   - System auto-manages exhaustion

4. **Use broad parameters initially**
   - `industry=hospitality` better than `business_type=hotel`
   - Allows more rotation options

### ❌ DON'T

1. **Don't manually change parameters daily**
   - System does this automatically
   - Manual changes can disrupt rotation

2. **Don't worry about duplicates**
   - System aggressively filters duplicates
   - Query rotation minimizes them anyway

3. **Don't reset state files frequently**
   - Query rotation needs history to work
   - Only reset if corrupted

4. **Don't run discovery multiple times per day with same params**
   - Daily limit exists for a reason
   - Query rotation is daily, not hourly

## Troubleshooting

### Issue: Getting too many duplicates

**Cause:** Source exhaustion - same sources returning same results

**Solution:**
```bash
# Check source exhaustion
curl http://localhost:8000/api/leads/query-rotation-stats

# If a source is >80% exhausted, it will auto-skip for 24 hours
# OR manually vary your parameters:
curl -X POST "http://localhost:8000/api/leads/discover?island=Maui"  # Try different island
curl -X POST "http://localhost:8000/api/leads/discover?industry=healthcare"  # Try different industry
```

### Issue: Not enough new leads daily

**Cause:** Running out of query variations for narrow parameters

**Solutions:**
1. Use broader parameters (remove island filter)
2. Alternate between industries daily
3. Increase daily limit if hitting cap early

### Issue: Query rotation not working

**Check:**
```bash
# View rotation stats
curl http://localhost:8000/api/leads/query-rotation-stats

# Should show increasing total_queries_used each run
# recent_queries should show different queries each time
```

If `total_queries_used` isn't increasing, check:
- State file permissions (`query_rotation_state.json`)
- Server logs for errors
- Query manager initialization

## Summary

### What This Solves

✅ **No repeated searches** - Each discovery uses different queries
✅ **No wasted API calls** - Avoids fetching same data
✅ **Continuous fresh leads** - Automatic rotation ensures variety
✅ **Source exhaustion handling** - Skips tired sources
✅ **Duplicate prevention** - Multi-level deduplication
✅ **Cost optimization** - Smart query management

### How It Works

1. **Query Generation:** Creates diverse queries from templates
2. **Query Tracking:** Remembers what's been used (7-day window)
3. **Query Rotation:** Cycles through variations automatically
4. **Source Tracking:** Monitors duplicate rates per source
5. **Intelligent Skipping:** Avoids exhausted sources temporarily

### The Result

You can run the **exact same discovery command every day** and get:
- Different queries each time
- Fresh leads each time
- Minimal duplicates
- Optimized API usage

**No manual intervention required** - the system handles everything automatically!
