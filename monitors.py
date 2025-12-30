"""
Datadog Monitor Definitions
Programmatically create and manage Datadog monitors
"""

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor
from datadog_api_client.v1.model.monitor_type import MonitorType
import os
from dotenv import load_dotenv

load_dotenv()


def create_monitors():
    """Create all Datadog monitors for LLM observability"""
    
    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
    configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
    
    with ApiClient(configuration) as api_client:
        api_instance = MonitorsApi(api_client)
        
        monitors = [
            # Monitor 1: High Latency
            {
                "name": "[LLM] High Response Latency",
                "type": MonitorType.METRIC_ALERT,
                "query": "avg(last_5m):avg:llm.latency{service:medical-qa} > 5000",
                "message": """
🐌 **High LLM Response Latency Detected**

The average response time has exceeded 5 seconds.

**Potential Causes:**
- High load on Gemini API
- Network issues
- Complex RAG retrieval
- Large context windows

**Action Items:**
- Check Gemini API status
- Review recent prompt complexity
- Analyze RAG retrieval performance
- Consider caching frequently asked questions

@incident-llm-engineering
                """,
                "tags": ["service:medical-qa", "team:ai", "severity:medium"],
                "priority": 3,
            },
            
            # Monitor 2: Safety Violations
            {
                "name": "[LLM] Safety Violation Detected",
                "type": MonitorType.METRIC_ALERT,
                "query": "sum(last_5m):sum:llm.safety_violation{*}.as_count() > 0",
                "message": """
⚠️ **LLM Safety Violation Detected**

Gemini has flagged a response with safety concerns.

**Categories Monitored:**
- Hate speech
- Harassment
- Dangerous content
- Sexually explicit content

**Immediate Actions:**
- Review the flagged prompt and response in Datadog logs
- Assess if additional content filtering is needed
- Consider updating system prompts with stronger safety guidelines
- Check for potential prompt injection attempts

**Context:** Check `llm.safety_violation` metric for category details.

@incident-llm-safety @incident-llm-engineering
                """,
                "tags": ["service:medical-qa", "team:ai", "severity:high"],
                "priority": 1,
            },
            
            # Monitor 3: High Risk Score
            {
                "name": "[LLM] High Risk Score Detected",
                "type": MonitorType.METRIC_ALERT,
                "query": "avg(last_5m):avg:llm.risk_score{service:medical-qa} > 0.7",
                "message": """
🚨 **High Risk LLM Response Detected**

The calculated risk score has exceeded the threshold of 0.7.

**Risk Factors:**
- Safety violations
- Uncertainty in response
- Medical advice without disclaimers
- Unusually high token count (potential hallucination)

**Recommended Actions:**
1. Review the interaction in Datadog logs (search for `event_type:llm_interaction`)
2. Check if the response contains inappropriate medical advice
3. Verify RAG retrieval quality - were relevant docs retrieved?
4. Consider adding response post-processing filters
5. Update knowledge base if gaps identified

**Dashboard:** [LLM Reliability Command Center](https://app.datadoghq.com)

@incident-llm-engineering
                """,
                "tags": ["service:medical-qa", "team:ai", "severity:high"],
                "priority": 2,
            },
            
            # Monitor 4: Token Usage Spike (Cost Anomaly)
            {
                "name": "[LLM] Unusual Token Usage - Cost Anomaly",
                "type": MonitorType.METRIC_ALERT,
                "query": "avg(last_15m):avg:llm.tokens{service:medical-qa} > 800",
                "message": """
💰 **Unusual Token Usage Detected**

Average token count per request has exceeded 800 tokens.

**Potential Issues:**
- Prompt injection attack (user forcing long responses)
- Context window bloat from RAG
- Model generating verbose/hallucinated content
- Cost anomaly that could impact budget

**Investigation Steps:**
1. Check recent prompts for unusual patterns
2. Review RAG retrieval - are we passing too much context?
3. Analyze response quality - is the model hallucinating?
4. Check for potential abuse or automated requests
5. Consider implementing response length limits

**Cost Impact:** At $0.002/1K tokens, sustained high usage could increase costs significantly.

@incident-llm-engineering @finance
                """,
                "tags": ["service:medical-qa", "team:ai", "severity:medium", "cost:alert"],
                "priority": 3,
            },
            
            # Monitor 5: High Request Rate
            {
                "name": "[LLM] High Request Rate",
                "type": MonitorType.METRIC_ALERT,
                "query": "sum(last_5m):sum:llm.requests.total{service:medical-qa}.as_rate() > 10",
                "message": """
📈 **High LLM Request Rate Detected**

Request rate has exceeded 10 requests per second.

**Possible Causes:**
- Traffic spike (legitimate or DDoS)
- Automated bot activity
- Load testing without proper tagging

**Actions:**
- Verify traffic source in Datadog APM
- Check for rate limiting implementation
- Review authentication logs
- Consider enabling request throttling

@incident-llm-engineering @platform
                """,
                "tags": ["service:medical-qa", "team:platform", "severity:low"],
                "priority": 4,
            },
        ]
        
        created_monitors = []
        for monitor_config in monitors:
            try:
                monitor = Monitor(
                    name=monitor_config["name"],
                    type=monitor_config["type"],
                    query=monitor_config["query"],
                    message=monitor_config["message"],
                    tags=monitor_config["tags"],
                    priority=monitor_config.get("priority", 3),
                )
                
                response = api_instance.create_monitor(body=monitor)
                created_monitors.append(response)
                print(f"✅ Created monitor: {monitor_config['name']}")
                
            except Exception as e:
                print(f"❌ Error creating monitor {monitor_config['name']}: {str(e)}")
        
        return created_monitors


def list_monitors():
    """List all existing monitors"""
    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
    configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
    
    with ApiClient(configuration) as api_client:
        api_instance = MonitorsApi(api_client)
        
        try:
            monitors = api_instance.list_monitors(tags="service:medical-qa")
            print(f"\nFound {len(monitors)} monitors:")
            for monitor in monitors:
                print(f"- {monitor.name} (ID: {monitor.id})")
            return monitors
        except Exception as e:
            print(f"Error listing monitors: {str(e)}")
            return []


if __name__ == "__main__":
    print("Creating Datadog monitors for LLM Reliability Command Center...\n")
    created = create_monitors()
    print(f"\n✅ Successfully created {len(created)} monitors!")
    print("\n📊 Listing all monitors:")
    list_monitors()

