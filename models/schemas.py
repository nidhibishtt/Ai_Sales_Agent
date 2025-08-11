from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ClientInquiry(BaseModel):
    """Model for structured client inquiry data"""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    role_counts: Dict[str, int] = Field(default_factory=dict)
    urgency: Optional[UrgencyLevel] = None
    budget_range: Optional[str] = None
    experience_level: Optional[str] = None
    additional_requirements: Optional[str] = None
    contact_info: Optional[Dict[str, str]] = Field(default_factory=dict)


class ServicePackage(BaseModel):
    """Model for recruiting service packages"""
    package_id: str
    name: str
    description: str
    target_industries: List[str]
    target_roles: List[str]
    price_range: str
    features: List[str]
    typical_timeline: str
    success_rate: Optional[str] = None


class ConversationState(BaseModel):
    """Model for maintaining conversation state"""
    session_id: str
    client_inquiry: ClientInquiry
    recommended_packages: List[ServicePackage] = Field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    current_stage: str = "greeting"  # greeting, inquiry, recommendation, proposal, follow_up
    next_actions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProposalResponse(BaseModel):
    """Model for generated proposal responses"""
    summary: str
    recommended_package: ServicePackage
    personalized_pitch: str
    next_steps: List[str]
    estimated_timeline: str
    price_estimate: Optional[str] = None


class ExtractionResult(BaseModel):
    """Model for NER extraction results"""
    entities: Dict[str, Any]
    confidence_scores: Dict[str, float]
    extracted_inquiry: ClientInquiry
