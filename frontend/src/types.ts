export interface Case {
  case_id: string;
  amount_paise: number;
  payment_method: string;
  bank: string;
  failure_code: string;
  retries_attempted: number;
  time_since_failure_minutes: number;
  historical_payment_success_rate: number;
  engagement_score: number;
  customer_value_band: 'low' | 'medium' | 'high' | string;
  is_demo?: number;
}

export interface CandidateAction {
  action: number;
  name: string;
  estimated_uplift: number;
  support: number;
  confidence: 'LOW' | 'MEDIUM' | 'HIGH' | string;
  expected_incremental_value_paise: number;
  status: 'SELECTED' | 'NOT SELECTED' | 'ABSTAINED' | 'POLICY_REJECTED' | 'AVAILABLE';
}

export interface DecisionResponse {
  candidate_actions: CandidateAction[];
  recommended_action: number;
  governor_status: 'APPROVED' | 'POLICY_REJECTED' | 'REJECTED';
  rejection_reason?: string;
  explanation: string;
}

export interface Incident {
  id: string;
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  start_time: number;
  duration_minutes: number;
  affected_payment_method: string;
  affected_bank: string;
  transactions_affected: number;
  revenue_exposed_paise: number;
  status: 'ACTIVE' | 'RESOLVED' | 'MONITORING';
}

export interface AuditEvent {
  id: number;
  timestamp: number; // Unix seconds
  case_id: string;
  correlation_id: string;
  event_type: string;
  description: string;
  model_version?: string;
  policy_version?: string;
}

export interface OverviewMetrics {
  revenue_at_risk: number;
  gross_recovery: number;
  natural_recovery: number;
  incremental_recovery: number;
  net_incremental_recovery: number;
  interventions: number;
  abstentions: number;
  policy_rejections: number;
  verified_recoveries: number;
  policy_violations: number;
}

export interface ExecutionRecord {
  correlation_id: string;
  case_id: string;
  action_id: number;
  provider_id: string;
  status: 'PROPOSED' | 'APPROVED' | 'PENDING_VERIFICATION' | 'VERIFIED_RECOVERED' | 'POLICY_REJECTED' | 'EXECUTED_NO_ACTION';
  recovered_amount: number;
  simulated: number;
  timestamp: number;
}
