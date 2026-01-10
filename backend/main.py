"""
CareOrbit - Multi-Agent Healthcare Coordination System
Production-grade MVP for Imagine Cup 2026

This backend implements a multi-agent AI system for chronic disease care coordination
using Azure OpenAI and Microsoft AI services patterns.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from enum import Enum
import asyncio
import json
import os
import uuid
import httpx
from contextlib import asynccontextmanager

# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

class Settings:
    """Application settings - configure via environment variables"""
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    AZURE_AI_SEARCH_ENDPOINT: str = os.getenv("AZURE_AI_SEARCH_ENDPOINT", "")
    AZURE_AI_SEARCH_KEY: str = os.getenv("AZURE_AI_SEARCH_KEY", "")
    AZURE_AI_SEARCH_INDEX: str = os.getenv("AZURE_AI_SEARCH_INDEX", "clinical-guidelines")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()

# ============================================================================
# DATA MODELS (FHIR-Aligned)
# ============================================================================

class PatientStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECEASED = "deceased"

class CareGapSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class MedicationStatus(str, Enum):
    ACTIVE = "active"
    STOPPED = "stopped"
    ON_HOLD = "on-hold"
    COMPLETED = "completed"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no-show"

# Patient Models
class Patient(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: PatientStatus = PatientStatus.ACTIVE
    conditions: List[str] = []
    allergies: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    email: Optional[str] = None
    phone: Optional[str] = None
    conditions: List[str] = []
    allergies: List[str] = []

# Medication Models
class Medication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    name: str
    dosage: str
    frequency: str
    prescriber: str
    specialty: str
    start_date: date
    end_date: Optional[date] = None
    status: MedicationStatus = MedicationStatus.ACTIVE
    instructions: Optional[str] = None
    side_effects: List[str] = []
    interactions: List[str] = []
    refills_remaining: int = 0

class MedicationCreate(BaseModel):
    patient_id: str
    name: str
    dosage: str
    frequency: str
    prescriber: str
    specialty: str
    start_date: date
    instructions: Optional[str] = None

# Appointment Models
class Appointment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    provider_name: str
    specialty: str
    facility: str
    appointment_date: datetime
    duration_minutes: int = 30
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reason: str
    notes: Optional[str] = None
    telehealth: bool = False

class AppointmentCreate(BaseModel):
    patient_id: str
    provider_name: str
    specialty: str
    facility: str
    appointment_date: datetime
    duration_minutes: int = 30
    reason: str
    telehealth: bool = False

# Care Gap Models
class CareGap(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    title: str
    description: str
    severity: CareGapSeverity
    category: str
    guideline_reference: str
    recommended_action: str
    due_date: Optional[date] = None
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

# Chat/Agent Models
class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    patient_id: str
    role: str  # "user", "assistant", "agent"
    content: str
    agent_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    patient_id: str
    message: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent_name: str
    response: str
    confidence: float
    actions_taken: List[str] = []
    recommendations: List[str] = []

class OrchestrationResult(BaseModel):
    primary_response: str
    agent_contributions: List[AgentResponse]
    care_gaps_detected: List[CareGap] = []
    medication_alerts: List[str] = []
    appointment_suggestions: List[str] = []

# Health Summary Models
class HealthSummary(BaseModel):
    patient_id: str
    overall_status: str
    active_conditions: List[str]
    active_medications: int
    upcoming_appointments: int
    open_care_gaps: int
    critical_alerts: List[str]
    last_updated: datetime

# ============================================================================
# IN-MEMORY DATABASE (Replace with Azure PostgreSQL/Cosmos DB in production)
# ============================================================================

class Database:
    """In-memory database for MVP demonstration"""
    def __init__(self):
        self.patients: Dict[str, Patient] = {}
        self.medications: Dict[str, Medication] = {}
        self.appointments: Dict[str, Appointment] = {}
        self.care_gaps: Dict[str, CareGap] = {}
        self.chat_history: Dict[str, List[ChatMessage]] = {}
        self._initialize_demo_data()
    
    def _initialize_demo_data(self):
        """Initialize with realistic demo data for MVP demonstration"""
        # Demo Patient - Eleanor Thompson (Multi-chronic condition patient)
        demo_patient = Patient(
            id="patient-001",
            first_name="Eleanor",
            last_name="Thompson",
            date_of_birth=date(1952, 3, 15),
            gender="female",
            email="eleanor.thompson@email.com",
            phone="+1-555-0123",
            address="123 Oak Street, Springfield, IL 62701",
            emergency_contact="Michael Thompson (Son): +1-555-0124",
            conditions=[
                "Type 2 Diabetes Mellitus",
                "Essential Hypertension",
                "Chronic Heart Failure (Stage B)",
                "Major Depressive Disorder",
                "Osteoarthritis (Bilateral Knees)"
            ],
            allergies=["Penicillin", "Sulfa drugs"]
        )
        self.patients[demo_patient.id] = demo_patient
        
        # Demo Medications (Multiple specialists)
        demo_medications = [
            Medication(
                id="med-001",
                patient_id="patient-001",
                name="Metformin",
                dosage="1000mg",
                frequency="Twice daily with meals",
                prescriber="Dr. Sarah Chen",
                specialty="Endocrinology",
                start_date=date(2020, 1, 15),
                status=MedicationStatus.ACTIVE,
                instructions="Take with food to reduce stomach upset",
                side_effects=["Nausea", "Diarrhea"],
                interactions=["May interact with contrast dye"],
                refills_remaining=3
            ),
            Medication(
                id="med-002",
                patient_id="patient-001",
                name="Lisinopril",
                dosage="20mg",
                frequency="Once daily in morning",
                prescriber="Dr. James Wilson",
                specialty="Cardiology",
                start_date=date(2019, 6, 1),
                status=MedicationStatus.ACTIVE,
                instructions="Monitor for dry cough",
                side_effects=["Dry cough", "Dizziness"],
                interactions=["Potassium supplements may cause hyperkalemia"],
                refills_remaining=2
            ),
            Medication(
                id="med-003",
                patient_id="patient-001",
                name="Carvedilol",
                dosage="12.5mg",
                frequency="Twice daily",
                prescriber="Dr. James Wilson",
                specialty="Cardiology",
                start_date=date(2021, 3, 10),
                status=MedicationStatus.ACTIVE,
                instructions="Take with food, do not stop suddenly",
                side_effects=["Fatigue", "Dizziness", "Weight gain"],
                interactions=["May mask hypoglycemia symptoms in diabetics"],
                refills_remaining=1
            ),
            Medication(
                id="med-004",
                patient_id="patient-001",
                name="Sertraline",
                dosage="100mg",
                frequency="Once daily in morning",
                prescriber="Dr. Emily Rodriguez",
                specialty="Psychiatry",
                start_date=date(2022, 8, 20),
                status=MedicationStatus.ACTIVE,
                instructions="May take 4-6 weeks for full effect",
                side_effects=["Nausea", "Insomnia", "Sexual dysfunction"],
                interactions=["Avoid MAOIs, caution with NSAIDs"],
                refills_remaining=4
            ),
            Medication(
                id="med-005",
                patient_id="patient-001",
                name="Furosemide",
                dosage="40mg",
                frequency="Once daily in morning",
                prescriber="Dr. James Wilson",
                specialty="Cardiology",
                start_date=date(2023, 1, 5),
                status=MedicationStatus.ACTIVE,
                instructions="Take early in day to avoid nighttime urination",
                side_effects=["Frequent urination", "Electrolyte imbalance"],
                interactions=["May increase lithium levels, potassium loss with steroids"],
                refills_remaining=2
            )
        ]
        for med in demo_medications:
            self.medications[med.id] = med
        
        # Demo Appointments
        today = datetime.now()
        demo_appointments = [
            Appointment(
                id="apt-001",
                patient_id="patient-001",
                provider_name="Dr. Sarah Chen",
                specialty="Endocrinology",
                facility="Springfield Diabetes Center",
                appointment_date=today + timedelta(days=7),
                duration_minutes=30,
                status=AppointmentStatus.SCHEDULED,
                reason="Quarterly A1C check and diabetes management review",
                telehealth=False
            ),
            Appointment(
                id="apt-002",
                patient_id="patient-001",
                provider_name="Dr. James Wilson",
                specialty="Cardiology",
                facility="Heart Health Associates",
                appointment_date=today + timedelta(days=14),
                duration_minutes=45,
                status=AppointmentStatus.SCHEDULED,
                reason="Heart failure monitoring and medication adjustment",
                telehealth=True
            ),
            Appointment(
                id="apt-003",
                patient_id="patient-001",
                provider_name="Dr. Emily Rodriguez",
                specialty="Psychiatry",
                facility="Behavioral Health Center",
                appointment_date=today + timedelta(days=21),
                duration_minutes=30,
                status=AppointmentStatus.SCHEDULED,
                reason="Depression follow-up and medication review",
                telehealth=True
            ),
            Appointment(
                id="apt-004",
                patient_id="patient-001",
                provider_name="Dr. Michael Park",
                specialty="Primary Care",
                facility="Springfield Family Medicine",
                appointment_date=today - timedelta(days=30),
                duration_minutes=30,
                status=AppointmentStatus.COMPLETED,
                reason="Annual wellness visit",
                notes="Blood pressure slightly elevated. Referred to cardiology."
            )
        ]
        for apt in demo_appointments:
            self.appointments[apt.id] = apt
        
        # Demo Care Gaps
        demo_care_gaps = [
            CareGap(
                id="gap-001",
                patient_id="patient-001",
                title="Overdue Diabetic Eye Exam",
                description="Last retinal exam was 18 months ago. HEDIS guidelines recommend annual diabetic retinopathy screening.",
                severity=CareGapSeverity.HIGH,
                category="Preventive Care",
                guideline_reference="HEDIS Comprehensive Diabetes Care - Eye Exam",
                recommended_action="Schedule dilated eye exam with ophthalmologist within 30 days",
                due_date=date.today() + timedelta(days=30)
            ),
            CareGap(
                id="gap-002",
                patient_id="patient-001",
                title="Missing Foot Exam",
                description="No documented foot exam in the past year. Diabetic patients require annual comprehensive foot exams.",
                severity=CareGapSeverity.MEDIUM,
                category="Diabetes Management",
                guideline_reference="ADA Standards of Medical Care - Comprehensive Foot Exam",
                recommended_action="Request foot exam at next endocrinology appointment",
                due_date=date.today() + timedelta(days=7)
            ),
            CareGap(
                id="gap-003",
                patient_id="patient-001",
                title="Depression Screening Due",
                description="PHQ-9 assessment not completed in past 6 months. Regular monitoring recommended for patients on antidepressants.",
                severity=CareGapSeverity.MEDIUM,
                category="Mental Health",
                guideline_reference="USPSTF Depression Screening Recommendation",
                recommended_action="Complete PHQ-9 questionnaire before next psychiatry visit",
                due_date=date.today() + timedelta(days=14)
            ),
            CareGap(
                id="gap-004",
                patient_id="patient-001",
                title="Flu Vaccination Needed",
                description="No flu vaccination record for current season. Strongly recommended for patients with heart failure and diabetes.",
                severity=CareGapSeverity.HIGH,
                category="Immunization",
                guideline_reference="CDC ACIP Influenza Vaccination Recommendations",
                recommended_action="Schedule flu shot at pharmacy or next doctor visit",
                due_date=date.today() + timedelta(days=14)
            )
        ]
        for gap in demo_care_gaps:
            self.care_gaps[gap.id] = gap

db = Database()

# ============================================================================
# MULTI-AGENT SYSTEM
# ============================================================================

class BaseAgent:
    """Base class for all healthcare coordination agents"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def _call_azure_openai(self, system_prompt: str, user_message: str, context: Dict = None) -> str:
        """Call Azure OpenAI for agent reasoning"""
        if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_API_KEY:
            # Fallback for demo mode without Azure credentials
            return await self._demo_response(user_message, context)
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            if context:
                context_message = f"Context: {json.dumps(context, default=str)}"
                messages.insert(1, {"role": "system", "content": context_message})
            
            response = await self.http_client.post(
                f"{settings.AZURE_OPENAI_ENDPOINT}/openai/deployments/{settings.AZURE_OPENAI_DEPLOYMENT}/chat/completions?api-version=2024-02-01",
                headers={
                    "api-key": settings.AZURE_OPENAI_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Azure OpenAI error: {e}")
            return await self._demo_response(user_message, context)
    
    async def _demo_response(self, user_message: str, context: Dict = None) -> str:
        """Demo response when Azure credentials not available"""
        raise NotImplementedError("Subclasses must implement _demo_response")
    
    async def process(self, patient_id: str, message: str, context: Dict = None) -> AgentResponse:
        """Process a message and return agent response"""
        raise NotImplementedError("Subclasses must implement process")


class PatientHistoryAgent(BaseAgent):
    """Agent responsible for managing and summarizing patient history"""
    
    def __init__(self):
        super().__init__(
            name="Patient History Agent",
            description="Analyzes and summarizes patient medical history across all providers"
        )
    
    async def _demo_response(self, user_message: str, context: Dict = None) -> str:
        patient = context.get("patient") if context else None
        if patient:
            conditions = ", ".join(patient.get("conditions", [])[:3])
            return f"Based on the patient's history, they are managing {conditions}. Their care involves multiple specialists coordinating treatment across these conditions."
        return "I can help you understand your complete medical history and how your conditions relate to each other."
    
    async def process(self, patient_id: str, message: str, context: Dict = None) -> AgentResponse:
        patient = db.patients.get(patient_id)
        if not patient:
            return AgentResponse(
                agent_name=self.name,
                response="Patient not found in the system.",
                confidence=0.0,
                actions_taken=[],
                recommendations=[]
            )
        
        # Build patient context
        patient_context = {
            "patient": patient.model_dump(),
            "conditions": patient.conditions,
            "allergies": patient.allergies
        }
        
        system_prompt = """You are a Patient History Agent in a healthcare coordination system. 
        Your role is to analyze and summarize patient medical history, identifying key patterns,
        relationships between conditions, and important historical events.
        
        Be empathetic, clear, and focus on helping the patient understand their health journey.
        Always emphasize the importance of coordinated care across specialists."""
        
        response = await self._call_azure_openai(system_prompt, message, patient_context)
        
        return AgentResponse(
            agent_name=self.name,
            response=response,
            confidence=0.9,
            actions_taken=["Analyzed patient history", "Reviewed condition relationships"],
            recommendations=["Continue coordinating care across all specialists"]
        )


class MedicationReconciliationAgent(BaseAgent):
    """Agent responsible for medication management and interaction detection"""
    
    def __init__(self):
        super().__init__(
            name="Medication Reconciliation Agent",
            description="Monitors medications, detects interactions, and ensures safe polypharmacy management"
        )
    
    # Common drug interactions database (simplified for MVP)
    INTERACTIONS = {
        ("metformin", "contrast"): "Metformin should be held 48 hours before and after IV contrast procedures",
        ("lisinopril", "potassium"): "ACE inhibitors can increase potassium levels - monitor carefully",
        ("carvedilol", "metformin"): "Beta-blockers may mask hypoglycemia symptoms in diabetics",
        ("sertraline", "nsaids"): "SSRIs with NSAIDs increase bleeding risk",
        ("furosemide", "lisinopril"): "Both affect blood pressure - monitor for hypotension"
    }
    
    def _check_interactions(self, medications: List[Medication]) -> List[str]:
        """Check for drug-drug interactions"""
        alerts = []
        med_names = [med.name.lower() for med in medications if med.status == MedicationStatus.ACTIVE]
        
        for (drug1, drug2), warning in self.INTERACTIONS.items():
            if drug1 in med_names or drug2 in med_names:
                for med_name in med_names:
                    if drug1 in med_name.lower() or drug2 in med_name.lower():
                        alerts.append(warning)
                        break
        
        # Check for specific combination alerts
        if "carvedilol" in " ".join(med_names).lower() and "metformin" in " ".join(med_names).lower():
            alerts.append("⚠️ Carvedilol may mask low blood sugar symptoms. Monitor glucose carefully.")
        
        return list(set(alerts))
    
    async def _demo_response(self, user_message: str, context: Dict = None) -> str:
        medications = context.get("medications", []) if context else []
        if medications:
            return f"You are currently taking {len(medications)} active medications from multiple specialists. I'm monitoring for interactions and will alert you to any concerns."
        return "I help manage your medications and check for potential interactions between drugs from different doctors."
    
    async def process(self, patient_id: str, message: str, context: Dict = None) -> AgentResponse:
        # Get patient medications
        patient_meds = [med for med in db.medications.values() if med.patient_id == patient_id]
        active_meds = [med for med in patient_meds if med.status == MedicationStatus.ACTIVE]
        
        # Check for interactions
        interaction_alerts = self._check_interactions(active_meds)
        
        # Build context
        med_context = {
            "medications": [med.model_dump() for med in active_meds],
            "total_medications": len(active_meds),
            "specialists_prescribing": list(set(med.specialty for med in active_meds))
        }
        
        system_prompt = """You are a Medication Reconciliation Agent in a healthcare coordination system.
        Your role is to help patients understand their medications, identify potential interactions,
        and ensure safe management of multiple prescriptions from different specialists.
        
        Be clear about medication purposes, timing, and any precautions.
        Always recommend discussing concerns with healthcare providers."""
        
        response = await self._call_azure_openai(system_prompt, message, med_context)
        
        # Add interaction alerts to response if relevant
        if interaction_alerts and "medication" in message.lower():
            response += "\n\n⚠️ **Important Alerts:**\n" + "\n".join(f"• {alert}" for alert in interaction_alerts)
        
        return AgentResponse(
            agent_name=self.name,
            response=response,
            confidence=0.95,
            actions_taken=["Reviewed medication list", "Checked drug interactions"],
            recommendations=interaction_alerts if interaction_alerts else ["Continue current medication regimen"]
        )


class CareGapDetectionAgent(BaseAgent):
    """Agent responsible for identifying gaps in care based on clinical guidelines"""
    
    def __init__(self):
        super().__init__(
            name="Care Gap Detection Agent",
            description="Identifies missed preventive care and guideline-recommended screenings"
        )
    
    async def _demo_response(self, user_message: str, context: Dict = None) -> str:
        care_gaps = context.get("care_gaps", []) if context else []
        if care_gaps:
            high_priority = [g for g in care_gaps if g.get("severity") in ["high", "critical"]]
            return f"I've identified {len(care_gaps)} care gaps, with {len(high_priority)} requiring prompt attention. Let me help you prioritize these."
        return "I monitor your care against clinical guidelines to ensure you're receiving all recommended screenings and preventive care."
    
    async def process(self, patient_id: str, message: str, context: Dict = None) -> AgentResponse:
        # Get patient's care gaps
        patient_gaps = [gap for gap in db.care_gaps.values() 
                       if gap.patient_id == patient_id and not gap.resolved]
        
        # Build context
        gap_context = {
            "care_gaps": [gap.model_dump() for gap in patient_gaps],
            "total_gaps": len(patient_gaps),
            "high_priority_count": len([g for g in patient_gaps if g.severity in [CareGapSeverity.HIGH, CareGapSeverity.CRITICAL]])
        }
        
        system_prompt = """You are a Care Gap Detection Agent in a healthcare coordination system.
        Your role is to identify gaps in care based on clinical guidelines and help patients
        understand what preventive care and screenings they need.
        
        Prioritize high-severity gaps and provide clear, actionable recommendations.
        Be supportive and help patients feel empowered to address these gaps."""
        
        response = await self._call_azure_openai(system_prompt, message, gap_context)
        
        return AgentResponse(
            agent_name=self.name,
            response=response,
            confidence=0.9,
            actions_taken=["Reviewed clinical guidelines", "Identified care gaps"],
            recommendations=[gap.recommended_action for gap in patient_gaps[:3]]
        )


class AppointmentCoordinationAgent(BaseAgent):
    """Agent responsible for coordinating appointments across specialists"""
    
    def __init__(self):
        super().__init__(
            name="Appointment Coordination Agent",
            description="Manages and optimizes appointments across multiple healthcare providers"
        )
    
    async def _demo_response(self, user_message: str, context: Dict = None) -> str:
        appointments = context.get("appointments", []) if context else []
        upcoming = [a for a in appointments if a.get("status") == "scheduled"]
        if upcoming:
            return f"You have {len(upcoming)} upcoming appointments. I can help you prepare for each visit and ensure your doctors have the information they need."
        return "I help coordinate your appointments across all your specialists to minimize travel and ensure comprehensive care."
    
    async def process(self, patient_id: str, message: str, context: Dict = None) -> AgentResponse:
        # Get patient appointments
        patient_apts = [apt for apt in db.appointments.values() if apt.patient_id == patient_id]
        upcoming = [apt for apt in patient_apts 
                   if apt.status == AppointmentStatus.SCHEDULED and apt.appointment_date > datetime.now()]
        
        # Build context
        apt_context = {
            "appointments": [apt.model_dump() for apt in upcoming],
            "upcoming_count": len(upcoming),
            "specialties": list(set(apt.specialty for apt in upcoming))
        }
        
        system_prompt = """You are an Appointment Coordination Agent in a healthcare coordination system.
        Your role is to help patients manage appointments across multiple specialists,
        prepare for visits, and optimize their healthcare schedule.
        
        Provide practical scheduling advice and help patients prepare questions for their doctors.
        Consider travel time, telehealth options, and appointment grouping opportunities."""
        
        response = await self._call_azure_openai(system_prompt, message, apt_context)
        
        return AgentResponse(
            agent_name=self.name,
            response=response,
            confidence=0.85,
            actions_taken=["Reviewed appointment schedule", "Analyzed coordination opportunities"],
            recommendations=[f"Prepare questions for {apt.specialty} appointment on {apt.appointment_date.strftime('%B %d')}" 
                           for apt in upcoming[:2]]
        )


class OrchestratorAgent:
    """Main orchestrator that coordinates all specialist agents"""
    
    def __init__(self):
        self.agents = {
            "history": PatientHistoryAgent(),
            "medication": MedicationReconciliationAgent(),
            "care_gap": CareGapDetectionAgent(),
            "appointment": AppointmentCoordinationAgent()
        }
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    def _determine_relevant_agents(self, message: str) -> List[str]:
        """Determine which agents should respond to a message"""
        message_lower = message.lower()
        relevant = []
        
        # Keyword-based routing (would use embeddings/classification in production)
        if any(word in message_lower for word in ["history", "condition", "diagnosis", "health", "overview", "summary"]):
            relevant.append("history")
        
        if any(word in message_lower for word in ["medication", "medicine", "drug", "pill", "prescription", "dose", "interaction"]):
            relevant.append("medication")
        
        if any(word in message_lower for word in ["screening", "test", "exam", "checkup", "preventive", "gap", "overdue", "due"]):
            relevant.append("care_gap")
        
        if any(word in message_lower for word in ["appointment", "visit", "schedule", "doctor", "specialist", "telehealth"]):
            relevant.append("appointment")
        
        # Default to all agents for general queries
        if not relevant or any(word in message_lower for word in ["help", "what", "how", "everything", "all"]):
            relevant = list(self.agents.keys())
        
        return relevant
    
    async def _synthesize_responses(self, message: str, agent_responses: List[AgentResponse]) -> str:
        """Synthesize multiple agent responses into a coherent reply"""
        if not agent_responses:
            return "I'm here to help coordinate your healthcare. Could you tell me more about what you'd like to know?"
        
        if len(agent_responses) == 1:
            return agent_responses[0].response
        
        # Combine responses intelligently
        synthesis = "Based on my analysis across your care team:\n\n"
        
        for response in agent_responses:
            if response.confidence > 0.7:
                synthesis += f"**{response.agent_name}**: {response.response}\n\n"
        
        # Add unified recommendations
        all_recommendations = []
        for response in agent_responses:
            all_recommendations.extend(response.recommendations[:2])
        
        if all_recommendations:
            synthesis += "**Key Recommendations:**\n"
            for rec in all_recommendations[:4]:
                synthesis += f"• {rec}\n"
        
        return synthesis
    
    async def process_message(self, patient_id: str, message: str) -> OrchestrationResult:
        """Process a message through the multi-agent system"""
        # Determine which agents should respond
        relevant_agents = self._determine_relevant_agents(message)
        
        # Run relevant agents in parallel
        tasks = []
        for agent_key in relevant_agents:
            agent = self.agents[agent_key]
            tasks.append(agent.process(patient_id, message))
        
        agent_responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and collect valid responses
        valid_responses = [r for r in agent_responses if isinstance(r, AgentResponse)]
        
        # Synthesize responses
        primary_response = await self._synthesize_responses(message, valid_responses)
        
        # Collect care gaps and alerts
        patient_gaps = [gap for gap in db.care_gaps.values() 
                       if gap.patient_id == patient_id and not gap.resolved]
        
        medication_alerts = []
        for response in valid_responses:
            if response.agent_name == "Medication Reconciliation Agent":
                medication_alerts.extend([r for r in response.recommendations if "⚠️" in r or "alert" in r.lower()])
        
        return OrchestrationResult(
            primary_response=primary_response,
            agent_contributions=valid_responses,
            care_gaps_detected=patient_gaps[:3],
            medication_alerts=medication_alerts,
            appointment_suggestions=[r.recommendations[0] for r in valid_responses 
                                    if r.agent_name == "Appointment Coordination Agent" and r.recommendations][:2]
        )

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    print("🏥 CareOrbit Multi-Agent Healthcare System Starting...")
    print(f"📊 Loaded {len(db.patients)} patients, {len(db.medications)} medications")
    print(f"🔍 {len(db.care_gaps)} care gaps detected")
    yield
    print("👋 CareOrbit shutting down...")

app = FastAPI(
    title="CareOrbit API",
    description="Multi-Agent Healthcare Coordination System for Chronic Disease Management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://localhost:3000",
        "https://careorbit.vercel.app",
        "https://careorbit1.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "CareOrbit API",
        "version": "1.0.0",
        "status": "healthy",
        "description": "Multi-Agent Healthcare Coordination System"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "agents": {
            "history": "active",
            "medication": "active",
            "care_gap": "active",
            "appointment": "active"
        },
        "azure_services": {
            "openai": "configured" if settings.AZURE_OPENAI_ENDPOINT else "demo_mode",
            "ai_search": "configured" if settings.AZURE_AI_SEARCH_ENDPOINT else "demo_mode"
        }
    }

# Patient Endpoints
@app.get("/api/patients", response_model=List[Patient])
async def get_patients():
    """Get all patients"""
    return list(db.patients.values())

@app.get("/api/patients/{patient_id}", response_model=Patient)
async def get_patient(patient_id: str):
    """Get a specific patient"""
    patient = db.patients.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.post("/api/patients", response_model=Patient)
async def create_patient(patient_data: PatientCreate):
    """Create a new patient"""
    patient = Patient(**patient_data.model_dump())
    db.patients[patient.id] = patient
    return patient

@app.get("/api/patients/{patient_id}/summary", response_model=HealthSummary)
async def get_patient_summary(patient_id: str):
    """Get comprehensive health summary for a patient"""
    patient = db.patients.get(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Gather data
    medications = [m for m in db.medications.values() 
                  if m.patient_id == patient_id and m.status == MedicationStatus.ACTIVE]
    appointments = [a for a in db.appointments.values() 
                   if a.patient_id == patient_id and a.status == AppointmentStatus.SCHEDULED 
                   and a.appointment_date > datetime.now()]
    care_gaps = [g for g in db.care_gaps.values() 
                if g.patient_id == patient_id and not g.resolved]
    
    # Determine critical alerts
    critical_alerts = []
    high_gaps = [g for g in care_gaps if g.severity in [CareGapSeverity.HIGH, CareGapSeverity.CRITICAL]]
    if high_gaps:
        critical_alerts.append(f"{len(high_gaps)} high-priority care gaps need attention")
    
    low_refill_meds = [m for m in medications if m.refills_remaining <= 1]
    if low_refill_meds:
        critical_alerts.append(f"{len(low_refill_meds)} medications need refill soon")
    
    return HealthSummary(
        patient_id=patient_id,
        overall_status="Stable - Active Monitoring" if len(critical_alerts) < 2 else "Needs Attention",
        active_conditions=patient.conditions,
        active_medications=len(medications),
        upcoming_appointments=len(appointments),
        open_care_gaps=len(care_gaps),
        critical_alerts=critical_alerts,
        last_updated=datetime.utcnow()
    )

# Medication Endpoints
@app.get("/api/patients/{patient_id}/medications", response_model=List[Medication])
async def get_patient_medications(patient_id: str, active_only: bool = False):
    """Get medications for a patient"""
    medications = [m for m in db.medications.values() if m.patient_id == patient_id]
    if active_only:
        medications = [m for m in medications if m.status == MedicationStatus.ACTIVE]
    return medications

@app.post("/api/medications", response_model=Medication)
async def create_medication(med_data: MedicationCreate):
    """Create a new medication record"""
    medication = Medication(**med_data.model_dump())
    db.medications[medication.id] = medication
    return medication

# Appointment Endpoints
@app.get("/api/patients/{patient_id}/appointments", response_model=List[Appointment])
async def get_patient_appointments(patient_id: str, upcoming_only: bool = False):
    """Get appointments for a patient"""
    appointments = [a for a in db.appointments.values() if a.patient_id == patient_id]
    if upcoming_only:
        appointments = [a for a in appointments 
                       if a.status == AppointmentStatus.SCHEDULED and a.appointment_date > datetime.now()]
    appointments.sort(key=lambda x: x.appointment_date)
    return appointments

@app.post("/api/appointments", response_model=Appointment)
async def create_appointment(apt_data: AppointmentCreate):
    """Create a new appointment"""
    appointment = Appointment(**apt_data.model_dump())
    db.appointments[appointment.id] = appointment
    return appointment

# Care Gap Endpoints
@app.get("/api/patients/{patient_id}/care-gaps", response_model=List[CareGap])
async def get_patient_care_gaps(patient_id: str, include_resolved: bool = False):
    """Get care gaps for a patient"""
    gaps = [g for g in db.care_gaps.values() if g.patient_id == patient_id]
    if not include_resolved:
        gaps = [g for g in gaps if not g.resolved]
    gaps.sort(key=lambda x: (0 if x.severity == CareGapSeverity.CRITICAL else 
                             1 if x.severity == CareGapSeverity.HIGH else 
                             2 if x.severity == CareGapSeverity.MEDIUM else 3))
    return gaps

@app.patch("/api/care-gaps/{gap_id}/resolve")
async def resolve_care_gap(gap_id: str):
    """Mark a care gap as resolved"""
    gap = db.care_gaps.get(gap_id)
    if not gap:
        raise HTTPException(status_code=404, detail="Care gap not found")
    gap.resolved = True
    gap.resolved_at = datetime.utcnow()
    return {"status": "resolved", "gap_id": gap_id}

# Chat/Agent Endpoints
@app.post("/api/chat", response_model=OrchestrationResult)
async def chat_with_agents(request: ChatRequest):
    """Send a message to the multi-agent system"""
    # Verify patient exists
    patient = db.patients.get(request.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Store user message
    user_msg = ChatMessage(
        patient_id=request.patient_id,
        role="user",
        content=request.message
    )
    if request.patient_id not in db.chat_history:
        db.chat_history[request.patient_id] = []
    db.chat_history[request.patient_id].append(user_msg)
    
    # Process through orchestrator
    result = await orchestrator.process_message(request.patient_id, request.message)
    
    # Store assistant response
    assistant_msg = ChatMessage(
        patient_id=request.patient_id,
        role="assistant",
        content=result.primary_response,
        metadata={
            "agents_used": [r.agent_name for r in result.agent_contributions],
            "care_gaps_mentioned": len(result.care_gaps_detected)
        }
    )
    db.chat_history[request.patient_id].append(assistant_msg)
    
    return result

@app.get("/api/patients/{patient_id}/chat-history", response_model=List[ChatMessage])
async def get_chat_history(patient_id: str, limit: int = 50):
    """Get chat history for a patient"""
    history = db.chat_history.get(patient_id, [])
    return history[-limit:]

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
