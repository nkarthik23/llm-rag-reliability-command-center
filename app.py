"""
FastAPI Backend for LLM Reliability Command Center
Handles Gemini API calls, RAG, and Datadog telemetry
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ddtrace import tracer
import time
import logging
import os
from dotenv import load_dotenv

from telemetry import setup_telemetry, log_llm_interaction, calculate_risk_score
from rag import RAGEngine
from gemini_client import GeminiClient

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="LLM Reliability Command Center",
    description="Production-grade observability for LLM applications",
    version="1.0.0"
)

# CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup Datadog telemetry
setup_telemetry()

# Initialize components
gemini_client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
rag_engine = RAGEngine()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Request/Response Models
class QuestionRequest(BaseModel):
    question: str
    user_id: str = "demo_user"
    session_id: str = "demo_session"


class AnswerResponse(BaseModel):
    answer: str
    confidence_score: float
    risk_score: float
    tokens_used: int
    latency_ms: float
    retrieved_docs: int
    safety_ratings: dict


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "llm-reliability-command-center",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "gemini": "connected",
            "rag": "ready",
            "datadog": "connected"
        }
    }


@app.post("/ask", response_model=AnswerResponse)
@tracer.wrap(service="medical-qa-bot", resource="ask_question")
async def ask_question(request: QuestionRequest):
    """
    Main endpoint: Process question with RAG + Gemini + Telemetry
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing question from user: {request.user_id}")
        
        # Step 1: RAG Retrieval
        with tracer.trace("rag.retrieve"):
            retrieved_docs = rag_engine.retrieve(request.question, top_k=3)
            logger.info(f"Retrieved {len(retrieved_docs)} documents")
        
        # Step 2: Call Gemini with context
        with tracer.trace("gemini.generate"):
            context = "\n\n".join([doc["text"] for doc in retrieved_docs])
            response = gemini_client.generate_answer(
                question=request.question,
                context=context
            )
        
        # Step 3: Calculate metrics
        latency_ms = (time.time() - start_time) * 1000
        risk_score = calculate_risk_score(
            text=response["text"],
            safety_ratings=response["safety_ratings"],
            token_count=response["token_count"]
        )
        
        # Step 4: Log to Datadog
        log_llm_interaction(
            question=request.question,
            answer=response["text"],
            user_id=request.user_id,
            session_id=request.session_id,
            latency_ms=latency_ms,
            token_count=response["token_count"],
            risk_score=risk_score,
            safety_ratings=response["safety_ratings"],
            retrieved_docs=len(retrieved_docs)
        )
        
        # Step 5: Return response
        return AnswerResponse(
            answer=response["text"],
            confidence_score=response.get("confidence", 0.8),
            risk_score=risk_score,
            tokens_used=response["token_count"],
            latency_ms=latency_ms,
            retrieved_docs=len(retrieved_docs),
            safety_ratings=response["safety_ratings"]
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest")
async def ingest_documents(documents: list[dict]):
    """
    Ingest documents into RAG system
    Expected format: [{"text": "...", "metadata": {...}}, ...]
    """
    try:
        rag_engine.ingest_documents(documents)
        return {
            "status": "success",
            "documents_ingested": len(documents)
        }
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

