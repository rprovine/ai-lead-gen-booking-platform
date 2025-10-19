# Supabase Setup Guide

## ✅ Completed Steps

1. ✅ Installed Supabase Python client
2. ✅ Created Supabase project: `lenilani-lead-gen`
3. ✅ Created database schema (supabase_schema.sql)
4. ✅ Created database integration layer (database.py)
5. ✅ Created LeniLani content scraper (lenilani_scraper.py)

## 🔧 Remaining Setup Steps

### Step 1: Get Your Supabase API Key

1. Go to: https://supabase.com/dashboard/project/gxooanjnjiharjnnkqvm/settings/api

2. Copy the **anon/public** key (looks like: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

3. Open `backend/.env` and replace:
   ```
   SUPABASE_KEY=your_anon_key_here
   ```
   with your actual key:
   ```
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

### Step 2: Run the Database Schema

1. Go to: https://supabase.com/dashboard/project/gxooanjnjiharjnnkqvm/editor

2. Click **SQL Editor** in the left sidebar

3. Open the file `backend/supabase_schema.sql`

4. Copy all the SQL code

5. Paste it into the Supabase SQL Editor

6. Click **Run** (or press Cmd+Enter)

7. You should see: "Success. No rows returned"

### Step 3: Verify Tables Created

Go to **Table Editor** and you should see these tables:
- ✅ leads
- ✅ lead_intelligence
- ✅ appointments
- ✅ outreach

## 📊 What This Gives You

### Persistent Storage
- **Leads stay saved** even when backend restarts
- Query by industry, score, location
- Full history of all discovered leads

### AI Intelligence Storage
- Each lead's AI-generated intelligence is saved
- No need to regenerate intelligence every time
- Fast retrieval for PDF playbooks

### Appointment Tracking
- All booked meetings saved
- Track status (scheduled, completed, cancelled)
- Link appointments to leads

### Outreach History
- Track all emails, SMS, LinkedIn messages
- See what was sent and when
- Monitor open/reply rates

### Analytics
- Real-time dashboard metrics
- Lead conversion funnel
- Performance tracking

## 🌐 LeniLani Content Integration

The `lenilani_scraper.py` module will:
1. **Load your website content** from www.lenilani.com
2. **Extract company data:**
   - Services offered
   - Team information
   - Case studies
   - Value propositions
   - Contact details
3. **Use in AI prompts** for personalized intelligence and outreach

This ensures all sales intelligence references YOUR actual services, case studies, and value props!

## 🚀 Next Steps

Once you've:
1. Added the Supabase key to `.env`
2. Run the SQL schema

I'll integrate it into the backend so:
- Discovered leads are saved to Supabase
- Intelligence is cached in database
- You can restart the backend without losing data
- Dashboard loads real data from database

## 🔍 Testing

After setup, test with:
```bash
# 1. Restart backend
cd backend
./venv/bin/python main.py

# 2. Discover leads
curl -X POST http://localhost:8000/api/leads/discover

# 3. Check Supabase dashboard - you should see leads in the table!
```

## 💡 Benefits

**Before (In-Memory):**
- ❌ Leads lost on restart
- ❌ No historical data
- ❌ Can't query or filter
- ❌ No analytics tracking

**After (Supabase):**
- ✅ Persistent storage
- ✅ Full history
- ✅ Advanced queries
- ✅ Real-time analytics
- ✅ Scales to millions of leads
- ✅ Automatic backups

---

**Ready to complete setup? Just add the API key and run the SQL!**
