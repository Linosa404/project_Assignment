#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from gradio_conversational_chatbot import extract_intent_and_slots, normalize_dates_from_slots

# Test just the enhanced NLP components (without API calls)
test_cases = [
    "Find flights from Berlin to Rome from July 1 to July 10",
    "Show me parks in Munich", 
    "What's the weather in London?",
    "Book a hotel in Paris for 2 adults",
    "Finde Flüge von Berlin nach Rom",
    "Zeig mir Parks in München"
]

print("🧪 Testing Enhanced NLP Components")
print("="*60)

for i, msg in enumerate(test_cases, 1):
    print(f"\n🔍 Test {i}: {msg}")
    print("-" * 50)
    try:
        # Test intent and slot extraction
        intent, slots = extract_intent_and_slots(msg)
        normalized_slots = normalize_dates_from_slots(slots, msg)
        
        print(f"✅ Intent: {intent}")
        print(f"✅ Raw Slots: {slots}")
        print(f"✅ Normalized Slots: {normalized_slots}")
        
        # Check for improvements
        if intent and (slots or normalized_slots):
            print("🎯 SUCCESS: Both intent and slots extracted!")
        elif intent:
            print("⚠️  PARTIAL: Intent extracted, slots missing")
        else:
            print("❌ FAILED: No intent extracted")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🎉 Enhanced NLP component test completed!")
