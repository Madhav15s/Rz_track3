# CausalRecover Frontend API Contract

The frontend consumes an existing FastAPI backend.

Base URL:

http://127.0.0.1:8000

## Read endpoints

GET /api/overview
GET /api/cases
GET /api/cases/{case_id}
GET /api/incidents
GET /api/evaluation
GET /api/audit

## Mutation

POST /api/cases/{case_id}/execute

The frontend MUST NOT implement:
- causal calculations
- treatment-effect estimation
- economic policy
- policy authorization
- Razorpay authorization
- payment verification

The backend is the source of truth.

## Important data distinction

Live decision views may use:
- estimated_uplift
- support
- confidence
- expected_incremental_value
- selected_action
- policy_status

Live decision views MUST NOT expose:
- y_0
- y_1
- y_2
- y_3
- y_4
- y_5
- true_uplift
- oracle_action
- hidden latent variables

Those are evaluation-only concepts.