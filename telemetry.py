"""
Datadog Telemetry & Monitoring
Handles all Datadog instrumentation, metrics, and logging
"""

import os
import logging
from typing import Dict, Optional
from datadog import initialize, statsd
from ddtrace import tracer
import json

logger = logging.getLogger(__name__)


def setup_telemetry():
    """Initialize Datadog monitoring"""
    dd_api_key = os.getenv('DD_API_KEY')
    
    # Skip Datadog if no API key provided
    if not dd_api_key or dd_api_key == 'your_datadog_api_key_here':
        logger.warning("⚠️  Datadog API key not configured - telemetry disabled")
        logger.warning("   Add DD_API_KEY to .env to enable Datadog monitoring")
        return
    
    options = {
        'api_key': dd_api_key,
        'app_key': os.getenv('DD_APP_KEY'),
        'statsd_host': '127.0.0.1',
        'statsd_port': 8125,
    }
    
    try:
        initialize(**options)
        logger.info("✅ Datadog telemetry initialized")
    except Exception as e:
        logger.warning(f"Datadog initialization warning: {e}")


def log_llm_interaction(
    question: str,
    answer: str,
    user_id: str,
    session_id: str,
    latency_ms: float,
    token_count: int,
    risk_score: float,
    safety_ratings: Dict,
    retrieved_docs: int
):
    """
    Log LLM interaction to Datadog with custom metrics
    """
    
    # Send metrics (wrapped in try/except in case Datadog not configured)
    try:
        statsd.increment('llm.requests.total', tags=[
            f'user:{user_id}',
            f'session:{session_id}'
        ])
        
        statsd.histogram('llm.latency', latency_ms, tags=['service:medical-qa'])
        statsd.gauge('llm.tokens', token_count, tags=['service:medical-qa'])
        statsd.gauge('llm.risk_score', risk_score, tags=['service:medical-qa'])
        statsd.gauge('llm.retrieved_docs', retrieved_docs, tags=['service:medical-qa'])
    except Exception as e:
        logger.debug(f"Datadog metrics not sent (not configured): {e}")
    
    # Check for high-risk safety ratings
    high_risk_categories = []
    for category, rating in safety_ratings.items():
        if rating in ['MEDIUM', 'HIGH']:
            high_risk_categories.append(category)
            try:
                statsd.increment('llm.safety_violation', tags=[
                    f'category:{category}',
                    f'severity:{rating}'
                ])
            except Exception:
                pass
    
    # Structured logging for Datadog
    log_data = {
        'event_type': 'llm_interaction',
        'question': question[:200],  # Truncate for log size
        'answer': answer[:500],
        'user_id': user_id,
        'session_id': session_id,
        'metrics': {
            'latency_ms': latency_ms,
            'token_count': token_count,
            'risk_score': risk_score,
            'retrieved_docs': retrieved_docs
        },
        'safety_ratings': safety_ratings,
        'high_risk_categories': high_risk_categories
    }
    
    # Log at appropriate level based on risk
    if risk_score > 0.7:
        logger.warning(f"HIGH RISK INTERACTION: {json.dumps(log_data)}")
        try:
            statsd.increment('llm.high_risk_interaction')
        except Exception:
            pass
    elif high_risk_categories:
        logger.warning(f"SAFETY VIOLATION: {json.dumps(log_data)}")
    else:
        logger.info(f"LLM Interaction: {json.dumps(log_data)}")


def calculate_risk_score(
    text: str,
    safety_ratings: Dict,
    token_count: int
) -> float:
    """
    Calculate risk score for LLM response
    
    Risk factors:
    - Safety violations
    - High token count (potential hallucination)
    - Uncertainty phrases
    - Medical disclaimer missing
    
    Returns: float between 0.0 and 1.0
    """
    risk = 0.0
    
    # Factor 1: Safety ratings
    for category, rating in safety_ratings.items():
        if rating == 'HIGH':
            risk += 0.4
        elif rating == 'MEDIUM':
            risk += 0.2
    
    # Factor 2: Token count (very long responses may be verbose/uncertain)
    if token_count > 1000:
        risk += 0.3
    elif token_count > 500:
        risk += 0.15
    
    # Factor 3: Uncertainty phrases
    text_lower = text.lower()
    uncertainty_phrases = [
        "i'm not sure", "i don't know", "maybe", "possibly",
        "might be", "could be", "uncertain", "not certain"
    ]
    
    uncertainty_count = sum(1 for phrase in uncertainty_phrases if phrase in text_lower)
    risk += min(0.2, uncertainty_count * 0.05)
    
    # Factor 4: Medical context - missing disclaimers
    disclaimer_phrases = ["consult", "doctor", "medical professional", "physician"]
    has_disclaimer = any(phrase in text_lower for phrase in disclaimer_phrases)
    
    # Medical advice without disclaimer is risky
    medical_keywords = ["take", "medication", "dose", "treatment", "diagnose"]
    has_medical_advice = any(keyword in text_lower for keyword in medical_keywords)
    
    if has_medical_advice and not has_disclaimer:
        risk += 0.2
    
    # Ensure risk is between 0 and 1
    return min(1.0, max(0.0, risk))


def send_custom_metric(metric_name: str, value: float, tags: Optional[list] = None):
    """Send a custom metric to Datadog"""
    statsd.gauge(metric_name, value, tags=tags or [])


def send_custom_event(title: str, text: str, alert_type: str = "info", tags: Optional[list] = None):
    """Send a custom event to Datadog"""
    logger.info(f"Custom Event: {title} - {text}")
    # Note: For full event API support, use datadog_api_client
    

if __name__ == "__main__":
    # Test telemetry
    setup_telemetry()
    
    # Test risk calculation
    test_response = "You should take 500mg of ibuprofen every 6 hours. Maybe consult your doctor."
    test_safety = {"HARM_CATEGORY_HATE_SPEECH": "NEGLIGIBLE"}
    
    risk = calculate_risk_score(test_response, test_safety, token_count=50)
    print(f"Risk score: {risk}")

