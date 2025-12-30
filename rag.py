"""
RAG Engine using ChromaDB
Handles document ingestion, embedding, and retrieval
"""

import chromadb
from chromadb.utils import embedding_functions
import logging
from typing import List, Dict
import json

logger = logging.getLogger(__name__)


class RAGEngine:
    def __init__(self, collection_name: str = "medical_docs"):
        """Initialize ChromaDB for RAG"""
        self.client = chromadb.Client()
        
        # Use sentence transformers for embeddings
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get collection
        try:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Created new collection: {collection_name}")
        except Exception:
            self.collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Using existing collection: {collection_name}")
    
    def ingest_documents(self, documents: List[Dict]) -> None:
        """
        Ingest documents into ChromaDB
        
        Args:
            documents: List of dicts with 'text' and optional 'metadata'
        """
        texts = []
        metadatas = []
        ids = []
        
        for idx, doc in enumerate(documents):
            texts.append(doc["text"])
            metadatas.append(doc.get("metadata", {}))
            ids.append(f"doc_{idx}")
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Ingested {len(documents)} documents")
    
    def retrieve(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve most relevant documents for a query
        
        Returns:
            List of dicts with 'text', 'metadata', 'distance'
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results
        retrieved = []
        if results['documents'] and len(results['documents']) > 0:
            for idx, doc in enumerate(results['documents'][0]):
                retrieved.append({
                    "text": doc,
                    "metadata": results['metadatas'][0][idx] if results['metadatas'] else {},
                    "distance": results['distances'][0][idx] if results['distances'] else 0.0
                })
        
        logger.info(f"Retrieved {len(retrieved)} documents for query")
        return retrieved
    
    def load_sample_medical_docs(self) -> None:
        """Load sample medical documents for demo"""
        sample_docs = [
            {
                "text": "Common flu symptoms include fever, cough, sore throat, runny or stuffy nose, muscle or body aches, headaches, and fatigue. Most people recover within a few days to less than two weeks.",
                "metadata": {"category": "symptoms", "condition": "flu"}
            },
            {
                "text": "Acetaminophen (Tylenol) is used to treat mild to moderate pain and to reduce fever. The typical adult dose is 325-650 mg every 4-6 hours. Do not exceed 4,000 mg per day.",
                "metadata": {"category": "medication", "drug": "acetaminophen"}
            },
            {
                "text": "For minor cuts and scrapes: wash the wound with soap and water, apply an antibiotic ointment, cover with a bandage. Seek medical attention if the wound is deep, won't stop bleeding, or shows signs of infection.",
                "metadata": {"category": "first_aid", "condition": "cuts"}
            },
            {
                "text": "High blood pressure (hypertension) is often called a 'silent killer' because it typically has no symptoms. Regular monitoring is essential. Normal blood pressure is less than 120/80 mmHg.",
                "metadata": {"category": "conditions", "condition": "hypertension"}
            },
            {
                "text": "Ibuprofen is a nonsteroidal anti-inflammatory drug (NSAID) used for pain, fever, and inflammation. Take with food to reduce stomach upset. Avoid if you have kidney problems or stomach ulcers.",
                "metadata": {"category": "medication", "drug": "ibuprofen"}
            },
            {
                "text": "If someone is choking and cannot breathe, speak, or cough, perform the Heimlich maneuver: stand behind them, make a fist above their navel, and give quick upward thrusts. Call 911 immediately.",
                "metadata": {"category": "emergency", "condition": "choking"}
            },
            {
                "text": "Type 2 diabetes occurs when your body doesn't use insulin properly. Risk factors include being overweight, physically inactive, and having a family history. Management includes diet, exercise, and possibly medication.",
                "metadata": {"category": "conditions", "condition": "diabetes"}
            },
            {
                "text": "Migraine headaches are characterized by intense, throbbing pain, often on one side of the head. They may be accompanied by nausea, vomiting, and sensitivity to light and sound.",
                "metadata": {"category": "symptoms", "condition": "migraine"}
            },
            {
                "text": "CPR (cardiopulmonary resuscitation) steps: Call 911, place hands in center of chest, push hard and fast at 100-120 compressions per minute, allow chest to rise completely between compressions.",
                "metadata": {"category": "emergency", "procedure": "CPR"}
            },
            {
                "text": "Antibiotics treat bacterial infections, NOT viral infections like the common cold or flu. Taking antibiotics when not needed can lead to antibiotic resistance. Always complete the full course prescribed.",
                "metadata": {"category": "medication", "type": "antibiotics"}
            }
        ]
        
        self.ingest_documents(sample_docs)
        logger.info("Loaded sample medical documents")


if __name__ == "__main__":
    # Test the RAG engine
    rag = RAGEngine()
    rag.load_sample_medical_docs()
    
    # Test retrieval
    results = rag.retrieve("What should I do for flu symptoms?")
    print(f"\nRetrieved {len(results)} documents:")
    for doc in results:
        print(f"- {doc['text'][:100]}...")

