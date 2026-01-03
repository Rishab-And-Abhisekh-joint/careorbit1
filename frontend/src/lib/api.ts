// CareOrbit API Client
// Handles all communication with the FastAPI backend

import type {
  Patient,
  Medication,
  Appointment,
  CareGap,
  HealthSummary,
  OrchestrationResult,
  ChatMessage,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(error.detail || 'Request failed', response.status);
  }
  
  return response.json();
}

// Patient API
export const patientApi = {
  getAll: () => fetchApi<Patient[]>('/api/patients'),
  
  getById: (id: string) => fetchApi<Patient>(`/api/patients/${id}`),
  
  getSummary: (id: string) => fetchApi<HealthSummary>(`/api/patients/${id}/summary`),
  
  create: (data: Partial<Patient>) =>
    fetchApi<Patient>('/api/patients', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// Medication API
export const medicationApi = {
  getByPatient: (patientId: string, activeOnly = false) =>
    fetchApi<Medication[]>(
      `/api/patients/${patientId}/medications${activeOnly ? '?active_only=true' : ''}`
    ),
  
  create: (data: Partial<Medication>) =>
    fetchApi<Medication>('/api/medications', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// Appointment API
export const appointmentApi = {
  getByPatient: (patientId: string, upcomingOnly = false) =>
    fetchApi<Appointment[]>(
      `/api/patients/${patientId}/appointments${upcomingOnly ? '?upcoming_only=true' : ''}`
    ),
  
  create: (data: Partial<Appointment>) =>
    fetchApi<Appointment>('/api/appointments', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// Care Gap API
export const careGapApi = {
  getByPatient: (patientId: string, includeResolved = false) =>
    fetchApi<CareGap[]>(
      `/api/patients/${patientId}/care-gaps${includeResolved ? '?include_resolved=true' : ''}`
    ),
  
  resolve: (gapId: string) =>
    fetchApi<{ status: string; gap_id: string }>(`/api/care-gaps/${gapId}/resolve`, {
      method: 'PATCH',
    }),
};

// Chat/Agent API
export const chatApi = {
  sendMessage: (patientId: string, message: string, context?: Record<string, any>) =>
    fetchApi<OrchestrationResult>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        patient_id: patientId,
        message,
        context,
      }),
    }),
  
  getHistory: (patientId: string, limit = 50) =>
    fetchApi<ChatMessage[]>(`/api/patients/${patientId}/chat-history?limit=${limit}`),
};

// Health Check API
export const healthApi = {
  check: () => fetchApi<{ status: string; agents: Record<string, string> }>('/api/health'),
};

export { ApiError };
