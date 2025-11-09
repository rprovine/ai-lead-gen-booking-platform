# LeniLani Lead Generation & Appointment Booking Platform

AI-powered lead discovery, qualification, and appointment booking system for LeniLani Consulting, specializing in Hawaii-based businesses.

## Features

### Lead Discovery & Enrichment
- **Smart Query Rotation**: Intelligent search query rotation system that cycles through multiple variations to discover diverse leads
- **Automated Lead Discovery**: AI-powered web scraping to find Hawaii businesses needing tech services
- **ICP Management**: Define and manage your Ideal Customer Profile with smart targeting
- **Lead Enrichment Pipeline**: Automated workflow to enrich leads with Perplexity research and AI-generated playbooks
- **Intelligent Lead Scoring**: LangChain agents score leads based on multiple factors
- **5-Stage Sales Pipeline**: Track leads through NEW → CONTACTED → QUALIFIED → OPPORTUNITY → WON/LOST lifecycle with visual status management

### Settings & Configuration 🆕
- **Business Profile**: Configure your company information, value proposition, and sales cycle
- **ICP Builder**: Create detailed ideal customer profiles with comprehensive targeting criteria:
  - **Basic Demographics**: Employee count, revenue, company age, industries, geography
  - **Industry Classification**: NAICS codes and SIC codes for precise industry targeting
  - **Business Models**: Filter by B2B, B2C, B2B2C, Marketplace, SaaS models
  - **Technographic Filters**: Target by tech stack, required/excluded technologies
  - **Platform Usage**: Filter by ecommerce platforms, CRM systems, marketing automation, payment processors
  - **Digital Presence**: Social media, mobile apps, blogs, SaaS designation
  - **Company Stage**: Funding rounds, certifications (ISO, SOC2), strategic partnerships
  - **Decision Makers**: Titles, seniority levels, departments, multiple decision maker criteria
- **Lead Preferences**: Set batch sizes, scoring thresholds, and quality vs quantity preferences
- **Search & Discovery**: Configure search keywords, priority websites, and territories
- **Data Source Management**: Manage API keys for 13+ external data sources (Apollo, Hunter, Perplexity, etc.)
- **Notifications**: Email and Slack alerts for new high-score leads
- **Integrations**: CRM auto-sync, export formats, and webhook configurations
- **AI Personalization**: Customize AI tone, research depth, and model preferences

### Pipeline Management & Analytics 🆕
- **Lead Detail Views**: Comprehensive lead information modal showing company details, decision makers, pain points, and tech stack
- **Visual Status Workflow**: Drag-and-drop status updates with dropdown controls on each lead card
- **Stage Filtering**: Filter leads by pipeline stage (All, New, Contacted, Qualified, Opportunity, Won, Lost)
- **Pipeline Analytics Dashboard**: Real-time metrics showing:
  - Lead count and percentage for each pipeline stage
  - Win rate (Won / Total Closed deals)
  - Stage-to-stage conversion rates
  - Active pipeline count (leads in progress)
  - Visual funnel with progress bars for each conversion stage
- **Status History**: Track status changes with timestamps and optional notes
- **Performance Metrics**: Monitor qualification rates, opportunity conversion, and overall pipeline health

### AI-Powered Intelligence
- **Perplexity AI Research**: Real-time company intelligence from the past 90 days (news, leadership, market position)
- **Enhanced Contact Finding**: Multi-source decision maker discovery using Apollo.io, Hunter.io, Perplexity AI, and Google Search
- **PDF Sales Playbooks**: Professional downloadable playbooks with AI insights and Perplexity research
- **AI Insights**: Claude-powered sales intelligence with actionable recommendations

### AI Predictive Analytics 🆕
- **Conversion Probability Predictions**: Gemini 2.5 Flash AI analyzes leads to predict likelihood of conversion (0-100%)
- **ICP Match Scoring**: Intelligent scoring (0-100%) showing how well leads align with your Ideal Customer Profile
- **Pipeline Velocity Tracking**: Monitor time spent in each pipeline stage and identify bottlenecks
- **Conversion Factors Analysis**: Detailed breakdown of positive and negative factors affecting conversion probability
- **ICP Matching Insights**: View specific factors that match or miss your ICP criteria
- **Recommended Actions**: AI-powered next steps with priority levels, timing guidance, and reasoning
- **Best Contact Times**: Intelligent recommendations for optimal outreach timing based on lead characteristics
- **Dual Prediction Model**: Primary Gemini AI analysis with rule-based fallback for consistent predictions
- **Workflow Integration**: Predictions available only after AI Intelligence generation to ensure data quality

### Outreach & CRM
- **Smart Email Templates**: Auto-generated emails in professional, casual, or consultative styles
- **Personalized Outreach**: Generate custom emails, SMS, and LinkedIn messages using Claude/Gemini
- **Smart Appointment Booking**: Automated scheduling at your Honolulu office (1050 Queen Street, Suite 100)
- **Multi-Channel Campaigns**: Email, SMS, and LinkedIn outreach orchestration
- **HubSpot Integration**: Automatic CRM synchronization with leads, contacts, companies, and formatted intelligence notes

### Campaign Management 🆕
- **Automated Multi-Touch Outreach**: Create campaigns to contact multiple leads simultaneously with AI-personalized messaging
- **Multi-Channel Support**: Orchestrate outreach across email, SMS, and LinkedIn in unified campaigns
- **Smart Targeting**: Filter leads by industry, score range, and other ICP criteria for precise campaign targeting
- **Campaign Status Tracking**: Monitor campaigns through draft, active, paused, and completed states
- **Performance Analytics**: Track total leads, contacted count, opens, replies, and conversions for each campaign
- **AI Personalization**: Each lead receives personalized messaging based on their intelligence data and company profile
- **Guided Workflow**: Clear explanatory UI showing benefits, workflow steps, and prerequisites for successful campaigns

### Analytics & Automation
- **Real-time Analytics**: Dashboard showing leads, conversions, and revenue potential
- **Automated Daily Discovery**: Cron job system for hands-free lead generation
- **Database Migration Tools**: Easy schema updates and data management

## Tech Stack

**Backend:**
- FastAPI (Python)
- LangChain (Claude 3.5 Sonnet, Gemini, OpenAI)
- Gemini 2.5 Flash for predictive analytics
- Supabase (PostgreSQL)
- Perplexity AI (Sonar Pro) for research
- ReportLab for PDF generation
- Redis (optional)
- Celery for background tasks (optional)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Framer Motion

**Integrations:**
- Anthropic Claude API (3.5 Sonnet)
- Perplexity AI (Sonar Pro - research & contact discovery)
- Google Gemini API
- OpenAI API
- SerpAPI (Google Maps/Business data)
- Google Custom Search API (Contact discovery)
- Apollo.io (Decision maker contact finder)
- Hunter.io (Email finder & verification)
- RocketReach (Executive contact data)
- HubSpot (Full CRM sync with contacts, companies, and notes)
- SendGrid (Email - optional)
- Twilio (SMS - optional)
- Google Calendar API (optional)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (optional)
- API keys (see [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md))

### Option 1: Local Development (Recommended for getting started)

#### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ai-lead-gen-booking-platform
```

#### 2. Set up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.template .env
# Edit .env and add your API keys (see API_KEYS_GUIDE.md)

# Run the backend
python main.py
```

Backend will be available at http://localhost:8000

#### 3. Set up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
# .env.local is already created with the correct API URL

# Run the development server
npm run dev
```

Frontend will be available at http://localhost:3000

#### 4. Access the Dashboard

Open your browser to http://localhost:3000 and you'll see the LeniLani Lead Generation Platform dashboard!

### Option 2: Docker Compose (For production-like environment)

```bash
# Make sure your API keys are set in the .env file
docker-compose up -d

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Configuration

### Required API Keys

**Minimum setup (to get started):**
1. ANTHROPIC_API_KEY - Get from https://console.anthropic.com/
2. GOOGLE_AI_API_KEY - Get from https://makersuite.google.com/app/apikey
3. OPENAI_API_KEY - Get from https://platform.openai.com/api-keys

**Optional (for full functionality):**
- SENDGRID_API_KEY - For email outreach
- TWILIO credentials - For SMS outreach
- HUBSPOT_API_KEY - For CRM integration
- Firebase credentials - For persistent storage

See [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md) for detailed setup instructions.

### Environment Variables

Edit `backend/.env`:

```bash
# AI/ML APIs (Required)
ANTHROPIC_API_KEY=sk-ant-your-key-here
GOOGLE_AI_API_KEY=AIza-your-key-here
OPENAI_API_KEY=sk-your-key-here

# Email (Optional)
SENDGRID_API_KEY=SG.your-key-here

# SMS (Optional)
TWILIO_ACCOUNT_SID=AC-your-sid-here
TWILIO_AUTH_TOKEN=your-token-here
TWILIO_PHONE_NUMBER=+1808XXXXXXX

# CRM (Optional)
HUBSPOT_API_KEY=pat-na1-your-key-here

# Database (Optional - uses in-memory by default)
DATABASE_URL=postgresql://postgres:password@localhost:5432/lenilani_leads
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json

# Office Address
OFFICE_ADDRESS=1050 Queen Street, Suite 100, Honolulu, HI 96814
```

## Usage

### 1. Discover Leads

Click the **"Discover New Leads"** button in the dashboard. The AI will:
- Use smart query rotation to search for diverse Hawaii businesses
- Analyze their websites for opportunities
- Score each lead based on multiple factors
- Find decision maker contact information from multiple sources
- Display them in your pipeline

### 2. Manage Pipeline Status

Use the visual pipeline controls to move leads through your sales funnel:
- **NEW**: Recently discovered leads
- **CONTACTED**: Leads you've reached out to
- **QUALIFIED**: Leads that meet your ICP criteria
- **OPPORTUNITY**: Active deals in progress
- **WON**: Successfully closed deals
- **LOST**: Deals that didn't close

Update status using the dropdown on each lead card or filter by stage using the tabs.

### 3. Enrich Leads

The enrichment pipeline automatically:
- Conducts Perplexity AI research on each company
- Finds decision maker contacts (Apollo, Hunter, Perplexity, Google)
- Generates personalized PDF sales playbooks
- Creates AI-powered sales intelligence

### 4. Sync to HubSpot

Send enriched leads to HubSpot CRM:
- Creates/updates contact records for decision makers
- Creates/updates company records
- Adds formatted intelligence notes with research
- Links to downloadable PDF playbooks

### 5. Generate Outreach

For each lead, you can:
- Click the email icon to generate a personalized email
- Click the SMS icon to generate a text message
- Review and edit the AI-generated content
- Send directly through the platform

### 6. Generate Predictive Analytics

After generating AI Intelligence for a lead, click the **"Predict"** button to get comprehensive analytics:
- **Conversion Probability**: AI-powered prediction of likelihood to convert (0-100%)
- **Conversion Factors**: Detailed positive and negative factors affecting conversion
- **ICP Match Score**: How well the lead aligns with your Ideal Customer Profile (0-100%)
- **ICP Insights**: Specific matching and missing factors for your ICP criteria
- **Pipeline Velocity**: Time spent in pipeline and velocity score
- **Recommended Action**: AI-suggested next steps with priority, timing, and reasoning
- **Best Contact Time**: Optimal time windows for outreach based on lead profile

The Predict button is only available after AI Intelligence has been generated to ensure predictions are based on comprehensive data.

### 7. Create Outreach Campaigns

Navigate to the **Campaigns** tab to automate multi-lead outreach:

**Benefits:**
- Save time by contacting multiple leads at once instead of one-by-one
- Target precisely with ICP-based filters (industry, score, location)
- Track performance with open rates, reply rates, and conversion metrics

**How Campaigns Work:**
1. **Create Campaign** - Set campaign name, description, and select target filters (industry, score range)
2. **Choose Channels** - Select email, SMS, and/or LinkedIn for multi-touch outreach
3. **AI Personalization** - System automatically personalizes each message using lead intelligence data
4. **Launch & Track** - Start the campaign and monitor real-time analytics (contacted, opened, replied, converted)

**Prerequisites:**
- Generate AI Intelligence for leads first to enable personalized messaging
- Configure SendGrid (email), Twilio (SMS), or LinkedIn integration in Settings

**Campaign Status:**
- **Draft**: Campaign created but not yet started
- **Active**: Currently sending messages to leads
- **Paused**: Temporarily stopped, can be resumed
- **Completed**: All leads have been contacted

### 8. Book Appointments

Click **"Book Meeting"** to schedule an appointment at your Honolulu office. The system will:
- Find available time slots
- Create a calendar event
- Send confirmations to the lead
- Add reminders

### 9. Monitor Analytics

The dashboard provides comprehensive metrics:

**Overview Cards:**
- Total leads discovered
- Qualified leads (score > 70)
- Appointments booked
- Conversion rate
- Revenue potential

**Pipeline Analytics:**
- Lead count and percentage for each stage
- Win rate (Won / Total Closed)
- Contact → Qualified conversion rate
- Qualified → Opportunity conversion rate
- Active pipeline count
- Visual funnel showing stage-to-stage progression

### 10. Automated Daily Discovery (Optional)

Set up a cron job for hands-free lead generation:
```bash
# Run the setup script
cd backend
chmod +x daily_discovery.sh
./setup_hubspot.sh  # Configure HubSpot integration first

# Add to crontab for daily 9 AM runs
crontab -e
# Add: 0 9 * * * /path/to/backend/daily_discovery.sh
```

See `backend/CRON_JOB_SETUP.md` for detailed instructions.

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

**Lead Management:**
- `POST /api/leads/discover` - Discover new leads from multiple sources
- `GET /api/leads?status=NEW&min_score=70` - Get leads with filters (status, min_score)
- `POST /api/leads/score` - Score a lead
- `PUT /api/leads/{lead_id}/status` - Update lead pipeline status (NEW, CONTACTED, QUALIFIED, OPPORTUNITY, WON, LOST)
- `POST /api/leads/{lead_id}/intelligence?refresh=true` - Generate AI intelligence with Perplexity research
- `POST /api/leads/{lead_id}/predictions` - Generate AI predictive analytics (conversion probability, ICP match, velocity, recommended actions)
- `GET /api/leads/{lead_id}/playbook` - Download PDF sales playbook
- `POST /api/leads/{lead_id}/email-template?template_style=professional` - Generate email template
- `POST /api/leads/{lead_id}/send-to-hubspot` - Sync lead to HubSpot CRM

**Outreach & Campaigns:**
- `POST /api/outreach/generate` - Generate personalized outreach (email, SMS, LinkedIn)
- `POST /api/outreach/send` - Send outreach message
- `POST /api/campaigns` - Create new campaign with name, description, target filters, and channels
- `GET /api/campaigns` - Get all campaigns with performance metrics
- `GET /api/campaigns/{campaign_id}` - Get campaign details with lead list
- `PUT /api/campaigns/{campaign_id}` - Update campaign (name, description, filters, status)
- `DELETE /api/campaigns/{campaign_id}` - Delete campaign
- `POST /api/campaigns/{campaign_id}/leads` - Add leads to campaign (manual or filter-based)
- `POST /api/campaigns/{campaign_id}/start` - Launch campaign and begin outreach
- `POST /api/campaigns/{campaign_id}/pause` - Pause active campaign
- `POST /api/campaigns/{campaign_id}/resume` - Resume paused campaign

**Appointments:**
- `GET /api/appointments/slots` - Get available appointment slots
- `POST /api/appointments/book` - Book an appointment
- `GET /api/appointments` - Get all appointments

**Analytics:**
- `GET /api/analytics/dashboard` - Get dashboard analytics
- `GET /health` - Health check endpoint

**Settings & Configuration:**
- `GET /api/settings/business-profile` - Get business profile
- `PUT /api/settings/business-profile` - Update business profile
- `GET /api/settings/icp` - Get all ICP configurations
- `POST /api/settings/icp` - Create new ICP configuration
- `PUT /api/settings/icp/{icp_id}` - Update ICP configuration
- `DELETE /api/settings/icp/{icp_id}` - Delete ICP configuration
- `GET /api/settings/lead-preferences` - Get lead preferences
- `PUT /api/settings/lead-preferences` - Update lead preferences
- `GET /api/settings/search-discovery` - Get search & discovery settings
- `PUT /api/settings/search-discovery` - Update search & discovery settings
- `GET /api/settings/notifications` - Get notification settings
- `PUT /api/settings/notifications` - Update notification settings
- `GET /api/settings/integrations` - Get integration settings
- `PUT /api/settings/integrations` - Update integration settings
- `GET /api/settings/ai-personalization` - Get AI personalization settings
- `PUT /api/settings/ai-personalization` - Update AI personalization settings
- `GET /api/settings/data-sources` - Get all data source configurations
- `PUT /api/settings/data-sources/{source_id}` - Update data source configuration

## Project Structure

```
ai-lead-gen-booking-platform/
├── backend/
│   ├── main.py                          # FastAPI application
│   ├── database.py                      # Supabase database client
│   ├── predictive_analytics.py          # AI predictions with Gemini 2.5 Flash
│   ├── executive_finder.py              # Multi-source contact finder
│   ├── lead_enrichment_pipeline.py      # Automated enrichment workflow
│   ├── query_manager.py                 # Smart query rotation system
│   ├── icp_manager.py                   # ICP management
│   ├── backfill_intelligence_flags.py   # Utility to backfill has_intelligence flags
│   ├── requirements.txt                 # Python dependencies
│   ├── .env.template                    # Environment variables template
│   ├── migrations/                      # Database migration scripts
│   │   ├── add_decision_makers_column.sql
│   │   ├── add_hubspot_fields.sql
│   │   └── add_status_tracking.sql
├── supabase/
│   └── migrations/
│       ├── 20251108104601_create_data_sources_table.sql
│       ├── 20251108105500_fix_data_sources_rls.sql
│       ├── 20251108112000_create_settings_tables.sql
│       └── 20251108150000_add_lead_status_workflow.sql
│   ├── Documentation/
│   │   ├── COMPLETE_SYSTEM_SUMMARY.md   # Full system overview
│   │   ├── HOW_IT_WORKS.md              # Workflow documentation
│   │   ├── HUBSPOT_INTEGRATION.md       # HubSpot setup guide
│   │   ├── SMART_DISCOVERY_README.md    # Query rotation docs
│   │   ├── ENRICHMENT_WORKFLOW.md       # Enrichment process
│   │   ├── QUICK_REFERENCE.md           # Common commands
│   │   └── CRON_JOB_SETUP.md            # Automation setup
│   ├── Utility Scripts/
│   │   ├── setup_hubspot.sh             # HubSpot configuration
│   │   ├── daily_discovery.sh           # Cron job script
│   │   ├── enrich_researched_leads.py   # Enrichment utility
│   │   ├── apply_migration.py           # Database migrations
│   │   ├── reload_schema.py             # Schema management
│   │   ├── reset_lead_status.py         # Status reset utility
│   │   └── test_*.py                    # Testing utilities
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Main dashboard
│   │   ├── settings/
│   │   │   └── page.tsx                 # Settings & Configuration UI
│   │   ├── layout.tsx                   # App layout
│   │   └── globals.css                  # Global styles
│   ├── components/
│   │   └── ui/                          # shadcn/ui components
│   ├── lib/
│   │   └── utils.ts                     # Utility functions
│   ├── package.json
│   └── Dockerfile
├── infrastructure/
│   └── deploy.sh                        # Deployment script
├── docker-compose.yml
├── README.md
├── CHANGELOG.md
└── API_KEYS_GUIDE.md
```

## Deployment

### Deploy to Google Cloud Run + Vercel

```bash
# Set environment variables
export GCP_PROJECT_ID=your-project-id
export ANTHROPIC_API_KEY=your-key
export GOOGLE_AI_API_KEY=your-key
export OPENAI_API_KEY=your-key

# Run deployment script
cd infrastructure
chmod +x deploy.sh
./deploy.sh
```

This will:
1. Build and push backend to Google Cloud Run
2. Build and deploy frontend to Vercel
3. Configure environment variables
4. Return URLs for both services

## Customization

### Modify Lead Discovery Criteria

Edit `backend/main.py` in the `LeadDiscoveryService.discover_hawaii_businesses()` method to customize:
- Search queries
- Target industries
- Company size filters
- Geographic focus

### Customize Outreach Templates

Modify the prompts in `OutreachGenerator` class to adjust:
- Email tone and style
- SMS message format
- Value propositions
- Call-to-action language

### Adjust Lead Scoring

Update the `LeadScoringAgent` class to change:
- Scoring weights
- Industry priorities
- Location preferences
- Company size importance

## Troubleshooting

### Backend won't start
- Check that all required API keys are set in `.env`
- Verify Python version is 3.11+
- Try: `pip install -r requirements.txt --upgrade`

### Frontend build errors
- Delete `node_modules` and `.next` folders
- Run `npm install` again
- Check Node.js version is 20+

### API key errors
- Verify keys have no extra spaces
- Check keys are valid and not expired
- Ensure billing is enabled for paid APIs
- See [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md)

### Leads not being discovered
- Check your API rate limits
- Verify network connectivity
- Review API usage dashboards
- Check backend logs for errors

## Development

### Run tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code formatting

```bash
# Backend
black .
flake8 .

# Frontend
npm run lint
```

## Documentation

Comprehensive guides are available in the `backend/` directory:

- **[COMPLETE_SYSTEM_SUMMARY.md](backend/COMPLETE_SYSTEM_SUMMARY.md)** - Complete system architecture and workflow overview
- **[HOW_IT_WORKS.md](backend/HOW_IT_WORKS.md)** - Detailed explanation of the lead generation process
- **[HUBSPOT_INTEGRATION.md](backend/HUBSPOT_INTEGRATION.md)** - HubSpot setup and integration guide
- **[SMART_DISCOVERY_README.md](backend/SMART_DISCOVERY_README.md)** - Query rotation system documentation
- **[ENRICHMENT_WORKFLOW.md](backend/ENRICHMENT_WORKFLOW.md)** - Lead enrichment pipeline details
- **[QUICK_REFERENCE.md](backend/QUICK_REFERENCE.md)** - Common commands and workflows
- **[CRON_JOB_SETUP.md](backend/CRON_JOB_SETUP.md)** - Automated discovery setup guide
- **[QUERY_ROTATION_GUIDE.md](backend/QUERY_ROTATION_GUIDE.md)** - Smart query management
- **[SYSTEM_VS_HUBSPOT.md](backend/SYSTEM_VS_HUBSPOT.md)** - Understanding system vs HubSpot data flow

## Support

For issues, questions, or contributions:
- Check the comprehensive documentation in `backend/` folder
- Review the [API_KEYS_GUIDE.md](./API_KEYS_GUIDE.md)
- Visit FastAPI docs: http://localhost:8000/docs
- Check application logs for errors

## License

MIT License - See LICENSE file for details

## About LeniLani Consulting

This platform is built for LeniLani Consulting, a Honolulu-based technology consulting firm specializing in:
- AI/ML Solutions & Chatbot Development
- Data Analytics & Business Intelligence
- Fractional CTO Services
- Digital Marketing & HubSpot Implementation

**Office**: 1050 Queen Street, Suite 100, Honolulu, HI 96814

## Security & Privacy

- All API keys are stored locally and never shared
- Lead data is stored in your own Firebase/PostgreSQL instance
- Outreach is sent from your own SendGrid/Twilio accounts
- No data is sent to third parties except the configured APIs
- See `.gitignore` for excluded sensitive files

## Roadmap

- [ ] LinkedIn API integration for automated connection requests
- [ ] Advanced analytics with charts and graphs
- [ ] Email template library
- [ ] A/B testing for outreach campaigns
- [ ] Automated follow-up sequences
- [ ] Integration with Google Calendar for smart scheduling
- [ ] Mobile app (React Native)
- [ ] Multi-language support (Hawaiian, Japanese, Chinese)

## Recent Updates

### November 9, 2025 - Appointment System Improvements
- **Fixed Appointment Display**: Resolved issue where appointments created from Leads tab weren't showing in Appointments tab
- **Database Schema Updates**: Added missing columns (`organization_id`, `updated_at`) to appointments table
- **Simplified RLS**: Disabled Row Level Security for single-tenant simplicity
- **Navigation Improvements**: Fixed "Go to Leads Tab" button to use proper React state management
- **Scroll Behavior**: Smart scroll behavior - Leads tab scrolls to top, Appointments tab preserves position
- **Supabase Integration**: All appointments now properly persist to Supabase database
- **Removed Duplicate Endpoints**: Cleaned up redundant API routes for appointments

---

Built with ❤️ in Honolulu, Hawaii
