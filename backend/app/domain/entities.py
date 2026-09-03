from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Customer:
    id: str
    # Latent variables (hidden from production)
    latent_payment_reliability: float
    latent_liquidity: float
    latent_digital_engagement: float
    latent_price_sensitivity: float
    latent_urgency: float
    latent_customer_value: float
    
    # Responsiveness to specific actions
    latent_retry_responsiveness: float
    latent_delayed_retry_responsiveness: float
    latent_message_responsiveness: float
    latent_alternate_method_responsiveness: float
    latent_human_escalation_responsiveness: float

@dataclass
class PaymentCase:
    id: str
    customer_id: str
    amount_paise: int
    payment_method: str
    failure_code: str
    time_since_failure_minutes: int
    incident_id: Optional[str] = None
    
    # Observable features (derived with noise from latent)
    historical_payment_success_rate: float = 0.0
    customer_value_band: str = "medium"
    engagement_score: float = 0.0

@dataclass
class PotentialOutcome:
    case_id: str
    y_0: int  # NO_ACTION
    y_1: int  # RETRY_NOW
    y_2: int  # RETRY_LATER
    y_3: int  # PAYMENT_MESSAGE
    y_4: int  # ALTERNATE_METHOD
    y_5: int  # HUMAN_ESCALATION

@dataclass
class TreatmentAssignment:
    case_id: str
    assigned_action: int
    propensity: float
    eligible_actions: List[int]
    policy_version: str

@dataclass
class ObservedOutcome:
    case_id: str
    assigned_action: int
    y_observed: int
