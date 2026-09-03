import json
import os
import uuid

def create_demo_data():
    os.makedirs("data/demo", exist_ok=True)
    
    # 1. Natural Recovery Trap: high natural recovery, slight uplift, negative net value
    case_1 = {
        "case_id": "demo_trap_001",
        "customer_id": "cust_demo_1",
        "amount_paise": 500000, # 5000 INR
        "failure_code": "NETWORK_ERROR",
        "payment_method": "upi",
        "y_0": 0.90, # True natural recovery (prob)
        "y_1": 0.91, # True retry now recovery (prob)
        "y_2": 0.92,
        "y_3": 0.92,
        "y_4": 0.93,
        "y_5": 0.95
    }
    
    # 2. Hidden Goldmine: low natural recovery, high specific uplift
    case_2 = {
        "case_id": "demo_gold_002",
        "customer_id": "cust_demo_2",
        "amount_paise": 1500000, # 15000 INR
        "failure_code": "INSUFFICIENT_FUNDS",
        "payment_method": "card",
        "y_0": 0.15,
        "y_1": 0.16,
        "y_2": 0.65, # RETRY LATER works great
        "y_3": 0.20,
        "y_4": 0.35,
        "y_5": 0.40
    }
    
    # 3. Harmful Intervention: Action makes it worse
    case_3 = {
        "case_id": "demo_harm_003",
        "customer_id": "cust_demo_3",
        "amount_paise": 200000,
        "failure_code": "BANK_TIMEOUT",
        "payment_method": "netbanking",
        "y_0": 0.60,
        "y_1": 0.30, # Immediate retry triggers fraud lock
        "y_2": 0.65,
        "y_3": 0.65,
        "y_4": 0.85, # Alternate method works great
        "y_5": 0.70
    }
    
    # 4. Policy Rejection / Abstention: Hard decline
    case_4 = {
        "case_id": "demo_reject_004",
        "customer_id": "cust_demo_4",
        "amount_paise": 750000,
        "failure_code": "BANK_DECLINE",
        "payment_method": "card",
        "y_0": 0.05,
        "y_1": 0.80, # The model thinks it can recover it
        "y_2": 0.80,
        "y_3": 0.10,
        "y_4": 0.15,
        "y_5": 0.10
    }
    
    cases = [case_1, case_2, case_3, case_4]
    with open("data/demo/cases.json", "w") as f:
        json.dump(cases, f, indent=2)
        
    print("Demo dataset seeded to data/demo/cases.json")

if __name__ == "__main__":
    create_demo_data()
