'use client';

import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity,
  Pill,
  Calendar,
  AlertTriangle,
  MessageCircle,
  User,
  Heart,
  Brain,
  Stethoscope,
  Clock,
  ChevronRight,
  Send,
  Bot,
  Shield,
  Zap,
  TrendingUp,
  Bell,
  Menu,
  X,
  Video,
  MapPin,
  RefreshCw,
} from 'lucide-react';
import { 
  patientApi, 
  medicationApi, 
  appointmentApi, 
  careGapApi, 
  chatApi 
} from '@/lib/api';
import { 
  formatDate, 
  formatDateTime, 
  formatRelativeTime, 
  calculateAge,
  getSeverityColor,
  getStatusColor,
  formatFrequency,
  cn,
} from '@/lib/utils';
import type {
  Patient,
  Medication,
  Appointment,
  CareGap,
  HealthSummary,
  OrchestrationResult,
  ChatMessage,
} from '@/types';

// ============================================================================
// COMPONENTS
// ============================================================================

// Dashboard Stats Card
function StatsCard({ 
  title, 
  value, 
  subtitle, 
  icon: Icon, 
  variant = 'default',
  trend,
}: {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  variant?: 'default' | 'success' | 'warning' | 'danger';
  trend?: { direction: 'up' | 'down'; value: string };
}) {
  const variantStyles = {
    default: 'from-careorbit-500/20 to-cyan-500/20 border-careorbit-500/30',
    success: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/30',
    warning: 'from-amber-500/20 to-orange-500/20 border-amber-500/30',
    danger: 'from-red-500/20 to-rose-500/20 border-red-500/30',
  };

  const iconColors = {
    default: 'text-careorbit-400',
    success: 'text-emerald-400',
    warning: 'text-amber-400',
    danger: 'text-red-400',
  };

  return (
    <div className={cn(
      'glass-card p-6 bg-gradient-to-br card-hover',
      variantStyles[variant]
    )}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-slate-400 font-medium">{title}</p>
          <p className="text-3xl font-bold mt-1 text-white">{value}</p>
          {subtitle && (
            <p className="text-sm text-slate-500 mt-1">{subtitle}</p>
          )}
          {trend && (
            <div className={cn(
              'flex items-center gap-1 mt-2 text-sm',
              trend.direction === 'up' ? 'text-emerald-400' : 'text-red-400'
            )}>
              <TrendingUp className={cn('w-4 h-4', trend.direction === 'down' && 'rotate-180')} />
              <span>{trend.value}</span>
            </div>
          )}
        </div>
        <div className={cn(
          'p-3 rounded-xl bg-white/5',
          iconColors[variant]
        )}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}

// Medication Card Component
function MedicationCard({ medication }: { medication: Medication }) {
  return (
    <div className="glass-card p-4 card-hover border-l-4 border-l-careorbit-500">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-white">{medication.name}</h4>
            <span className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium',
              getStatusColor(medication.status)
            )}>
              {medication.status}
            </span>
          </div>
          <p className="text-careorbit-400 font-medium mt-1">
            {medication.dosage} • {formatFrequency(medication.frequency)}
          </p>
          <p className="text-sm text-slate-400 mt-1">
            Prescribed by {medication.prescriber} ({medication.specialty})
          </p>
          {medication.instructions && (
            <p className="text-sm text-slate-500 mt-2 italic">
              "{medication.instructions}"
            </p>
          )}
        </div>
        <div className="text-right">
          <div className={cn(
            'text-sm font-medium',
            medication.refills_remaining <= 1 ? 'text-amber-400' : 'text-slate-400'
          )}>
            {medication.refills_remaining} refills
          </div>
        </div>
      </div>
      {medication.interactions.length > 0 && (
        <div className="mt-3 p-2 bg-amber-500/10 rounded-lg border border-amber-500/20">
          <p className="text-xs text-amber-400 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            {medication.interactions[0]}
          </p>
        </div>
      )}
    </div>
  );
}

// Appointment Card Component
function AppointmentCard({ appointment }: { appointment: Appointment }) {
  const appointmentDate = new Date(appointment.appointment_date);
  const isUpcoming = appointmentDate > new Date();

  return (
    <div className={cn(
      'glass-card p-4 card-hover',
      isUpcoming ? 'border-l-4 border-l-emerald-500' : 'border-l-4 border-l-slate-600'
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-white">{appointment.provider_name}</h4>
            {appointment.telehealth && (
              <span className="px-2 py-0.5 rounded-full text-xs bg-purple-500/20 text-purple-400 flex items-center gap-1">
                <Video className="w-3 h-3" />
                Telehealth
              </span>
            )}
          </div>
          <p className="text-careorbit-400 font-medium">{appointment.specialty}</p>
          <p className="text-sm text-slate-400 mt-1 flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {appointment.facility}
          </p>
          <p className="text-sm text-slate-500 mt-1">{appointment.reason}</p>
        </div>
        <div className="text-right">
          <p className="text-sm font-medium text-white">
            {formatRelativeTime(appointment.appointment_date)}
          </p>
          <p className="text-xs text-slate-400">
            {formatDateTime(appointment.appointment_date)}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {appointment.duration_minutes} min
          </p>
        </div>
      </div>
    </div>
  );
}

// Care Gap Card Component
function CareGapCard({ 
  careGap, 
  onResolve 
}: { 
  careGap: CareGap; 
  onResolve?: (id: string) => void;
}) {
  return (
    <div className={cn(
      'glass-card p-4 card-hover border-l-4',
      careGap.severity === 'critical' && 'border-l-red-500',
      careGap.severity === 'high' && 'border-l-orange-500',
      careGap.severity === 'medium' && 'border-l-yellow-500',
      careGap.severity === 'low' && 'border-l-green-500',
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <AlertTriangle className={cn(
              'w-4 h-4',
              careGap.severity === 'critical' && 'text-red-500',
              careGap.severity === 'high' && 'text-orange-500',
              careGap.severity === 'medium' && 'text-yellow-500',
              careGap.severity === 'low' && 'text-green-500',
            )} />
            <h4 className="font-semibold text-white">{careGap.title}</h4>
            <span className={cn(
              'px-2 py-0.5 rounded-full text-xs font-medium uppercase border',
              getSeverityColor(careGap.severity)
            )}>
              {careGap.severity}
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-2">{careGap.description}</p>
          <div className="mt-3 p-3 bg-careorbit-500/10 rounded-lg border border-careorbit-500/20">
            <p className="text-sm text-careorbit-400 font-medium">
              ✨ Recommended: {careGap.recommended_action}
            </p>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Based on: {careGap.guideline_reference}
          </p>
        </div>
      </div>
      {onResolve && (
        <button
          onClick={() => onResolve(careGap.id)}
          className="mt-3 text-sm text-careorbit-400 hover:text-careorbit-300 
                     flex items-center gap-1 transition-colors"
        >
          Mark as addressed <ChevronRight className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

// Chat Message Component
function ChatMessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <div className={cn(
      'flex gap-3',
      isUser ? 'flex-row-reverse' : 'flex-row'
    )}>
      <div className={cn(
        'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
        isUser 
          ? 'bg-careorbit-500' 
          : 'bg-gradient-to-br from-purple-500 to-pink-500'
      )}>
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-white" />
        )}
      </div>
      <div className={cn(
        'max-w-[80%] rounded-2xl px-4 py-3',
        isUser 
          ? 'bg-careorbit-500 text-white rounded-br-md' 
          : 'glass-card rounded-bl-md'
      )}>
        {message.agent_name && (
          <p className="text-xs text-purple-400 font-medium mb-1">
            {message.agent_name}
          </p>
        )}
        <div 
          className="text-sm whitespace-pre-wrap"
          dangerouslySetInnerHTML={{ 
            __html: message.content
              .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
              .replace(/\n\n/g, '<br /><br />')
              .replace(/• /g, '<br />• ')
          }}
        />
        <p className={cn(
          'text-xs mt-2',
          isUser ? 'text-careorbit-200' : 'text-slate-500'
        )}>
          {new Date(message.timestamp).toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
          })}
        </p>
      </div>
    </div>
  );
}

// Chat Input Component
function ChatInput({ 
  onSend, 
  disabled 
}: { 
  onSend: (message: string) => void; 
  disabled: boolean;
}) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask about your medications, appointments, or care gaps..."
        disabled={disabled}
        className="flex-1 bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3
                   text-white placeholder-slate-500 focus:outline-none focus:border-careorbit-500
                   focus:ring-2 focus:ring-careorbit-500/20 transition-all disabled:opacity-50"
        aria-label="Chat message input"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="px-6 py-3 bg-gradient-to-r from-careorbit-500 to-cyan-500 
                   rounded-xl text-white font-medium flex items-center gap-2
                   hover:from-careorbit-600 hover:to-cyan-600 transition-all
                   disabled:opacity-50 disabled:cursor-not-allowed
                   focus:outline-none focus:ring-2 focus:ring-careorbit-500/50"
        aria-label="Send message"
      >
        <Send className="w-5 h-5" />
      </button>
    </form>
  );
}

// ============================================================================
// MAIN DASHBOARD PAGE
// ============================================================================

export default function DashboardPage() {
  // State
  const [patient, setPatient] = useState<Patient | null>(null);
  const [summary, setSummary] = useState<HealthSummary | null>(null);
  const [medications, setMedications] = useState<Medication[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [careGaps, setCareGaps] = useState<CareGap[]>([]);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'medications' | 'appointments' | 'gaps' | 'chat'>('overview');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Demo patient ID
  const DEMO_PATIENT_ID = 'patient-001';

  // Load data
  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [patientData, summaryData, medsData, aptsData, gapsData] = await Promise.all([
        patientApi.getById(DEMO_PATIENT_ID),
        patientApi.getSummary(DEMO_PATIENT_ID),
        medicationApi.getByPatient(DEMO_PATIENT_ID, true),
        appointmentApi.getByPatient(DEMO_PATIENT_ID, true),
        careGapApi.getByPatient(DEMO_PATIENT_ID),
      ]);

      setPatient(patientData);
      setSummary(summaryData);
      setMedications(medsData);
      setAppointments(aptsData);
      setCareGaps(gapsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle chat message
  const handleSendMessage = async (message: string) => {
    // Add user message
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      patient_id: DEMO_PATIENT_ID,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    };
    setChatMessages(prev => [...prev, userMessage]);
    setIsChatLoading(true);

    try {
      const result = await chatApi.sendMessage(DEMO_PATIENT_ID, message);
      
      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}-response`,
        patient_id: DEMO_PATIENT_ID,
        role: 'assistant',
        content: result.primary_response,
        timestamp: new Date().toISOString(),
        metadata: {
          agents: result.agent_contributions.map(a => a.agent_name),
        },
      };
      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: `msg-${Date.now()}-error`,
        patient_id: DEMO_PATIENT_ID,
        role: 'assistant',
        content: 'I apologize, but I encountered an issue processing your request. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Handle care gap resolution
  const handleResolveCareGap = async (gapId: string) => {
    try {
      await careGapApi.resolve(gapId);
      setCareGaps(prev => prev.filter(g => g.id !== gapId));
    } catch (error) {
      console.error('Failed to resolve care gap:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4" />
          <p className="text-slate-400">Loading your health dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-40 glass border-b border-slate-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-careorbit-500 to-cyan-500 
                            flex items-center justify-center shadow-lg shadow-careorbit-500/25">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gradient">CareOrbit</h1>
                <p className="text-xs text-slate-500">Multi-Agent Care Coordination</p>
              </div>
            </div>

            {/* Patient Info */}
            {patient && (
              <div className="hidden md:flex items-center gap-4">
                <div className="text-right">
                  <p className="text-sm font-medium text-white">
                    {patient.first_name} {patient.last_name}
                  </p>
                  <p className="text-xs text-slate-400">
                    {calculateAge(patient.date_of_birth)} years old • {patient.conditions.length} conditions
                  </p>
                </div>
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 
                              flex items-center justify-center text-white font-bold">
                  {patient.first_name[0]}{patient.last_name[0]}
                </div>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 text-slate-400 hover:text-white"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-slate-700/50 p-4">
            <nav className="flex flex-col gap-2">
              {['overview', 'medications', 'appointments', 'gaps', 'chat'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => {
                    setActiveTab(tab as any);
                    setMobileMenuOpen(false);
                  }}
                  className={cn(
                    'px-4 py-2 rounded-lg text-left capitalize transition-colors',
                    activeTab === tab 
                      ? 'bg-careorbit-500/20 text-careorbit-400' 
                      : 'text-slate-400 hover:text-white'
                  )}
                >
                  {tab === 'gaps' ? 'Care Gaps' : tab}
                </button>
              ))}
            </nav>
          </div>
        )}
      </header>

      {/* Navigation Tabs */}
      <nav className="hidden md:block border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-16 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-1">
            {[
              { id: 'overview', label: 'Overview', icon: Activity },
              { id: 'medications', label: 'Medications', icon: Pill },
              { id: 'appointments', label: 'Appointments', icon: Calendar },
              { id: 'gaps', label: 'Care Gaps', icon: AlertTriangle },
              { id: 'chat', label: 'AI Assistant', icon: MessageCircle },
            ].map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={cn(
                  'flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all border-b-2',
                  activeTab === id
                    ? 'text-careorbit-400 border-careorbit-500'
                    : 'text-slate-400 border-transparent hover:text-white hover:border-slate-600'
                )}
              >
                <Icon className="w-4 h-4" />
                {label}
                {id === 'gaps' && careGaps.length > 0 && (
                  <span className="px-2 py-0.5 text-xs bg-red-500/20 text-red-400 rounded-full">
                    {careGaps.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Tab */}
        {activeTab === 'overview' && summary && (
          <div className="space-y-8 animate-fade-in">
            {/* Welcome Section */}
            <div className="glass-card p-6 bg-gradient-to-r from-careorbit-500/10 to-purple-500/10">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <h2 className="text-2xl font-bold text-white">
                    Welcome back, {patient?.first_name}
                  </h2>
                  <p className="text-slate-400 mt-1">
                    Here's your health coordination summary for today
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={cn(
                    'px-4 py-2 rounded-full text-sm font-medium',
                    summary.critical_alerts.length === 0
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-amber-500/20 text-amber-400'
                  )}>
                    {summary.overall_status}
                  </span>
                  <button 
                    onClick={loadData}
                    className="p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                    aria-label="Refresh data"
                  >
                    <RefreshCw className="w-5 h-5 text-slate-400" />
                  </button>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                title="Active Conditions"
                value={summary.active_conditions.length}
                subtitle="Being managed"
                icon={Heart}
                variant="default"
              />
              <StatsCard
                title="Medications"
                value={summary.active_medications}
                subtitle="Currently taking"
                icon={Pill}
                variant="success"
              />
              <StatsCard
                title="Upcoming Visits"
                value={summary.upcoming_appointments}
                subtitle="Scheduled"
                icon={Calendar}
                variant="default"
              />
              <StatsCard
                title="Care Gaps"
                value={summary.open_care_gaps}
                subtitle="Need attention"
                icon={AlertTriangle}
                variant={summary.open_care_gaps > 0 ? 'warning' : 'success'}
              />
            </div>

            {/* Critical Alerts */}
            {summary.critical_alerts.length > 0 && (
              <div className="glass-card p-6 border-l-4 border-l-amber-500 bg-gradient-to-r from-amber-500/10 to-transparent">
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-amber-500/20">
                    <Bell className="w-6 h-6 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">Attention Needed</h3>
                    <ul className="mt-2 space-y-2">
                      {summary.critical_alerts.map((alert, idx) => (
                        <li key={idx} className="text-slate-300 flex items-center gap-2">
                          <ChevronRight className="w-4 h-4 text-amber-400" />
                          {alert}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Conditions Overview */}
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Stethoscope className="w-5 h-5 text-careorbit-400" />
                Your Health Conditions
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {patient?.conditions.map((condition, idx) => (
                  <div key={idx} className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-careorbit-500" />
                      <span className="text-slate-200">{condition}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                onClick={() => setActiveTab('chat')}
                className="glass-card p-6 text-left card-hover group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20
                                group-hover:from-purple-500/30 group-hover:to-pink-500/30 transition-colors">
                    <Bot className="w-6 h-6 text-purple-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">Ask AI Assistant</h4>
                    <p className="text-sm text-slate-400">Get answers about your care</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => setActiveTab('gaps')}
                className="glass-card p-6 text-left card-hover group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-500/20
                                group-hover:from-amber-500/30 group-hover:to-orange-500/30 transition-colors">
                    <Shield className="w-6 h-6 text-amber-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">Review Care Gaps</h4>
                    <p className="text-sm text-slate-400">{careGaps.length} items need attention</p>
                  </div>
                </div>
              </button>

              <button
                onClick={() => setActiveTab('appointments')}
                className="glass-card p-6 text-left card-hover group"
              >
                <div className="flex items-center gap-4">
                  <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/20
                                group-hover:from-emerald-500/30 group-hover:to-teal-500/30 transition-colors">
                    <Calendar className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">View Appointments</h4>
                    <p className="text-sm text-slate-400">{appointments.length} upcoming visits</p>
                  </div>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Medications Tab */}
        {activeTab === 'medications' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white">Your Medications</h2>
                <p className="text-slate-400 mt-1">
                  {medications.length} active medications from {
                    [...new Set(medications.map(m => m.specialty))].length
                  } specialists
                </p>
              </div>
            </div>

            <div className="grid gap-4">
              {medications.map((med) => (
                <MedicationCard key={med.id} medication={med} />
              ))}
            </div>

            {medications.length === 0 && (
              <div className="text-center py-12">
                <Pill className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No active medications</p>
              </div>
            )}
          </div>
        )}

        {/* Appointments Tab */}
        {activeTab === 'appointments' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white">Upcoming Appointments</h2>
                <p className="text-slate-400 mt-1">
                  {appointments.length} scheduled visits with your care team
                </p>
              </div>
            </div>

            <div className="grid gap-4">
              {appointments.map((apt) => (
                <AppointmentCard key={apt.id} appointment={apt} />
              ))}
            </div>

            {appointments.length === 0 && (
              <div className="text-center py-12">
                <Calendar className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                <p className="text-slate-400">No upcoming appointments</p>
              </div>
            )}
          </div>
        )}

        {/* Care Gaps Tab */}
        {activeTab === 'gaps' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-white">Care Gaps</h2>
                <p className="text-slate-400 mt-1">
                  {careGaps.length} recommended actions based on clinical guidelines
                </p>
              </div>
            </div>

            <div className="grid gap-4">
              {careGaps.map((gap) => (
                <CareGapCard 
                  key={gap.id} 
                  careGap={gap} 
                  onResolve={handleResolveCareGap}
                />
              ))}
            </div>

            {careGaps.length === 0 && (
              <div className="text-center py-12">
                <Shield className="w-12 h-12 text-emerald-500 mx-auto mb-4" />
                <p className="text-emerald-400 font-medium">All caught up!</p>
                <p className="text-slate-400 mt-1">No care gaps identified</p>
              </div>
            )}
          </div>
        )}

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="space-y-6 animate-fade-in">
            <div className="flex items-center gap-4">
              <div className="p-3 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-white">AI Care Assistant</h2>
                <p className="text-slate-400">
                  Powered by Multi-Agent Orchestration with Azure OpenAI
                </p>
              </div>
            </div>

            {/* Agent Info */}
            <div className="glass-card p-4 border-l-4 border-l-purple-500">
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-2 text-slate-400">
                  <Brain className="w-4 h-4" />
                  <span>4 Specialized Agents</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <Zap className="w-4 h-4" />
                  <span>Real-time Coordination</span>
                </div>
                <div className="flex items-center gap-2 text-slate-400">
                  <Shield className="w-4 h-4" />
                  <span>HIPAA-Aware</span>
                </div>
              </div>
            </div>

            {/* Chat Messages */}
            <div className="glass-card p-6 min-h-[400px] flex flex-col">
              <div className="flex-1 space-y-4 mb-4 max-h-[500px] overflow-y-auto">
                {chatMessages.length === 0 ? (
                  <div className="text-center py-12">
                    <MessageCircle className="w-12 h-12 text-slate-600 mx-auto mb-4" />
                    <p className="text-slate-400">Start a conversation</p>
                    <p className="text-sm text-slate-500 mt-2">
                      Try asking about your medications, appointments, or care gaps
                    </p>
                    <div className="flex flex-wrap justify-center gap-2 mt-4">
                      {[
                        "What medications am I taking?",
                        "When is my next appointment?",
                        "What care gaps need attention?",
                        "Explain my conditions",
                      ].map((suggestion) => (
                        <button
                          key={suggestion}
                          onClick={() => handleSendMessage(suggestion)}
                          className="px-3 py-1.5 text-sm bg-slate-800 hover:bg-slate-700 
                                   rounded-lg text-slate-300 transition-colors"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  chatMessages.map((msg) => (
                    <ChatMessageBubble key={msg.id} message={msg} />
                  ))
                )}
                {isChatLoading && (
                  <div className="flex gap-3">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 
                                  flex items-center justify-center">
                      <Bot className="w-4 h-4 text-white" />
                    </div>
                    <div className="glass-card px-4 py-3 rounded-2xl rounded-bl-md">
                      <div className="flex items-center gap-2">
                        <div className="spinner" />
                        <span className="text-sm text-slate-400">Consulting care agents...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <ChatInput onSend={handleSendMessage} disabled={isChatLoading} />
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Heart className="w-4 h-4 text-careorbit-500" />
              <span>CareOrbit - Multi-Agent Healthcare Coordination</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-slate-500">
              <span>Powered by Microsoft Azure AI</span>
              <span>•</span>
              <span>Imagine Cup 2026</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
