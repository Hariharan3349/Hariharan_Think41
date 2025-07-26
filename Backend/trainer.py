import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import re
import json
import logging
from typing import List, Dict, Any, Tuple
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotTrainer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            ngram_range=(1, 2),
            stop_words='english',
            lowercase=True
        )
        self.intent_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Training data for different intents
        self.training_data = self._create_training_data()
        
    def _create_training_data(self) -> List[Tuple[str, str]]:
        """Create comprehensive training data for intent classification"""
        training_data = []
        
        # Greeting intent
        greeting_phrases = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "howdy", "greetings", "what's up", "yo", "hi there", "hello there",
            "good day", "morning", "afternoon", "evening"
        ]
        for phrase in greeting_phrases:
            training_data.append((phrase, 'greeting'))
        
        # Product search intent
        product_search_phrases = [
            "search for", "find", "look for", "show me", "i want", "i need",
            "looking for", "searching for", "find me", "get me", "show me some",
            "i'm looking for", "can you find", "help me find", "where can i find",
            "do you have", "do you sell", "are there any", "show me products",
            "browse", "explore", "view", "see", "check out"
        ]
        for phrase in product_search_phrases:
            training_data.append((phrase, 'product_search'))
        
        # Product categories
        product_categories = [
            "tshirts", "t-shirts", "shirts", "jeans", "pants", "dresses", 
            "shoes", "sneakers", "boots", "hoodies", "jackets", "sweaters",
            "skirts", "shorts", "blouses", "tops", "outfits", "clothing",
            "apparel", "fashion", "wear", "attire"
        ]
        for category in product_categories:
            training_data.append((category, 'product_search'))
            training_data.append((f"show me {category}", 'product_search'))
            training_data.append((f"find {category}", 'product_search'))
            training_data.append((f"search for {category}", 'product_search'))
        
        # Inventory/Stock intent
        inventory_phrases = [
            "how many", "stock", "in stock", "available", "left", "quantity",
            "inventory", "check stock", "stock level", "availability",
            "do you have in stock", "is it available", "how much stock",
            "remaining", "supply", "on hand", "inventory level",
            "stock status", "availability status", "stock check"
        ]
        for phrase in inventory_phrases:
            training_data.append((phrase, 'inventory'))
        
        # Order tracking intent
        order_phrases = [
            "track", "tracking", "order status", "where is my order",
            "order tracking", "track my order", "order number", "order id",
            "shipped", "delivered", "delivery status", "shipping status",
            "when will it arrive", "order update", "order information",
            "order details", "order history", "my orders", "order #"
        ]
        for phrase in order_phrases:
            training_data.append((phrase, 'order_status'))
        
        # Return policy intent
        return_phrases = [
            "return", "refund", "exchange", "return policy", "refund policy",
            "money back", "return item", "send back", "return process",
            "how to return", "return information", "return details",
            "return window", "return conditions", "return shipping",
            "return address", "return label", "return authorization"
        ]
        for phrase in return_phrases:
            training_data.append((phrase, 'return_policy'))
        
        # Shipping intent
        shipping_phrases = [
            "shipping", "delivery", "how long", "when", "shipping time",
            "delivery time", "shipping cost", "delivery cost", "shipping fee",
            "free shipping", "express shipping", "overnight", "standard shipping",
            "shipping method", "delivery method", "shipping options",
            "tracking number", "shipping address", "delivery address"
        ]
        for phrase in shipping_phrases:
            training_data.append((phrase, 'shipping'))
        
        # Help intent
        help_phrases = [
            "help", "support", "assist", "problem", "issue", "trouble",
            "need help", "can you help", "assistance", "support needed",
            "having trouble", "don't understand", "confused", "what can you do",
            "capabilities", "features", "how does this work", "guide me"
        ]
        for phrase in help_phrases:
            training_data.append((phrase, 'help'))
        
        # Goodbye intent
        goodbye_phrases = [
            "bye", "goodbye", "see you", "thank you", "thanks", "thank you very much",
            "appreciate it", "that's all", "that's it", "done", "finished",
            "end", "close", "exit", "quit", "good night", "see you later",
            "take care", "have a good day", "farewell"
        ]
        for phrase in goodbye_phrases:
            training_data.append((phrase, 'goodbye'))
        
        # Product information intent
        product_info_phrases = [
            "details", "information", "tell me about", "what is", "price", "cost",
            "product details", "product information", "specifications", "features",
            "description", "about this", "more info", "product specs", "product features",
            "what about", "tell me more", "explain", "describe", "product details"
        ]
        for phrase in product_info_phrases:
            training_data.append((phrase, 'product_info'))
        
        return training_data
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better classification"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and lemmatize
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens 
                 if token not in self.stop_words and len(token) > 2]
        
        return ' '.join(tokens)
    
    def train(self) -> Dict[str, Any]:
        """Train the intent classification model"""
        logger.info("Starting chatbot training...")
        
        # Prepare training data
        texts = []
        labels = []
        
        for text, label in self.training_data:
            processed_text = self.preprocess_text(text)
            texts.append(processed_text)
            labels.append(label)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Vectorize text
        logger.info("Vectorizing text data...")
        X_train_vectorized = self.vectorizer.fit_transform(X_train)
        X_test_vectorized = self.vectorizer.transform(X_test)
        
        # Train classifier
        logger.info("Training intent classifier...")
        self.intent_classifier.fit(X_train_vectorized, y_train)
        
        # Evaluate
        y_pred = self.intent_classifier.predict(X_test_vectorized)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Training completed! Accuracy: {accuracy:.4f}")
        logger.info("\nClassification Report:")
        logger.info(classification_report(y_test, y_pred))
        
        # Save models
        self.save_models()
        
        return {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred),
            'feature_names': self.vectorizer.get_feature_names_out().tolist()
        }
    
    def predict_intent(self, text: str) -> Tuple[str, float]:
        """Predict intent for a given text"""
        processed_text = self.preprocess_text(text)
        vectorized_text = self.vectorizer.transform([processed_text])
        
        # Get prediction and probability
        prediction = self.intent_classifier.predict(vectorized_text)[0]
        probabilities = self.intent_classifier.predict_proba(vectorized_text)[0]
        confidence = max(probabilities)
        
        return prediction, confidence
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from text using patterns and ML"""
        entities = {}
        text_lower = text.lower()
        
        # Extract product IDs
        product_id_patterns = [
            r'product\s*#?(\d+)',
            r'item\s*#?(\d+)',
            r'product\s*id\s*(\d+)',
            r'item\s*id\s*(\d+)'
        ]
        
        for pattern in product_id_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities['product_id'] = int(match.group(1))
                break
        
        # Extract order numbers
        order_patterns = [
            r'order\s*#?(\d+)',
            r'order\s*number\s*(\d+)',
            r'order\s*id\s*(\d+)'
        ]
        
        for pattern in order_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities['order_id'] = int(match.group(1))
                break
        
        # Extract user IDs
        user_patterns = [
            r'user\s*#?(\d+)',
            r'user\s*id\s*(\d+)',
            r'customer\s*#?(\d+)',
            r'customer\s*id\s*(\d+)'
        ]
        
        for pattern in user_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities['user_id'] = int(match.group(1))
                break
        
        # Extract product types
        product_types = [
            'tshirt', 't-shirt', 'shirt', 'jeans', 'pants', 'dress', 
            'shoes', 'sneakers', 'hoodie', 'jacket', 'sweater'
        ]
        
        for product_type in product_types:
            if product_type in text_lower:
                entities['product_type'] = product_type
                break
        
        # Extract quantities
        quantity_patterns = [
            r'(\d+)\s*(items?|pieces?|units?)',
            r'quantity\s*of\s*(\d+)',
            r'(\d+)\s*available',
            r'(\d+)\s*in\s*stock'
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, text_lower)
            if match:
                entities['quantity'] = int(match.group(1))
                break
        
        return entities
    
    def save_models(self):
        """Save trained models to disk"""
        logger.info("Saving trained models...")
        
        # Save vectorizer
        with open('models/vectorizer.pkl', 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        # Save classifier
        with open('models/intent_classifier.pkl', 'wb') as f:
            pickle.dump(self.intent_classifier, f)
        
        # Save training metadata
        metadata = {
            'training_data_size': len(self.training_data),
            'feature_count': len(self.vectorizer.get_feature_names_out()),
            'classes': self.intent_classifier.classes_.tolist()
        }
        
        with open('models/training_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("Models saved successfully!")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            logger.info("Loading trained models...")
            
            # Load vectorizer
            with open('models/vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            # Load classifier
            with open('models/intent_classifier.pkl', 'rb') as f:
                self.intent_classifier = pickle.load(f)
            
            logger.info("Models loaded successfully!")
            return True
            
        except FileNotFoundError:
            logger.warning("No trained models found. Please train the model first.")
            return False
    
    def generate_training_report(self) -> Dict[str, Any]:
        """Generate a comprehensive training report"""
        # Test the model with various examples
        test_examples = [
            "hello there",
            "search for jeans",
            "how many tshirts are in stock",
            "track my order #123",
            "what's your return policy",
            "how long does shipping take",
            "help me",
            "thank you"
        ]
        
        results = []
        for example in test_examples:
            intent, confidence = self.predict_intent(example)
            entities = self.extract_entities(example)
            results.append({
                'text': example,
                'predicted_intent': intent,
                'confidence': confidence,
                'entities': entities
            })
        
        return {
            'test_examples': results,
            'model_info': {
                'feature_count': len(self.vectorizer.get_feature_names_out()),
                'classes': self.intent_classifier.classes_.tolist(),
                'training_data_size': len(self.training_data)
            }
        }

# Create models directory
import os
os.makedirs('models', exist_ok=True)

if __name__ == "__main__":
    # Train the model
    trainer = ChatbotTrainer()
    results = trainer.train()
    
    # Generate and print report
    report = trainer.generate_training_report()
    print("\n" + "="*50)
    print("TRAINING REPORT")
    print("="*50)
    print(f"Accuracy: {results['accuracy']:.4f}")
    print(f"Feature count: {report['model_info']['feature_count']}")
    print(f"Training data size: {report['model_info']['training_data_size']}")
    print(f"Classes: {report['model_info']['classes']}")
    
    print("\nTest Examples:")
    for result in report['test_examples']:
        print(f"Text: '{result['text']}'")
        print(f"Intent: {result['predicted_intent']} (confidence: {result['confidence']:.3f})")
        print(f"Entities: {result['entities']}")
        print("-" * 30) 