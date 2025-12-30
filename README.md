# 🏥 LLM Reliability Command Center

**Production-grade observability for LLM applications powered by Gemini + Datadog**

Built for the Google Cloud AI Partner Catalyst Hackathon - Datadog Challenge

## 🎯 What This Is

A medical Q&A chatbot whose **behavior, safety, cost, and correctness** are continuously monitored in Datadog, with automatic incidents created when the model misbehaves — giving AI engineers real, actionable observability.

**This is not just a chatbot demo. The chatbot is the vehicle. The product is the observability system.**

## ✨ Features

- 🤖 **Gemini-powered Q&A** with RAG (Retrieval Augmented Generation)
- 📊 **Real-time Datadog Monitoring** of all LLM interactions
- ⚠️ **Safety Violation Detection** using Gemini's safety ratings
- 🎯 **Risk Scoring** for potentially problematic responses
- 💰 **Token Usage Tracking** for cost anomaly detection
- 🚨 **Automatic Incident Creation** with full context for debugging
- 📈 **Custom Datadog Dashboard** showing LLM health metrics

## 🏗️ Architecture

```
┌─────────────┐
│  Streamlit  │  ← User Interface
│  (Frontend) │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   FastAPI   │  ← Business Logic + Instrumentation
│  (Backend)  │
└──────┬──────┘
       │
   ┌───┴────┬──────────────┬──────────────┐
   ▼        ▼              ▼              ▼
┌─────┐ ┌─────┐     ┌──────────┐    ┌─────────┐
│Gemini│ │Chroma│    │ Datadog  │    │ Monitors│
│ API │ │  DB  │    │ APM/Logs │    │ Incidents│
└─────┘ └─────┘     └──────────┘    └─────────┘
```

## 📋 Prerequisites

1. **Python 3.10+**
2. **Google AI Studio API Key**: Get from https://aistudio.google.com/app/apikey
3. **Datadog Account**: Sign up at https://www.datadoghq.com/ (free trial available)
   - API Key
   - Application Key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd llm-rag-reliability-command-center

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys:
# - GEMINI_API_KEY
# - DD_API_KEY
# - DD_APP_KEY
```

### 3. Initialize RAG Knowledge Base

```python
# Run this once to load sample medical documents
python -c "from rag import RAGEngine; rag = RAGEngine(); rag.load_sample_medical_docs()"
```

### 4. Start the Backend

```bash
# Terminal 1: Start FastAPI backend
python app.py

# Backend will run on http://localhost:8000
```

### 5. Start the Frontend

```bash
# Terminal 2: Start Streamlit frontend
streamlit run frontend.py

# Frontend will open in your browser at http://localhost:8501
```

### 6. Create Datadog Monitors (Optional)

```bash
# Create monitors programmatically
python monitors.py
```

Alternatively, create monitors manually in Datadog UI using the configurations in `monitors.py`.

## 🎬 Demo Scenarios

Run automated demo scenarios to trigger monitors:

```bash
python demo_scenarios.py
```

This will run through various scenarios:
- ✅ Normal question (no alerts)
- ⚠️ Safety violation
- 🚨 High-risk medical advice
- 💰 Token usage spike
- 🤔 Potential hallucination
- 📈 High request rate

## 📊 Datadog Dashboard

### Key Metrics Monitored:

1. **Request Rate**: `llm.requests.total`
2. **Response Latency**: `llm.latency`
3. **Token Usage**: `llm.tokens`
4. **Risk Scores**: `llm.risk_score`
5. **Safety Violations**: `llm.safety_violation`

### Monitors Created:

1. **High Latency**: Alerts when responses take >5 seconds
2. **Safety Violations**: Triggers on any safety rating flags
3. **High Risk Score**: Alerts when risk score >0.7
4. **Token Anomaly**: Detects unusual token usage (cost impact)
5. **High Request Rate**: Monitors for traffic spikes

## 🧪 Testing

### Test Individual Components:

```bash
# Test Gemini client
python gemini_client.py

# Test RAG engine
python rag.py

# Test telemetry
python telemetry.py
```

### Test Full Flow:

1. Open frontend: http://localhost:8501
2. Ask: "What are the symptoms of flu?" (should be safe)
3. Ask: "How do I perform surgery at home?" (should trigger safety alert)
4. Check Datadog dashboard for metrics and alerts

## 📁 Project Structure

```
llm-rag-reliability-command-center/
├── app.py                 # FastAPI backend
├── frontend.py            # Streamlit UI
├── gemini_client.py       # Gemini API wrapper
├── rag.py                 # RAG with ChromaDB
├── telemetry.py          # Datadog instrumentation
├── monitors.py           # Datadog monitor definitions
├── demo_scenarios.py     # Demo scripts for presentation
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md            # This file
```

## 🎯 Risk Scoring Logic

Risk score (0.0 to 1.0) is calculated based on:

- **Safety Ratings**: HIGH = +0.4, MEDIUM = +0.2
- **Token Count**: >1000 tokens = +0.3, >500 = +0.15
- **Uncertainty Phrases**: "maybe", "not sure", etc. = +0.05 each
- **Medical Advice Without Disclaimer**: +0.2

Risk > 0.7 = HIGH (alert triggered)
Risk 0.4-0.7 = MEDIUM (monitor closely)
Risk < 0.4 = LOW (safe)

## 🚨 Incident Response

When a monitor triggers, Datadog incidents include:

- **Full prompt and response**
- **Risk score and safety ratings**
- **Token count and latency**
- **Retrieved documents context**
- **Suggested remediation steps**

AI engineers can immediately:
1. See exactly what went wrong
2. Understand the context
3. Take corrective action
4. Track resolution

## 🎤 Presentation Flow (5 min)

1. **Problem** (30s): "LLMs in production fail silently"
2. **Solution** (30s): "Real-time observability for safety, cost, correctness"
3. **Live Demo** (3min):
   - Show dashboard (healthy state)
   - Ask normal question → works fine
   - Ask unsafe question → alert fires live
   - Show incident with full context
4. **Tech** (30s): "Gemini + Datadog + RAG + FastAPI"
5. **Impact** (30s): "Production-ready LLM observability"

## 🔧 Troubleshooting

### Backend won't start
- Check API keys in `.env`
- Ensure port 8000 is free
- Verify `pip install -r requirements.txt` completed

### Frontend can't connect
- Ensure backend is running on port 8000
- Check `BACKEND_URL` in `.env`

### No metrics in Datadog
- Verify Datadog API keys are correct
- Check `DD_SITE` matches your region
- Run `python telemetry.py` to test connection

### Monitors not triggering
- Ensure monitors were created (run `monitors.py`)
- Check monitor thresholds in Datadog UI
- Verify metrics are flowing (check Datadog Metrics Explorer)

## 📚 Resources

- [Gemini API Docs](https://ai.google.dev/docs)
- [Datadog APM Python](https://docs.datadoghq.com/tracing/setup_overview/setup/python/)
- [ChromaDB Docs](https://docs.trychroma.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

## 🏆 Hackathon Submission

This project demonstrates:
- ✅ Integration of Google Cloud (Gemini) + Partner (Datadog)
- ✅ End-to-end observability monitoring strategy
- ✅ LLM and runtime telemetry streaming
- ✅ Detection rules with actionable incidents
- ✅ Clear dashboard showing application health
- ✅ Production-grade approach to LLM reliability

## 📝 License

MIT License - Built for educational and hackathon purposes

## 👤 Author

Built for Google Cloud AI Partner Catalyst Hackathon 2024

---

**🎯 Ready to win? Run the demo and show off real LLM observability!**
