#!/usr/bin/env python3
"""
Accuracy evaluation script for travel assistant
Tests specific problematic queries and measures improvement
"""

import sys
import os
import traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from gradio_conversational_chatbot import chat_fn, extract_intent_and_slots

def test_slot_extraction():
    """Test slot extraction accuracy on key examples"""
    
    test_cases = [
        # English flight queries
        {
            "text": "Find flights from Berlin to Rome",
            "expected": {"origin": "Berlin", "destination": "Rome"},
            "type": "flight_slots"
        },
        {
            "text": "Book a flight from London to Paris",
            "expected": {"origin": "London", "destination": "Paris"},
            "type": "flight_slots"
        },
        {
            "text": "I need flights from Munich to Vienna",
            "expected": {"origin": "Munich", "destination": "Vienna"},
            "type": "flight_slots"
        },
        
        # Date range extraction
        {
            "text": "from July 1 to July 10",
            "expected": {"start_date": "July 1", "end_date": "July 10"},
            "type": "date_slots"
        },
        {
            "text": "from December 16 to 23, 2025",
            "expected": {"start_date": "December 16", "end_date": "23"},
            "type": "date_slots"
        },
        
        # Weather city extraction
        {
            "text": "What's the weather in London",
            "expected": {"city": "London"},
            "type": "weather_slots"
        },
        {
            "text": "Weather forecast for Paris",
            "expected": {"city": "Paris"},
            "type": "weather_slots"
        },
        
        # Hotel city extraction
        {
            "text": "Book a hotel in Munich",
            "expected": {"city": "Munich"},
            "type": "hotel_slots"
        },
        {
            "text": "I need accommodation in Berlin",
            "expected": {"city": "Berlin"},
            "type": "hotel_slots"
        },
        
        # German queries (should already work well)
        {
            "text": "Finde Flüge von Berlin nach Rom",
            "expected": {"origin": "Berlin", "destination": "Rom"},
            "type": "flight_slots_de"
        },
        {
            "text": "Wie ist das Wetter in München",
            "expected": {"city": "München"},
            "type": "weather_slots_de"
        }
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("🧪 Testing Slot Extraction Accuracy")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        try:
            intent, slots = extract_intent_and_slots(case["text"])
            
            # Check if expected slots are found
            case_correct = True
            for key, expected_value in case["expected"].items():
                actual_value = slots.get(key)
                if not actual_value or expected_value.lower() not in actual_value.lower():
                    case_correct = False
                    break
            
            status = "✅ PASS" if case_correct else "❌ FAIL"
            print(f"{i:2d}. {status} [{case['type']}] {case['text']}")
            print(f"    Expected: {case['expected']}")
            print(f"    Got: {slots}")
            print()
            
            if case_correct:
                correct += 1
                
        except Exception as e:
            print(f"{i:2d}. ❌ ERROR [{case['type']}] {case['text']}")
            print(f"    Error: {e}")
            print()
    
    accuracy = (correct / total) * 100
    print(f"📊 Slot Extraction Accuracy: {correct}/{total} = {accuracy:.1f}%")
    return accuracy

def test_intent_classification():
    """Test intent classification accuracy"""
    
    test_cases = [
        {"text": "Find flights from Berlin to Rome", "expected": "flight"},
        {"text": "What's the weather in London", "expected": "weather"},
        {"text": "Book a hotel in Paris", "expected": "hotel"},
        {"text": "Show me parks in Munich", "expected": "attractions"},
        {"text": "Flight tickets to Rome", "expected": "flight"},
        {"text": "Weather forecast for tomorrow", "expected": "weather"},
        {"text": "Hotel reservation in Berlin", "expected": "hotel"},
        {"text": "Tourist attractions in Paris", "expected": "attractions"},
        {"text": "Finde Flüge nach Rom", "expected": "flight"},
        {"text": "Wie ist das Wetter", "expected": "weather"},
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("\n🎯 Testing Intent Classification Accuracy")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        try:
            intent, slots = extract_intent_and_slots(case["text"])
            
            case_correct = case["expected"] in (intent or "").lower()
            status = "✅ PASS" if case_correct else "❌ FAIL"
            
            print(f"{i:2d}. {status} {case['text']}")
            print(f"    Expected: {case['expected']}")
            print(f"    Got: {intent}")
            print()
            
            if case_correct:
                correct += 1
                
        except Exception as e:
            print(f"{i:2d}. ❌ ERROR {case['text']}")
            print(f"    Error: {e}")
            print()
    
    accuracy = (correct / total) * 100
    print(f"📊 Intent Classification Accuracy: {correct}/{total} = {accuracy:.1f}%")
    return accuracy

def test_end_to_end():
    """Test complete end-to-end functionality"""
    
    test_cases = [
        {
            "text": "Find flights from Berlin to Rome from July 1 to July 10",
            "should_contain": ["flight", "berlin", "rome"],
            "should_not_error": True
        },
        {
            "text": "What's the weather in London from December 16 to 23, 2025?",
            "should_contain": ["weather", "london"],
            "should_not_error": True
        },
        {
            "text": "Book a hotel in Paris for 2 adults and 1 child",
            "should_contain": ["hotel", "paris"],
            "should_not_error": True
        },
        {
            "text": "Show me parks in Munich",
            "should_contain": ["attractions", "munich"],
            "should_not_error": True
        },
        {
            "text": "Finde Flüge von Berlin nach Rom",
            "should_contain": ["flight", "berlin", "rom"],
            "should_not_error": True
        }
    ]
    
    correct = 0
    total = len(test_cases)
    
    print("\n🔄 Testing End-to-End Functionality")
    print("=" * 60)
    
    for i, case in enumerate(test_cases, 1):
        try:
            response = chat_fn(case["text"], history=None)
            response_lower = response.lower()
            
            # Check if response contains expected elements
            contains_expected = all(term in response_lower for term in case["should_contain"])
            
            status = "✅ PASS" if contains_expected else "❌ FAIL"
            print(f"{i:2d}. {status} {case['text']}")
            print(f"    Should contain: {case['should_contain']}")
            print(f"    Response length: {len(response)} chars")
            print()
            
            if contains_expected:
                correct += 1
                
        except Exception as e:
            print(f"{i:2d}. ❌ ERROR {case['text']}")
            print(f"    Error: {e}")
            print()
    
    accuracy = (correct / total) * 100
    print(f"📊 End-to-End Accuracy: {correct}/{total} = {accuracy:.1f}%")
    return accuracy

def main():
    """Run comprehensive accuracy tests"""
    
    print("🚀 Travel Assistant Accuracy Evaluation")
    print("=" * 60)
    print()
    
    slot_accuracy = test_slot_extraction()
    intent_accuracy = test_intent_classification()
    e2e_accuracy = test_end_to_end()
    
    overall_accuracy = (slot_accuracy + intent_accuracy + e2e_accuracy) / 3
    
    print("\n📈 OVERALL RESULTS")
    print("=" * 60)
    print(f"Slot Extraction:      {slot_accuracy:.1f}%")
    print(f"Intent Classification: {intent_accuracy:.1f}%")
    print(f"End-to-End:          {e2e_accuracy:.1f}%")
    print(f"Overall Average:     {overall_accuracy:.1f}%")
    
    if overall_accuracy >= 80:
        print("\n🎉 TARGET ACHIEVED: 80% accuracy reached!")
    else:
        print(f"\n🎯 TARGET: {80 - overall_accuracy:.1f}% improvement needed for 80% goal")
    
    return overall_accuracy

if __name__ == "__main__":
    main()
