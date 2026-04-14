from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class AgentMode(Enum):
    ADMIN_SECURITY = "admin_security"
    USER_ADVISORY = "user_advisory"

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

@dataclass
class GroceryProfile:
    dietary_restrictions: List[str]
    household_size: int
    weekly_budget: float
    pantry_inventory: List[str]

@dataclass
class UserContext:
    user_id: str
    role: UserRole
    location: str
    preferences: Dict[str, Any]
    transaction_history: List[Dict[str, Any]]
    token: str = None
    grocery_profile: Optional[GroceryProfile] = None

    def __post_init__(self):
        # Default mock profile if none provided
        if self.grocery_profile is None:
            self.grocery_profile = GroceryProfile(
                dietary_restrictions=[],
                household_size=2,
                weekly_budget=150.0,
                pantry_inventory=["salt", "pepper", "olive oil", "sugar", "rice"]
            )

class ThreatAnalysisResult(BaseModel):
    threat_detected: bool = Field(description="Whether a threat was detected")
    threat_type: str = Field(description="Type of threat detected")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    severity: str = Field(description="Threat severity: LOW, MEDIUM, HIGH, CRITICAL")
    recommendation: str = Field(description="Recommended action")
    explanation: str = Field(description="Detailed explanation of the threat")

class FinancialAdvice(BaseModel):
    analysis_summary: str = Field(description="Summary of spending analysis")
    weekly_spending: float = Field(description="Current weekly spending amount")
    recommended_reduction: float = Field(description="Recommended spending reduction")
    savings_suggestions: List[str] = Field(description="List of specific savings suggestions")
    grocery_deals: List[Dict[str, str]] = Field(description="List of grocery deals found")
    action_plan: str = Field(description="Step-by-step action plan")
    spending_by_category: Dict[str, float] = Field(default_factory=dict, description="Spending breakdown by category")
    financial_news: List[Dict[str, str]] = Field(default_factory=list, description="Relevant financial news items")
