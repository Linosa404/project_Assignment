#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from gradio_conversational_chatbot import chat_fn

# Test specific cases with enhanced models
test_cases = [
    "Find flights from Berlin to Rome from July 1 to July 10",
    "Show me parks in Munich", 
    "What's the weather in London from December 16 to 23, 2025?",
    "Book a hotel in Paris for 2 adults and 1 child",
    # German tests
    "Finde Flüge von Berlin nach Rom vom 1. Juli bis 10. Juli",
    "Zeig mir Parks in München"
]

print("🧪 Testing Enhanced Models Integration")
print("="*60)

for i, msg in enumerate(test_cases, 1):
    print(f"\n🔍 Test {i}: {msg}")
    print("-" * 50)
    try:
        response = chat_fn(msg, history=None)
        print(f"✅ Success")
        # Print first 200 chars of response to verify it works
        print(f"Response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🎉 Enhanced model integration test completed!")
