from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from datetime import datetime

from database import db_manager
from chatbot import chatbot
from conversation_manager import ConversationManager
from llm_service import LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Customer Support Chatbot",
    description="AI-powered chatbot for e-commerce clothing store customer support",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatResponse(BaseModel):
    response: str
    timestamp: str
    user_id: str

class ProductSearchRequest(BaseModel):
    query: str
    limit: int = 10

class ProductInfo(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    department: str
    retail_price: float
    cost: float

class ConversationRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None

class ConversationResponse(BaseModel):
    response: str
    conversation_id: str
    timestamp: str
    user_id: str
    needs_clarification: bool = False

class ConversationSummary(BaseModel):
    conversation_id: str
    title: str
    user_id: str
    created_at: str
    updated_at: str
    is_active: bool
    message_count: int
    last_message: Optional[str] = None
    last_message_time: Optional[str] = None

class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[Dict[str, Any]]

# Initialize services
conversation_manager = ConversationManager()
llm_service = LLMService()

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "E-commerce Customer Support Chatbot API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "chatbot-api"}

# Chat endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Main chat endpoint that processes user messages"""
    try:
        logger.info(f"Received message from user {chat_message.user_id}: {chat_message.message}")
        
        # Process message through chatbot
        response = chatbot.process_message(chat_message.message)
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        return ChatResponse(
            response=response,
            timestamp=timestamp,
            user_id=chat_message.user_id
        )
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")

# Product endpoints
@app.get("/products", response_model=List[ProductInfo])
async def get_products(limit: int = 100):
    """Get list of products"""
    try:
        products = db_manager.get_products(limit=limit)
        return [ProductInfo(**product) for product in products]
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail="Error fetching products")

@app.get("/products/search")
async def search_products(query: str, limit: int = 20):
    """Search products by name, brand, or category"""
    try:
        products = db_manager.search_products(query, limit=limit)
        return {"products": products, "query": query, "count": len(products)}
    except Exception as e:
        logger.error(f"Error searching products: {e}")
        raise HTTPException(status_code=500, detail="Error searching products")

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """Get detailed product information"""
    try:
        product = db_manager.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Get inventory status
        inventory = db_manager.get_inventory_status(product_id)
        product['inventory'] = inventory
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching product")

@app.get("/products/popular")
async def get_popular_products(limit: int = 10):
    """Get most popular products"""
    try:
        products = db_manager.get_popular_products(limit=limit)
        return {"products": products, "count": len(products)}
    except Exception as e:
        logger.error(f"Error fetching popular products: {e}")
        raise HTTPException(status_code=500, detail="Error fetching popular products")

# Order endpoints
@app.get("/orders/user/{user_id}")
async def get_user_orders(user_id: int):
    """Get orders for a specific user"""
    try:
        orders = db_manager.get_user_orders(user_id)
        return {"orders": orders, "user_id": user_id, "count": len(orders)}
    except Exception as e:
        logger.error(f"Error fetching orders for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching orders")

@app.get("/orders/{order_id}/items")
async def get_order_items(order_id: int):
    """Get items for a specific order"""
    try:
        items = db_manager.get_order_details(order_id)
        return {"items": items, "order_id": order_id, "count": len(items)}
    except Exception as e:
        logger.error(f"Error fetching order items for order {order_id}: {e}")
        raise HTTPException(status_code=500, detail="Error fetching order items")

# Catalog endpoints
@app.get("/categories")
async def get_categories():
    """Get all product categories"""
    try:
        categories = db_manager.get_categories()
        return {"categories": categories, "count": len(categories)}
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Error fetching categories")

@app.get("/brands")
async def get_brands():
    """Get all product brands"""
    try:
        brands = db_manager.get_brands()
        return {"brands": brands, "count": len(brands)}
    except Exception as e:
        logger.error(f"Error fetching brands: {e}")
        raise HTTPException(status_code=500, detail="Error fetching brands")

# Chatbot info endpoint
@app.get("/chatbot/capabilities")
async def get_chatbot_capabilities():
    """Get information about chatbot capabilities"""
    return {
        "capabilities": [
            "Product search and recommendations",
            "Product information and pricing",
            "Order tracking and status",
            "Return and refund policies",
            "Shipping information",
            "General customer support",
            "Conversation history and context",
            "LLM-powered intelligent responses"
        ],
        "supported_intents": list(chatbot.intents.keys()),
        "example_queries": [
            "Hello",
            "Search for jeans",
            "What's the price of product 123?",
            "Track my order #456",
            "What's your return policy?",
            "How long does shipping take?"
        ]
    }

# Enhanced Chat API with conversation history and LLM integration
@app.post("/api/chat", response_model=ConversationResponse)
async def enhanced_chat_endpoint(chat_request: ConversationRequest):
    """Enhanced chat endpoint with conversation history and LLM integration"""
    try:
        logger.info(f"Received message from user {chat_request.user_id}: {chat_request.message}")
        
        # Get or create conversation
        if chat_request.conversation_id:
            conversation = conversation_manager.get_conversation(chat_request.conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conversation = conversation_manager.create_conversation(chat_request.user_id)
        
        # Get conversation history
        conversation_history = conversation_manager.get_conversation_history(conversation.conversation_id)
        
        # Process message through chatbot for intent and entities
        intent = chatbot.classify_intent(chat_request.message)
        entities = chatbot.extract_entities(chat_request.message)
        
        # Generate database context for LLM
        database_context = ""
        if intent == "product_search":
            products = db_manager.search_products(chat_request.message, limit=3)
            if products:
                database_context = f"Found {len(products)} products matching the query"
        elif intent == "inventory":
            inventory = db_manager.get_inventory_status(chat_request.message)
            if inventory:
                database_context = f"Found inventory information for {len(inventory)} products"
        
        # Generate response using LLM
        llm_response, needs_clarification = llm_service.generate_response(
            chat_request.message,
            conversation_history,
            intent,
            entities,
            database_context
        )
        
        # Store user message
        conversation_manager.add_message(
            conversation.conversation_id,
            "user",
            chat_request.message,
            intent,
            None,  # confidence will be calculated by ML model
            entities
        )
        
        # Store assistant response
        conversation_manager.add_message(
            conversation.conversation_id,
            "assistant",
            llm_response,
            intent,
            None,
            entities
        )
        
        timestamp = datetime.now().isoformat()
        
        return ConversationResponse(
            response=llm_response,
            conversation_id=conversation.conversation_id,
            timestamp=timestamp,
            user_id=chat_request.user_id,
            needs_clarification=needs_clarification
        )
        
    except Exception as e:
        logger.error(f"Error processing enhanced chat message: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")

# Conversation management endpoints
@app.get("/api/conversations/{user_id}", response_model=List[ConversationSummary])
async def get_user_conversations(user_id: str, limit: int = 10):
    """Get all conversations for a user"""
    try:
        conversations = conversation_manager.get_user_conversations(user_id, limit)
        summaries = []
        for conv in conversations:
            summary = conversation_manager.get_conversation_summary(conv.conversation_id)
            if summary:
                summaries.append(ConversationSummary(**summary))
        return summaries
    except Exception as e:
        logger.error(f"Error fetching user conversations: {e}")
        raise HTTPException(status_code=500, detail="Error fetching conversations")

@app.get("/api/conversations/{conversation_id}/history", response_model=ConversationHistory)
async def get_conversation_history(conversation_id: str, limit: int = 50):
    """Get conversation history"""
    try:
        messages = conversation_manager.get_conversation_history(conversation_id, limit)
        return ConversationHistory(
            conversation_id=conversation_id,
            messages=messages
        )
    except Exception as e:
        logger.error(f"Error fetching conversation history: {e}")
        raise HTTPException(status_code=500, detail="Error fetching conversation history")

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        success = conversation_manager.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Error deleting conversation")

@app.post("/api/conversations/{conversation_id}/close")
async def close_conversation(conversation_id: str):
    """Close a conversation (mark as inactive)"""
    try:
        success = conversation_manager.close_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return {"message": "Conversation closed successfully"}
    except Exception as e:
        logger.error(f"Error closing conversation: {e}")
        raise HTTPException(status_code=500, detail="Error closing conversation")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 