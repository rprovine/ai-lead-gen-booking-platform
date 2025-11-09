# Changelog

All notable changes to the LeniLani Lead Generation & Appointment Booking Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.1] - 2025-11-09

### Improved
- **Enhanced Status Filter Tabs UX**:
  - Added prominent scroll arrow buttons on left/right sides when tabs overflow
  - Implemented solid backgrounds with borders and shadows for better visibility
  - Added dynamic padding to prevent text overlap with arrows
  - Increased icon size and contrast for improved accessibility
  - Smart show/hide logic based on scroll position
  - Smooth scroll animations when clicking arrows
  - Responsive behavior that adapts to screen size changes
  - Added `scrollbar-hide` utility class for cleaner appearance

- **AI Insights Action Buttons**:
  - Fixed "View High-Score Leads" functionality with proper filter parsing
  - Fixed "Create Campaign" button to correctly open campaign creation modal
  - Fixed "View New Leads" to navigate to leads tab with proper filtering
  - Added visual filter banner showing active filters with lead count
  - Implemented scroll-to-first-lead functionality after filtering
  - Added clear filter button for easy reset

- **Navigation Improvements**:
  - Added floating scroll-to-top button that appears after scrolling 400px
  - Smooth scroll animations throughout the application
  - Improved tab switching with controlled state management

## [0.2.0] - 2025-11-08

### Added - Comprehensive Settings & Configuration System

#### Frontend Features
- **New Settings Page** (`/settings`) with 8 comprehensive configuration tabs:
  - Data Sources: Manage API keys for 13+ external services (Apollo, Hunter, Perplexity, Anthropic, Google, OpenAI, SerpAPI, RocketReach, HubSpot, SendGrid, Twilio)
  - Business Profile: Configure company information, value proposition, products/services, deal size, and sales cycle
  - ICP Builder: Create and manage multiple Ideal Customer Profiles with detailed targeting criteria
  - Lead Preferences: Set batch sizes, minimum scoring thresholds, quality vs quantity slider, excluded companies/domains
  - Search & Discovery: Configure priority keywords, websites, territories, social platforms, and news sources
  - Notifications: Set up email and Slack alerts with customizable thresholds and digest frequency
  - Integrations: Configure CRM auto-sync, export formats, webhooks, and calendar integration
  - AI Personalization: Customize AI tone (professional/casual/consultative), research depth, and preferred models

- **New UI Components**:
  - Input component with proper styling and validation
  - Label component for form fields
  - Switch component for boolean toggles
  - Responsive tabbed interface with Lucide icons

- **Settings Navigation**:
  - Added Settings button to main dashboard header
  - Back navigation from Settings page to Dashboard

#### Backend Features
- **Database Schema** (7 new Supabase tables):
  - `business_profile` - Company information and value proposition
  - `icp_config` - Ideal Customer Profile configurations with full CRUD support
  - `lead_preferences` - Lead generation preferences and exclusions
  - `search_discovery_settings` - Search configuration and data sources
  - `notification_settings` - Email and Slack notification preferences
  - `integration_settings` - CRM and export configurations
  - `ai_personalization_settings` - AI behavior customization
  - `data_sources_config` - API key management for 13 external services

- **New API Endpoints** (18 total):
  - `GET/PUT /api/settings/business-profile` - Business profile management
  - `GET/POST/PUT/DELETE /api/settings/icp` - ICP CRUD operations
  - `GET/PUT /api/settings/lead-preferences` - Lead preferences management
  - `GET/PUT /api/settings/search-discovery` - Search settings management
  - `GET/PUT /api/settings/notifications` - Notification settings management
  - `GET/PUT /api/settings/integrations` - Integration settings management
  - `GET/PUT /api/settings/ai-personalization` - AI settings management
  - `GET/PUT /api/settings/data-sources` - Data source configuration

- **Database Methods** in `database.py`:
  - Business profile get/upsert methods
  - ICP configuration full CRUD (get_all, get_by_id, create, update, delete)
  - Settings get/upsert methods for all 5 settings categories
  - All methods use async/await pattern with proper error handling

- **Pydantic Models** for validation:
  - BusinessProfileUpdate
  - ICPConfigCreate, ICPConfigUpdate
  - LeadPreferencesUpdate
  - SearchDiscoverySettingsUpdate
  - NotificationSettingsUpdate
  - IntegrationSettingsUpdate
  - AIPersonalizationSettingsUpdate
  - DataSourceUpdate

#### Database Migrations
- `20251108104601_create_data_sources_table.sql` - Initial data sources table with 13 pre-populated services
- `20251108105500_fix_data_sources_rls.sql` - Row-level security policy fix for default organization
- `20251108112000_create_settings_tables.sql` - Comprehensive settings tables with RLS policies and triggers

#### Security
- Row Level Security (RLS) enabled on all settings tables
- Default organization policy for 'default' organization_id
- API key masking in frontend (show only last 4 characters)
- Secure storage of sensitive configuration in Supabase

#### Multi-Tenant Architecture
- All settings tables include `organization_id` field (defaults to 'default')
- Settings infrastructure ready for future multi-tenant implementation
- Current app functionality unchanged - settings stored but not yet integrated into lead generation logic

### Changed
- Updated README.md with Settings & Configuration section
- Updated API documentation with new settings endpoints
- Updated project structure documentation
- Added @radix-ui/react-switch and @radix-ui/react-label dependencies to frontend

### Technical Details
- Frontend: Next.js 14, React 18, TypeScript, Tailwind CSS, shadcn/ui
- Backend: FastAPI (Python), async/await patterns
- Database: Supabase (PostgreSQL) with JSONB fields for flexible configuration
- API: RESTful endpoints with Pydantic validation
- UI: Responsive design with tab-based navigation

### Notes
- Settings are stored in database but not yet integrated into lead generation workflows
- This update prepares the platform for future user authentication and multi-tenant capabilities
- Existing app functionality remains completely unchanged

---

## [0.1.0] - 2025-10-27

### Added
- Initial release of LeniLani Lead Generation & Appointment Booking Platform
- AI-powered lead discovery with smart query rotation
- Perplexity AI research integration for company intelligence
- Multi-source contact finding (Apollo, Hunter, Perplexity, Google)
- PDF sales playbook generation
- HubSpot CRM integration
- Automated email/SMS outreach generation
- Appointment booking system
- Real-time analytics dashboard
- Automated daily discovery with cron jobs

[Unreleased]: https://github.com/yourusername/ai-lead-gen-booking-platform/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/yourusername/ai-lead-gen-booking-platform/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/ai-lead-gen-booking-platform/releases/tag/v0.1.0
