import os
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, api_key: str = None, base_url: str = "https://api.groq.com/openai/v1"):
        """Initialize the LLM service with Groq API"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url
        self.model = "llama3-8b-8192"  # Fast and cost-effective model
        
        if not self.api_key:
            logger.warning("No Groq API key provided. LLM features will be disabled.")
    
    def _make_request(self, messages: List[Dict], temperature: float = 0.7) -> Optional[str]:
        """Make a request to the Groq API"""
        if not self.api_key:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling Groq API: {e}")
            return None
    
    def generate_response(self, user_message: str, conversation_history: List[Dict], 
                         intent: str, entities: Dict, database_context: str = "") -> Tuple[str, bool]:
        """
        Generate an intelligent response using the LLM
        
        Returns:
            Tuple of (response_text, needs_clarification)
        """
        if not self.api_key:
            return self._fallback_response(user_message, intent, entities), False
        
        # Build system prompt
        system_prompt = self._build_system_prompt(intent, entities, database_context)
        
        # Build conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 5 messages for context)
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response
        response = self._make_request(messages, temperature=0.7)
        
        if response:
            # Check if response indicates need for clarification
            needs_clarification = self._check_for_clarification(response)
            return response, needs_clarification
        else:
            return self._fallback_response(user_message, intent, entities), False
    
    def _build_system_prompt(self, intent: str, entities: Dict, database_context: str) -> str:
        """Build a system prompt for the LLM"""
        prompt = f"""You are an intelligent e-commerce customer support assistant. You help customers with product searches, order tracking, inventory queries, and general support.

Current Context:
- Detected Intent: {intent}
- Extracted Entities: {json.dumps(entities) if entities else 'None'}
- Database Context: {database_context}

Your capabilities:
1. Product Search: Help customers find products by category, brand, or description
2. Inventory Queries: Provide stock information and availability
3. Order Tracking: Help track orders and provide status updates
4. Return Policy: Explain return and refund policies
5. Shipping Information: Provide delivery and shipping details
6. General Support: Answer customer service questions

Guidelines:
- Be helpful, friendly, and professional
- If you need more information to help the customer, ask clarifying questions
- Provide specific, actionable information when possible
- If you don't have enough information, ask for clarification
- Keep responses concise but informative
- Always maintain a helpful and positive tone

If you need to ask clarifying questions, start your response with "I'd be happy to help! To provide you with the best assistance, I need a bit more information:" followed by your specific questions."""
        
        return prompt
    
    def _check_for_clarification(self, response: str) -> bool:
        """Check if the response indicates a need for clarification"""
        clarification_indicators = [
            "I need a bit more information",
            "To provide you with the best assistance",
            "Could you please clarify",
            "Can you provide more details",
            "I need to know",
            "To help you better",
            "Could you specify",
            "What exactly are you looking for"
        ]
        
        response_lower = response.lower()
        return any(indicator.lower() in response_lower for indicator in clarification_indicators)
    
    def _fallback_response(self, user_message: str, intent: str, entities: Dict) -> str:
        """Generate a fallback response when LLM is not available"""
        if intent == "greeting":
            return "Hello! I'm here to help you with your shopping needs. What can I assist you with today?"
        elif intent == "product_search":
            return "I'd be happy to help you find products! Could you please provide more details about what you're looking for?"
        elif intent == "inventory":
            return "I can help you check product availability. Could you specify which product or category you're interested in?"
        elif intent == "order_status":
            return "I can help you track your order. Do you have an order number I can look up for you?"
        elif intent == "return_policy":
            return "I'd be happy to explain our return policy. What specific information would you like to know?"
        elif intent == "shipping":
            return "I can provide shipping information. What would you like to know about delivery options or timing?"
        elif intent == "help":
            return "I'm here to help! I can assist with product searches, order tracking, inventory checks, return policies, and shipping information. What do you need help with?"
        elif intent == "goodbye":
            return "Thank you for chatting with us! Have a great day and feel free to return if you need anything else."
        else:
            return "I'm here to help! Could you please provide more details about what you're looking for?"
    
    def generate_clarifying_questions(self, intent: str, entities: Dict) -> List[str]:
        """Generate specific clarifying questions based on intent and entities"""
        questions = []
        
        if intent == "product_search":
            if not entities.get("product_type"):
                questions.append("What type of product are you looking for? (e.g., t-shirts, dresses, shoes)")
            if not entities.get("brand"):
                questions.append("Do you have a specific brand in mind?")
            if not entities.get("price_range"):
                questions.append("What's your budget range?")
        
        elif intent == "inventory":
            if not entities.get("product_type"):
                questions.append("Which product or category would you like to check stock for?")
            if not entities.get("product_id"):
                questions.append("Do you have a specific product ID or name?")
        
        elif intent == "order_status":
            if not entities.get("order_id"):
                questions.append("Could you provide your order number?")
            if not entities.get("user_id"):
                questions.append("Could you provide your user ID for verification?")
        
        elif intent == "return_policy":
            questions.append("Are you looking for information about returns, exchanges, or refunds?")
            questions.append("What type of product are you planning to return?")
        
        elif intent == "shipping":
            questions.append("Are you asking about shipping costs, delivery times, or tracking information?")
            questions.append("What's your shipping destination?")
        
        return questions
    
    def enhance_response_with_context(self, base_response: str, conversation_history: List[Dict], 
                                    intent: str, entities: Dict) -> str:
        """Enhance a response with conversation context and personalization"""
        if not conversation_history:
            return base_response
        
        # Check if this is a follow-up question
        if len(conversation_history) > 1:
            last_user_message = None
            for msg in reversed(conversation_history[:-1]):
                if msg["role"] == "user":
                    last_user_message = msg["content"]
                    break
            
            if last_user_message:
                # Add context about previous interaction
                if intent == "product_search" and "product" in last_user_message.lower():
                    base_response += f"\n\nBased on our previous conversation about products, I can also help you with similar items or alternatives if needed."
                elif intent == "inventory" and "stock" in last_user_message.lower():
                    base_response += f"\n\nI can also help you check stock for other products or categories if you're interested."
        
        return base_response 