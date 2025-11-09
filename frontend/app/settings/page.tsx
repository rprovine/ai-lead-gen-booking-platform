'use client';

import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Settings as SettingsIcon,
  Database,
  Brain,
  Search,
  Mail,
  MessageSquare,
  CheckCircle2,
  XCircle,
  Loader2,
  Eye,
  EyeOff,
  ExternalLink,
  ArrowLeft,
  Building2,
  Target,
  Sliders,
  Bell,
  Plug,
  Sparkles,
  Plus,
  Trash2,
  Save,
  ArrowUp,
  ChevronLeft,
  ChevronRight,
  Info
} from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============= TYPES =============

interface DataSource {
  id: string;
  organization_id: string;
  source_type: string;
  source_name: string;
  is_enabled: boolean;
  api_key_masked?: string;
  api_secret_masked?: string;
  config: {
    description: string;
    docs_url: string;
    required_fields: string[];
  };
  last_tested_at?: string;
  test_status?: 'success' | 'failed' | 'not_tested';
  test_message?: string;
  created_at: string;
  updated_at: string;
}

interface BusinessProfile {
  company_name?: string;
  industry?: string;
  description?: string;
  products_services?: string;
  value_proposition?: string;
  typical_deal_size?: string;
  sales_cycle_length?: string;
  key_differentiators?: string;
  case_studies?: string;
  website?: string;
}

interface ICPConfig {
  id?: string;
  profile_name: string;
  is_active: boolean;
  employee_count_min?: number;
  employee_count_max?: number;
  annual_revenue_min?: number;
  annual_revenue_max?: number;
  company_age_min?: number;
  company_age_max?: number;
  company_types: string[];
  industries: string[];
  sub_industries: string[];
  industry_keywords: string[];
  excluded_industries: string[];
  target_countries: string[];
  target_states: string[];
  target_cities: string[];
  decision_maker_titles: string[];
  decision_maker_seniority: string[];
  decision_maker_departments: string[];
  multiple_decision_makers: boolean;
  recently_funded: boolean;
  actively_hiring: boolean;
  recent_tech_adoption: boolean;
  expanding_locations: boolean;
  // Advanced filtering fields
  naics_codes: string[];
  sic_codes: string[];
  business_models: string[];
  tech_stack: string[];
  required_technologies: string[];
  excluded_technologies: string[];
  ecommerce_platforms: string[];
  crm_systems: string[];
  marketing_automation: string[];
  payment_processors: string[];
  uses_social_media?: boolean;
  has_mobile_app?: boolean;
  has_blog?: boolean;
  is_saas_company?: boolean;
  funding_stage: string[];
  certifications: string[];
  partnerships: string[];
}

interface LeadPreferences {
  leads_per_batch?: number;
  min_lead_score?: number;
  refresh_frequency?: string;
  quality_vs_quantity?: number;
  excluded_companies: string[];
  excluded_domains: string[];
  include_competitors?: boolean;
}

interface SearchDiscoverySettings {
  priority_keywords: string[];
  priority_websites: string[];
  search_territories: string[];
  social_platforms: string[];
  news_sources: string[];
}

interface NotificationSettings {
  email_enabled?: boolean;
  email_address?: string;
  new_lead_alerts?: boolean;
  lead_score_threshold?: number;
  digest_frequency?: string;
  slack_webhook?: string;
  teams_webhook?: string;
}

interface IntegrationSettings {
  crm_type?: string;
  crm_auto_sync?: boolean;
  export_format?: string;
  webhook_url?: string;
  calendar_integration?: boolean;
  calendar_type?: string;
}

interface AIPersonalizationSettings {
  tone?: string;
  research_depth?: string;
  preferred_model?: string;
  custom_prompt_template?: string;
}

// ============= CONSTANTS =============

const categoryIcons = {
  ai: Brain,
  contact_finding: Search,
  discovery: Database,
  outreach: Mail
};

const categories = {
  'AI & Intelligence': ['anthropic', 'openai', 'google_ai', 'perplexity'],
  'Contact Finding': ['apollo', 'hunter', 'rocketreach'],
  'Lead Discovery': ['serpapi', 'linkedin', 'linkedin_sales_nav'],
  'CRM & Outreach': ['hubspot', 'sendgrid', 'twilio']
};

const EMPLOYEE_RANGES = [
  { label: '1-10', min: 1, max: 10 },
  { label: '11-50', min: 11, max: 50 },
  { label: '51-200', min: 51, max: 200 },
  { label: '201-500', min: 201, max: 500 },
  { label: '501-1000', min: 501, max: 1000 },
  { label: '1001-5000', min: 1001, max: 5000 },
  { label: '5000+', min: 5001, max: 999999 },
];

const REVENUE_RANGES = [
  { label: '$0-$1M', min: 0, max: 1000000 },
  { label: '$1M-$10M', min: 1000000, max: 10000000 },
  { label: '$10M-$50M', min: 10000000, max: 50000000 },
  { label: '$50M-$100M', min: 50000000, max: 100000000 },
  { label: '$100M-$500M', min: 100000000, max: 500000000 },
  { label: '$500M+', min: 500000000, max: 9999999999 },
];

const COMPANY_TYPES = ['Public', 'Private', 'Startup', 'Non-profit', 'Government'];
const SENIORITY_LEVELS = ['C-Suite', 'VP', 'Director', 'Manager', 'Individual Contributor'];
const DEPARTMENTS = ['Sales', 'Marketing', 'IT', 'Operations', 'Finance', 'HR', 'Product', 'Engineering'];

// Tab descriptions and benefits
const TAB_INFO = {
  'business-profile': {
    title: 'Business Profile',
    description: 'Define your company identity to help AI understand your business and generate more relevant, targeted leads.',
    benefits: ['Personalized lead targeting', 'Better AI-generated outreach', 'Aligned with your value proposition']
  },
  'icp': {
    title: 'Ideal Customer Profile (ICP)',
    description: 'Create detailed profiles of your perfect customers to focus on high-quality leads that match your target market.',
    benefits: ['Higher conversion rates', 'Reduced wasted outreach', 'Multiple targeting strategies', 'Precision lead filtering']
  },
  'lead-preferences': {
    title: 'Lead Generation Preferences',
    description: 'Fine-tune how leads are discovered, scored, and delivered to match your sales capacity and quality standards.',
    benefits: ['Control lead volume', 'Set quality thresholds', 'Optimize for your sales cycle', 'Exclude competitors']
  },
  'search-discovery': {
    title: 'Search & Discovery',
    description: 'Configure where and how the platform searches for leads across the web, news sources, and social platforms.',
    benefits: ['Multi-source discovery', 'Geo-targeted searches', 'Industry-specific keywords', 'Real-time lead alerts']
  },
  'data-sources': {
    title: 'Data Sources & API Keys',
    description: 'Connect your API keys for AI services, contact databases, and enrichment tools to power lead generation.',
    benefits: ['All-in-one integration hub', 'Secure credential storage', 'Connection testing', 'Enable/disable sources']
  },
  'notifications': {
    title: 'Alerts & Notifications',
    description: 'Stay informed with real-time alerts for high-quality leads via email, Slack, or Microsoft Teams.',
    benefits: ['Instant lead notifications', 'Custom score thresholds', 'Digest scheduling', 'Multi-channel alerts']
  },
  'integrations': {
    title: 'CRM & Integrations',
    description: 'Seamlessly sync leads to your CRM, configure export formats, and set up webhooks for custom workflows.',
    benefits: ['Auto-sync to CRM', 'Multiple export formats', 'Webhook support', 'Calendar integration']
  },
  'ai': {
    title: 'AI Personalization',
    description: 'Customize how AI researches leads, generates outreach, and personalizes communication to match your brand voice.',
    benefits: ['Custom AI tone', 'Research depth control', 'Model selection', 'Advanced prompt templates']
  }
};

export default function SettingsPage() {
  // Data Sources State
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [editingSource, setEditingSource] = useState<string | null>(null);
  const [editFormData, setEditFormData] = useState<any>({});
  const [showApiKey, setShowApiKey] = useState<string | null>(null);
  const [testingSource, setTestingSource] = useState<string | null>(null);

  // Business Profile State
  const [businessProfile, setBusinessProfile] = useState<BusinessProfile>({});
  const [savingProfile, setSavingProfile] = useState(false);

  // ICP State
  const [icpConfigs, setIcpConfigs] = useState<ICPConfig[]>([]);
  const [editingICP, setEditingICP] = useState<ICPConfig | null>(null);
  const [savingICP, setSavingICP] = useState(false);

  // Lead Preferences State
  const [leadPreferences, setLeadPreferences] = useState<LeadPreferences>({
    excluded_companies: [],
    excluded_domains: [],
  });
  const [savingPreferences, setSavingPreferences] = useState(false);

  // Search & Discovery State
  const [searchSettings, setSearchSettings] = useState<SearchDiscoverySettings>({
    priority_keywords: [],
    priority_websites: [],
    search_territories: [],
    social_platforms: [],
    news_sources: [],
  });
  const [savingSearch, setSavingSearch] = useState(false);

  // Notification State
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({});
  const [savingNotifications, setSavingNotifications] = useState(false);

  // Integration State
  const [integrationSettings, setIntegrationSettings] = useState<IntegrationSettings>({});
  const [savingIntegrations, setSavingIntegrations] = useState(false);

  // AI Personalization State
  const [aiSettings, setAiSettings] = useState<AIPersonalizationSettings>({});
  const [savingAI, setSavingAI] = useState(false);

  const [loading, setLoading] = useState(true);

  // Tab scroll state
  const [activeTab, setActiveTab] = useState('business-profile');
  const tabsScrollRef = useRef<HTMLDivElement>(null);
  const [showLeftScroll, setShowLeftScroll] = useState(false);
  const [showRightScroll, setShowRightScroll] = useState(false);

  // Scroll to top state
  const [showScrollTop, setShowScrollTop] = useState(false);

  // ============= FETCH DATA =============

  useEffect(() => {
    fetchAllSettings();
  }, []);

  // Scroll management effects
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };

    const handleResize = () => {
      checkTabsScroll();
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('resize', handleResize);

    // Initial check
    checkTabsScroll();

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  useEffect(() => {
    if (tabsScrollRef.current) {
      tabsScrollRef.current.addEventListener('scroll', checkTabsScroll);
      return () => {
        if (tabsScrollRef.current) {
          tabsScrollRef.current.removeEventListener('scroll', checkTabsScroll);
        }
      };
    }
  }, []);

  const checkTabsScroll = () => {
    if (tabsScrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = tabsScrollRef.current;
      setShowLeftScroll(scrollLeft > 0);
      setShowRightScroll(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  const scrollTabs = (direction: 'left' | 'right') => {
    if (tabsScrollRef.current) {
      const scrollAmount = 200;
      const newScrollLeft = direction === 'left'
        ? tabsScrollRef.current.scrollLeft - scrollAmount
        : tabsScrollRef.current.scrollLeft + scrollAmount;

      tabsScrollRef.current.scrollTo({
        left: newScrollLeft,
        behavior: 'smooth'
      });
    }
  };

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  const fetchAllSettings = async () => {
    setLoading(true);
    await Promise.all([
      fetchDataSources(),
      fetchBusinessProfile(),
      fetchICPConfigs(),
      fetchLeadPreferences(),
      fetchSearchSettings(),
      fetchNotificationSettings(),
      fetchIntegrationSettings(),
      fetchAISettings(),
    ]);
    setLoading(false);
  };

  const fetchDataSources = async () => {
    try {
      const response = await fetch(`${API_URL}/api/data-sources`);
      if (response.ok) {
        const data = await response.json();
        setDataSources(data);
      }
    } catch (error) {
      console.error('Error fetching data sources:', error);
    }
  };

  const fetchBusinessProfile = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/business-profile`);
      if (response.ok) {
        const data = await response.json();
        setBusinessProfile(data);
      }
    } catch (error) {
      console.error('Error fetching business profile:', error);
    }
  };

  const fetchICPConfigs = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/icp`);
      if (response.ok) {
        const data = await response.json();
        setIcpConfigs(data);
      }
    } catch (error) {
      console.error('Error fetching ICP configs:', error);
    }
  };

  const fetchLeadPreferences = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/lead-preferences`);
      if (response.ok) {
        const data = await response.json();
        setLeadPreferences({
          ...data,
          excluded_companies: data.excluded_companies || [],
          excluded_domains: data.excluded_domains || [],
        });
      }
    } catch (error) {
      console.error('Error fetching lead preferences:', error);
    }
  };

  const fetchSearchSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/search-discovery`);
      if (response.ok) {
        const data = await response.json();
        setSearchSettings({
          priority_keywords: data.priority_keywords || [],
          priority_websites: data.priority_websites || [],
          search_territories: data.search_territories || [],
          social_platforms: data.social_platforms || [],
          news_sources: data.news_sources || [],
        });
      }
    } catch (error) {
      console.error('Error fetching search settings:', error);
    }
  };

  const fetchNotificationSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/notifications`);
      if (response.ok) {
        const data = await response.json();
        setNotificationSettings(data);
      }
    } catch (error) {
      console.error('Error fetching notification settings:', error);
    }
  };

  const fetchIntegrationSettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/integrations`);
      if (response.ok) {
        const data = await response.json();
        setIntegrationSettings(data);
      }
    } catch (error) {
      console.error('Error fetching integration settings:', error);
    }
  };

  const fetchAISettings = async () => {
    try {
      const response = await fetch(`${API_URL}/api/settings/ai-personalization`);
      if (response.ok) {
        const data = await response.json();
        setAiSettings(data);
      }
    } catch (error) {
      console.error('Error fetching AI settings:', error);
    }
  };

  // ============= SAVE FUNCTIONS =============

  const saveBusinessProfile = async () => {
    setSavingProfile(true);
    try {
      const response = await fetch(`${API_URL}/api/settings/business-profile`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(businessProfile),
      });
      if (response.ok) {
        alert('Business profile saved successfully!');
      }
    } catch (error) {
      console.error('Error saving business profile:', error);
      alert('Failed to save business profile');
    }
    setSavingProfile(false);
  };

  const saveICP = async () => {
    if (!editingICP) return;
    setSavingICP(true);
    try {
      const url = editingICP.id
        ? `${API_URL}/api/settings/icp/${editingICP.id}`
        : `${API_URL}/api/settings/icp`;
      const method = editingICP.id ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingICP),
      });

      if (response.ok) {
        await fetchICPConfigs();
        setEditingICP(null);
        alert('ICP saved successfully!');
      }
    } catch (error) {
      console.error('Error saving ICP:', error);
      alert('Failed to save ICP');
    }
    setSavingICP(false);
  };

  const deleteICP = async (id: string) => {
    if (!confirm('Are you sure you want to delete this ICP?')) return;
    try {
      const response = await fetch(`${API_URL}/api/settings/icp/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        await fetchICPConfigs();
        alert('ICP deleted successfully!');
      }
    } catch (error) {
      console.error('Error deleting ICP:', error);
      alert('Failed to delete ICP');
    }
  };

  const saveLeadPreferences = async () => {
    setSavingPreferences(true);
    try {
      const response = await fetch(`${API_URL}/api/settings/lead-preferences`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(leadPreferences),
      });
      if (response.ok) {
        alert('Lead preferences saved successfully!');
      }
    } catch (error) {
      console.error('Error saving lead preferences:', error);
      alert('Failed to save lead preferences');
    }
    setSavingPreferences(false);
  };

  const saveSearchSettings = async () => {
    setSavingSearch(true);
    try {
      const response = await fetch(`${API_URL}/api/settings/search-discovery`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchSettings),
      });
      if (response.ok) {
        alert('Search settings saved successfully!');
      }
    } catch (error) {
      console.error('Error saving search settings:', error);
      alert('Failed to save search settings');
    }
    setSavingSearch(false);
  };

  const saveNotificationSettings = async () => {
    setSavingNotifications(true);
    try {
      const response = await fetch(`${API_URL}/api/settings/notifications`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(notificationSettings),
      });
      if (response.ok) {
        alert('Notification settings saved successfully!');
      }
    } catch (error) {
      console.error('Error saving notification settings:', error);
      alert('Failed to save notification settings');
    }
    setSavingNotifications(false);
  };

  const saveIntegrationSettings = async () => {
    setSavingIntegrations(true);
    try {
      const response = await fetch(`${API_URL}/api/settings/integrations`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(integrationSettings),
      });
      if (response.ok) {
        alert('Integration settings saved successfully!');
      }
    } catch (error) {
      console.error('Error saving integration settings:', error);
      alert('Failed to save integration settings');
    }
    setSavingIntegrations(false);
  };

  const saveAISettings = async () => {
    setSavingAI(true);
    try {
      const response = await fetch(`${API_URL}/api/settings/ai-personalization`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(aiSettings),
      });
      if (response.ok) {
        alert('AI settings saved successfully!');
      }
    } catch (error) {
      console.error('Error saving AI settings:', error);
      alert('Failed to save AI settings');
    }
    setSavingAI(false);
  };

  // ============= DATA SOURCE FUNCTIONS (existing) =============

  const toggleDataSource = async (sourceType: string, enabled: boolean) => {
    try {
      const response = await fetch(`${API_URL}/api/data-sources/${sourceType}/toggle?enabled=${enabled}`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchDataSources();
      }
    } catch (error) {
      console.error('Error toggling data source:', error);
    }
  };

  const startEditing = (source: DataSource) => {
    setEditingSource(source.source_type);
    setEditFormData({
      api_key: '',
      api_secret: '',
      ...source.config
    });
  };

  const cancelEditing = () => {
    setEditingSource(null);
    setEditFormData({});
    setShowApiKey(null);
  };

  const saveConfiguration = async (sourceType: string) => {
    try {
      const updateData: any = {};
      if (editFormData.api_key) updateData.api_key = editFormData.api_key;
      if (editFormData.api_secret) updateData.api_secret = editFormData.api_secret;
      if (editFormData.account_sid || editFormData.auth_token || editFormData.phone_number) {
        updateData.config = {
          account_sid: editFormData.account_sid,
          auth_token: editFormData.auth_token,
          phone_number: editFormData.phone_number
        };
      }

      const response = await fetch(`${API_URL}/api/data-sources/${sourceType}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        fetchDataSources();
        cancelEditing();
      }
    } catch (error) {
      console.error('Error saving configuration:', error);
    }
  };

  const testConnection = async (sourceType: string) => {
    setTestingSource(sourceType);
    try {
      const response = await fetch(`${API_URL}/api/data-sources/${sourceType}/test`, {
        method: 'POST'
      });
      if (response.ok) {
        fetchDataSources();
      }
    } catch (error) {
      console.error('Error testing connection:', error);
    }
    setTestingSource(null);
  };

  const renderSourceCard = (source: DataSource) => {
    const isEditing = editingSource === source.source_type;
    const isConfigured = source.api_key_masked || source.api_secret_masked;

    return (
      <Card key={source.source_type}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Database className="h-5 w-5" />
              <div>
                <CardTitle className="text-lg">{source.source_name}</CardTitle>
                <CardDescription>{source.config.description}</CardDescription>
              </div>
            </div>
            <Switch
              checked={source.is_enabled}
              onCheckedChange={(checked) => toggleDataSource(source.source_type, checked)}
            />
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {!isEditing ? (
            <>
              {isConfigured && (
                <div className="text-sm text-muted-foreground">
                  API Key: {source.api_key_masked}
                </div>
              )}

              {source.test_message && (
                <div className={`text-sm p-2 rounded ${
                  source.test_status === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                }`}>
                  {source.test_message}
                </div>
              )}

              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => startEditing(source)}>
                  {isConfigured ? 'Update' : 'Configure'}
                </Button>
                {isConfigured && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => testConnection(source.source_type)}
                    disabled={testingSource === source.source_type}
                  >
                    {testingSource === source.source_type ? (
                      <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Testing...</>
                    ) : ('Test Connection')}
                  </Button>
                )}
                <Button variant="ghost" size="sm" asChild>
                  <a href={source.config.docs_url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </Button>
              </div>
            </>
          ) : (
            <div className="space-y-4">
              {source.config.required_fields.includes('api_key') && (
                <div className="space-y-2">
                  <Label>API Key</Label>
                  <div className="flex gap-2">
                    <Input
                      type={showApiKey === source.source_type ? 'text' : 'password'}
                      value={editFormData.api_key || ''}
                      onChange={(e) => setEditFormData({ ...editFormData, api_key: e.target.value })}
                      placeholder="Enter your API key"
                    />
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setShowApiKey(showApiKey === source.source_type ? null : source.source_type)}
                    >
                      {showApiKey === source.source_type ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
              )}

              <div className="flex gap-2">
                <Button size="sm" onClick={() => saveConfiguration(source.source_type)}>Save</Button>
                <Button size="sm" variant="outline" onClick={cancelEditing}>Cancel</Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <SettingsIcon className="h-8 w-8" />
          <div>
            <h1 className="text-3xl font-bold">Settings</h1>
            <p className="text-muted-foreground">Configure your lead generation platform</p>
          </div>
        </div>
        <Link href="/">
          <Button variant="outline" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        {/* Tabs with scroll arrows */}
        <div className="relative">
          {/* Left scroll button */}
          {showLeftScroll && (
            <button
              onClick={() => scrollTabs('left')}
              className="absolute left-0 top-0 bottom-0 z-10 w-10 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 shadow-md flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              aria-label="Scroll left"
            >
              <ChevronLeft className="h-6 w-6 text-gray-900 dark:text-gray-100" />
            </button>
          )}

          {/* Right scroll button */}
          {showRightScroll && (
            <button
              onClick={() => scrollTabs('right')}
              className="absolute right-0 top-0 bottom-0 z-10 w-10 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-700 shadow-md flex items-center justify-center hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
              aria-label="Scroll right"
            >
              <ChevronRight className="h-6 w-6 text-gray-900 dark:text-gray-100" />
            </button>
          )}

          <div
            ref={tabsScrollRef}
            className="overflow-x-auto scrollbar-hide"
            style={{
              paddingLeft: showLeftScroll ? '44px' : '0',
              paddingRight: showRightScroll ? '44px' : '0'
            }}
          >
            <TabsList className="inline-flex w-auto min-w-full">
              <TabsTrigger value="business-profile" className="flex-shrink-0">
                <Building2 className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Business</span>
              </TabsTrigger>
              <TabsTrigger value="icp" className="flex-shrink-0">
                <Target className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">ICP</span>
              </TabsTrigger>
              <TabsTrigger value="lead-preferences" className="flex-shrink-0">
                <Sliders className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Leads</span>
              </TabsTrigger>
              <TabsTrigger value="search-discovery" className="flex-shrink-0">
                <Search className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Search</span>
              </TabsTrigger>
              <TabsTrigger value="data-sources" className="flex-shrink-0">
                <Database className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Sources</span>
              </TabsTrigger>
              <TabsTrigger value="notifications" className="flex-shrink-0">
                <Bell className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Alerts</span>
              </TabsTrigger>
              <TabsTrigger value="integrations" className="flex-shrink-0">
                <Plug className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">Integrations</span>
              </TabsTrigger>
              <TabsTrigger value="ai" className="flex-shrink-0">
                <Sparkles className="h-4 w-4 mr-2" />
                <span className="hidden sm:inline">AI</span>
              </TabsTrigger>
            </TabsList>
          </div>
        </div>

        {/* Business Profile Tab */}
        <TabsContent value="business-profile">
          {/* Info Banner */}
          <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-1">
                  {TAB_INFO['business-profile'].title}
                </h3>
                <p className="text-sm text-blue-800 dark:text-blue-200 mb-2">
                  {TAB_INFO['business-profile'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['business-profile'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Your Business Profile</CardTitle>
              <CardDescription>Tell us about your business to help AI generate better leads</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Company Name</Label>
                  <Input
                    value={businessProfile.company_name || ''}
                    onChange={(e) => setBusinessProfile({ ...businessProfile, company_name: e.target.value })}
                    placeholder="Your company name"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Industry</Label>
                  <Input
                    value={businessProfile.industry || ''}
                    onChange={(e) => setBusinessProfile({ ...businessProfile, industry: e.target.value })}
                    placeholder="e.g., SaaS, Marketing, Consulting"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Business Description</Label>
                <textarea
                  className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background"
                  value={businessProfile.description || ''}
                  onChange={(e) => setBusinessProfile({ ...businessProfile, description: e.target.value })}
                  placeholder="Brief description of what your business does"
                />
              </div>

              <div className="space-y-2">
                <Label>Products & Services</Label>
                <textarea
                  className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background"
                  value={businessProfile.products_services || ''}
                  onChange={(e) => setBusinessProfile({ ...businessProfile, products_services: e.target.value })}
                  placeholder="List your main products and services"
                />
              </div>

              <div className="space-y-2">
                <Label>Value Proposition</Label>
                <textarea
                  className="w-full min-h-[100px] p-3 rounded-md border border-input bg-background"
                  value={businessProfile.value_proposition || ''}
                  onChange={(e) => setBusinessProfile({ ...businessProfile, value_proposition: e.target.value })}
                  placeholder="What makes your business unique? What problems do you solve?"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Typical Deal Size</Label>
                  <Input
                    value={businessProfile.typical_deal_size || ''}
                    onChange={(e) => setBusinessProfile({ ...businessProfile, typical_deal_size: e.target.value })}
                    placeholder="e.g., $10k-$50k"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Sales Cycle Length</Label>
                  <Input
                    value={businessProfile.sales_cycle_length || ''}
                    onChange={(e) => setBusinessProfile({ ...businessProfile, sales_cycle_length: e.target.value })}
                    placeholder="e.g., 30-60 days"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Website</Label>
                <Input
                  type="url"
                  value={businessProfile.website || ''}
                  onChange={(e) => setBusinessProfile({ ...businessProfile, website: e.target.value })}
                  placeholder="https://yourcompany.com"
                />
              </div>

              <Button onClick={saveBusinessProfile} disabled={savingProfile} className="w-full">
                {savingProfile ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : <><Save className="mr-2 h-4 w-4" />Save Business Profile</>}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* ICP Builder Tab */}
        <TabsContent value="icp">
          {/* Info Banner */}
          <div className="mb-6 p-4 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-green-900 dark:text-green-100 mb-1">
                  {TAB_INFO['icp'].title}
                </h3>
                <p className="text-sm text-green-800 dark:text-green-200 mb-2">
                  {TAB_INFO['icp'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['icp'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            {icpConfigs.length === 0 && !editingICP && (
              <Card>
                <CardHeader>
                  <CardTitle>No ICP Profiles Yet</CardTitle>
                  <CardDescription>Create your first Ideal Customer Profile to target the right leads</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button onClick={() => setEditingICP({
                    profile_name: 'Default ICP',
                    is_active: true,
                    company_types: [],
                    industries: [],
                    sub_industries: [],
                    industry_keywords: [],
                    excluded_industries: [],
                    target_countries: ['US'],
                    target_states: ['HI'],
                    target_cities: [],
                    decision_maker_titles: [],
                    decision_maker_seniority: [],
                    decision_maker_departments: [],
                    multiple_decision_makers: false,
                    recently_funded: false,
                    actively_hiring: false,
                    recent_tech_adoption: false,
                    expanding_locations: false,
                    naics_codes: [],
                    sic_codes: [],
                    business_models: [],
                    tech_stack: [],
                    required_technologies: [],
                    excluded_technologies: [],
                    ecommerce_platforms: [],
                    crm_systems: [],
                    marketing_automation: [],
                    payment_processors: [],
                    funding_stage: [],
                    certifications: [],
                    partnerships: [],
                  })}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create ICP Profile
                  </Button>
                </CardContent>
              </Card>
            )}

            {icpConfigs.map((icp) => (
              <Card key={icp.id}>
                <CardHeader>
                  <div className="flex justify-between items-center">
                    <div>
                      <CardTitle>{icp.profile_name}</CardTitle>
                      <CardDescription>
                        {icp.employee_count_min && icp.employee_count_max && `${icp.employee_count_min}-${icp.employee_count_max} employees`}
                        {icp.industries.length > 0 && ` • ${icp.industries.join(', ')}`}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => setEditingICP(icp)}>Edit</Button>
                      <Button variant="destructive" size="sm" onClick={() => deleteICP(icp.id!)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>
            ))}

            {editingICP && (
              <Card>
                <CardHeader>
                  <CardTitle>{editingICP.id ? 'Edit ICP Profile' : 'Create ICP Profile'}</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Profile Name</Label>
                    <Input
                      value={editingICP.profile_name}
                      onChange={(e) => setEditingICP({ ...editingICP, profile_name: e.target.value })}
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Min Employees</Label>
                      <Input
                        type="number"
                        value={editingICP.employee_count_min || ''}
                        onChange={(e) => setEditingICP({ ...editingICP, employee_count_min: parseInt(e.target.value) || undefined })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Max Employees</Label>
                      <Input
                        type="number"
                        value={editingICP.employee_count_max || ''}
                        onChange={(e) => setEditingICP({ ...editingICP, employee_count_max: parseInt(e.target.value) || undefined })}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Industries (comma-separated)</Label>
                    <Input
                      value={editingICP.industries.join(', ')}
                      onChange={(e) => setEditingICP({ ...editingICP, industries: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                      placeholder="Technology, Healthcare, Finance"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Target States (comma-separated)</Label>
                    <Input
                      value={editingICP.target_states.join(', ')}
                      onChange={(e) => setEditingICP({ ...editingICP, target_states: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                      placeholder="HI, CA, NY"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Decision Maker Titles (comma-separated)</Label>
                    <Input
                      value={editingICP.decision_maker_titles.join(', ')}
                      onChange={(e) => setEditingICP({ ...editingICP, decision_maker_titles: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                      placeholder="CEO, VP Sales, CTO"
                    />
                  </div>

                  {/* Advanced Filtering Section */}
                  <div className="pt-6 border-t border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-gray-100">Advanced Filtering</h3>

                    {/* Industry Classification */}
                    <div className="space-y-4 mb-6">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Industry Classification</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>NAICS Codes (comma-separated)</Label>
                          <Input
                            value={editingICP.naics_codes.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, naics_codes: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="541511, 541512, 541519"
                          />
                          <p className="text-xs text-gray-500">North American Industry Classification System codes</p>
                        </div>
                        <div className="space-y-2">
                          <Label>SIC Codes (comma-separated)</Label>
                          <Input
                            value={editingICP.sic_codes.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, sic_codes: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="7371, 7372, 7373"
                          />
                          <p className="text-xs text-gray-500">Standard Industrial Classification codes</p>
                        </div>
                      </div>
                    </div>

                    {/* Business Model */}
                    <div className="space-y-2 mb-6">
                      <Label>Business Models (comma-separated)</Label>
                      <Input
                        value={editingICP.business_models.join(', ')}
                        onChange={(e) => setEditingICP({ ...editingICP, business_models: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                        placeholder="B2B, B2C, B2B2C, Marketplace, SaaS"
                      />
                      <p className="text-xs text-gray-500">Target specific business models</p>
                    </div>

                    {/* Technographic Filters */}
                    <div className="space-y-4 mb-6">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Technographic Filters</h4>
                      <div className="space-y-2">
                        <Label>Tech Stack (comma-separated)</Label>
                        <Input
                          value={editingICP.tech_stack.join(', ')}
                          onChange={(e) => setEditingICP({ ...editingICP, tech_stack: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                          placeholder="React, Python, AWS, Docker"
                        />
                        <p className="text-xs text-gray-500">Technologies the company uses</p>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Required Technologies (comma-separated)</Label>
                          <Input
                            value={editingICP.required_technologies.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, required_technologies: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="Salesforce, HubSpot"
                          />
                          <p className="text-xs text-gray-500">Must use these technologies</p>
                        </div>
                        <div className="space-y-2">
                          <Label>Excluded Technologies (comma-separated)</Label>
                          <Input
                            value={editingICP.excluded_technologies.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, excluded_technologies: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="Oracle, SAP"
                          />
                          <p className="text-xs text-gray-500">Should not use these technologies</p>
                        </div>
                      </div>
                    </div>

                    {/* Platform Filters */}
                    <div className="space-y-4 mb-6">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Platform & Tools</h4>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Ecommerce Platforms (comma-separated)</Label>
                          <Input
                            value={editingICP.ecommerce_platforms.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, ecommerce_platforms: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="Shopify, WooCommerce, Magento"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>CRM Systems (comma-separated)</Label>
                          <Input
                            value={editingICP.crm_systems.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, crm_systems: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="Salesforce, HubSpot, Pipedrive"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Marketing Automation (comma-separated)</Label>
                          <Input
                            value={editingICP.marketing_automation.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, marketing_automation: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="Marketo, Pardot, ActiveCampaign"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Payment Processors (comma-separated)</Label>
                          <Input
                            value={editingICP.payment_processors.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, payment_processors: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="Stripe, PayPal, Square"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Digital Presence & Company Attributes */}
                    <div className="space-y-4 mb-6">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Digital Presence & Attributes</h4>
                      <div className="grid grid-cols-4 gap-4">
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={editingICP.uses_social_media ?? false}
                            onCheckedChange={(checked) => setEditingICP({ ...editingICP, uses_social_media: checked })}
                          />
                          <Label>Social Media</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={editingICP.has_mobile_app ?? false}
                            onCheckedChange={(checked) => setEditingICP({ ...editingICP, has_mobile_app: checked })}
                          />
                          <Label>Mobile App</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={editingICP.has_blog ?? false}
                            onCheckedChange={(checked) => setEditingICP({ ...editingICP, has_blog: checked })}
                          />
                          <Label>Has Blog</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Switch
                            checked={editingICP.is_saas_company ?? false}
                            onCheckedChange={(checked) => setEditingICP({ ...editingICP, is_saas_company: checked })}
                          />
                          <Label>SaaS Company</Label>
                        </div>
                      </div>
                    </div>

                    {/* Company Stage & Credentials */}
                    <div className="space-y-4">
                      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">Company Stage & Credentials</h4>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>Funding Stage (comma-separated)</Label>
                          <Input
                            value={editingICP.funding_stage.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, funding_stage: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="Seed, Series A, Series B"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Certifications (comma-separated)</Label>
                          <Input
                            value={editingICP.certifications.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, certifications: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="ISO 27001, SOC2, HIPAA"
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Partnerships (comma-separated)</Label>
                          <Input
                            value={editingICP.partnerships.join(', ')}
                            onChange={(e) => setEditingICP({ ...editingICP, partnerships: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                            placeholder="AWS Partner, Microsoft Partner"
                          />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={saveICP} disabled={savingICP}>
                      {savingICP ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : 'Save ICP'}
                    </Button>
                    <Button variant="outline" onClick={() => setEditingICP(null)}>Cancel</Button>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Lead Preferences Tab */}
        <TabsContent value="lead-preferences">
          {/* Info Banner */}
          <div className="mb-6 p-4 bg-purple-50 dark:bg-purple-950 border border-purple-200 dark:border-purple-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-purple-600 dark:text-purple-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-purple-900 dark:text-purple-100 mb-1">
                  {TAB_INFO['lead-preferences'].title}
                </h3>
                <p className="text-sm text-purple-800 dark:text-purple-200 mb-2">
                  {TAB_INFO['lead-preferences'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['lead-preferences'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Lead Generation Preferences</CardTitle>
              <CardDescription>Configure how leads are generated and scored</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Leads per Batch</Label>
                  <Input
                    type="number"
                    value={leadPreferences.leads_per_batch || 50}
                    onChange={(e) => setLeadPreferences({ ...leadPreferences, leads_per_batch: parseInt(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Minimum Lead Score</Label>
                  <Input
                    type="number"
                    value={leadPreferences.min_lead_score || 70}
                    onChange={(e) => setLeadPreferences({ ...leadPreferences, min_lead_score: parseInt(e.target.value) })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Refresh Frequency</Label>
                <select
                  className="w-full p-2 rounded-md border border-input bg-background"
                  value={leadPreferences.refresh_frequency || 'weekly'}
                  onChange={(e) => setLeadPreferences({ ...leadPreferences, refresh_frequency: e.target.value })}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Quality vs Quantity (Higher = More Quality)</Label>
                <Input
                  type="range"
                  min="0"
                  max="100"
                  value={leadPreferences.quality_vs_quantity || 70}
                  onChange={(e) => setLeadPreferences({ ...leadPreferences, quality_vs_quantity: parseInt(e.target.value) })}
                />
                <div className="text-center text-sm text-muted-foreground">{leadPreferences.quality_vs_quantity || 70}%</div>
              </div>

              <Button onClick={saveLeadPreferences} disabled={savingPreferences} className="w-full">
                {savingPreferences ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : 'Save Preferences'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Search & Discovery Tab */}
        <TabsContent value="search-discovery">
          {/* Info Banner */}
          <div className="mb-6 p-4 bg-orange-50 dark:bg-orange-950 border border-orange-200 dark:border-orange-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-orange-600 dark:text-orange-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-orange-900 dark:text-orange-100 mb-1">
                  {TAB_INFO['search-discovery'].title}
                </h3>
                <p className="text-sm text-orange-800 dark:text-orange-200 mb-2">
                  {TAB_INFO['search-discovery'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['search-discovery'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Search & Discovery Settings</CardTitle>
              <CardDescription>Configure where and how to discover leads</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Priority Keywords (comma-separated)</Label>
                <Input
                  value={searchSettings.priority_keywords.join(', ')}
                  onChange={(e) => setSearchSettings({ ...searchSettings, priority_keywords: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                  placeholder="SaaS, Marketing, Cloud Services"
                />
              </div>

              <div className="space-y-2">
                <Label>Priority Websites (comma-separated)</Label>
                <Input
                  value={searchSettings.priority_websites.join(', ')}
                  onChange={(e) => setSearchSettings({ ...searchSettings, priority_websites: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                  placeholder="pacificbusinessnews.com, hawaiibusiness.com"
                />
              </div>

              <div className="space-y-2">
                <Label>Search Territories (comma-separated)</Label>
                <Input
                  value={searchSettings.search_territories.join(', ')}
                  onChange={(e) => setSearchSettings({ ...searchSettings, search_territories: e.target.value.split(',').map(s => s.trim()).filter(Boolean) })}
                  placeholder="Hawaii, California, New York"
                />
              </div>

              <Button onClick={saveSearchSettings} disabled={savingSearch} className="w-full">
                {savingSearch ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : 'Save Search Settings'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Sources Tab */}
        <TabsContent value="data-sources" className="space-y-6">
          {/* Info Banner */}
          <div className="p-4 bg-cyan-50 dark:bg-cyan-950 border border-cyan-200 dark:border-cyan-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-cyan-600 dark:text-cyan-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-cyan-900 dark:text-cyan-100 mb-1">
                  {TAB_INFO['data-sources'].title}
                </h3>
                <p className="text-sm text-cyan-800 dark:text-cyan-200 mb-2">
                  {TAB_INFO['data-sources'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['data-sources'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-cyan-100 dark:bg-cyan-900 text-cyan-800 dark:text-cyan-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {Object.entries(categories).map(([categoryName, sourceTypes]) => {
            const categorySources = dataSources.filter(s => sourceTypes.includes(s.source_type));
            if (categorySources.length === 0) return null;

            return (
              <div key={categoryName}>
                <h2 className="text-2xl font-semibold mb-4">{categoryName}</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {categorySources.map(renderSourceCard)}
                </div>
              </div>
            );
          })}
        </TabsContent>

        {/* Notifications Tab */}
        <TabsContent value="notifications">
          {/* Info Banner */}
          <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-yellow-600 dark:text-yellow-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100 mb-1">
                  {TAB_INFO['notifications'].title}
                </h3>
                <p className="text-sm text-yellow-800 dark:text-yellow-200 mb-2">
                  {TAB_INFO['notifications'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['notifications'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Notification Settings</CardTitle>
              <CardDescription>Configure alerts for new leads and updates</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Label>Email Notifications</Label>
                <Switch
                  checked={notificationSettings.email_enabled || false}
                  onCheckedChange={(checked) => setNotificationSettings({ ...notificationSettings, email_enabled: checked })}
                />
              </div>

              {notificationSettings.email_enabled && (
                <>
                  <div className="space-y-2">
                    <Label>Email Address</Label>
                    <Input
                      type="email"
                      value={notificationSettings.email_address || ''}
                      onChange={(e) => setNotificationSettings({ ...notificationSettings, email_address: e.target.value })}
                      placeholder="your@email.com"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <Label>New Lead Alerts</Label>
                    <Switch
                      checked={notificationSettings.new_lead_alerts || false}
                      onCheckedChange={(checked) => setNotificationSettings({ ...notificationSettings, new_lead_alerts: checked })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Alert Score Threshold</Label>
                    <Input
                      type="number"
                      value={notificationSettings.lead_score_threshold || 80}
                      onChange={(e) => setNotificationSettings({ ...notificationSettings, lead_score_threshold: parseInt(e.target.value) })}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Digest Frequency</Label>
                    <select
                      className="w-full p-2 rounded-md border border-input bg-background"
                      value={notificationSettings.digest_frequency || 'daily'}
                      onChange={(e) => setNotificationSettings({ ...notificationSettings, digest_frequency: e.target.value })}
                    >
                      <option value="realtime">Real-time</option>
                      <option value="daily">Daily Digest</option>
                      <option value="weekly">Weekly Digest</option>
                    </select>
                  </div>
                </>
              )}

              <div className="space-y-2">
                <Label>Slack Webhook URL (optional)</Label>
                <Input
                  value={notificationSettings.slack_webhook || ''}
                  onChange={(e) => setNotificationSettings({ ...notificationSettings, slack_webhook: e.target.value })}
                  placeholder="https://hooks.slack.com/services/..."
                />
              </div>

              <Button onClick={saveNotificationSettings} disabled={savingNotifications} className="w-full">
                {savingNotifications ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : 'Save Notification Settings'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Integrations Tab */}
        <TabsContent value="integrations">
          {/* Info Banner */}
          <div className="mb-6 p-4 bg-pink-50 dark:bg-pink-950 border border-pink-200 dark:border-pink-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-pink-600 dark:text-pink-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-pink-900 dark:text-pink-100 mb-1">
                  {TAB_INFO['integrations'].title}
                </h3>
                <p className="text-sm text-pink-800 dark:text-pink-200 mb-2">
                  {TAB_INFO['integrations'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['integrations'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-pink-100 dark:bg-pink-900 text-pink-800 dark:text-pink-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Integration Settings</CardTitle>
              <CardDescription>Connect with your CRM and other tools</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>CRM Type</Label>
                <select
                  className="w-full p-2 rounded-md border border-input bg-background"
                  value={integrationSettings.crm_type || 'none'}
                  onChange={(e) => setIntegrationSettings({ ...integrationSettings, crm_type: e.target.value })}
                >
                  <option value="none">None</option>
                  <option value="hubspot">HubSpot</option>
                  <option value="salesforce">Salesforce</option>
                  <option value="pipedrive">Pipedrive</option>
                </select>
              </div>

              {integrationSettings.crm_type && integrationSettings.crm_type !== 'none' && (
                <div className="flex items-center justify-between">
                  <Label>Auto-sync to CRM</Label>
                  <Switch
                    checked={integrationSettings.crm_auto_sync || false}
                    onCheckedChange={(checked) => setIntegrationSettings({ ...integrationSettings, crm_auto_sync: checked })}
                  />
                </div>
              )}

              <div className="space-y-2">
                <Label>Export Format</Label>
                <select
                  className="w-full p-2 rounded-md border border-input bg-background"
                  value={integrationSettings.export_format || 'csv'}
                  onChange={(e) => setIntegrationSettings({ ...integrationSettings, export_format: e.target.value })}
                >
                  <option value="csv">CSV</option>
                  <option value="json">JSON</option>
                  <option value="xlsx">Excel (XLSX)</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Webhook URL (optional)</Label>
                <Input
                  value={integrationSettings.webhook_url || ''}
                  onChange={(e) => setIntegrationSettings({ ...integrationSettings, webhook_url: e.target.value })}
                  placeholder="https://yourapp.com/webhook"
                />
              </div>

              <Button onClick={saveIntegrationSettings} disabled={savingIntegrations} className="w-full">
                {savingIntegrations ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : 'Save Integration Settings'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Personalization Tab */}
        <TabsContent value="ai">
          {/* Info Banner */}
          <div className="mb-6 p-4 bg-indigo-50 dark:bg-indigo-950 border border-indigo-200 dark:border-indigo-800 rounded-lg">
            <div className="flex gap-3">
              <Info className="h-5 w-5 text-indigo-600 dark:text-indigo-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-indigo-900 dark:text-indigo-100 mb-1">
                  {TAB_INFO['ai'].title}
                </h3>
                <p className="text-sm text-indigo-800 dark:text-indigo-200 mb-2">
                  {TAB_INFO['ai'].description}
                </p>
                <div className="flex flex-wrap gap-2">
                  {TAB_INFO['ai'].benefits.map((benefit, idx) => (
                    <Badge key={idx} variant="secondary" className="text-xs bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200">
                      {benefit}
                    </Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>AI Personalization</CardTitle>
              <CardDescription>Configure how AI researches and engages with leads</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Communication Tone</Label>
                <select
                  className="w-full p-2 rounded-md border border-input bg-background"
                  value={aiSettings.tone || 'professional'}
                  onChange={(e) => setAiSettings({ ...aiSettings, tone: e.target.value })}
                >
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                  <option value="direct">Direct</option>
                  <option value="casual">Casual</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Research Depth</Label>
                <select
                  className="w-full p-2 rounded-md border border-input bg-background"
                  value={aiSettings.research_depth || 'standard'}
                  onChange={(e) => setAiSettings({ ...aiSettings, research_depth: e.target.value })}
                >
                  <option value="quick">Quick (Fast, basic info)</option>
                  <option value="standard">Standard (Balanced)</option>
                  <option value="deep">Deep (Comprehensive, slower)</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Preferred AI Model</Label>
                <select
                  className="w-full p-2 rounded-md border border-input bg-background"
                  value={aiSettings.preferred_model || 'claude-sonnet'}
                  onChange={(e) => setAiSettings({ ...aiSettings, preferred_model: e.target.value })}
                >
                  <option value="claude-sonnet">Claude Sonnet (Best quality)</option>
                  <option value="claude-haiku">Claude Haiku (Faster)</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-3.5">GPT-3.5 (Economical)</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label>Custom Prompt Template (Advanced)</Label>
                <textarea
                  className="w-full min-h-[150px] p-3 rounded-md border border-input bg-background font-mono text-sm"
                  value={aiSettings.custom_prompt_template || ''}
                  onChange={(e) => setAiSettings({ ...aiSettings, custom_prompt_template: e.target.value })}
                  placeholder="You are a B2B sales intelligence assistant..."
                />
              </div>

              <Button onClick={saveAISettings} disabled={savingAI} className="w-full">
                {savingAI ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : 'Save AI Settings'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

      </Tabs>

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 p-3 bg-primary text-primary-foreground rounded-full shadow-lg hover:bg-primary/90 transition-all duration-200 hover:scale-110"
          aria-label="Scroll to top"
        >
          <ArrowUp className="h-5 w-5" />
        </button>
      )}
    </div>
  );
}
