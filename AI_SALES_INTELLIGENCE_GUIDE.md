# AI Sales Intelligence Features Guide

Complete guide to using the three AI-powered sales intelligence features.

---

## Overview

Your platform now has **3 powerful AI features** to supercharge your sales process:

1. **🧠 AI Sales Intelligence** - Detailed analysis when you click on a lead
2. **📄 PDF Sales Playbook** - Professional downloadable sales playbooks
3. **✉️ Smart Email Templates** - Auto-populated emails with AI insights

---

## Feature 1: AI Sales Intelligence 🧠

**Get detailed, actionable sales insights for any lead**

### What You Get:

- **Executive Summary** - Quick snapshot of the opportunity
- **Hot Buttons** (5 items) - Pain points where you can add value
- **Recommended Approach** - Strategic guidance on engagement
- **Talking Points** (6 items) - Specific value propositions
- **Decision Maker Insights** - Who to target, priorities, best contact method
- **Budget Analysis** - Estimated range, investment likelihood
- **Competitive Positioning** - Your advantages vs competitors
- **Appointment Strategy** - Hooks, format, follow-up cadence
- **Next Steps** - Actionable items to move the deal forward

### How to Use:

**API Endpoint:**
```http
POST http://localhost:8000/api/leads/{lead_id}/intelligence
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/leads/lead_1/intelligence"
```

**Response:**
```json
{
  "lead_id": "lead_1",
  "intelligence": {
    "executive_summary": "...",
    "hot_buttons": ["...", "...", "..."],
    "talking_points": ["...", "...", "..."],
    "decision_maker": {
      "target_role": "CEO/Owner",
      "priorities": ["Revenue growth", "Cost reduction"],
      "best_contact": "Email + LinkedIn, mid-morning HST"
    },
    "budget": {
      "estimated_range": "$30,000 - $75,000",
      "investment_likelihood": "High"
    },
    ...
  }
}
```

### When to Use:

- Before reaching out to a lead
- Preparing for sales calls
- Creating personalized outreach
- Building sales presentations
- Team briefings on prospects

---

## Feature 2: PDF Sales Playbook 📄

**Download professional, multi-page sales playbooks**

### What's Included:

**Cover Page:**
- Company name & logo area
- Lead score & key metrics
- Industry, location, size
- Investment likelihood
- LeniLani branding

**Content Sections:**
1. Executive Summary
2. Hot Buttons & Pain Points
3. Recommended Approach
4. Key Talking Points
5. Decision Maker Intelligence
6. Budget Analysis
7. Competitive Positioning
8. Appointment Setting Strategy
9. Next Steps Checklist

### How to Use:

**API Endpoint:**
```http
GET http://localhost:8000/api/leads/{lead_id}/playbook
```

**Download via Browser:**
```
http://localhost:8000/api/leads/lead_1/playbook
```

**Download via Command Line:**
```bash
curl -X GET "http://localhost:8000/api/leads/lead_1/playbook" -o "Sales_Playbook.pdf"
```

**File Name Format:**
```
Sales_Playbook_Aloha_Hotels_&_Resorts.pdf
```

### Use Cases:

- **Sales Team Prep** - Print and bring to meetings
- **CRM Attachment** - Add to HubSpot/Salesforce
- **Email Attachment** - Send to prospects
- **Team Briefings** - Distribute before calls
- **Proposal Appendix** - Include with formal proposals

---

## Feature 3: Smart Email Templates ✉️

**AI-generated emails pre-populated with intelligence data**

### Template Styles:

**1. Professional** (Default)
- Formal tone
- Detailed value propositions
- Specific meeting times
- Company address & contact

**2. Casual**
- Friendly Hawaii "aloha" vibe
- Conversational language
- Coffee chat approach
- Relaxed tone

**3. Consultative**
- Executive-level messaging
- Strategic technology roadmap
- Phased approach
- Budget ranges included

### How to Use:

**API Endpoint:**
```http
POST http://localhost:8000/api/leads/{lead_id}/email-template?template_style={style}
```

**Template Styles:**
- `professional` (default)
- `casual`
- `consultative`

**Examples:**

**Professional Template:**
```bash
curl -X POST "http://localhost:8000/api/leads/lead_1/email-template?template_style=professional"
```

**Casual Template:**
```bash
curl -X POST "http://localhost:8000/api/leads/lead_1/email-template?template_style=casual"
```

**Consultative Template:**
```bash
curl -X POST "http://localhost:8000/api/leads/lead_1/email-template?template_style=consultative"
```

### Response Format:

```json
{
  "lead_id": "lead_1",
  "template_style": "professional",
  "subject": "Transform Aloha Hotels & Resorts's Operations with AI",
  "body": "Dear Decision Maker,\n\nI hope this email finds you well...",
  "intelligence_summary": {
    "hot_buttons": [
      "Digital transformation needs in Tourism & Hospitality",
      "Operational efficiency and cost reduction",
      "Customer experience enhancement"
    ],
    "talking_points": [
      "40%+ efficiency gains for Hawaii tourism businesses",
      "Local team at 1050 Queen Street - in-person collaboration",
      "Proven track record with Hawaii companies"
    ],
    "hook": "Free AI Readiness Assessment ($2,500 value)"
  }
}
```

### Template Comparison:

| Feature | Professional | Casual | Consultative |
|---------|-------------|--------|--------------|
| **Tone** | Formal | Friendly | Executive |
| **Length** | Medium (200-250 words) | Short (100-150 words) | Long (300-350 words) |
| **Best For** | First contact, established companies | Startups, tech companies | Large enterprises, C-suite |
| **Call-to-Action** | Schedule meeting | Coffee chat | Executive briefing |
| **Formality** | High | Low | Very High |

---

## Integration Examples

### Full Workflow

1. **Discover leads** → Get real Hawaii businesses
2. **Click on lead card** → See AI intelligence
3. **Download PDF playbook** → Prepare for outreach
4. **Generate email** → Send personalized message
5. **Book appointment** → Close the deal

### API Workflow (Automated):

```bash
# Step 1: Discover leads
curl -X POST "http://localhost:8000/api/leads/discover"

# Step 2: Get intelligence for lead_1
curl -X POST "http://localhost:8000/api/leads/lead_1/intelligence"

# Step 3: Download PDF playbook
curl -X GET "http://localhost:8000/api/leads/lead_1/playbook" -o "playbook.pdf"

# Step 4: Generate professional email
curl -X POST "http://localhost:8000/api/leads/lead_1/email-template?template_style=professional"

# Step 5: Book appointment (after lead responds)
curl -X POST "http://localhost:8000/api/appointments/book" \
  -H "Content-Type: application/json" \
  -d '{"lead_id":"lead_1", "date_time":"2025-10-25T14:00:00"}'
```

---

## Testing the Features

### Test with API Documentation UI:

1. Go to: http://localhost:8000/docs
2. Find these endpoints:
   - `POST /api/leads/{lead_id}/intelligence`
   - `GET /api/leads/{lead_id}/playbook`
   - `POST /api/leads/{lead_id}/email-template`
3. Click "Try it out"
4. Enter `lead_1` as the lead_id
5. Execute

### Test with Sample Leads:

Your platform has 5 demo leads ready to test:
- `lead_1` - Aloha Hotels & Resorts (Score: 85)
- `lead_2` - Pacific Dental Care (Score: 72)
- `lead_3` - Hawaii Food Distributors (Score: 68)
- `lead_4` - Island Tech Solutions (Score: 78)
- `lead_5` - Kauai Adventure Tours (Score: 81)

---

## Advanced Usage

### Batch Processing:

Generate playbooks for all high-scoring leads:

```bash
#!/bin/bash
# Generate playbooks for all leads with score >= 75

for lead_id in lead_1 lead_4 lead_5; do
  curl -X GET "http://localhost:8000/api/leads/${lead_id}/playbook" \
    -o "Playbook_${lead_id}.pdf"
  echo "Generated playbook for $lead_id"
done
```

### Email Campaign:

Create email templates for different personas:

```bash
# Professional for enterprise clients
curl -X POST "http://localhost:8000/api/leads/lead_1/email-template?template_style=professional" > enterprise_email.json

# Casual for startups
curl -X POST "http://localhost:8000/api/leads/lead_4/email-template?template_style=casual" > startup_email.json

# Consultative for C-suite
curl -X POST "http://localhost:8000/api/leads/lead_1/email-template?template_style=consultative" > executive_email.json
```

---

## Customization Options

### Email Templates

Want to modify the email styles? Edit these functions in `backend/main.py`:
- `_generate_professional_email()` - Line 923
- `_generate_casual_email()` - Line 963
- `_generate_consultative_email()` - Line 990

### PDF Playbook Design

Customize the playbook appearance in `backend/sales_playbook_generator.py`:
- Colors, fonts, layout
- Add your logo
- Custom sections
- Branding elements

### Intelligence Analysis

Modify intelligence generation in `backend/main.py`:
- Class: `SalesIntelligenceAnalyzer` (Line 508)
- Method: `analyze_lead_for_sales()` (Line 528)

---

## Best Practices

### For Sales Teams:

1. **Review Intelligence First** - Always check AI insights before outreach
2. **Customize Templates** - Edit auto-generated emails to add personal touch
3. **Use Appropriate Style** - Match email tone to company culture
4. **Print Playbooks** - Bring physical copies to meetings
5. **Follow Cadence** - Use suggested follow-up timeline

### For Managers:

1. **Train Team** - Show reps how to use all three features
2. **Track Usage** - Monitor which features drive most conversions
3. **A/B Test** - Try different template styles
4. **Feedback Loop** - Update templates based on what works

### For Developers:

1. **Cache Intelligence** - Store generated analysis to avoid re-generating
2. **Batch Operations** - Process multiple leads at once
3. **Error Handling** - Check for 404s on invalid lead_ids
4. **Rate Limiting** - Don't overwhelm the AI APIs

---

## Troubleshooting

### Intelligence Not Generating

**Check:**
- Lead ID exists: `GET /api/leads`
- Claude API key is valid in `.env`
- Backend logs for errors

**Fix:**
```bash
# Verify lead exists
curl http://localhost:8000/api/leads | grep lead_1

# Test Claude connection
curl http://localhost:8000/ | grep claude
```

### PDF Download Fails

**Check:**
- ReportLab installed: `pip list | grep reportlab`
- Sufficient disk space
- Write permissions

**Fix:**
```bash
cd backend
./venv/bin/pip install reportlab
```

### Empty Email Templates

**Check:**
- Intelligence data available
- Template style is valid
- No special characters in company name

**Fix:**
Try different template style or regenerate intelligence first.

---

## Performance Tips

### Speed Up Intelligence Generation:

1. **Enable Caching** - Store generated intelligence
2. **Parallel Processing** - Generate for multiple leads at once
3. **Simplified Analysis** - Reduce AI prompt complexity for faster response

### Optimize PDF Generation:

1. **Remove Images** - Faster generation without logos/graphics
2. **Reduce Sections** - Only include most important parts
3. **Batch Generate** - Create multiple PDFs in one operation

---

## Next Steps

1. ✅ **Test All Three Features** - Try them with demo leads
2. ✅ **Customize Templates** - Edit email styles to match your voice
3. ✅ **Train Your Team** - Show sales reps how to use these tools
4. ✅ **Build UI Modal** - Add click-to-view intelligence in dashboard (coming soon)
5. ✅ **Integrate with CRM** - Push playbooks to HubSpot/Salesforce

---

## Support

**API Documentation:** http://localhost:8000/docs

**Backend:** http://localhost:8000

**Frontend:** http://localhost:3002

---

**Ready to close more deals with AI-powered sales intelligence!** 🚀📊💼
