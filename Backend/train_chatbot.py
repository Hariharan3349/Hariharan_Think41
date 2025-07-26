#!/usr/bin/env python3
"""
Chatbot Training Script
Trains the ML model for intent classification and entity extraction
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.trainer import ChatbotTrainer
import json

def main():
    print("🤖 E-Commerce Chatbot Training")
    print("=" * 50)
    
    # Initialize trainer
    print("📚 Initializing trainer...")
    trainer = ChatbotTrainer()
    
    # Train the model
    print("🎯 Training ML model...")
    results = trainer.train()
    
    # Generate training report
    print("📊 Generating training report...")
    report = trainer.generate_training_report()
    
    # Print results
    print("\n" + "="*50)
    print("🎉 TRAINING COMPLETED!")
    print("="*50)
    print(f"📈 Accuracy: {results['accuracy']:.4f}")
    print(f"🔧 Feature count: {report['model_info']['feature_count']}")
    print(f"📚 Training data size: {report['model_info']['training_data_size']}")
    print(f"🏷️  Classes: {', '.join(report['model_info']['classes'])}")
    
    print("\n🧪 Test Examples:")
    print("-" * 50)
    for result in report['test_examples']:
        print(f"💬 Text: '{result['text']}'")
        print(f"🎯 Intent: {result['predicted_intent']} (confidence: {result['confidence']:.3f})")
        print(f"🏷️  Entities: {result['entities']}")
        print("-" * 30)
    
    # Save detailed report
    with open('training_report.json', 'w') as f:
        json.dump({
            'accuracy': results['accuracy'],
            'classification_report': results['classification_report'],
            'test_examples': report['test_examples'],
            'model_info': report['model_info']
        }, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: training_report.json")
    print("\n✅ Training completed successfully!")
    print("🚀 The chatbot is now ready to use with ML-powered intent classification!")

if __name__ == "__main__":
    main() 