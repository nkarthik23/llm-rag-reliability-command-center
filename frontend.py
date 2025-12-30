"""
Streamlit Frontend for LLM Reliability Command Center
User interface for asking questions and viewing metrics
"""

import streamlit as st
import httpx
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Page config
st.set_page_config(
    page_title="LLM Reliability Command Center",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS with Inter font
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global font */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Main header */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .metric-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Risk indicators */
    .high-risk {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 1rem;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.2);
        border: none;
    }
    
    .medium-risk {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 1rem;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(245, 158, 11, 0.2);
        border: none;
    }
    
    .low-risk {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 1rem;
        font-weight: 600;
        box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);
        border: none;
    }
    
    /* Button styling */
    .stButton>button {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-radius: 0.75rem;
        padding: 0.75rem 2rem;
        transition: all 0.2s;
        border: none;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Text input */
    .stTextArea textarea {
        font-family: 'Inter', sans-serif;
        border-radius: 0.75rem;
        border: 2px solid #e5e7eb;
        padding: 1rem;
        font-size: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 1.8rem;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #6b7280;
    }
    
    /* Info/success/warning boxes */
    .stAlert {
        border-radius: 0.75rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f9fafb 0%, #f3f4f6 100%);
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #1f2937 !important;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] .stMarkdown {
        color: #374151 !important;
    }
    
    [data-testid="stSidebar"] code {
        background-color: #e5e7eb !important;
        color: #1f2937 !important;
    }
    
    [data-testid="stSidebar"] .element-container {
        color: #374151 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        border-radius: 0.5rem;
    }
    
    /* Code blocks */
    code {
        font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
        background-color: #f3f4f6;
        padding: 0.2rem 0.4rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e5e7eb;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏥 Medical Q&A Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">🔍 LLM Reliability Command Center · Powered by Gemini + Datadog</div>', unsafe_allow_html=True)

# Sidebar - Info
with st.sidebar:
    st.markdown("### ℹ️ About")
    st.markdown("""
    This application demonstrates **production-grade observability** for LLM applications.
    """)
    
    st.markdown("### ✨ Features")
    st.markdown("""
    - 🤖 Gemini 2.5 Flash
    - 📚 RAG with 10 medical docs
    - 📊 Real-time monitoring
    - ⚠️ Safety detection
    - 🎯 Risk scoring
    - 💰 Cost tracking
    """)
    
    st.markdown("### 📊 Datadog Metrics")
    st.markdown("""
    - Response latency
    - Token usage
    - Safety violations
    - Risk scores
    - Request rate
    """)
    
    st.markdown("### ⚠️ Demo Triggers")
    st.markdown("**Try these to see alerts:**")
    st.code("How do I perform surgery at home?", language=None)
    st.code("What's the lethal dose of aspirin?", language=None)
    
    st.markdown("---")
    st.caption("Built for Google Cloud AI Hackathon")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = f"user_{int(time.time())}"
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"

# Main chat interface
st.markdown("### 💬 Ask a Medical Question")

# Chat input
question = st.text_area(
    "Your question:",
    height=100,
    placeholder="e.g., What are the symptoms of flu? How do I treat a minor cut?"
)

col1, col2 = st.columns([1, 5])
with col1:
    ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
with col2:
    clear_button = st.button("🗑️ Clear History", use_container_width=True)

if clear_button:
    st.session_state.chat_history = []
    st.rerun()

# Handle question
if ask_button and question:
    with st.spinner("🤔 Thinking... (monitoring in Datadog)"):
        try:
            # Call backend API
            response = httpx.post(
                f"{BACKEND_URL}/ask",
                json={
                    "question": question,
                    "user_id": st.session_state.user_id,
                    "session_id": st.session_state.session_id
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "question": question,
                    "answer": data["answer"],
                    "metrics": {
                        "risk_score": data["risk_score"],
                        "confidence": data["confidence_score"],
                        "latency_ms": data["latency_ms"],
                        "tokens": data["tokens_used"],
                        "retrieved_docs": data["retrieved_docs"],
                        "safety_ratings": data["safety_ratings"]
                    }
                })
                
                st.rerun()
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
                
        except httpx.ConnectError:
            st.error("⚠️ Cannot connect to backend. Make sure the FastAPI server is running on port 8000.")
            st.code("python app.py", language="bash")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display chat history
if st.session_state.chat_history:
    st.markdown("---")
    st.markdown("### 📝 Conversation History")
    
    for idx, chat in enumerate(reversed(st.session_state.chat_history)):
        with st.container():
            # Question
            st.markdown(f"##### 🙋 Question {len(st.session_state.chat_history) - idx}")
            st.info(chat["question"])
            
            # Answer
            st.markdown("##### 🤖 Answer")
            st.success(chat["answer"])
            
            # Metrics
            metrics = chat["metrics"]
            risk_score = metrics["risk_score"]
            
            # Risk indicator
            if risk_score > 0.7:
                st.markdown('<div class="high-risk">⚠️ HIGH RISK - Alert sent to Datadog</div>', unsafe_allow_html=True)
            elif risk_score > 0.4:
                st.markdown('<div class="medium-risk">⚡ MEDIUM RISK - Monitoring closely</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="low-risk">✅ LOW RISK - Safe response</div>', unsafe_allow_html=True)
            
            # Detailed metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Risk Score", f"{risk_score:.2f}")
            with col2:
                st.metric("Confidence", f"{metrics['confidence']:.2f}")
            with col3:
                st.metric("Latency", f"{metrics['latency_ms']:.0f}ms")
            with col4:
                st.metric("Tokens", metrics['tokens'])
            with col5:
                st.metric("Docs Retrieved", metrics['retrieved_docs'])
            
            # Safety ratings
            if metrics['safety_ratings']:
                with st.expander("🔒 Safety Ratings"):
                    for category, rating in metrics['safety_ratings'].items():
                        st.write(f"- **{category}**: {rating}")
            
            st.markdown("---")

else:
    st.markdown("""
        <div style='text-align: center; padding: 3rem; color: #9ca3af;'>
            <h3 style='color: #6b7280;'>👋 Welcome!</h3>
            <p>Ask a medical question above to get started.</p>
            <p style='font-size: 0.9rem;'>Your interaction will be monitored for safety and reliability.</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #9ca3af; font-size: 0.9rem;'>
        🔍 All interactions monitored in Datadog · 🚨 Automated incident creation · 📊 Real-time observability
    </div>
""", unsafe_allow_html=True)

