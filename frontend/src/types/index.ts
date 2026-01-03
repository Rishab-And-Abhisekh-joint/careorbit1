// CareOrbit Type Definitions
// FHIR-aligned types for healthcare coordination

export type PatientStatus = 'active' | 'inactive' | 'deceased';
export type CareGapSeverity = 'low' | 'medium' | 'high' | 'critical';
export type MedicationStatus = 'active' | 'stopped' | 'on-hold' | 'completed';
export type AppointmentStatus = 'scheduled' | 'completed' | 'cancelled' | 'no-show';

export interface Patient {
  id: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  gender: string;
  email?: string;
  phone?: string;
  address?: string;
  emergency_contact?: string;
  status: PatientStatus;
  conditions: string[];
  allergies: string[];
  created_at: string;
}

export interface Medication {
  id: string;
  patient_id: string;
  name: string;
  dosage: string;
  frequency: string;
  prescriber: string;
  specialty: string;
  start_date: string;
  end_date?: string;
  status: MedicationStatus;
  instructions?: string;
  side_effects: string[];
  interactions: string[];
  refills_remaining: number;
}

export interface Appointment {
  id: string;
  patient_id: string;
  provider_name: string;
  specialty: string;
  facility: string;
  appointment_date: string;
  duration_minutes: number;
  status: AppointmentStatus;
  reason: string;
  notes?: string;
  telehealth: boolean;
}

export interface CareGap {
  id: string;
  patient_id: string;
  title: string;
  description: string;
  severity: CareGapSeverity;
  category: string;
  guideline_reference: string;
  recommended_action: string;
  due_date?: string;
  detected_at: string;
  resolved: boolean;
  resolved_at?: string;
}

export interface ChatMessage {
  id: string;
  patient_id: string;
  role: 'user' | 'assistant' | 'agent';
  content: string;
  agent_name?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface AgentResponse {
  agent_name: string;
  response: string;
  confidence: number;
  actions_taken: string[];
  recommendations: string[];
}

export interface OrchestrationResult {
  primary_response: string;
  agent_contributions: AgentResponse[];
  care_gaps_detected: CareGap[];
  medication_alerts: string[];
  appointment_suggestions: string[];
}

export interface HealthSummary {
  patient_id: string;
  overall_status: string;
  active_conditions: string[];
  active_medications: number;
  upcoming_appointments: number;
  open_care_gaps: number;
  critical_alerts: string[];
  last_updated: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  error?: string;
  status: number;
}

// Component Props Types
export interface DashboardCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export interface MedicationCardProps {
  medication: Medication;
  onRefillRequest?: (id: string) => void;
}

export interface AppointmentCardProps {
  appointment: Appointment;
  onReschedule?: (id: string) => void;
  onCancel?: (id: string) => void;
}

export interface CareGapCardProps {
  careGap: CareGap;
  onResolve?: (id: string) => void;
  onSchedule?: (id: string) => void;
}
