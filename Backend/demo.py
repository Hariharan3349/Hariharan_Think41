#!/usr/bin/env python3
"""
E-Commerce Customer Support Chatbot Demo
This script demonstrates the chatbot functionality with example interactions.
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def send_chat_message(message: str, user_id: str = "demo_user") -> Dict[str, Any]:
    """Send a chat message and return the response"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message, "user_id": user_id},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Request failed: {response.status_code}"}
    except Exception as e:
        return {"error": f"Request error: {e}"}

def demo_chat_interactions():
    """Demonstrate various chat interactions"""
    print("\n🤖 Chatbot Demo - Example Interactions")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "category": "Greeting",
            "message": "Hello",
            "description": "Basic greeting interaction"
        },
        {
            "category": "Product Search",
            "message": "Tshirts",
            "description": "Simple product search (single word)"
        },
        {
            "category": "Product Search",
            "message": "Dresses",
            "description": "Product category search"
        },
        {
            "category": "Product Search",
            "message": "Shoes",
            "description": "Footwear search"
        },
        {
            "category": "Product Search",
            "message": "Search for jeans",
            "description": "Explicit product search"
        },
        {
            "category": "Product Search",
            "message": "Find Nike shoes",
            "description": "Brand-specific product search"
        },
        {
            "category": "Product Information",
            "message": "Tell me about product 123",
            "description": "Product information request"
        },
        {
            "category": "Order Tracking",
            "message": "Track my order #456",
            "description": "Order tracking request"
        },
        {
            "category": "Return Policy",
            "message": "What's your return policy?",
            "description": "Return policy inquiry"
        },
        {
            "category": "Shipping",
            "message": "How long does shipping take?",
            "description": "Shipping information request"
        },
        {
            "category": "Inventory",
            "message": "how many classic Tshirts are left in stock",
            "description": "Inventory stock inquiry"
        },
        {
            "category": "Inventory",
            "message": "check stock for dresses",
            "description": "Stock check for specific category"
        },
        {
            "category": "Inventory",
            "message": "available quantity of jeans",
            "description": "Available quantity inquiry"
        },
        {
            "category": "Help",
            "message": "Help",
            "description": "Help request"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['category']}: {test_case['description']}")
        print(f"   User: {test_case['message']}")
        
        response = send_chat_message(test_case['message'])
        
        if "error" in response:
            print(f"   ❌ Error: {response['error']}")
        else:
            print(f"   Bot: {response['response'][:100]}{'...' if len(response['response']) > 100 else ''}")
        
        time.sleep(1)  # Small delay between requests

def test_api_endpoints():
    """Test various API endpoints"""
    print("\n🔧 API Endpoints Testing")
    print("=" * 30)
    
    endpoints = [
        ("/products?limit=5", "Get products"),
        ("/products/search?query=shirt&limit=3", "Search products"),
        ("/categories", "Get categories"),
        ("/brands", "Get brands"),
        ("/products/popular?limit=5", "Get popular products"),
        ("/chatbot/capabilities", "Get chatbot capabilities")
    ]
    
    for endpoint, description in endpoints:
        print(f"\n📡 Testing: {description}")
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   ✅ Success: {len(data)} items returned")
                elif isinstance(data, dict):
                    if 'count' in data:
                        print(f"   ✅ Success: {data['count']} items returned")
                    else:
                        print(f"   ✅ Success: {len(data)} fields returned")
                else:
                    print(f"   ✅ Success: Response received")
            else:
                print(f"   ❌ Failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main demo function"""
    print("🛍️ E-Commerce Customer Support Chatbot Demo")
    print("=" * 50)
    
    # Check if backend is running
    if not test_health_check():
        print("\n❌ Backend is not running. Please start the backend first:")
        print("   python backend/main.py")
        return
    
    # Run API endpoint tests
    test_api_endpoints()
    
    # Run chat interaction demo
    demo_chat_interactions()
    
    print("\n🎉 Demo completed!")
    print("\n💡 To use the full chat interface, visit:")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 