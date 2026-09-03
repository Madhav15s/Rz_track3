import json
import os
from backend.app.causal.estimators import TLearner
from backend.app.policy.economic_policy import EconomicPolicyOptimizer, DeterministicPolicyGovernor
from backend.app.razorpay.adapter import RazorpayTestAdapter, OutcomeLedger
import pandas as pd
import numpy as np

def run_demo():
    print("--- CAUSAL RECOVER: END-TO-END DEMO ---")
    
    # 1. Train quick dummy model
    print("1. Bootstrapping Models...")
    np.random.seed(42)
    df_feat = pd.DataFrame([{
        'case_id': f'c_{i}', 
        'amount_paise': 50000, 
        'failure_code': 'BANK_TIMEOUT',
        'time_since_failure_minutes': 10,
        'historical_payment_success_rate': 0.8,
        'engagement_score': 0.9,
        'payment_method': 'card',
        'customer_value_band': 'high'
    } for i in range(100)])
    df_treat = pd.DataFrame([{'case_id': f'c_{i}', 'assigned_action': i%6, 'propensity': 1/6} for i in range(100)])
    df_out = pd.DataFrame([{'case_id': f'c_{i}', 'assigned_action': i%6, 'y_observed': 1 if (np.random.rand() < 0.2 or (i%6==2 and np.random.rand() < 0.9)) else 0} for i in range(100)])
    
    # Inject guaranteed 0 and 1 for each action
    for a in range(6):
        df_out.loc[a, 'y_observed'] = 0
        df_out.loc[a+6, 'y_observed'] = 1
    
    model = TLearner()
    model.fit(df_feat, df_treat, df_out)
    optimizer = EconomicPolicyOptimizer(model)
    governor = DeterministicPolicyGovernor()
    
    ledger = OutcomeLedger()
    adapter = RazorpayTestAdapter(ledger)
    
    # 2. Synthetic Failure Incident
    context = {
        'case_id': 'fail_9999',
        'amount_paise': 75000,
        'failure_code': 'BANK_TIMEOUT',
        'retries_attempted': 0,
        'time_since_failure_minutes': 10,
        'historical_payment_success_rate': 0.8,
        'engagement_score': 0.9,
        'payment_method': 'card',
        'customer_value_band': 'high'
    }
    
    audit_trace = {"incident": context, "steps": []}
    print(f"\n2. Incident Detected: {context['case_id']} - {context['failure_code']}")
    
    # 3. Causal Policy Recommendation
    decision = optimizer.get_best_action(context)
    action_id = decision['recommended_action']
    print(f"\n3. Causal Intelligence recommends Action {action_id}")
    print(f"   Expected Incremental Value: {decision['expected_incremental_value']} paise")
    audit_trace['steps'].append({"step": "causal_recommendation", "decision": decision})
    
    # 4. Governor Approval
    approval = governor.evaluate(context, action_id)
    print(f"\n4. Policy Governor: {approval['status']}")
    print(f"   Correlation ID: {approval.get('correlation_id')}")
    audit_trace['steps'].append({"step": "governor_evaluation", "approval": approval})
    
    # 5. Razorpay Execution
    if approval['status'] == 'APPROVED':
        print("\n5. Executing via Razorpay Adapter...")
        result = adapter.execute_action(action_id, context, approval)
        print(f"   Status: {result['api_status']}")
        print(f"   Provider ID: {result['provider_id']}")
        audit_trace['steps'].append({"step": "razorpay_execution", "result": result})
        
        # 6. Webhook
        print("\n6. Simulating Razorpay Webhook...")
        webhook_payload = {
            "webhook_id": "wh_evt_888",
            "provider_id": result['provider_id'],
            "event_type": "payment_link.paid",
            "amount": context['amount_paise']
        }
        wh_result = ledger.verify_webhook(**webhook_payload)
        print(f"   Webhook Verification: {wh_result['status']}")
        audit_trace['steps'].append({"step": "webhook_received", "verification": wh_result})
        
        # 7. Verification Ledger
        print("\n7. Final Ledger Verification")
        final_state = ledger.get_status(approval['correlation_id'])
        print(f"   Recovered Amount: {final_state['recovered_amount']} paise")
        audit_trace['steps'].append({"step": "ledger_final", "state": final_state})
        
    os.makedirs('data/demo', exist_ok=True)
    with open('data/demo/e2e_audit_trace.json', 'w') as f:
        json.dump(audit_trace, f, indent=2)
    print("\n[Audit trace saved to data/demo/e2e_audit_trace.json]")

if __name__ == "__main__":
    run_demo()
