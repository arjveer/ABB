"""
Email data models and structures for the email assistant.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from enum import Enum


class EmailCategory(str, Enum):
    """Email categories for classification."""
    URGENT = "urgent"
    WORK = "work"
    PERSONAL = "personal"
    PROMOTIONAL = "promotional"
    SOCIAL = "social"
    FINANCIAL = "financial"
    TRAVEL = "travel"
    HEALTH = "health"
    EDUCATION = "education"
    SPAM = "spam"
    UNKNOWN = "unknown"


class EmailPriority(str, Enum):
    """Email priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EmailAction(str, Enum):
    """Suggested actions for emails."""
    REPLY = "reply"
    FORWARD = "forward"
    ARCHIVE = "archive"
    DELETE = "delete"
    SCHEDULE = "schedule"
    FLAG = "flag"
    IGNORE = "ignore"


class Email(BaseModel):
    """Email data model."""
    id: str = Field(..., description="Unique email identifier")
    subject: str = Field(..., description="Email subject line")
    sender: EmailStr = Field(..., description="Sender email address")
    recipient: EmailStr = Field(..., description="Recipient email address")
    body: str = Field(..., description="Email body content")
    timestamp: datetime = Field(..., description="Email timestamp")
    category: Optional[EmailCategory] = Field(None, description="Classified category")
    priority: Optional[EmailPriority] = Field(None, description="Assigned priority")
    suggested_action: Optional[EmailAction] = Field(None, description="Suggested action")
    confidence_score: Optional[float] = Field(None, description="Classification confidence")
    tags: List[str] = Field(default_factory=list, description="Email tags")
    is_read: bool = Field(default=False, description="Read status")
    is_important: bool = Field(default=False, description="Important flag")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmailDraft(BaseModel):
    """Email draft model."""
    id: str = Field(..., description="Draft identifier")
    subject: str = Field(..., description="Draft subject")
    recipient: EmailStr = Field(..., description="Recipient email")
    body: str = Field(..., description="Draft body content")
    tone: str = Field(..., description="Email tone (formal, casual, etc.)")
    purpose: str = Field(..., description="Email purpose")
    created_at: datetime = Field(default_factory=datetime.now)
    is_sent: bool = Field(default=False, description="Sent status")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EmailAnalysis(BaseModel):
    """Email analysis results."""
    email_id: str
    category: EmailCategory
    priority: EmailPriority
    suggested_action: EmailAction
    confidence_score: float
    key_topics: List[str] = Field(default_factory=list)
    sentiment: str = Field(..., description="Email sentiment (positive, negative, neutral)")
    urgency_indicators: List[str] = Field(default_factory=list)
    suggested_reply_tone: str = Field(..., description="Suggested tone for reply")
    estimated_response_time: str = Field(..., description="Estimated time to respond")
    related_emails: List[str] = Field(default_factory=list, description="Related email IDs")


class EmailSummary(BaseModel):
    """Email inbox summary."""
    total_emails: int
    unread_count: int
    urgent_count: int
    category_breakdown: Dict[EmailCategory, int]
    priority_breakdown: Dict[EmailPriority, int]
    action_breakdown: Dict[EmailAction, int]
    top_senders: List[Dict[str, Any]]
    recent_emails: List[Email]
    suggested_actions: List[Dict[str, Any]]


class EmailAgentConfig(BaseModel):
    """Configuration for email agents."""
    openai_model: str = "gpt-4"
    embedding_model: str = "all-MiniLM-L6-v2"
    max_emails_per_batch: int = 50
    confidence_threshold: float = 0.7
    enable_auto_categorization: bool = True
    enable_priority_assignment: bool = True
    enable_action_suggestions: bool = True
    enable_draft_generation: bool = True
