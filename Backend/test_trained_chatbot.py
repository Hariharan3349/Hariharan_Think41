#!/usr/bin/env python3
"""
Test Trained Chatbot Script
Demonstrates the ML-powered chatbot capabilities
"""

import requests
import json
import time
from typing import List, Dict

class TrainedChatbotTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
    
    def test_query(self, message: str, expected_intent: str = None, user_id: str = "test_user") -> Dict:
        """Test a single query and return results"""
        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json={"message": message, "user_id": user_id},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "message": message,
                    "response": result["response"],
                    "status": "success",
                    "expected_intent": expected_intent
                }
            else:
                return {
                    "message": message,
                    "response": f"Error: {response.status_code}",
                    "status": "error",
                    "expected_intent": expected_intent
                }
                
        except Exception as e:
            return {
                "message": message,
                "response": f"Exception: {str(e)}",
                "status": "error",
                "expected_intent": expected_intent
            }
    
    def run_comprehensive_tests(self):
        """Run comprehensive tests on the trained chatbot"""
        print("🤖 TRAINED CHATBOT COMPREHENSIVE TEST")
        print("=" * 60)
        
        # Test cases with expected intents
        test_cases = [
            # Greeting tests
            ("hello", "greeting"),
            ("hi there", "greeting"),
            ("good morning", "greeting"),
            
            # Product search tests
            ("tshirts", "product_search"),
            ("dresses", "product_search"),
            ("shoes", "product_search"),
            ("jeans", "product_search"),
            ("search for hoodies", "product_search"),
            ("find me some pants", "product_search"),
            ("show me jackets", "product_search"),
            
            # Inventory tests
            ("how many classic Tshirts are left in stock", "inventory"),
            ("check stock for dresses", "inventory"),
            ("available quantity of jeans", "inventory"),
            ("stock status for shoes", "inventory"),
            ("how much inventory do you have", "inventory"),
            
            # Order tracking tests
            ("track my order #123", "order_status"),
            ("where is my order", "order_status"),
            ("order status for #456", "order_status"),
            ("tracking information", "order_status"),
            
            # Policy tests
            ("what's your return policy", "return_policy"),
            ("return information", "return_policy"),
            ("refund policy", "return_policy"),
            
            # Shipping tests
            ("how long does shipping take", "shipping"),
            ("shipping information", "shipping"),
            ("delivery time", "shipping"),
            
            # Help tests
            ("help me", "help"),
            ("I need assistance", "help"),
            ("what can you do", "help"),
            
            # Goodbye tests
            ("thank you", "goodbye"),
            ("bye", "goodbye"),
            ("goodbye", "goodbye"),
            
            # Complex queries
            ("I'm looking for a red dress for a party", "product_search"),
            ("Can you tell me about the shipping costs for orders over $50", "shipping"),
            ("What's the return window for electronics", "return_policy"),
            ("Do you have any summer dresses in stock", "inventory"),
        ]
        
        print(f"🧪 Running {len(test_cases)} test cases...")
        print("-" * 60)
        
        successful_tests = 0
        total_tests = len(test_cases)
        
        for i, (message, expected_intent) in enumerate(test_cases, 1):
            print(f"Test {i:2d}/{total_tests}: {message}")
            
            result = self.test_query(message, expected_intent)
            self.test_results.append(result)
            
            if result["status"] == "success":
                print(f"   ✅ Success")
                successful_tests += 1
            else:
                print(f"   ❌ Failed: {result['response']}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        print(f"📈 Success rate: {(successful_tests/total_tests)*100:.1f}%")
        
        # Show some example responses
        print("\n🎯 EXAMPLE RESPONSES:")
        print("-" * 60)
        
        example_categories = ["greeting", "product_search", "inventory", "order_status"]
        for category in example_categories:
            for result in self.test_results:
                if result["expected_intent"] == category and result["status"] == "success":
                    print(f"\n{category.upper()}:")
                    print(f"Q: {result['message']}")
                    response_preview = result['response'][:100] + "..." if len(result['response']) > 100 else result['response']
                    print(f"A: {response_preview}")
                    break
        
        return self.test_results
    
    def test_ml_accuracy(self):
        """Test ML model accuracy with specific examples"""
        print("\n🤖 ML MODEL ACCURACY TEST")
        print("=" * 60)
        
        # Test cases that should be correctly classified by ML
        ml_test_cases = [
            ("hello there", "greeting"),
            ("search for jeans", "product_search"),
            ("how many tshirts are in stock", "inventory"),
            ("track my order #123", "order_status"),
            ("what's your return policy", "return_policy"),
            ("how long does shipping take", "shipping"),
            ("help me", "help"),
            ("thank you", "goodbye"),
        ]
        
        correct_classifications = 0
        total_ml_tests = len(ml_test_cases)
        
        for message, expected_intent in ml_test_cases:
            result = self.test_query(message, expected_intent)
            
            # Check if the response indicates correct intent classification
            response_lower = result["response"].lower()
            
            # Simple heuristics to check if intent was correctly classified
            intent_correct = False
            if expected_intent == "greeting" and any(word in response_lower for word in ["hello", "hi", "welcome"]):
                intent_correct = True
            elif expected_intent == "product_search" and any(word in response_lower for word in ["products", "matching", "found"]):
                intent_correct = True
            elif expected_intent == "inventory" and any(word in response_lower for word in ["stock", "available", "items"]):
                intent_correct = True
            elif expected_intent == "order_status" and any(word in response_lower for word in ["order", "track", "status"]):
                intent_correct = True
            elif expected_intent == "return_policy" and any(word in response_lower for word in ["return", "policy", "refund"]):
                intent_correct = True
            elif expected_intent == "shipping" and any(word in response_lower for word in ["shipping", "delivery", "time"]):
                intent_correct = True
            elif expected_intent == "help" and any(word in response_lower for word in ["help", "assist", "can help"]):
                intent_correct = True
            elif expected_intent == "goodbye" and any(word in response_lower for word in ["thank", "goodbye", "bye"]):
                intent_correct = True
            
            if intent_correct:
                correct_classifications += 1
                print(f"✅ {message} → {expected_intent}")
            else:
                print(f"❌ {message} → Expected: {expected_intent}")
        
        ml_accuracy = (correct_classifications / total_ml_tests) * 100
        print(f"\n🎯 ML Classification Accuracy: {ml_accuracy:.1f}%")
        
        return ml_accuracy

def main():
    tester = TrainedChatbotTester()
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server is not responding properly")
            return
    except:
        print("❌ Backend server is not running. Please start it first.")
        return
    
    print("✅ Backend server is running. Starting tests...")
    
    # Run comprehensive tests
    results = tester.run_comprehensive_tests()
    
    # Test ML accuracy
    ml_accuracy = tester.test_ml_accuracy()
    
    # Save results
    with open('trained_chatbot_test_results.json', 'w') as f:
        json.dump({
            'test_results': results,
            'ml_accuracy': ml_accuracy,
            'timestamp': time.time()
        }, f, indent=2)
    
    print(f"\n📄 Test results saved to: trained_chatbot_test_results.json")
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    main() 