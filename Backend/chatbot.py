import re
import random
import pickle
import os
from typing import Dict, List, Any, Tuple
from database import db_manager

class EcommerceChatbot:
    def __init__(self, use_ml_model=True):
        self.use_ml_model = use_ml_model
        self.ml_models_loaded = False
        
        # Fallback intents for when ML model is not available
        self.intents = {
            'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'goodbye': ['bye', 'goodbye', 'see you', 'thank you', 'thanks'],
            'product_search': ['search', 'find', 'look for', 'show me', 'product', 'item'],
            'product_info': ['details', 'information', 'tell me about', 'what is', 'price', 'cost'],
            'inventory': ['stock', 'in stock', 'available', 'how many', 'left', 'quantity', 'inventory'],
            'order_status': ['order', 'track', 'status', 'where is', 'shipped', 'delivered'],
            'return_policy': ['return', 'refund', 'exchange', 'policy', 'money back'],
            'shipping': ['shipping', 'delivery', 'how long', 'when', 'tracking'],
            'help': ['help', 'support', 'assist', 'problem', 'issue']
        }
        
        # Load ML models if available
        if self.use_ml_model:
            self._load_ml_models()
        
        self.responses = {
            'greeting': [
                "Hello! Welcome to our clothing store. How can I help you today?",
                "Hi there! I'm here to assist you with your shopping needs. What can I help you find?",
                "Welcome! I'm your personal shopping assistant. How may I help you?"
            ],
            'goodbye': [
                "Thank you for shopping with us! Have a great day!",
                "Goodbye! Feel free to come back if you need anything else.",
                "Thanks for chatting with us. Happy shopping!"
            ],
            'help': [
                "I can help you with:\n• Finding products\n• Product information\n• Order tracking\n• Return policies\n• Shipping information\nWhat would you like to know?",
                "Here's what I can assist you with:\n• Product search and recommendations\n• Order status and tracking\n• Return and refund policies\n• Shipping and delivery information\nHow can I help?"
            ]
        }
    
    def _load_ml_models(self):
        """Load trained ML models if available"""
        try:
            models_dir = 'models'
            if os.path.exists(os.path.join(models_dir, 'vectorizer.pkl')) and \
               os.path.exists(os.path.join(models_dir, 'intent_classifier.pkl')):
                
                with open(os.path.join(models_dir, 'vectorizer.pkl'), 'rb') as f:
                    self.vectorizer = pickle.load(f)
                
                with open(os.path.join(models_dir, 'intent_classifier.pkl'), 'rb') as f:
                    self.intent_classifier = pickle.load(f)
                
                self.ml_models_loaded = True
                print("✅ ML models loaded successfully!")
            else:
                print("⚠️  ML models not found. Using rule-based classification.")
                self.ml_models_loaded = False
                
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            self.ml_models_loaded = False
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for ML model"""
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        from nltk.stem import WordNetLemmatizer
        
        # Download required NLTK data if not available
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        # Preprocess text
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        lemmatizer = WordNetLemmatizer()
        
        tokens = [lemmatizer.lemmatize(token) for token in tokens 
                 if token not in stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def classify_intent(self, message: str) -> str:
        """Classify the intent of the user message using ML or rule-based approach"""
        
        # Try ML model first if available
        if self.ml_models_loaded:
            try:
                processed_text = self._preprocess_text(message)
                vectorized_text = self.vectorizer.transform([processed_text])
                
                prediction = self.intent_classifier.predict(vectorized_text)[0]
                probabilities = self.intent_classifier.predict_proba(vectorized_text)[0]
                confidence = max(probabilities)
                
                # Use ML prediction if confidence is high enough
                if confidence > 0.3:  # Threshold for ML confidence
                    return prediction
                    
            except Exception as e:
                print(f"ML prediction failed, falling back to rule-based: {e}")
        
        # Fallback to rule-based classification
        message_lower = message.lower()
        
        # Check for inventory intent first (before product search)
        inventory_keywords = ['stock', 'in stock', 'available', 'how many', 'left', 'quantity', 'inventory']
        for keyword in inventory_keywords:
            if keyword in message_lower:
                return 'inventory'
        
        # Check for product search intent
        product_keywords = ['tshirt', 't-shirt', 'shirt', 'jeans', 'pants', 'dress', 'shoes', 'sneakers', 'hoodie', 'jacket', 'sweater']
        for keyword in product_keywords:
            if keyword in message_lower:
                return 'product_search'
        
        # Check other intents
        for intent, keywords in self.intents.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return intent
        
        return 'unknown'
    
    def extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from the message"""
        entities = {}
        message_lower = message.lower()
        
        # Extract product names, brands, categories
        products = db_manager.get_products(limit=1000)
        for product in products:
            if product['name'].lower() in message_lower:
                entities['product_name'] = product['name']
                entities['product_id'] = product['id']
                break
        
        # Extract order numbers (simple pattern)
        order_pattern = r'order[:\s]*#?(\d+)'
        order_match = re.search(order_pattern, message_lower)
        if order_match:
            entities['order_id'] = int(order_match.group(1))
        
        # Extract user ID (simple pattern)
        user_pattern = r'user[:\s]*#?(\d+)'
        user_match = re.search(user_pattern, message_lower)
        if user_match:
            entities['user_id'] = int(user_match.group(1))
        
        return entities
    
    def generate_response(self, intent: str, entities: Dict[str, Any], message: str) -> str:
        """Generate appropriate response based on intent and entities"""
        
        if intent == 'greeting':
            return random.choice(self.responses['greeting'])
        
        elif intent == 'goodbye':
            return random.choice(self.responses['goodbye'])
        
        elif intent == 'help':
            return random.choice(self.responses['help'])
        
        elif intent == 'product_search':
            return self._handle_product_search(entities, message)
        
        elif intent == 'product_info':
            return self._handle_product_info(entities, message)
        
        elif intent == 'order_status':
            return self._handle_order_status(entities, message)
        
        elif intent == 'return_policy':
            return self._handle_return_policy()
        
        elif intent == 'shipping':
            return self._handle_shipping_info()
        
        elif intent == 'inventory':
            return self._handle_inventory_query(entities, message)
        
        else:
            return self._handle_unknown_intent(message)
    
    def _handle_product_search(self, entities: Dict[str, Any], message: str) -> str:
        """Handle product search requests"""
        search_terms = self._extract_search_terms(message)
        
        if not search_terms:
            return "What type of product are you looking for? I can help you find clothing items by name, brand, or category."
        
        products = db_manager.search_products(search_terms[0], limit=5)
        
        if not products:
            return f"I couldn't find any products matching '{search_terms[0]}'. Could you try a different search term?"
        
        response = f"Here are some products matching '{search_terms[0]}':\n\n"
        for i, product in enumerate(products, 1):
            response += f"{i}. {product['name']} by {product['brand']}\n"
            response += f"   Category: {product['category']}\n"
            response += f"   Price: ${product['retail_price']:.2f}\n\n"
        
        response += "Would you like more details about any of these products?"
        return response
    
    def _handle_product_info(self, entities: Dict[str, Any], message: str) -> str:
        """Handle product information requests"""
        if 'product_id' in entities:
            product = db_manager.get_product_by_id(entities['product_id'])
            if product:
                inventory = db_manager.get_inventory_status(entities['product_id'])
                
                response = f"Here's information about {product['name']}:\n\n"
                response += f"Brand: {product['brand']}\n"
                response += f"Category: {product['category']}\n"
                response += f"Department: {product['department']}\n"
                response += f"Price: ${product['retail_price']:.2f}\n"
                response += f"Available: {inventory['available_items']} items\n"
                
                if inventory['available_items'] > 0:
                    response += "\n✅ This item is currently in stock!"
                else:
                    response += "\n❌ This item is currently out of stock."
                
                return response
        
        return "I'd be happy to provide product information! Could you please specify which product you're interested in?"
    
    def _handle_order_status(self, entities: Dict[str, Any], message: str) -> str:
        """Handle order status requests"""
        if 'order_id' in entities:
            # In a real system, you'd look up the actual order
            return f"I can see order #{entities['order_id']}. Let me check the status for you. Please provide your user ID for verification."
        
        if 'user_id' in entities:
            orders = db_manager.get_user_orders(entities['user_id'])
            if orders:
                response = f"Here are your recent orders:\n\n"
                for order in orders[:3]:  # Show last 3 orders
                    response += f"Order #{order['order_id']}: {order['status']}\n"
                    response += f"Items: {order['item_count']}\n"
                    response += f"Created: {order['created_at']}\n\n"
                return response
            else:
                return f"I couldn't find any orders for user #{entities['user_id']}. Please check your user ID."
        
        return "I can help you track your order! Please provide your order number or user ID."
    
    def _handle_return_policy(self) -> str:
        """Handle return policy questions"""
        return """Our return policy is customer-friendly:

📦 **Return Window**: 30 days from delivery
✅ **Conditions**: Items must be unworn, unwashed, and with original tags
🔄 **Process**: 
1. Contact customer service
2. Get return authorization
3. Ship item back
4. Refund processed within 5-7 business days

💳 **Refunds**: Original payment method
🚚 **Return Shipping**: Free for defective items

Need help with a specific return? Please provide your order number."""
    
    def _handle_shipping_info(self) -> str:
        """Handle shipping information requests"""
        return """Here's our shipping information:

🚚 **Standard Shipping**: 5-7 business days
⚡ **Express Shipping**: 2-3 business days  
🛩️ **Overnight**: Next business day

💰 **Shipping Costs**:
• Orders over $50: FREE standard shipping
• Standard: $5.99
• Express: $12.99
• Overnight: $24.99

📦 **Tracking**: All orders include tracking numbers
🌍 **International**: Available to select countries

Need to track a specific order? Please provide your order number."""
    
    def _handle_inventory_query(self, entities: Dict[str, Any], message: str) -> str:
        """Handle inventory and stock queries"""
        message_lower = message.lower()
        
        # Extract product type from message
        product_types = ['tshirt', 't-shirt', 'shirt', 'jeans', 'pants', 'dress', 'shoes', 'sneakers', 'hoodie', 'jacket', 'sweater']
        found_product = None
        
        for product_type in product_types:
            if product_type in message_lower:
                found_product = product_type
                break
        
        if found_product:
            # Search for products of this type
            products = db_manager.search_products(found_product, limit=3)
            
            if products:
                response = f"Here's the current stock information for {found_product} products:\n\n"
                
                for i, product in enumerate(products, 1):
                    inventory = db_manager.get_inventory_status(product['id'])
                    response += f"{i}. {product['name']} by {product['brand']}\n"
                    response += f"   Available: {inventory['available_items']} items\n"
                    response += f"   Total Stock: {inventory['total_items']} items\n"
                    response += f"   Price: ${product['retail_price']:.2f}\n\n"
                
                response += "Would you like more details about any specific product?"
                return response
            else:
                return f"I couldn't find any {found_product} products in our inventory. Could you try a different search term?"
        
        # If no specific product type found, provide general inventory info
        return """I can help you check inventory for specific products. Please specify what type of item you're looking for, such as:

• "How many t-shirts are in stock?"
• "Check stock for jeans"
• "Available quantity of dresses"
• "Inventory for shoes"

What product would you like to check?"""
    
    def _handle_unknown_intent(self, message: str) -> str:
        """Handle unknown intents"""
        return """I'm not sure I understood that. I can help you with:

• Finding products
• Product information and pricing
• Order tracking and status
• Return and refund policies
• Shipping information

Could you please rephrase your question or let me know what you need help with?"""
    
    def _extract_search_terms(self, message: str) -> List[str]:
        """Extract search terms from message"""
        # Simple extraction - look for words after search-related terms
        search_patterns = [
            r'search for (.+)',
            r'find (.+)',
            r'look for (.+)',
            r'show me (.+)',
            r'product (.+)',
            r'item (.+)'
        ]
        
        for pattern in search_patterns:
            match = re.search(pattern, message.lower())
            if match:
                return [match.group(1).strip()]
        
        # If no pattern matches, try to extract meaningful words
        words = message.lower().split()
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # If we have meaningful words, return them
        if meaningful_words:
            return meaningful_words[:3]  # Return up to 3 meaningful words
        
        # If no meaningful words found, return the original message as a single search term
        return [message.lower().strip()]
    
    def process_message(self, message: str) -> str:
        """Main method to process user message and return response"""
        intent = self.classify_intent(message)
        entities = self.extract_entities(message)
        response = self.generate_response(intent, entities, message)
        return response

# Global chatbot instance
chatbot = EcommerceChatbot() 