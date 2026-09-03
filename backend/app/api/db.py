import sqlite3
import json
import os
from typing import Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "../../../data/causal_recover.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Cases
    c.execute('''
        CREATE TABLE IF NOT EXISTS cases (
            case_id TEXT PRIMARY KEY,
            amount_paise INTEGER,
            payment_method TEXT,
            bank TEXT,
            failure_code TEXT,
            retries_attempted INTEGER,
            time_since_failure_minutes INTEGER,
            historical_payment_success_rate REAL,
            engagement_score REAL,
            customer_value_band TEXT,
            is_demo BOOLEAN DEFAULT 0
        )
    ''')
    
    # Incidents
    c.execute('''
        CREATE TABLE IF NOT EXISTS incidents (
            id TEXT PRIMARY KEY,
            type TEXT,
            severity TEXT,
            start_time TEXT,
            duration_minutes INTEGER,
            affected_payment_method TEXT,
            affected_bank TEXT,
            transactions_affected INTEGER,
            revenue_exposed_paise INTEGER,
            status TEXT
        )
    ''')
    
    # Executions
    c.execute('''
        CREATE TABLE IF NOT EXISTS executions (
            correlation_id TEXT PRIMARY KEY,
            case_id TEXT,
            action_id INTEGER,
            provider_id TEXT,
            status TEXT,
            recovered_amount INTEGER,
            simulated BOOLEAN,
            timestamp REAL
        )
    ''')
    
    # Audit Events
    c.execute('''
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            case_id TEXT,
            correlation_id TEXT,
            event_type TEXT,
            description TEXT,
            model_version TEXT,
            policy_version TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def log_audit_event(case_id: str, correlation_id: str, event_type: str, description: str):
    import time
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO audit_events (timestamp, case_id, correlation_id, event_type, description, model_version, policy_version)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (time.time(), case_id, correlation_id, event_type, description, "SupportAware-v1", "Governor-v1"))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("DB initialized.")
