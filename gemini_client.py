"""
Gemini API Client
Handles all interactions with Google's Gemini API
"""

from google import genai
from google.genai import types
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """Initialize Gemini client"""
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        logger.info(f"Initialized Gemini client with model: {model_name}")
    
    def generate_answer(
        self, 
        question: str, 
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> Dict:
        """
        Generate answer using Gemini
        
        Returns:
            Dict with keys: text, token_count, safety_ratings, confidence
        """
        try:
            # Build prompt with context
            if context:
                prompt = f"""You are a helpful medical assistant. Answer the question based on the provided context.
                
Context:
{context}

Question: {question}

Answer: Provide a clear, accurate answer. If you're uncertain or the context doesn't contain enough information, say so explicitly."""
            else:
                prompt = question
            
            # Generate response using new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=500,
                )
            )
            
            # Extract text from response
            response_text = response.text if response.text else ""
            
            # Extract safety ratings (if available)
            safety_ratings = {}
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                    for rating in candidate.safety_ratings:
                        safety_ratings[rating.category.name] = rating.probability.name
            
            # Get token count (estimate)
            token_count = self._estimate_tokens(response_text)
            
            return {
                "text": response_text,
                "token_count": token_count,
                "safety_ratings": safety_ratings,
                "confidence": self._calculate_confidence_from_text(response_text)
            }
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            raise
    
    def _calculate_confidence_from_text(self, text: str) -> float:
        """
        Calculate confidence score based on response characteristics
        Simple heuristic for demo purposes
        """
        text_lower = text.lower()
        
        # Start with baseline
        confidence = 0.8
        
        # Reduce confidence for uncertainty phrases
        uncertainty_phrases = [
            "i'm not sure", "i don't know", "maybe", "possibly",
            "might be", "could be", "uncertain", "unclear"
        ]
        
        for phrase in uncertainty_phrases:
            if phrase in text_lower:
                confidence -= 0.1
        
        # Reduce confidence if response is very short (< 50 chars)
        if len(text_lower) < 50:
            confidence -= 0.1
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation)"""
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4


if __name__ == "__main__":
    # Test the client
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.generate_answer("What is 2+2?")
    print(f"Answer: {response['text']}")
    print(f"Tokens: {response['token_count']}")
    print(f"Confidence: {response['confidence']}")

