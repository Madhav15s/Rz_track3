import numpy as np
import uuid
import pandas as pd
from typing import List, Tuple
from backend.app.domain.entities import Customer, PaymentCase, PotentialOutcome

# Action Map
# 0 = NO_ACTION
# 1 = RETRY_NOW
# 2 = RETRY_LATER
# 3 = PAYMENT_MESSAGE
# 4 = ALTERNATE_METHOD
# 5 = HUMAN_ESCALATION

class SyntheticWorldGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = np.random.default_rng(seed)

    def generate_customers(self, num_customers: int) -> List[Customer]:
        customers = []
        for _ in range(num_customers):
            # Non-degenerate Beta distributions
            reliability = self.rng.beta(6, 2)
            liquidity = self.rng.beta(3, 3)
            engagement = self.rng.beta(2, 3)
            price_sens = self.rng.beta(2, 5)
            urgency = self.rng.beta(2, 4)
            
            # Long tail value
            value = self.rng.lognormal(mean=10, sigma=1.5)
            
            # Action responsiveness
            # Some customers are very responsive to retry now, others to later
            retry_resp = self.rng.beta(2, 4)
            delayed_resp = self.rng.beta(3, 3)
            msg_resp = engagement * self.rng.beta(3, 2)
            alt_resp = liquidity * self.rng.beta(2, 2)
            human_resp = self.rng.beta(4, 2) if value > 50000 else self.rng.beta(1, 5)

            cust = Customer(
                id=f"cust_{uuid.uuid4().hex[:8]}",
                latent_payment_reliability=reliability,
                latent_liquidity=liquidity,
                latent_digital_engagement=engagement,
                latent_price_sensitivity=price_sens,
                latent_urgency=urgency,
                latent_customer_value=value,
                latent_retry_responsiveness=retry_resp,
                latent_delayed_retry_responsiveness=delayed_resp,
                latent_message_responsiveness=msg_resp,
                latent_alternate_method_responsiveness=alt_resp,
                latent_human_escalation_responsiveness=human_resp
            )
            customers.append(cust)
        return customers

    def generate_cases_and_outcomes(self, customers: List[Customer]) -> Tuple[List[PaymentCase], List[PotentialOutcome]]:
        cases = []
        outcomes = []
        
        methods = ["upi", "card", "netbanking"]
        failures = ["INSUFFICIENT_FUNDS", "BANK_TIMEOUT", "BANK_DECLINE", "NETWORK_ERROR"]
        
        for cust in customers:
            # Observables with noise
            obs_success_rate = np.clip(cust.latent_payment_reliability + self.rng.normal(0, 0.1), 0, 1)
            band = "high" if cust.latent_customer_value > 200000 else ("low" if cust.latent_customer_value < 50000 else "medium")
            obs_engagement = np.clip(cust.latent_digital_engagement + self.rng.normal(0, 0.1), 0, 1)
            
            method = self.rng.choice(methods, p=[0.6, 0.3, 0.1])
            
            # Failure distribution depends on method
            if method == "upi":
                fail_probs = [0.4, 0.4, 0.0, 0.2]
            else:
                fail_probs = [0.3, 0.1, 0.5, 0.1]
                
            failure = self.rng.choice(failures, p=fail_probs)
            
            case_id = f"case_{uuid.uuid4().hex[:8]}"
            amount = int(np.clip(self.rng.lognormal(mean=7, sigma=1.2) * 100, 1000, 10000000)) # in paise
            
            case = PaymentCase(
                id=case_id,
                customer_id=cust.id,
                amount_paise=amount,
                payment_method=method,
                failure_code=failure,
                time_since_failure_minutes=int(self.rng.exponential(30)),
                historical_payment_success_rate=obs_success_rate,
                customer_value_band=band,
                engagement_score=obs_engagement
            )
            cases.append(case)
            
            # Generate potential outcomes using logistic formulation
            # p0 = natural recovery
            logit_p0 = (
                -2.0 
                + 3.0 * cust.latent_payment_reliability 
                + 2.0 * cust.latent_liquidity 
                - 1.0 * (failure == "INSUFFICIENT_FUNDS")
                - 1.5 * (failure == "BANK_DECLINE")
            )
            p0 = 1 / (1 + np.exp(-logit_p0))
            
            # Action 1: RETRY_NOW
            # Positive if network error, negative if insufficient funds
            logit_p1 = logit_p0 + 2.0 * cust.latent_retry_responsiveness - 2.0 * (failure == "INSUFFICIENT_FUNDS") + 1.5 * (failure == "BANK_TIMEOUT")
            p1 = 1 / (1 + np.exp(-logit_p1))
            
            # Action 2: RETRY_LATER
            # Stronger if insufficient funds
            logit_p2 = logit_p0 + 2.5 * cust.latent_delayed_retry_responsiveness + 1.5 * (failure == "INSUFFICIENT_FUNDS")
            p2 = 1 / (1 + np.exp(-logit_p2))
            
            # Action 3: PAYMENT_MESSAGE
            logit_p3 = logit_p0 + 2.0 * cust.latent_message_responsiveness
            p3 = 1 / (1 + np.exp(-logit_p3))
            
            # Action 4: ALTERNATE_METHOD
            logit_p4 = logit_p0 + 3.0 * cust.latent_alternate_method_responsiveness - 1.0 * (method == "netbanking")
            p4 = 1 / (1 + np.exp(-logit_p4))
            
            # Action 5: HUMAN_ESCALATION
            logit_p5 = logit_p0 + 4.0 * cust.latent_human_escalation_responsiveness
            p5 = 1 / (1 + np.exp(-logit_p5))
            
            # Sample actual outcomes from probabilities
            po = PotentialOutcome(
                case_id=case_id,
                y_0=self.rng.binomial(1, p0),
                y_1=self.rng.binomial(1, p1),
                y_2=self.rng.binomial(1, p2),
                y_3=self.rng.binomial(1, p3),
                y_4=self.rng.binomial(1, p4),
                y_5=self.rng.binomial(1, p5)
            )
            outcomes.append(po)
            
        return cases, outcomes

if __name__ == "__main__":
    gen = SyntheticWorldGenerator(seed=42)
    customers = gen.generate_customers(10)
    cases, outcomes = gen.generate_cases_and_outcomes(customers)
    print(f"Generated {len(customers)} customers and {len(cases)} cases.")
    print("Example PO:", outcomes[0])
