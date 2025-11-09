'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Users,
  Calendar,
  TrendingUp,
  Mail,
  MessageSquare,
  DollarSign,
  Building2,
  Brain,
  Target,
  Sparkles,
  Phone,
  Download,
  Loader2,
  Upload,
  Settings,
  Eye,
  Globe,
  MapPin,
  Award,
  Briefcase,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Zap,
  Clock,
  Circle
} from 'lucide-react'
import Link from 'next/link'
import axios from 'axios'
import { motion } from 'framer-motion'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface DecisionMaker {
  name: string
  title: string
  email: string
  phone?: string
  linkedin?: string
  confidence?: number
  source?: string
}

interface PredictionDetails {
  conversion_probability?: number
  conversion_confidence?: number
  conversion_factors?: {
    positive?: string[]
    negative?: string[]
  }
  icp_match_score?: number
  icp_matching_factors?: string[]
  icp_missing_factors?: string[]
  velocity_score?: number
  velocity_insight?: string
  days_in_pipeline?: number
  recommended_action?: string
  action_reasoning?: string
  action_priority?: string
  action_timing?: string
  best_contact_time?: string
  generated_at?: string
}

interface Lead {
  id?: string
  company_name: string
  website: string
  email?: string
  phone?: string
  industry: string
  employee_count?: number
  location: string
  tech_stack: string[]
  pain_points: string[]
  score: number
  status: string
  source: string
  created_at: string
  decision_makers?: DecisionMaker[]
  email_pattern?: string
  // Tracking fields
  hubspot_company_id?: string
  hubspot_contact_id?: string
  hubspot_synced_at?: string
  has_intelligence?: boolean
  intelligence_generated_at?: string
  // Predictive analytics fields
  conversion_probability?: number
  icp_match_score?: number
  lead_velocity_score?: number
  recommended_action?: string
  best_contact_time?: string
  last_prediction_at?: string
  // Full prediction details
  prediction_details?: PredictionDetails
}

interface Analytics {
  total_leads: number
  qualified_leads: number
  appointments_booked: number
  conversion_rate: number
  revenue_potential: number
}

interface SalesIntelligence {
  executive_summary: string
  hot_buttons: string[]
  recommended_approach: string
  talking_points: string[]
  decision_maker: {
    target_role: string
    priorities: string[]
    best_contact: string
  }
  budget: {
    estimated_range: string
    investment_likelihood: string
    signals: string
  }
  competitive_positioning: {
    likely_competitors: string[]
    our_differentiators: string[]
    hawaii_advantage: string
  }
  appointment_strategy: {
    hook: string
    format: string
    follow_up_cadence: string
  }
  next_steps: string[]
  confidence: number
  research_summary?: string
  perplexity_research?: {
    company_name: string
    research_date: string
    has_recent_data: boolean
    full_text: string
    recent_news: string
    leadership: string
    business_developments: string
    market_position: string
    challenges_opportunities: string
    summary: string
  }
}

interface EmailTemplate {
  subject: string
  body: string
  intelligence_summary: {
    hot_buttons: string[]
    talking_points: string[]
    hook: string
  }
}

interface Campaign {
  id: number
  name: string
  description: string
  target_filters: {
    industry?: string
    min_score?: number
    max_score?: number
  }
  channels: string[]
  status: string
  total_leads: number
  contacted_leads: number
  opened_count: number
  replied_count: number
  converted_count: number
  created_at: string
  started_at?: string
}

interface CampaignSequence {
  id?: number
  campaign_id: number
  sequence_number: number
  channel: string
  delay_days: number
  subject?: string
  content: string
  template_style: string
}

interface CampaignAnalytics {
  total_leads: number
  contacted_leads: number
  opened_count: number
  replied_count: number
  converted_count: number
  progress: number
  conversion_rate: number
  status: string
}

interface Appointment {
  id: number
  lead_id: string
  date_time: string
  location: string
  format: string
  status: string
  notes: string
  created_at: string
  lead?: Lead
}

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<Analytics>({
    total_leads: 0,
    qualified_leads: 0,
    appointments_booked: 0,
    conversion_rate: 0,
    revenue_potential: 0
  })
  const [leads, setLeads] = useState<Lead[]>([])
  const [isDiscovering, setIsDiscovering] = useState(false)
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [generatedOutreach, setGeneratedOutreach] = useState<string>('')
  const [showOutreach, setShowOutreach] = useState(false)

  // AI Intelligence states
  const [showIntelligence, setShowIntelligence] = useState(false)
  const [intelligence, setIntelligence] = useState<SalesIntelligence | null>(null)
  const [loadingIntelligence, setLoadingIntelligence] = useState(false)

  // Predictive analytics states
  const [generatingPredictions, setGeneratingPredictions] = useState<string | null>(null)

  // Email template states
  const [showEmailTemplate, setShowEmailTemplate] = useState(false)
  const [emailTemplate, setEmailTemplate] = useState<EmailTemplate | null>(null)
  const [emailStyle, setEmailStyle] = useState<'professional' | 'casual' | 'consultative'>('professional')
  const [loadingEmail, setLoadingEmail] = useState(false)

  // Lead detail modal state
  const [showLeadDetail, setShowLeadDetail] = useState(false)
  const [detailLead, setDetailLead] = useState<Lead | null>(null)

  // Lead status update state
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null)

  // PDF download states
  const [downloadingPlaybook, setDownloadingPlaybook] = useState<string | null>(null)

  // HubSpot sync states
  const [sendingToHubSpot, setSendingToHubSpot] = useState<string | null>(null)

  // Status filter state
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'NEW' | 'CONTACTED' | 'QUALIFIED' | 'OPPORTUNITY' | 'WON' | 'LOST'>('ALL')

  // Campaign states
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [showCreateCampaign, setShowCreateCampaign] = useState(false)
  const [showCampaignDetail, setShowCampaignDetail] = useState(false)
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null)
  const [campaignAnalytics, setCampaignAnalytics] = useState<CampaignAnalytics | null>(null)
  const [campaignSequences, setCampaignSequences] = useState<CampaignSequence[]>([])
  const [loadingCampaigns, setLoadingCampaigns] = useState(false)
  const [generatingSequences, setGeneratingSequences] = useState(false)

  // Campaign form states
  const [newCampaignName, setNewCampaignName] = useState('')
  const [newCampaignDescription, setNewCampaignDescription] = useState('')
  const [newCampaignIndustry, setNewCampaignIndustry] = useState('')
  const [newCampaignMinScore, setNewCampaignMinScore] = useState(70)
  const [newCampaignChannels, setNewCampaignChannels] = useState<string[]>(['email'])

  // Appointment states
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [showBookAppointment, setShowBookAppointment] = useState(false)
  const [bookingLead, setBookingLead] = useState<Lead | null>(null)
  const [appointmentDate, setAppointmentDate] = useState('')
  const [appointmentTime, setAppointmentTime] = useState('')
  const [appointmentFormat, setAppointmentFormat] = useState('in-person')
  const [appointmentNotes, setAppointmentNotes] = useState('')
  const [bookingAppointment, setBookingAppointment] = useState(false)

  // AI Insights states
  const [aiInsights, setAiInsights] = useState<any[]>([])
  const [loadingInsights, setLoadingInsights] = useState(false)

  useEffect(() => {
    // Scroll to top on page load - do it immediately and after a small delay
    // to override any scroll restoration
    window.scrollTo(0, 0)
    setTimeout(() => window.scrollTo(0, 0), 0)
    setTimeout(() => window.scrollTo(0, 0), 100)

    fetchAnalytics()
    fetchLeads()
    fetchCampaigns()
    fetchAppointments()
    fetchAIInsights()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/analytics/dashboard`)
      setAnalytics(response.data)
    } catch (error) {
      console.error('Error fetching analytics:', error)
    }
  }

  const fetchLeads = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/leads`)
      setLeads(response.data)
    } catch (error) {
      console.error('Error fetching leads:', error)
    }
  }

  const startDiscovery = async () => {
    setIsDiscovering(true)
    try {
      const response = await axios.post(`${API_URL}/api/leads/discover`)
      console.log('Discovery started:', response.data)

      // Wait a bit then refresh
      setTimeout(() => {
        fetchLeads()
        fetchAnalytics()
        setIsDiscovering(false)
      }, 3000)
    } catch (error) {
      console.error('Error starting discovery:', error)
      setIsDiscovering(false)
    }
  }

  const generateOutreach = async (lead: Lead, channel: string) => {
    try {
      const response = await axios.post(`${API_URL}/api/outreach/generate`, null, {
        params: {
          lead_id: lead.id,
          channel: channel
        }
      })

      setSelectedLead(lead)
      setGeneratedOutreach(response.data.content)
      setShowOutreach(true)
    } catch (error) {
      console.error('Error generating outreach:', error)
      alert('Error generating outreach. Please try again.')
    }
  }

  const sendOutreach = async (channel: string) => {
    if (!selectedLead) return

    try {
      await axios.post(`${API_URL}/api/outreach/send`, null, {
        params: {
          lead_id: selectedLead.id,
          channel: channel,
          content: generatedOutreach
        }
      })

      alert('Outreach sent successfully!')
      setShowOutreach(false)
    } catch (error) {
      console.error('Error sending outreach:', error)
      alert('Error sending outreach. Please check your API configuration.')
    }
  }

  const updateLeadStatus = async (leadId: string, newStatus: string) => {
    setUpdatingStatus(leadId)
    try {
      await axios.put(`${API_URL}/api/leads/${leadId}/status`, {
        status: newStatus
      })

      // Refresh leads to show updated status
      await fetchLeads()
    } catch (error) {
      console.error('Error updating lead status:', error)
      alert('Error updating lead status. Please try again.')
    } finally {
      setUpdatingStatus(null)
    }
  }

  const fetchIntelligence = async (lead: Lead) => {
    setSelectedLead(lead)
    setLoadingIntelligence(true)
    setShowIntelligence(true)

    try {
      const response = await axios.post(`${API_URL}/api/leads/${lead.id}/intelligence`)
      setIntelligence(response.data.intelligence)
    } catch (error) {
      console.error('Error fetching intelligence:', error)
      alert('Error fetching AI intelligence. This may take up to 90 seconds to generate.')
    } finally {
      setLoadingIntelligence(false)
    }
  }

  const downloadPlaybook = async (lead: Lead) => {
    setDownloadingPlaybook(lead.id || '')
    try {
      const response = await axios.get(`${API_URL}/api/leads/${lead.id}/playbook`, {
        responseType: 'blob'
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Sales_Playbook_${lead.company_name.replace(/\s+/g, '_')}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error downloading playbook:', error)
      alert('Error downloading playbook. Please try again.')
    } finally {
      setDownloadingPlaybook(null)
    }
  }

  const generatePredictions = async (leadId: string) => {
    setGeneratingPredictions(leadId)
    try {
      const response = await axios.post(`${API_URL}/api/leads/${leadId}/predictions`)

      // Store prediction details on the lead object for immediate display
      const predictions = response.data.predictions
      setLeads(prev => prev.map(lead =>
        lead.id === leadId
          ? { ...lead, prediction_details: predictions }
          : lead
      ))

      // Refresh leads to show updated predictions from database
      await fetchLeads()

      return predictions
    } catch (error) {
      console.error('Error generating predictions:', error)
      alert('Error generating predictions. Please try again.')
    } finally {
      setGeneratingPredictions(null)
    }
  }

  const generateEmailTemplate = async (lead: Lead, style: 'professional' | 'casual' | 'consultative') => {
    setSelectedLead(lead)
    setEmailStyle(style)
    setLoadingEmail(true)
    setShowEmailTemplate(true)

    try {
      const response = await axios.post(`${API_URL}/api/leads/${lead.id}/email-template`, null, {
        params: { template_style: style }
      })
      setEmailTemplate(response.data)
    } catch (error) {
      console.error('Error generating email template:', error)
      alert('Error generating email template. Please try again.')
    } finally {
      setLoadingEmail(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    alert('Copied to clipboard!')
  }

  // Campaign functions
  const fetchCampaigns = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/campaigns`)
      setCampaigns(response.data)
    } catch (error) {
      console.error('Error fetching campaigns:', error)
    }
  }

  const createCampaign = async () => {
    if (!newCampaignName) {
      alert('Please enter a campaign name')
      return
    }

    setLoadingCampaigns(true)
    try {
      const response = await axios.post(`${API_URL}/api/campaigns`, null, {
        params: {
          name: newCampaignName,
          description: newCampaignDescription,
          target_industry: newCampaignIndustry || undefined,
          min_score: newCampaignMinScore,
          max_score: 100,
          channels: newCampaignChannels
        }
      })

      // Reset form
      setNewCampaignName('')
      setNewCampaignDescription('')
      setNewCampaignIndustry('')
      setNewCampaignMinScore(70)
      setNewCampaignChannels(['email'])
      setShowCreateCampaign(false)

      // Refresh campaigns
      await fetchCampaigns()

      alert(`Campaign "${newCampaignName}" created successfully!`)
    } catch (error) {
      console.error('Error creating campaign:', error)
      alert('Error creating campaign. Please try again.')
    } finally {
      setLoadingCampaigns(false)
    }
  }

  const fetchCampaignDetails = async (campaign: Campaign) => {
    setSelectedCampaign(campaign)
    setShowCampaignDetail(true)

    try {
      // Fetch analytics
      const analyticsResponse = await axios.get(`${API_URL}/api/campaigns/${campaign.id}`)
      setCampaignAnalytics(analyticsResponse.data.analytics)

      // Fetch sequences if they exist
      if (campaign.total_leads > 0) {
        const sequencesResponse = await axios.get(`${API_URL}/api/campaigns/${campaign.id}/sequences`)
        setCampaignSequences(sequencesResponse.data || [])
      }
    } catch (error) {
      console.error('Error fetching campaign details:', error)
    }
  }

  const generateCampaignSequences = async (campaignId: number) => {
    setGeneratingSequences(true)
    try {
      const response = await axios.post(`${API_URL}/api/campaigns/${campaignId}/generate-sequences`)
      setCampaignSequences(response.data.sequences)
      alert('AI sequences generated successfully!')
    } catch (error) {
      console.error('Error generating sequences:', error)
      alert('Error generating sequences. Please try again.')
    } finally {
      setGeneratingSequences(false)
    }
  }

  const addLeadsToCampaign = async (campaignId: number, leadIds: string[]) => {
    try {
      await axios.post(`${API_URL}/api/campaigns/${campaignId}/leads`, { lead_ids: leadIds })
      alert(`Added ${leadIds.length} leads to campaign`)
      await fetchCampaigns()
    } catch (error) {
      console.error('Error adding leads to campaign:', error)
      alert('Error adding leads to campaign.')
    }
  }

  const startCampaign = async (campaignId: number) => {
    try {
      await axios.post(`${API_URL}/api/campaigns/${campaignId}/start`)
      alert('Campaign started!')
      await fetchCampaigns()
      setShowCampaignDetail(false)
    } catch (error) {
      console.error('Error starting campaign:', error)
      alert('Error starting campaign. Please try again.')
    }
  }

  const toggleCampaignChannel = (channel: string) => {
    if (newCampaignChannels.includes(channel)) {
      setNewCampaignChannels(newCampaignChannels.filter(c => c !== channel))
    } else {
      setNewCampaignChannels([...newCampaignChannels, channel])
    }
  }

  // Appointment functions
  const fetchAppointments = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/appointments`)
      setAppointments(response.data)
    } catch (error) {
      console.error('Error fetching appointments:', error)
    }
  }

  const fetchAIInsights = async () => {
    setLoadingInsights(true)
    try {
      const response = await axios.get(`${API_URL}/api/analytics/ai-insights`)
      setAiInsights(response.data.insights || [])
    } catch (error) {
      console.error('Error fetching AI insights:', error)
    } finally {
      setLoadingInsights(false)
    }
  }

  const openBookingModal = (lead: Lead) => {
    setBookingLead(lead)
    setAppointmentDate('')
    setAppointmentTime('')
    setAppointmentFormat('in-person')
    setAppointmentNotes('')
    setShowBookAppointment(true)
  }

  const bookAppointment = async () => {
    if (!bookingLead || !appointmentDate || !appointmentTime) {
      alert('Please fill in date and time')
      return
    }

    setBookingAppointment(true)
    try {
      const dateTime = `${appointmentDate}T${appointmentTime}:00Z`

      await axios.post(`${API_URL}/api/appointments`, null, {
        params: {
          lead_id: bookingLead.id,
          date_time: dateTime,
          format: appointmentFormat,
          notes: appointmentNotes
        }
      })

      alert(`Appointment booked with ${bookingLead.company_name}!`)
      setShowBookAppointment(false)
      await fetchAppointments()
      await fetchAnalytics()
    } catch (error) {
      console.error('Error booking appointment:', error)
      alert('Error booking appointment. Please try again.')
    } finally {
      setBookingAppointment(false)
    }
  }

  const sendToHubSpot = async (lead: Lead) => {
    setSendingToHubSpot(lead.id || '')
    try {
      const response = await axios.post(`${API_URL}/api/leads/${lead.id}/push-to-hubspot`)

      if (response.data.success) {
        const contactCount = response.data.hubspot_contact_ids?.length || 0
        alert(`✅ Successfully sent ${lead.company_name} to HubSpot!\n\nCompany ID: ${response.data.hubspot_company_id}\nContacts Created: ${contactCount}\n\nClick OK to view in HubSpot.`)

        // Open HubSpot in new tab
        if (response.data.hubspot_url) {
          window.open(response.data.hubspot_url, '_blank')
        }

        // Refresh leads to get updated status
        fetchLeads()
      }
    } catch (error: any) {
      console.error('Error sending to HubSpot:', error)
      const errorMessage = error.response?.data?.detail || 'Error sending lead to HubSpot. Please make sure HubSpot integration is configured.'
      alert(errorMessage)
    } finally {
      setSendingToHubSpot(null)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto p-6">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                LeniLani Lead Generation Platform
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">
                AI-Powered Lead Discovery & Appointment Booking for Hawaii Businesses
              </p>
              <p className="text-sm text-gray-500 mt-1">
                Office: 1050 Queen Street, Suite 100, Honolulu, HI 96814
              </p>
            </div>
            <Link href="/settings">
              <Button variant="outline" size="lg" className="gap-2">
                <Settings className="h-5 w-5" />
                Settings
              </Button>
            </Link>
          </div>
        </motion.div>

        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <motion.div whileHover={{ scale: 1.05 }} transition={{ type: "spring" }}>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Total Leads</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-2xl font-bold">{analytics.total_leads}</div>
                  <Building2 className="h-8 w-8 text-blue-500" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }} transition={{ type: "spring" }}>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Qualified Leads</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-2xl font-bold">{Math.round(analytics.qualified_leads)}</div>
                  <Target className="h-8 w-8 text-green-500" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }} transition={{ type: "spring" }}>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Appointments</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-2xl font-bold">{analytics.appointments_booked}</div>
                  <Calendar className="h-8 w-8 text-purple-500" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }} transition={{ type: "spring" }}>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Conversion Rate</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-2xl font-bold">{(analytics.conversion_rate * 100).toFixed(1)}%</div>
                  <TrendingUp className="h-8 w-8 text-orange-500" />
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }} transition={{ type: "spring" }}>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>Revenue Potential</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div className="text-2xl font-bold">${(analytics.revenue_potential / 1000).toFixed(0)}k</div>
                  <DollarSign className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Pipeline Analytics Dashboard */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-6 w-6 text-blue-600" />
                Sales Pipeline Analytics
              </CardTitle>
              <CardDescription>Track lead progression through your sales funnel</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Pipeline Stages */}
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                {/* NEW Stage */}
                <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border-2 border-gray-300">
                  <div className="flex items-center gap-2 mb-2">
                    <Circle className="h-4 w-4 text-gray-500" />
                    <h4 className="font-semibold text-sm">New</h4>
                  </div>
                  <div className="text-3xl font-bold text-gray-700 dark:text-gray-300">
                    {leads.filter(l => l.status === 'NEW').length}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {leads.length > 0 ? ((leads.filter(l => l.status === 'NEW').length / leads.length) * 100).toFixed(0) : 0}% of total
                  </p>
                </div>

                {/* CONTACTED Stage */}
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border-2 border-blue-300">
                  <div className="flex items-center gap-2 mb-2">
                    <ArrowRight className="h-4 w-4 text-blue-500" />
                    <h4 className="font-semibold text-sm">Contacted</h4>
                  </div>
                  <div className="text-3xl font-bold text-blue-700 dark:text-blue-300">
                    {leads.filter(l => l.status === 'CONTACTED').length}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {leads.length > 0 ? ((leads.filter(l => l.status === 'CONTACTED').length / leads.length) * 100).toFixed(0) : 0}% of total
                  </p>
                </div>

                {/* QUALIFIED Stage */}
                <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg border-2 border-purple-300">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-4 w-4 text-purple-500" />
                    <h4 className="font-semibold text-sm">Qualified</h4>
                  </div>
                  <div className="text-3xl font-bold text-purple-700 dark:text-purple-300">
                    {leads.filter(l => l.status === 'QUALIFIED').length}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {leads.length > 0 ? ((leads.filter(l => l.status === 'QUALIFIED').length / leads.length) * 100).toFixed(0) : 0}% of total
                  </p>
                </div>

                {/* OPPORTUNITY Stage */}
                <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg border-2 border-yellow-300">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="h-4 w-4 text-yellow-500" />
                    <h4 className="font-semibold text-sm">Opportunity</h4>
                  </div>
                  <div className="text-3xl font-bold text-yellow-700 dark:text-yellow-300">
                    {leads.filter(l => l.status === 'OPPORTUNITY').length}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {leads.length > 0 ? ((leads.filter(l => l.status === 'OPPORTUNITY').length / leads.length) * 100).toFixed(0) : 0}% of total
                  </p>
                </div>

                {/* WON Stage */}
                <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg border-2 border-green-400">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle2 className="h-4 w-4 text-green-500" />
                    <h4 className="font-semibold text-sm">Won</h4>
                  </div>
                  <div className="text-3xl font-bold text-green-700 dark:text-green-300">
                    {leads.filter(l => l.status === 'WON').length}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {leads.length > 0 ? ((leads.filter(l => l.status === 'WON').length / leads.length) * 100).toFixed(0) : 0}% of total
                  </p>
                </div>

                {/* LOST Stage */}
                <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg border-2 border-red-300">
                  <div className="flex items-center gap-2 mb-2">
                    <XCircle className="h-4 w-4 text-red-500" />
                    <h4 className="font-semibold text-sm">Lost</h4>
                  </div>
                  <div className="text-3xl font-bold text-red-700 dark:text-red-300">
                    {leads.filter(l => l.status === 'LOST').length}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {leads.length > 0 ? ((leads.filter(l => l.status === 'LOST').length / leads.length) * 100).toFixed(0) : 0}% of total
                  </p>
                </div>
              </div>

              {/* Pipeline Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Win Rate */}
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Win Rate</h4>
                  <div className="text-2xl font-bold text-green-700 dark:text-green-300">
                    {leads.filter(l => ['WON', 'LOST'].includes(l.status)).length > 0
                      ? ((leads.filter(l => l.status === 'WON').length / leads.filter(l => ['WON', 'LOST'].includes(l.status)).length) * 100).toFixed(1)
                      : 0}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {leads.filter(l => l.status === 'WON').length} won / {leads.filter(l => ['WON', 'LOST'].includes(l.status)).length} closed
                  </p>
                </div>

                {/* Contact to Qualified */}
                <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Contact → Qualified</h4>
                  <div className="text-2xl font-bold text-purple-700 dark:text-purple-300">
                    {leads.filter(l => ['CONTACTED', 'QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                      ? ((leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length / leads.filter(l => ['CONTACTED', 'QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100).toFixed(1)
                      : 0}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Qualification rate</p>
                </div>

                {/* Qualified to Opportunity */}
                <div className="bg-gradient-to-br from-purple-50 to-yellow-50 dark:from-purple-900/20 dark:to-yellow-900/20 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Qualified → Opportunity</h4>
                  <div className="text-2xl font-bold text-yellow-700 dark:text-yellow-300">
                    {leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                      ? ((leads.filter(l => ['OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length / leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100).toFixed(1)
                      : 0}%
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Opportunity conversion</p>
                </div>

                {/* Active Pipeline Value */}
                <div className="bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-900/20 dark:to-red-900/20 p-4 rounded-lg">
                  <h4 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Active Pipeline</h4>
                  <div className="text-2xl font-bold text-orange-700 dark:text-orange-300">
                    {leads.filter(l => ['NEW', 'CONTACTED', 'QUALIFIED', 'OPPORTUNITY'].includes(l.status)).length}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Leads in progress
                  </p>
                </div>
              </div>

              {/* Pipeline Funnel Visualization */}
              <div className="mt-6">
                <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Pipeline Funnel</h4>
                <div className="space-y-2">
                  {/* New → Contacted */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-600 dark:text-gray-400">New → Contacted</span>
                      <span className="text-xs font-semibold">
                        {leads.length > 0
                          ? ((leads.filter(l => l.status !== 'NEW').length / leads.length) * 100).toFixed(0)
                          : 0}%
                      </span>
                    </div>
                    <Progress
                      value={leads.length > 0 ? (leads.filter(l => l.status !== 'NEW').length / leads.length) * 100 : 0}
                      className="h-2"
                    />
                  </div>

                  {/* Contacted → Qualified */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-600 dark:text-gray-400">Contacted → Qualified</span>
                      <span className="text-xs font-semibold">
                        {leads.filter(l => ['CONTACTED', 'QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                          ? ((leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length / leads.filter(l => ['CONTACTED', 'QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100).toFixed(0)
                          : 0}%
                      </span>
                    </div>
                    <Progress
                      value={leads.filter(l => ['CONTACTED', 'QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                        ? (leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length / leads.filter(l => ['CONTACTED', 'QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100
                        : 0}
                      className="h-2"
                    />
                  </div>

                  {/* Qualified → Opportunity */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-600 dark:text-gray-400">Qualified → Opportunity</span>
                      <span className="text-xs font-semibold">
                        {leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                          ? ((leads.filter(l => ['OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length / leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100).toFixed(0)
                          : 0}%
                      </span>
                    </div>
                    <Progress
                      value={leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                        ? (leads.filter(l => ['OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length / leads.filter(l => ['QUALIFIED', 'OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100
                        : 0}
                      className="h-2"
                    />
                  </div>

                  {/* Opportunity → Won */}
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-gray-600 dark:text-gray-400">Opportunity → Won</span>
                      <span className="text-xs font-semibold">
                        {leads.filter(l => ['OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                          ? ((leads.filter(l => l.status === 'WON').length / leads.filter(l => ['OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100).toFixed(0)
                          : 0}%
                      </span>
                    </div>
                    <Progress
                      value={leads.filter(l => ['OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length > 0
                        ? (leads.filter(l => l.status === 'WON').length / leads.filter(l => ['OPPORTUNITY', 'WON', 'LOST'].includes(l.status)).length) * 100
                        : 0}
                      className="h-2"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Outreach Modal */}
        {showOutreach && selectedLead && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full"
            >
              <h2 className="text-2xl font-bold mb-4">Generated Outreach - {selectedLead.company_name}</h2>
              <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg mb-4 max-h-96 overflow-y-auto">
                <pre className="whitespace-pre-wrap font-sans text-sm">{generatedOutreach}</pre>
              </div>
              <div className="flex gap-3">
                <Button onClick={() => sendOutreach('email')} className="flex-1">
                  <Mail className="mr-2 h-4 w-4" />
                  Send Email
                </Button>
                <Button onClick={() => sendOutreach('sms')} variant="outline" className="flex-1">
                  <MessageSquare className="mr-2 h-4 w-4" />
                  Send SMS
                </Button>
                <Button onClick={() => setShowOutreach(false)} variant="secondary">
                  Close
                </Button>
              </div>
            </motion.div>
          </div>
        )}

        {/* AI Intelligence Modal */}
        {showIntelligence && selectedLead && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-5xl w-full my-8"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    AI Sales Intelligence
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">{selectedLead.company_name}</p>
                </div>
                <Button onClick={() => setShowIntelligence(false)} variant="ghost" size="sm">✕</Button>
              </div>

              {loadingIntelligence ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Brain className="h-16 w-16 text-blue-600 animate-pulse mb-4" />
                  <p className="text-lg font-semibold">Analyzing lead with AI...</p>
                  <p className="text-sm text-gray-500 mt-2">This may take up to 90 seconds</p>
                </div>
              ) : intelligence ? (
                <div className="space-y-6 max-h-[70vh] overflow-y-auto pr-2">
                  {/* Executive Summary */}
                  <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 p-4 rounded-lg">
                    <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-blue-600" />
                      Executive Summary
                    </h3>
                    <p className="text-sm">{intelligence.executive_summary}</p>
                    <div className="mt-3">
                      <Badge className="bg-blue-600">Confidence: {intelligence.confidence}/100</Badge>
                    </div>
                  </div>

                  {/* Perplexity AI Research */}
                  {intelligence.perplexity_research?.has_recent_data && (
                    <div className="bg-gradient-to-r from-green-50 to-teal-50 dark:from-green-900/20 dark:to-teal-900/20 p-4 rounded-lg border-2 border-green-200 dark:border-green-800">
                      <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                        <Brain className="h-5 w-5 text-green-600" />
                        Recent Intelligence (Past 90 Days)
                        <Badge className="bg-green-600 text-white">Perplexity AI</Badge>
                      </h3>

                      {/* Research Summary */}
                      {intelligence.research_summary && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                          <p className="text-sm font-semibold text-green-700 dark:text-green-400">Summary:</p>
                          <p className="text-sm mt-1">{intelligence.research_summary}</p>
                        </div>
                      )}

                      {/* Recent News */}
                      {intelligence.perplexity_research.recent_news && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                          <p className="text-sm font-semibold text-blue-700 dark:text-blue-400 mb-1">📰 Recent News & Announcements:</p>
                          <p className="text-sm whitespace-pre-line">{intelligence.perplexity_research.recent_news}</p>
                        </div>
                      )}

                      {/* Leadership Updates */}
                      {intelligence.perplexity_research.leadership && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                          <p className="text-sm font-semibold text-purple-700 dark:text-purple-400 mb-1">👔 Leadership Updates:</p>
                          <p className="text-sm whitespace-pre-line">{intelligence.perplexity_research.leadership}</p>
                        </div>
                      )}

                      {/* Business Developments */}
                      {intelligence.perplexity_research.business_developments && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                          <p className="text-sm font-semibold text-indigo-700 dark:text-indigo-400 mb-1">🚀 Business Developments:</p>
                          <p className="text-sm whitespace-pre-line">{intelligence.perplexity_research.business_developments}</p>
                        </div>
                      )}

                      {/* Market Position */}
                      {intelligence.perplexity_research.market_position && (
                        <div className="mb-3 p-3 bg-white dark:bg-gray-800 rounded-lg">
                          <p className="text-sm font-semibold text-orange-700 dark:text-orange-400 mb-1">📊 Market Position:</p>
                          <p className="text-sm whitespace-pre-line">{intelligence.perplexity_research.market_position}</p>
                        </div>
                      )}

                      {/* Challenges & Opportunities */}
                      {intelligence.perplexity_research.challenges_opportunities && (
                        <div className="p-3 bg-white dark:bg-gray-800 rounded-lg">
                          <p className="text-sm font-semibold text-red-700 dark:text-red-400 mb-1">⚡ Challenges & Opportunities:</p>
                          <p className="text-sm whitespace-pre-line">{intelligence.perplexity_research.challenges_opportunities}</p>
                        </div>
                      )}
                    </div>
                  )}

                  {/* No Recent Data Message */}
                  {intelligence.perplexity_research && !intelligence.perplexity_research.has_recent_data && (
                    <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        ℹ️ No significant recent news or developments found in the past 90 days.
                      </p>
                    </div>
                  )}

                  {/* Hot Buttons */}
                  <div>
                    <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                      <Target className="h-5 w-5 text-red-600" />
                      Hot Buttons & Pain Points
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {intelligence.hot_buttons.map((button, i) => (
                        <div key={i} className="bg-red-50 dark:bg-red-900/20 p-3 rounded-lg border-l-4 border-red-600">
                          <p className="text-sm">{button}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommended Approach */}
                  <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
                    <h3 className="font-bold text-lg mb-2 flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-green-600" />
                      Recommended Approach
                    </h3>
                    <p className="text-sm">{intelligence.recommended_approach}</p>
                  </div>

                  {/* Talking Points */}
                  <div>
                    <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                      <MessageSquare className="h-5 w-5 text-purple-600" />
                      Key Talking Points
                    </h3>
                    <div className="space-y-2">
                      {intelligence.talking_points.map((point, i) => (
                        <div key={i} className="flex gap-2">
                          <Badge variant="outline">{i + 1}</Badge>
                          <p className="text-sm flex-1">{point}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Decision Maker */}
                  <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                    <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                      <Users className="h-5 w-5 text-purple-600" />
                      Decision Maker Intelligence
                    </h3>
                    {typeof intelligence.decision_maker === 'string' ? (
                      <div className="text-sm whitespace-pre-line">{intelligence.decision_maker}</div>
                    ) : (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Target Role</p>
                            <p className="text-sm">{intelligence.decision_maker?.target_role || 'N/A'}</p>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Best Contact Method</p>
                            <p className="text-sm">{intelligence.decision_maker?.best_contact || 'N/A'}</p>
                          </div>
                        </div>
                        {intelligence.decision_maker?.priorities && Array.isArray(intelligence.decision_maker.priorities) && (
                          <div className="mt-3">
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Their Priorities:</p>
                            <div className="flex flex-wrap gap-2">
                              {intelligence.decision_maker.priorities.map((priority, i) => (
                                <Badge key={i} variant="secondary">{priority}</Badge>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  {/* Budget Analysis */}
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg">
                    <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                      <DollarSign className="h-5 w-5 text-yellow-600" />
                      Budget Analysis
                    </h3>
                    {typeof intelligence.budget === 'string' ? (
                      <div className="text-sm whitespace-pre-line">{intelligence.budget}</div>
                    ) : (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Estimated Range</p>
                            <p className="text-lg font-bold text-green-600">{intelligence.budget?.estimated_range || 'N/A'}</p>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Investment Likelihood</p>
                            <Badge className={intelligence.budget?.investment_likelihood === 'High' ? 'bg-green-600' : 'bg-yellow-600'}>
                              {intelligence.budget?.investment_likelihood || 'N/A'}
                            </Badge>
                          </div>
                        </div>
                        {intelligence.budget?.signals && (
                          <div className="mt-3">
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Signals</p>
                            <p className="text-sm">{intelligence.budget.signals}</p>
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  {/* Competitive Positioning */}
                  <div>
                    <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                      <Building2 className="h-5 w-5 text-orange-600" />
                      Competitive Positioning
                    </h3>
                    {typeof intelligence.competitive_positioning === 'string' ? (
                      <div className="text-sm whitespace-pre-line">{intelligence.competitive_positioning}</div>
                    ) : (
                      <>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Likely Competitors</p>
                            <div className="space-y-1">
                              {intelligence.competitive_positioning?.likely_competitors && Array.isArray(intelligence.competitive_positioning.likely_competitors) ? (
                                intelligence.competitive_positioning.likely_competitors.map((comp, i) => (
                                  <p key={i} className="text-sm">• {comp}</p>
                                ))
                              ) : (
                                <p className="text-sm">N/A</p>
                              )}
                            </div>
                          </div>
                          <div>
                            <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Our Differentiators</p>
                            <div className="space-y-1">
                              {intelligence.competitive_positioning?.our_differentiators && Array.isArray(intelligence.competitive_positioning.our_differentiators) ? (
                                intelligence.competitive_positioning.our_differentiators.map((diff, i) => (
                                  <p key={i} className="text-sm text-green-600 dark:text-green-400">✓ {diff}</p>
                                ))
                              ) : (
                                <p className="text-sm">N/A</p>
                              )}
                            </div>
                          </div>
                        </div>
                        {intelligence.competitive_positioning?.hawaii_advantage && (
                          <div className="mt-3 bg-blue-100 dark:bg-blue-900/40 p-3 rounded">
                            <p className="text-sm font-semibold text-blue-900 dark:text-blue-100">Hawaii Advantage</p>
                            <p className="text-sm text-blue-800 dark:text-blue-200">{intelligence.competitive_positioning.hawaii_advantage}</p>
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  {/* Appointment Strategy */}
                  <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
                    <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                      <Calendar className="h-5 w-5 text-teal-600" />
                      Appointment Setting Strategy
                    </h3>
                    {typeof intelligence.appointment_strategy === 'string' ? (
                      <div className="text-sm whitespace-pre-line">{intelligence.appointment_strategy}</div>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Hook</p>
                          <p className="text-sm font-bold text-teal-600">{intelligence.appointment_strategy?.hook || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Format</p>
                          <p className="text-sm">{intelligence.appointment_strategy?.format || 'N/A'}</p>
                        </div>
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Follow-up Cadence</p>
                          <p className="text-sm">{intelligence.appointment_strategy?.follow_up_cadence || 'N/A'}</p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Next Steps */}
                  <div>
                    <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-indigo-600" />
                      Next Steps
                    </h3>
                    <div className="space-y-2">
                      {intelligence.next_steps.map((step, i) => (
                        <div key={i} className="flex gap-3 items-start">
                          <Badge className="bg-indigo-600 mt-1">{i + 1}</Badge>
                          <p className="text-sm flex-1">{step}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-center text-gray-500 py-8">No intelligence data available</p>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 mt-6 pt-6 border-t">
                <Button
                  onClick={() => downloadPlaybook(selectedLead)}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600"
                  disabled={downloadingPlaybook === selectedLead.id}
                >
                  {downloadingPlaybook === selectedLead.id ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Downloading...
                    </>
                  ) : (
                    <>
                      <Download className="mr-2 h-4 w-4" />
                      Download PDF Playbook
                    </>
                  )}
                </Button>
                <Button onClick={() => {
                  setShowIntelligence(false)
                  generateEmailTemplate(selectedLead, 'professional')
                }} className="flex-1 bg-gradient-to-r from-green-600 to-teal-600">
                  <Mail className="mr-2 h-4 w-4" />
                  Generate Email
                </Button>
                <Button onClick={() => setShowIntelligence(false)} variant="outline">
                  Close
                </Button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Email Template Modal */}
        {showEmailTemplate && selectedLead && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold">Smart Email Template</h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">{selectedLead.company_name}</p>
                </div>
                <Button onClick={() => setShowEmailTemplate(false)} variant="ghost" size="sm">✕</Button>
              </div>

              {/* Style Selector */}
              <div className="mb-6">
                <p className="text-sm font-semibold mb-2">Email Style:</p>
                <div className="flex gap-2">
                  <Button
                    onClick={() => generateEmailTemplate(selectedLead, 'professional')}
                    variant={emailStyle === 'professional' ? 'default' : 'outline'}
                    size="sm"
                  >
                    Professional
                  </Button>
                  <Button
                    onClick={() => generateEmailTemplate(selectedLead, 'casual')}
                    variant={emailStyle === 'casual' ? 'default' : 'outline'}
                    size="sm"
                  >
                    Casual
                  </Button>
                  <Button
                    onClick={() => generateEmailTemplate(selectedLead, 'consultative')}
                    variant={emailStyle === 'consultative' ? 'default' : 'outline'}
                    size="sm"
                  >
                    Consultative
                  </Button>
                </div>
              </div>

              {loadingEmail ? (
                <div className="flex flex-col items-center justify-center py-12">
                  <Mail className="h-16 w-16 text-blue-600 animate-pulse mb-4" />
                  <p className="text-lg font-semibold">Generating email template...</p>
                </div>
              ) : emailTemplate ? (
                <div className="space-y-4">
                  {/* Subject */}
                  <div>
                    <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Subject:</p>
                    <div className="bg-gray-50 dark:bg-gray-900 p-3 rounded-lg flex justify-between items-center">
                      <p className="text-sm font-semibold">{emailTemplate.subject}</p>
                      <Button onClick={() => copyToClipboard(emailTemplate.subject)} size="sm" variant="ghost">
                        Copy
                      </Button>
                    </div>
                  </div>

                  {/* Body */}
                  <div>
                    <p className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2">Body:</p>
                    <div className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg">
                      <pre className="whitespace-pre-wrap font-sans text-sm">{emailTemplate.body}</pre>
                    </div>
                    <Button onClick={() => copyToClipboard(emailTemplate.body)} size="sm" className="mt-2">
                      Copy Email Body
                    </Button>
                  </div>

                  {/* Intelligence Summary */}
                  <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                    <h3 className="font-bold mb-3">Key Intelligence Used:</h3>
                    <div className="space-y-2 text-sm">
                      <div>
                        <p className="font-semibold text-gray-600 dark:text-gray-400">Hot Buttons:</p>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {emailTemplate.intelligence_summary.hot_buttons.map((button, i) => (
                            <Badge key={i} variant="secondary">{button}</Badge>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="font-semibold text-gray-600 dark:text-gray-400">Hook:</p>
                        <p className="text-blue-600 font-semibold">{emailTemplate.intelligence_summary.hook}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : null}

              <div className="flex gap-3 mt-6 pt-6 border-t">
                <Button onClick={() => copyToClipboard(`Subject: ${emailTemplate?.subject}\n\n${emailTemplate?.body}`)} className="flex-1">
                  Copy Full Email
                </Button>
                <Button onClick={() => setShowEmailTemplate(false)} variant="outline">
                  Close
                </Button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Create Campaign Modal */}
        {showCreateCampaign && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold">Create New Campaign</h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">Set up an automated outreach campaign</p>
                </div>
                <Button onClick={() => setShowCreateCampaign(false)} variant="ghost" size="sm">✕</Button>
              </div>

              <div className="space-y-4">
                {/* Campaign Name */}
                <div>
                  <label className="text-sm font-semibold block mb-2">Campaign Name *</label>
                  <input
                    type="text"
                    value={newCampaignName}
                    onChange={(e) => setNewCampaignName(e.target.value)}
                    placeholder="e.g., Tourism AI Chatbot Outreach"
                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-900 dark:border-gray-700"
                  />
                </div>

                {/* Description */}
                <div>
                  <label className="text-sm font-semibold block mb-2">Description</label>
                  <textarea
                    value={newCampaignDescription}
                    onChange={(e) => setNewCampaignDescription(e.target.value)}
                    placeholder="What is this campaign about?"
                    rows={3}
                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-900 dark:border-gray-700"
                  />
                </div>

                {/* Target Industry */}
                <div>
                  <label className="text-sm font-semibold block mb-2">Target Industry (Optional)</label>
                  <select
                    value={newCampaignIndustry}
                    onChange={(e) => setNewCampaignIndustry(e.target.value)}
                    className="w-full px-4 py-2 border rounded-lg dark:bg-gray-900 dark:border-gray-700"
                  >
                    <option value="">All Industries</option>
                    <option value="Tourism & Hospitality">Tourism & Hospitality</option>
                    <option value="Healthcare">Healthcare</option>
                    <option value="Retail">Retail</option>
                    <option value="Real Estate">Real Estate</option>
                    <option value="Professional Services">Professional Services</option>
                    <option value="Education">Education</option>
                  </select>
                </div>

                {/* Min Score */}
                <div>
                  <label className="text-sm font-semibold block mb-2">Minimum Lead Score: {newCampaignMinScore}</label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={newCampaignMinScore}
                    onChange={(e) => setNewCampaignMinScore(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0 (All)</span>
                    <span>50 (Moderate)</span>
                    <span>100 (High)</span>
                  </div>
                </div>

                {/* Channels */}
                <div>
                  <label className="text-sm font-semibold block mb-2">Outreach Channels</label>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      onClick={() => toggleCampaignChannel('email')}
                      variant={newCampaignChannels.includes('email') ? 'default' : 'outline'}
                      size="sm"
                    >
                      <Mail className="mr-2 h-4 w-4" />
                      Email
                    </Button>
                    <Button
                      type="button"
                      onClick={() => toggleCampaignChannel('sms')}
                      variant={newCampaignChannels.includes('sms') ? 'default' : 'outline'}
                      size="sm"
                    >
                      <MessageSquare className="mr-2 h-4 w-4" />
                      SMS
                    </Button>
                    <Button
                      type="button"
                      onClick={() => toggleCampaignChannel('linkedin')}
                      variant={newCampaignChannels.includes('linkedin') ? 'default' : 'outline'}
                      size="sm"
                      disabled
                    >
                      <Users className="mr-2 h-4 w-4" />
                      LinkedIn (Soon)
                    </Button>
                  </div>
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t">
                <Button
                  onClick={createCampaign}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600"
                  disabled={loadingCampaigns || !newCampaignName}
                >
                  {loadingCampaigns ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Create Campaign
                    </>
                  )}
                </Button>
                <Button onClick={() => setShowCreateCampaign(false)} variant="outline">
                  Cancel
                </Button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Campaign Details Modal */}
        {showCampaignDetail && selectedCampaign && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-5xl w-full my-8"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {selectedCampaign.name}
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">{selectedCampaign.description}</p>
                </div>
                <Button onClick={() => setShowCampaignDetail(false)} variant="ghost" size="sm">✕</Button>
              </div>

              {/* Campaign Analytics */}
              {campaignAnalytics && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold">{campaignAnalytics.total_leads}</div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Total Leads</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold text-blue-600">{campaignAnalytics.contacted_leads}</div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Contacted</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold text-green-600">{campaignAnalytics.replied_count}</div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Replied</p>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold text-purple-600">{campaignAnalytics.conversion_rate}%</div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">Conversion Rate</p>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Progress Bar */}
              {campaignAnalytics && campaignAnalytics.total_leads > 0 && (
                <div className="mb-6">
                  <div className="flex justify-between text-sm mb-2">
                    <span>Campaign Progress</span>
                    <span>{campaignAnalytics.progress}%</span>
                  </div>
                  <Progress value={campaignAnalytics.progress} />
                </div>
              )}

              {/* Campaign Sequences */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold">Outreach Sequences</h3>
                  {campaignSequences.length === 0 && (
                    <Button
                      onClick={() => generateCampaignSequences(selectedCampaign.id)}
                      disabled={generatingSequences}
                      size="sm"
                      className="bg-gradient-to-r from-blue-600 to-purple-600"
                    >
                      {generatingSequences ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Sparkles className="mr-2 h-4 w-4" />
                          Generate AI Sequences
                        </>
                      )}
                    </Button>
                  )}
                </div>

                {campaignSequences.length > 0 ? (
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {campaignSequences.map((sequence, index) => (
                      <div key={index} className="p-4 border rounded-lg bg-gray-50 dark:bg-gray-900">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge>Step {sequence.sequence_number}</Badge>
                          <Badge variant="outline">{sequence.channel}</Badge>
                          {sequence.delay_days > 0 && (
                            <span className="text-xs text-gray-500">+{sequence.delay_days} days</span>
                          )}
                        </div>
                        {sequence.subject && (
                          <p className="font-semibold text-sm mb-2">Subject: {sequence.subject}</p>
                        )}
                        <p className="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{sequence.content}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Brain className="h-12 w-12 mx-auto mb-3 text-gray-400" />
                    <p>No sequences yet. Generate AI-powered sequences to get started!</p>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-6 border-t">
                {selectedCampaign.status === 'draft' && (
                  <Button
                    onClick={() => startCampaign(selectedCampaign.id)}
                    className="flex-1 bg-gradient-to-r from-green-600 to-teal-600"
                    disabled={campaignSequences.length === 0}
                  >
                    <Target className="mr-2 h-4 w-4" />
                    Start Campaign
                  </Button>
                )}
                <Button onClick={() => setShowCampaignDetail(false)} variant="outline">
                  Close
                </Button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Book Appointment Modal */}
        {showBookAppointment && bookingLead && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-lg w-full"
            >
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold">Book Appointment</h2>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">
                    Schedule a meeting with {bookingLead.company_name}
                  </p>
                </div>
                <Button onClick={() => setShowBookAppointment(false)} variant="ghost" size="sm">✕</Button>
              </div>

              <div className="space-y-4">
                {/* Date Picker */}
                <div>
                  <label className="block text-sm font-medium mb-2">Date</label>
                  <input
                    type="date"
                    value={appointmentDate}
                    onChange={(e) => setAppointmentDate(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>

                {/* Time Picker */}
                <div>
                  <label className="block text-sm font-medium mb-2">Time</label>
                  <input
                    type="time"
                    value={appointmentTime}
                    onChange={(e) => setAppointmentTime(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  />
                </div>

                {/* Format Selection */}
                <div>
                  <label className="block text-sm font-medium mb-2">Meeting Format</label>
                  <select
                    value={appointmentFormat}
                    onChange={(e) => setAppointmentFormat(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                  >
                    <option value="in-person">In-Person (Honolulu Office)</option>
                    <option value="virtual">Virtual Meeting</option>
                    <option value="phone">Phone Call</option>
                  </select>
                </div>

                {/* Location Display */}
                {appointmentFormat === 'in-person' && (
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-sm text-blue-800 dark:text-blue-300">
                      📍 1050 Queen Street, Suite 100, Honolulu, HI 96814
                    </p>
                  </div>
                )}

                {/* Notes */}
                <div>
                  <label className="block text-sm font-medium mb-2">Notes (Optional)</label>
                  <textarea
                    value={appointmentNotes}
                    onChange={(e) => setAppointmentNotes(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600"
                    rows={3}
                    placeholder="Add any notes or agenda items..."
                  />
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 mt-6 pt-6 border-t">
                <Button
                  onClick={bookAppointment}
                  disabled={bookingAppointment || !appointmentDate || !appointmentTime}
                  className="flex-1 bg-gradient-to-r from-green-600 to-teal-600"
                >
                  {bookingAppointment ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Booking...
                    </>
                  ) : (
                    <>
                      <Calendar className="mr-2 h-4 w-4" />
                      Book Appointment
                    </>
                  )}
                </Button>
                <Button onClick={() => setShowBookAppointment(false)} variant="outline">
                  Cancel
                </Button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Lead Detail Modal */}
        {showLeadDetail && detailLead && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-4xl w-full my-8"
            >
              {/* Header */}
              <div className="flex justify-between items-start mb-6 pb-4 border-b">
                <div>
                  <h2 className="text-3xl font-bold">{detailLead.company_name}</h2>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    <Badge variant={detailLead.score > 70 ? 'default' : 'secondary'} className="text-sm">
                      <Award className="mr-1 h-3 w-3" />
                      Score: {detailLead.score.toFixed(0)}
                    </Badge>
                    <Badge variant="outline" className="text-sm">
                      <Briefcase className="mr-1 h-3 w-3" />
                      {detailLead.industry}
                    </Badge>
                    <Badge
                      className={
                        detailLead.status === 'IN_HUBSPOT'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                          : detailLead.status === 'RESEARCHED'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100'
                          : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-100'
                      }
                    >
                      {detailLead.status === 'IN_HUBSPOT' ? 'In HubSpot' : detailLead.status === 'RESEARCHED' ? 'Researched' : 'New'}
                    </Badge>
                  </div>
                </div>
                <Button onClick={() => setShowLeadDetail(false)} variant="ghost" size="sm">✕</Button>
              </div>

              {/* Content Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-h-[70vh] overflow-y-auto pr-2">
                {/* Company Information */}
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Building2 className="h-5 w-5 text-blue-600" />
                      Company Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {detailLead.website && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Website</p>
                          <a
                            href={detailLead.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline flex items-center gap-1"
                          >
                            <Globe className="h-4 w-4" />
                            {detailLead.website.replace(/^https?:\/\//, '')}
                          </a>
                        </div>
                      )}
                      {detailLead.phone && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Phone</p>
                          <a href={`tel:${detailLead.phone}`} className="text-blue-600 hover:underline flex items-center gap-1">
                            <Phone className="h-4 w-4" />
                            {detailLead.phone}
                          </a>
                        </div>
                      )}
                      {detailLead.email && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Email</p>
                          <a href={`mailto:${detailLead.email}`} className="text-blue-600 hover:underline flex items-center gap-1">
                            <Mail className="h-4 w-4" />
                            {detailLead.email}
                          </a>
                        </div>
                      )}
                      {detailLead.location && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Location</p>
                          <p className="flex items-center gap-1">
                            <MapPin className="h-4 w-4 text-red-600" />
                            {detailLead.location}
                          </p>
                        </div>
                      )}
                      {detailLead.employee_count && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Employees</p>
                          <p className="flex items-center gap-1">
                            <Users className="h-4 w-4 text-purple-600" />
                            {detailLead.employee_count} employees
                          </p>
                        </div>
                      )}
                      {detailLead.email_pattern && (
                        <div>
                          <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Email Pattern</p>
                          <p className="font-mono text-sm">{detailLead.email_pattern}</p>
                        </div>
                      )}
                      <div>
                        <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Source</p>
                        <p>{detailLead.source || 'N/A'}</p>
                      </div>
                      <div>
                        <p className="text-sm font-semibold text-gray-600 dark:text-gray-400">Created</p>
                        <p>{new Date(detailLead.created_at).toLocaleString()}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Decision Makers */}
                {detailLead.decision_makers && detailLead.decision_makers.length > 0 && (
                  <Card className="md:col-span-2">
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Users className="h-5 w-5 text-purple-600" />
                        Decision Makers ({detailLead.decision_makers.length})
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {detailLead.decision_makers.map((dm, i) => (
                          <div key={i} className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                            <div className="flex justify-between items-start mb-2">
                              <div>
                                <p className="font-semibold text-gray-900 dark:text-gray-100">{dm.name}</p>
                                <p className="text-sm text-gray-600 dark:text-gray-400">{dm.title}</p>
                              </div>
                              {dm.confidence && (
                                <Badge variant="outline" className="text-xs">
                                  {Math.round(dm.confidence * 100)}%
                                </Badge>
                              )}
                            </div>
                            <div className="space-y-1 text-sm">
                              {dm.email && (
                                <a href={`mailto:${dm.email}`} className="text-blue-600 hover:text-blue-800 flex items-center gap-1">
                                  <Mail className="h-3 w-3" />
                                  {dm.email}
                                </a>
                              )}
                              {dm.phone && (
                                <a href={`tel:${dm.phone}`} className="text-green-600 hover:text-green-800 flex items-center gap-1">
                                  <Phone className="h-3 w-3" />
                                  {dm.phone}
                                </a>
                              )}
                              {dm.linkedin && (
                                <a href={dm.linkedin} target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:text-purple-800 flex items-center gap-1">
                                  🔗 LinkedIn
                                </a>
                              )}
                            </div>
                            {dm.source && (
                              <p className="text-xs text-gray-400 mt-2">via {dm.source}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Pain Points */}
                {detailLead.pain_points && detailLead.pain_points.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Target className="h-5 w-5 text-red-600" />
                        Pain Points
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {detailLead.pain_points.map((pain, i) => (
                          <div key={i} className="flex gap-2 items-start">
                            <Badge variant="outline" className="shrink-0">{i + 1}</Badge>
                            <p className="text-sm">{pain}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Tech Stack */}
                {detailLead.tech_stack && detailLead.tech_stack.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-yellow-600" />
                        Tech Stack
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="flex flex-wrap gap-2">
                        {detailLead.tech_stack.map((tech, i) => (
                          <Badge key={i} variant="secondary">{tech}</Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Actions Footer */}
              <div className="mt-6 pt-6 border-t flex gap-2 flex-wrap justify-end">
                <Button
                  size="sm"
                  onClick={() => {
                    setShowLeadDetail(false)
                    fetchIntelligence(detailLead)
                  }}
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                >
                  <Brain className="mr-2 h-4 w-4" />
                  View AI Intelligence
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    setShowLeadDetail(false)
                    generateEmailTemplate(detailLead, 'professional')
                  }}
                  variant="outline"
                >
                  <Mail className="mr-2 h-4 w-4" />
                  Generate Email
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    setShowLeadDetail(false)
                    openBookingModal(detailLead)
                  }}
                  className="bg-gradient-to-r from-green-600 to-teal-600"
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  Book Meeting
                </Button>
                <Button onClick={() => setShowLeadDetail(false)} variant="outline">
                  Close
                </Button>
              </div>
            </motion.div>
          </div>
        )}

        {/* Main Content */}
        <Tabs defaultValue="leads" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="leads">Leads</TabsTrigger>
            <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
            <TabsTrigger value="appointments">Appointments</TabsTrigger>
            <TabsTrigger value="ai-insights">AI Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="leads">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Lead Pipeline</CardTitle>
                    <CardDescription>Discovered Hawaii businesses with potential</CardDescription>
                  </div>
                  <Button
                    onClick={startDiscovery}
                    disabled={isDiscovering}
                    className="bg-gradient-to-r from-blue-600 to-purple-600"
                  >
                    {isDiscovering ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Discovering & Scoring Leads... (5-10 min)
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        Discover New Leads
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {/* Status Filter Tabs */}
                <div className="mb-6 flex gap-2 border-b overflow-x-auto">
                  <button
                    onClick={() => setStatusFilter('ALL')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'ALL'
                        ? 'border-blue-600 text-blue-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    All ({leads.length})
                  </button>

                  <button
                    onClick={() => setStatusFilter('NEW')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'NEW'
                        ? 'border-gray-600 text-gray-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Circle className="inline h-3 w-3 mr-1" />
                    New ({leads.filter(l => l.status === 'NEW').length})
                  </button>

                  {/* AI Analyzed Filter - Second step after new lead */}
                  <button
                    onClick={() => setStatusFilter('AI_ANALYZED')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'AI_ANALYZED'
                        ? 'border-purple-600 text-purple-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Brain className="inline h-3 w-3 mr-1" />
                    AI Analyzed ({leads.filter(l => l.has_intelligence).length})
                  </button>

                  {/* Divider */}
                  <div className="border-l border-gray-300 mx-2"></div>
                  <button
                    onClick={() => setStatusFilter('CONTACTED')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'CONTACTED'
                        ? 'border-blue-600 text-blue-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <ArrowRight className="inline h-3 w-3 mr-1" />
                    Contacted ({leads.filter(l => l.status === 'CONTACTED').length})
                  </button>
                  <button
                    onClick={() => setStatusFilter('QUALIFIED')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'QUALIFIED'
                        ? 'border-indigo-600 text-indigo-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <CheckCircle2 className="inline h-3 w-3 mr-1" />
                    Qualified ({leads.filter(l => l.status === 'QUALIFIED').length})
                  </button>
                  <button
                    onClick={() => setStatusFilter('OPPORTUNITY')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'OPPORTUNITY'
                        ? 'border-yellow-600 text-yellow-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Target className="inline h-3 w-3 mr-1" />
                    Opportunity ({leads.filter(l => l.status === 'OPPORTUNITY').length})
                  </button>
                  <button
                    onClick={() => setStatusFilter('WON')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'WON'
                        ? 'border-green-600 text-green-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <CheckCircle2 className="inline h-3 w-3 mr-1" />
                    Won ({leads.filter(l => l.status === 'WON').length})
                  </button>
                  <button
                    onClick={() => setStatusFilter('LOST')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'LOST'
                        ? 'border-red-600 text-red-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <XCircle className="inline h-3 w-3 mr-1" />
                    Lost ({leads.filter(l => l.status === 'LOST').length})
                  </button>

                  {/* Divider */}
                  <div className="border-l border-gray-300 mx-2"></div>

                  {/* HubSpot Filter */}
                  <button
                    onClick={() => setStatusFilter('IN_HUBSPOT')}
                    className={`px-4 py-2 border-b-2 transition-colors whitespace-nowrap ${
                      statusFilter === 'IN_HUBSPOT'
                        ? 'border-orange-600 text-orange-600 font-medium'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    <Upload className="inline h-3 w-3 mr-1" />
                    In HubSpot ({leads.filter(l => l.hubspot_company_id).length})
                  </button>
                </div>

                <div className="space-y-4">
                  {leads.length === 0 ? (
                    <div className="text-center py-12">
                      <Brain className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                      <p className="text-gray-600 dark:text-gray-400">
                        No leads yet. Click "Discover New Leads" to get started!
                      </p>
                    </div>
                  ) : (
                    leads.filter(lead => {
                      if (statusFilter === 'ALL') return true
                      if (statusFilter === 'IN_HUBSPOT') return !!lead.hubspot_company_id
                      if (statusFilter === 'AI_ANALYZED') return !!lead.has_intelligence
                      return lead.status === statusFilter
                    }).map((lead, index) => (
                      <motion.div
                        key={lead.id || index}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="border rounded-lg hover:shadow-lg transition-shadow"
                      >
                        <div className="flex items-center justify-between p-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 flex-wrap">
                              <h3 className="font-semibold text-lg">{lead.company_name}</h3>
                              <Badge variant={lead.score > 70 ? 'default' : 'secondary'}>
                                Score: {lead.score.toFixed(0)}
                              </Badge>
                              <Badge variant="outline">{lead.industry}</Badge>

                              {/* HubSpot Sync Badge */}
                              {lead.hubspot_company_id && (
                                <Badge className="bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-100">
                                  🔗 HubSpot
                                </Badge>
                              )}

                              {/* AI Intelligence Badge */}
                              {lead.has_intelligence && (
                                <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100">
                                  🧠 AI Analyzed
                                </Badge>
                              )}
                            </div>

                            {/* Predictive Analytics Display - Enhanced */}
                            {(lead.prediction_details || lead.conversion_probability !== undefined) && (() => {
                              // Use prediction_details if available, otherwise fall back to top-level fields
                              const pd = lead.prediction_details || lead
                              return (
                              <div className="mt-3 p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg border border-green-200 dark:border-green-800">
                                {/* Header */}
                                <div className="flex items-center gap-2 mb-3 pb-2 border-b border-green-300 dark:border-green-700">
                                  <TrendingUp className="h-4 w-4 text-green-600" />
                                  <h4 className="text-sm font-semibold text-green-900 dark:text-green-100">AI Predictive Analytics</h4>
                                </div>

                                {/* Summary Row */}
                                <div className="flex items-center gap-4 flex-wrap text-xs mb-3">
                                  {pd.conversion_probability !== undefined && (
                                    <div className="flex items-center gap-1">
                                      <TrendingUp className="h-3 w-3 text-green-600" />
                                      <span className="font-semibold text-green-900 dark:text-green-100">
                                        {pd.conversion_probability.toFixed(0)}% Conversion
                                      </span>
                                      {pd.conversion_confidence && (
                                        <span className="text-gray-600 dark:text-gray-400 ml-1">
                                          ({pd.conversion_confidence.toFixed(0)}% confident)
                                        </span>
                                      )}
                                    </div>
                                  )}
                                  {pd.icp_match_score !== undefined && (
                                    <div className="flex items-center gap-1">
                                      <Target className="h-3 w-3 text-blue-600" />
                                      <span className="font-semibold text-blue-900 dark:text-blue-100">
                                        {pd.icp_match_score.toFixed(0)}% ICP Match
                                      </span>
                                    </div>
                                  )}
                                  {pd.velocity_score !== undefined && (
                                    <div className="flex items-center gap-1">
                                      <Zap className="h-3 w-3 text-yellow-600" />
                                      <span className="font-semibold text-yellow-900 dark:text-yellow-100">
                                        {pd.velocity_score.toFixed(0)} Velocity
                                      </span>
                                    </div>
                                  )}
                                </div>

                                {/* Conversion Factors */}
                                {pd.conversion_factors && (
                                  <div className="mb-3">
                                    {pd.conversion_factors.positive && pd.conversion_factors.positive.length > 0 && (
                                      <div className="mb-2">
                                        <div className="text-xs font-semibold text-green-700 dark:text-green-300 mb-1">
                                          ✓ Positive Factors:
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                          {pd.conversion_factors.positive.map((factor, idx) => (
                                            <span key={idx} className="text-xs px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200 rounded">
                                              {factor}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                    {pd.conversion_factors.negative && pd.conversion_factors.negative.length > 0 && (
                                      <div className="mb-2">
                                        <div className="text-xs font-semibold text-red-700 dark:text-red-300 mb-1">
                                          ⚠ Risk Factors:
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                          {pd.conversion_factors.negative.map((factor, idx) => (
                                            <span key={idx} className="text-xs px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200 rounded">
                                              {factor}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                )}

                                {/* ICP Factors */}
                                {(pd.icp_matching_factors || pd.icp_missing_factors) && (
                                  <div className="mb-3 pb-3 border-b border-green-200 dark:border-green-800">
                                    {pd.icp_matching_factors && pd.icp_matching_factors.length > 0 && (
                                      <div className="mb-2">
                                        <div className="text-xs font-semibold text-blue-700 dark:text-blue-300 mb-1">
                                          ✓ ICP Matches:
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                          {pd.icp_matching_factors.map((factor, idx) => (
                                            <span key={idx} className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 rounded">
                                              {factor}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                    {pd.icp_missing_factors && pd.icp_missing_factors.length > 0 && (
                                      <div>
                                        <div className="text-xs font-semibold text-orange-700 dark:text-orange-300 mb-1">
                                          ⚠ Missing:
                                        </div>
                                        <div className="flex flex-wrap gap-1">
                                          {pd.icp_missing_factors.map((factor, idx) => (
                                            <span key={idx} className="text-xs px-2 py-0.5 bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200 rounded">
                                              {factor}
                                            </span>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                )}

                                {/* Velocity Insight */}
                                {pd.velocity_insight && (
                                  <div className="mb-3 pb-3 border-b border-green-200 dark:border-green-800">
                                    <div className="text-xs">
                                      <span className="font-semibold text-yellow-700 dark:text-yellow-300">Pipeline Velocity:</span>
                                      <span className="text-gray-700 dark:text-gray-300 ml-1">{pd.velocity_insight}</span>
                                      {pd.days_in_pipeline !== undefined && (
                                        <span className="text-gray-600 dark:text-gray-400 ml-1">
                                          ({pd.days_in_pipeline} days in pipeline)
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                )}

                                {/* Recommended Action */}
                                {pd.recommended_action && (
                                  <div className="mb-3">
                                    <div className="flex items-start gap-2">
                                      <Sparkles className="h-3 w-3 text-purple-600 mt-0.5 flex-shrink-0" />
                                      <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-1">
                                          <span className="text-xs font-semibold text-purple-900 dark:text-purple-100">
                                            {pd.recommended_action}
                                          </span>
                                          {pd.action_priority && (
                                            <span className={`text-xs px-2 py-0.5 rounded ${
                                              pd.action_priority === 'critical'
                                                ? 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200'
                                                : pd.action_priority === 'high'
                                                ? 'bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-200'
                                                : pd.action_priority === 'medium'
                                                ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-200'
                                                : 'bg-gray-100 dark:bg-gray-900/30 text-gray-800 dark:text-gray-200'
                                            }`}>
                                              {pd.action_priority}
                                            </span>
                                          )}
                                          {pd.action_timing && (
                                            <span className="text-xs text-gray-600 dark:text-gray-400">
                                              {pd.action_timing}
                                            </span>
                                          )}
                                        </div>
                                        {pd.action_reasoning && (
                                          <div className="text-xs text-gray-700 dark:text-gray-300">
                                            {pd.action_reasoning}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  </div>
                                )}

                                {/* Best Contact Time */}
                                {pd.best_contact_time && (
                                  <div className="flex items-center gap-2 text-xs">
                                    <Clock className="h-3 w-3 text-indigo-600" />
                                    <span className="font-semibold text-indigo-700 dark:text-indigo-300">Best Contact Time:</span>
                                    <span className="text-gray-700 dark:text-gray-300">{pd.best_contact_time}</span>
                                  </div>
                                )}
                              </div>
                            )})()}

                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {lead.location} {lead.employee_count && `• ${lead.employee_count} employees`}
                            </p>
                            <div className="flex gap-2 mt-2 flex-wrap">
                              {lead.pain_points?.slice(0, 3).map((pain, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  {pain}
                                </Badge>
                              ))}
                            </div>
                            {/* Contact Information */}
                            {(lead.phone || lead.website || lead.email) && (
                              <div className="flex gap-3 mt-2 text-xs text-gray-500 dark:text-gray-400 flex-wrap">
                                {lead.phone && (
                                  <a href={`tel:${lead.phone}`} className="hover:text-blue-600 flex items-center gap-1">
                                    📞 {lead.phone}
                                  </a>
                                )}
                                {lead.website && (
                                  <a
                                    href={lead.website}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="hover:text-blue-600 flex items-center gap-1"
                                  >
                                    🌐 {lead.website.replace(/^https?:\/\//, '')}
                                  </a>
                                )}
                                {lead.email && (
                                  <a href={`mailto:${lead.email}`} className="hover:text-blue-600 flex items-center gap-1">
                                    ✉️ {lead.email}
                                  </a>
                                )}
                              </div>
                            )}
                            {/* Decision Makers */}
                            {lead.decision_makers && lead.decision_makers.length > 0 && (
                              <div className="mt-3 p-3 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                                <p className="text-xs font-semibold text-blue-900 dark:text-blue-100 mb-2 flex items-center gap-1">
                                  <Users className="h-3 w-3" />
                                  Decision Makers ({lead.decision_makers.length})
                                </p>
                                <div className="space-y-2">
                                  {lead.decision_makers.slice(0, 3).map((dm, i) => (
                                    <div key={i} className="text-xs bg-white dark:bg-gray-800 p-2 rounded border border-blue-100 dark:border-blue-900">
                                      <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1">
                                          <p className="font-semibold text-gray-900 dark:text-gray-100">{dm.name}</p>
                                          <p className="text-gray-600 dark:text-gray-400">{dm.title}</p>
                                        </div>
                                        {dm.confidence && (
                                          <Badge variant="outline" className="text-xs">
                                            {Math.round(dm.confidence * 100)}%
                                          </Badge>
                                        )}
                                      </div>
                                      <div className="mt-1 flex flex-col gap-1">
                                        {dm.email && (
                                          <a href={`mailto:${dm.email}`} className="text-blue-600 hover:text-blue-800 flex items-center gap-1">
                                            ✉️ {dm.email}
                                          </a>
                                        )}
                                        {dm.phone && (
                                          <a href={`tel:${dm.phone}`} className="text-green-600 hover:text-green-800 flex items-center gap-1">
                                            📞 {dm.phone}
                                          </a>
                                        )}
                                        {dm.linkedin && (
                                          <a href={dm.linkedin} target="_blank" rel="noopener noreferrer" className="text-purple-600 hover:text-purple-800 flex items-center gap-1">
                                            🔗 LinkedIn
                                          </a>
                                        )}
                                      </div>
                                      {dm.source && (
                                        <p className="text-xs text-gray-400 mt-1">via {dm.source}</p>
                                      )}
                                    </div>
                                  ))}
                                  {lead.decision_makers.length > 3 && (
                                    <p className="text-xs text-gray-500 text-center pt-1">
                                      +{lead.decision_makers.length - 3} more
                                    </p>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Action Buttons Row */}
                        <div className="px-4 pb-4 flex gap-2 flex-wrap">
                          <Button
                            size="sm"
                            onClick={() => {
                              setDetailLead(lead)
                              setShowLeadDetail(true)
                            }}
                            variant="outline"
                            title="View Full Lead Details"
                          >
                            <Eye className="mr-2 h-4 w-4" />
                            Details
                          </Button>

                          {/* Status Update Dropdown */}
                          <Select
                            value={lead.status}
                            onValueChange={(newStatus) => {
                              if (lead.id) {
                                updateLeadStatus(lead.id, newStatus)
                              }
                            }}
                            disabled={updatingStatus === lead.id}
                          >
                            <SelectTrigger className="h-9 w-[160px]">
                              {updatingStatus === lead.id ? (
                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                              ) : (
                                <>
                                  {lead.status === 'NEW' && <Circle className="h-3 w-3 mr-2 text-gray-500" />}
                                  {lead.status === 'CONTACTED' && <ArrowRight className="h-3 w-3 mr-2 text-blue-500" />}
                                  {lead.status === 'QUALIFIED' && <CheckCircle2 className="h-3 w-3 mr-2 text-purple-500" />}
                                  {lead.status === 'OPPORTUNITY' && <Target className="h-3 w-3 mr-2 text-yellow-500" />}
                                  {lead.status === 'WON' && <CheckCircle2 className="h-3 w-3 mr-2 text-green-500" />}
                                  {lead.status === 'LOST' && <XCircle className="h-3 w-3 mr-2 text-red-500" />}
                                </>
                              )}
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="NEW">
                                <div className="flex items-center">
                                  <Circle className="h-3 w-3 mr-2 text-gray-500" />
                                  New
                                </div>
                              </SelectItem>
                              <SelectItem value="CONTACTED">
                                <div className="flex items-center">
                                  <ArrowRight className="h-3 w-3 mr-2 text-blue-500" />
                                  Contacted
                                </div>
                              </SelectItem>
                              <SelectItem value="QUALIFIED">
                                <div className="flex items-center">
                                  <CheckCircle2 className="h-3 w-3 mr-2 text-purple-500" />
                                  Qualified
                                </div>
                              </SelectItem>
                              <SelectItem value="OPPORTUNITY">
                                <div className="flex items-center">
                                  <Target className="h-3 w-3 mr-2 text-yellow-500" />
                                  Opportunity
                                </div>
                              </SelectItem>
                              <SelectItem value="WON">
                                <div className="flex items-center">
                                  <CheckCircle2 className="h-3 w-3 mr-2 text-green-500" />
                                  Won
                                </div>
                              </SelectItem>
                              <SelectItem value="LOST">
                                <div className="flex items-center">
                                  <XCircle className="h-3 w-3 mr-2 text-red-500" />
                                  Lost
                                </div>
                              </SelectItem>
                            </SelectContent>
                          </Select>

                          <Button
                            size="sm"
                            onClick={() => fetchIntelligence(lead)}
                            className="bg-gradient-to-r from-blue-600 to-purple-600 flex-1"
                            title="View AI Sales Intelligence"
                          >
                            <Brain className="mr-2 h-4 w-4" />
                            AI Intelligence
                          </Button>
                          <span className="relative group inline-block">
                            <Button
                              size="sm"
                              onClick={() => {
                                if (lead.id && lead.has_intelligence) {
                                  generatePredictions(lead.id)
                                }
                              }}
                              className="bg-gradient-to-r from-green-600 to-emerald-600"
                              disabled={generatingPredictions === lead.id || !lead.has_intelligence}
                            >
                              {generatingPredictions === lead.id ? (
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              ) : (
                                <TrendingUp className="mr-2 h-4 w-4" />
                              )}
                              Predict
                            </Button>
                            {!lead.has_intelligence && (
                              <span className="invisible group-hover:visible absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1 text-sm text-white bg-gray-900 rounded whitespace-nowrap z-50">
                                Generate AI Intelligence first
                                <span className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900"></span>
                              </span>
                            )}
                          </span>
                          <Button
                            size="sm"
                            onClick={() => downloadPlaybook(lead)}
                            className="bg-gradient-to-r from-indigo-600 to-blue-600"
                            title="Download PDF Playbook"
                            disabled={downloadingPlaybook === lead.id}
                          >
                            {downloadingPlaybook === lead.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Download className="h-4 w-4" />
                            )}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => generateEmailTemplate(lead, 'professional')}
                            title="Generate Email Template"
                          >
                            <Mail className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => generateOutreach(lead, 'sms')}
                            title="Generate SMS"
                          >
                            <MessageSquare className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => openBookingModal(lead)}
                            className="bg-gradient-to-r from-green-600 to-teal-600"
                          >
                            <Calendar className="mr-2 h-4 w-4" />
                            Book
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => sendToHubSpot(lead)}
                            className={
                              lead.status === 'IN_HUBSPOT'
                                ? 'bg-gray-400 cursor-not-allowed'
                                : 'bg-gradient-to-r from-orange-600 to-red-600'
                            }
                            disabled={sendingToHubSpot === lead.id || lead.status === 'IN_HUBSPOT'}
                            title={
                              lead.status === 'IN_HUBSPOT'
                                ? 'Already in HubSpot'
                                : 'Send to HubSpot CRM'
                            }
                          >
                            {sendingToHubSpot === lead.id ? (
                              <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Sending...
                              </>
                            ) : lead.status === 'IN_HUBSPOT' ? (
                              <>
                                <Upload className="mr-2 h-4 w-4" />
                                Already in HubSpot
                              </>
                            ) : (
                              <>
                                <Upload className="mr-2 h-4 w-4" />
                                HubSpot
                              </>
                            )}
                          </Button>
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="campaigns">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>Outreach Campaigns</CardTitle>
                    <CardDescription>Automated multi-channel outreach sequences</CardDescription>
                  </div>
                  <Button
                    onClick={() => setShowCreateCampaign(true)}
                    className="bg-gradient-to-r from-blue-600 to-purple-600"
                  >
                    <Sparkles className="mr-2 h-4 w-4" />
                    Create Campaign
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {campaigns.length === 0 ? (
                    <div className="text-center py-12">
                      <Target className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                      <p className="text-gray-600 dark:text-gray-400 mb-4">
                        No campaigns yet. Create your first outreach campaign!
                      </p>
                      <Button
                        onClick={() => setShowCreateCampaign(true)}
                        variant="outline"
                      >
                        <Sparkles className="mr-2 h-4 w-4" />
                        Get Started
                      </Button>
                    </div>
                  ) : (
                    campaigns.map((campaign) => (
                      <motion.div
                        key={campaign.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="p-4 border rounded-lg hover:shadow-lg transition-shadow"
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="font-semibold text-lg">{campaign.name}</h3>
                              <Badge variant={
                                campaign.status === 'active' ? 'default' :
                                campaign.status === 'draft' ? 'secondary' :
                                campaign.status === 'paused' ? 'outline' : 'secondary'
                              }>
                                {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                              </Badge>
                            </div>

                            {campaign.description && (
                              <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                                {campaign.description}
                              </p>
                            )}

                            <div className="flex gap-2 flex-wrap mt-2">
                              {campaign.target_filters?.industry && (
                                <Badge variant="outline" className="text-xs">
                                  <Target className="mr-1 h-3 w-3" />
                                  {campaign.target_filters.industry}
                                </Badge>
                              )}
                              {campaign.target_filters?.min_score && (
                                <Badge variant="outline" className="text-xs">
                                  Score: {campaign.target_filters.min_score}+
                                </Badge>
                              )}
                              {campaign.channels.map((channel, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  {channel === 'email' && <Mail className="mr-1 h-3 w-3" />}
                                  {channel === 'sms' && <MessageSquare className="mr-1 h-3 w-3" />}
                                  {channel.charAt(0).toUpperCase() + channel.slice(1)}
                                </Badge>
                              ))}
                            </div>

                            <div className="flex gap-4 mt-3 text-sm text-gray-600 dark:text-gray-400">
                              <span>{campaign.total_leads} leads</span>
                              <span>•</span>
                              <span>{campaign.contacted_leads} contacted</span>
                              <span>•</span>
                              <span>{campaign.converted_count} converted</span>
                            </div>
                          </div>

                          <Button
                            size="sm"
                            onClick={() => fetchCampaignDetails(campaign)}
                            className="ml-4"
                          >
                            View Details
                          </Button>
                        </div>

                        {campaign.total_leads > 0 && (
                          <div className="mt-4">
                            <div className="flex justify-between text-sm mb-2">
                              <span>Campaign Progress</span>
                              <span>{Math.round((campaign.contacted_leads / campaign.total_leads) * 100)}%</span>
                            </div>
                            <Progress value={(campaign.contacted_leads / campaign.total_leads) * 100} />
                          </div>
                        )}
                      </motion.div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="appointments">
            <Card>
              <CardHeader>
                <CardTitle>Scheduled Appointments</CardTitle>
                <CardDescription>Upcoming meetings with your leads</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {appointments.length === 0 ? (
                    <div className="text-center py-12">
                      <Calendar className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                      <p className="text-gray-600 dark:text-gray-400">
                        No appointments scheduled yet. Book an appointment from the Leads tab!
                      </p>
                    </div>
                  ) : (
                    appointments.map((appointment, index) => (
                      <motion.div
                        key={appointment.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.1 }}
                        className="p-4 border rounded-lg hover:shadow-md transition-shadow"
                      >
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <h3 className="font-semibold text-lg">
                              {appointment.lead?.company_name || 'Unknown Company'}
                            </h3>
                            {appointment.lead?.industry && (
                              <p className="text-sm text-gray-500">{appointment.lead.industry}</p>
                            )}
                          </div>
                          <Badge
                            className={
                              appointment.status === 'scheduled' ? 'bg-green-100 text-green-800' :
                              appointment.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                              appointment.status === 'cancelled' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }
                          >
                            {appointment.status}
                          </Badge>
                        </div>

                        <div className="space-y-2 text-sm">
                          {/* Date & Time */}
                          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                            <Calendar className="h-4 w-4" />
                            <span>
                              {new Date(appointment.date_time).toLocaleDateString('en-US', {
                                weekday: 'long',
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                                timeZone: 'Pacific/Honolulu'
                              })} HST
                            </span>
                          </div>

                          {/* Format */}
                          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                            {appointment.format === 'in-person' && <Building2 className="h-4 w-4" />}
                            {appointment.format === 'virtual' && <span className="h-4 w-4">💻</span>}
                            {appointment.format === 'phone' && <span className="h-4 w-4">📞</span>}
                            <span className="capitalize">{appointment.format}</span>
                            {appointment.format === 'in-person' && (
                              <span className="text-xs">• {appointment.location}</span>
                            )}
                          </div>

                          {/* Notes */}
                          {appointment.notes && (
                            <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded text-gray-600 dark:text-gray-400">
                              <span className="font-medium">Notes:</span> {appointment.notes}
                            </div>
                          )}

                          {/* Contact Info */}
                          {appointment.lead && (
                            <div className="flex gap-3 mt-3 pt-3 border-t text-xs">
                              {appointment.lead.email && (
                                <span className="text-blue-600">✉️ {appointment.lead.email}</span>
                              )}
                              {appointment.lead.phone && (
                                <span className="text-green-600">📞 {appointment.lead.phone}</span>
                              )}
                            </div>
                          )}
                        </div>
                      </motion.div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="ai-insights">
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle>AI-Powered Insights</CardTitle>
                    <CardDescription>Real-time analysis and recommendations from your lead data</CardDescription>
                  </div>
                  <Button onClick={fetchAIInsights} size="sm" variant="outline">
                    <Brain className="mr-2 h-4 w-4" />
                    Refresh Insights
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                {loadingInsights ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <Brain className="h-16 w-16 text-blue-600 animate-pulse mb-4" />
                    <p className="text-lg font-semibold">Analyzing your lead pipeline...</p>
                  </div>
                ) : aiInsights.length === 0 ? (
                  <div className="text-center py-12">
                    <Brain className="h-16 w-16 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600 dark:text-gray-400">
                      No insights available. Add more leads to get AI-powered recommendations.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {aiInsights.map((insight, index) => (
                      <div
                        key={index}
                        className={`p-4 rounded-lg ${
                          insight.type === 'opportunity' ? 'bg-blue-50 dark:bg-blue-900/20' :
                          insight.type === 'pattern' ? 'bg-green-50 dark:bg-green-900/20' :
                          insight.type === 'recommendations' ? 'bg-purple-50 dark:bg-purple-900/20' :
                          'bg-orange-50 dark:bg-orange-900/20'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          {insight.icon === 'Brain' && <Brain className="h-6 w-6 text-blue-600 mt-1 flex-shrink-0" />}
                          {insight.icon === 'Target' && <Target className="h-6 w-6 text-green-600 mt-1 flex-shrink-0" />}
                          {insight.icon === 'Sparkles' && <Sparkles className="h-6 w-6 text-purple-600 mt-1 flex-shrink-0" />}
                          {insight.icon === 'TrendingUp' && <TrendingUp className="h-6 w-6 text-orange-600 mt-1 flex-shrink-0" />}
                          <div className="flex-1">
                            <h3 className="font-semibold">{insight.title}</h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {insight.description}
                            </p>
                            {insight.action_items && (
                              <ul className="text-sm text-gray-600 dark:text-gray-400 mt-2 space-y-1 list-disc list-inside">
                                {insight.action_items.map((item: string, i: number) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            )}
                            {insight.action && (
                              <Button size="sm" className="mt-3" onClick={() => {
                                // You could implement filtering here in the future
                                console.log('Filter:', insight.action.filter)
                              }}>
                                {insight.action.label}
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
