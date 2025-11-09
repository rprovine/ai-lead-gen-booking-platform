# Changelog

All notable changes to the LeniLani Lead Generation & Appointment Booking Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.3] - 2025-11-09

### Added
- **Advanced ICP Filtering** - Comprehensive targeting capabilities for precise lead generation:
  - **Industry Classification**: NAICS codes and SIC codes for precise industry targeting
  - **Business Models**: Filter by B2B, B2C, B2B2C, Marketplace, SaaS, and other business models
  - **Technographic Filters**: Target companies based on their technology stack
    - General tech stack (React, Python, AWS, Docker, etc.)
    - Required technologies (must-have tools)
    - Excluded technologies (technologies to avoid)
  - **Platform & Tools**: Filter by specific platforms and systems
    - Ecommerce platforms (Shopify, WooCommerce, Magento)
    - CRM systems (Salesforce, HubSpot, Pipedrive)
    - Marketing automation (Marketo, Pardot, ActiveCampaign)
    - Payment processors (Stripe, PayPal, Square)
  - **Digital Presence**: Boolean filters for online presence
    - Social media usage
    - Mobile app availability
    - Blog presence
    - SaaS company designation
  - **Company Stage & Credentials**: Target companies by maturity and certifications
    - Funding stage (Seed, Series A, Series B, etc.)
    - Certifications (ISO 27001, SOC2, HIPAA)
    - Strategic partnerships (AWS Partner, Microsoft Partner)

### Improved
- **ICP Builder UI**: Enhanced ICP configuration interface with organized sections
  - Added "Advanced Filtering" section with clear subsections
  - Grouped related fields with descriptive headers
  - Added helpful placeholder text and descriptions for each field
  - Implemented toggle switches for boolean presence filters
  - Clean visual hierarchy with borders and spacing

### Changed
- Updated `icp_config` table schema with 17 new JSONB and boolean columns
- Extended TypeScript `ICPConfig` interface with advanced filtering fields
- Updated Pydantic `ICPConfigCreate` model to handle new fields
- Enhanced default ICP initialization with all new field defaults

### Database
- New migration: `20251109120000_add_advanced_icp_filters.sql`
  - Added columns: naics_codes, sic_codes, business_models, tech_stack, required_technologies, excluded_technologies
  - Added columns: ecommerce_platforms, crm_systems, marketing_automation, payment_processors
  - Added columns: uses_social_media, has_mobile_app, has_blog, is_saas_company
  - Added columns: funding_stage, certifications, partnerships
  - All JSONB arrays default to empty arrays, boolean fields default to NULL

### Technical Details
- Frontend: React form fields with comma-separated input handling for arrays
- Backend: Pydantic models automatically validate and serialize JSONB fields
- Database: PostgreSQL JSONB fields provide flexible array storage
- UI: Organized into 5 subsections (Industry, Business Model, Technographic, Platforms, Digital Presence, Company Stage)

## [0.2.2] - 2025-11-09

### Improved
- **Enhanced Settings Page UX**:
  - Added prominent horizontal scroll arrow buttons for settings tabs navigation
  - Implemented solid backgrounds with borders and shadows for better arrow visibility
  - Added dynamic padding to prevent text overlap with scroll arrows
  - Smart show/hide logic for arrows based on scroll position
  - Smooth scroll animations when clicking arrows
  - Responsive behavior adapting to screen size changes

- **Settings Tab Information Banners**:
  - Added color-coded info banners for each of the 8 settings tabs
  - Comprehensive descriptions explaining the purpose of each section
  - Bullet-pointed benefits highlighting value for each configuration area
  - Visual hierarchy with icons and badges for better information consumption
  - Consistent design pattern across all tabs for professional appearance

- **Settings Navigation Improvements**:
  - Added floating scroll-to-top button appearing after scrolling 400px
  - Controlled tab state management with active tab tracking
  - Improved mobile responsiveness with flex-shrink-0 for tab buttons
  - Enhanced touch targets and keyboard navigation support

- **Information Architecture**:
  - Business Profile: Personalization benefits highlighted
  - ICP Builder: Conversion optimization focus
  - Lead Preferences: Quality control emphasis
  - Search & Discovery: Multi-source strategy
  - Data Sources: Security and integration benefits
  - Notifications: Real-time alerts advantages
  - Integrations: Workflow automation benefits
  - AI Personalization: Customization capabilities

### Changed
- Settings tabs now use controlled component pattern with active state
- TabsList changed from grid layout to inline-flex for better scroll behavior
- Added useRef and useState hooks for scroll management
- Enhanced with ChevronLeft, ChevronRight, ArrowUp, and Info icons

### Technical Details
- Implemented horizontal scroll detection with scroll event listeners
- Added resize event listeners for responsive arrow visibility
- Created TAB_INFO constant with comprehensive metadata for all 8 tabs
- Reusable info banner pattern with consistent color schemes
- Mobile-first responsive design with proper touch handling

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

[Unreleased]: https://github.com/yourusername/ai-lead-gen-booking-platform/compare/v0.2.3...HEAD
[0.2.3]: https://github.com/yourusername/ai-lead-gen-booking-platform/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/yourusername/ai-lead-gen-booking-platform/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/yourusername/ai-lead-gen-booking-platform/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/yourusername/ai-lead-gen-booking-platform/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/yourusername/ai-lead-gen-booking-platform/releases/tag/v0.1.0
