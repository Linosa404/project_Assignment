#!/usr/bin/env python3
import sys
import os
import re
import json
from typing import Dict, List, Tuple
from dataclasses import dataclass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@dataclass
class TestCase:
    query: str
    expected_intent: str
    expected_slots: Dict[str, str]
    language: str = "en"

@dataclass
class TestResult:
    query: str
    expected_intent: str
    actual_intent: str
    expected_slots: Dict[str, str]
    actual_slots: Dict[str, str]
    intent_correct: bool
    slots_correct: bool
    overall_correct: bool

# Define expected test cases with ground truth
test_cases = [
    TestCase("Find flights from Berlin to Rome from July 1 to July 10", 
             "flight_search", 
             {"origin": "Berlin", "destination": "Rome", "start_date": "July 1", "end_date": "July 10"}),
    
    TestCase("What's the weather in London from December 16 to 23, 2025?", 
             "weather", 
             {"city": "London", "start_date": "December 16", "end_date": "December 23"}),
    
    TestCase("Book a hotel in Paris for 2 adults and 1 child from August 5 to August 10", 
             "hotel_booking", 
             {"city": "Paris", "adults": "2", "children": "1", "start_date": "August 5", "end_date": "August 10"}),
    
    TestCase("Show me parks in Munich", 
             "attractions", 
             {"city": "Munich"}),
    
    TestCase("Random unrelated question", 
             "unknown", 
             {}),
    
    # German test cases
    TestCase("Finde Flüge von Berlin nach Rom vom 1. Juli bis 10. Juli", 
             "flight_search", 
             {"origin": "Berlin", "destination": "Rom", "start_date": "1. Juli", "end_date": "10. Juli"}, "de"),
    
    TestCase("Wie ist das Wetter in London vom 16. bis 23. Dezember 2025?", 
             "weather", 
             {"city": "London", "start_date": "16. Dezember", "end_date": "23. Dezember"}, "de"),
    
    TestCase("Buche ein Hotel in Paris für 2 Erwachsene und 1 Kind vom 5. bis 10. August", 
             "hotel_booking", 
             {"city": "Paris", "adults": "2", "children": "1", "start_date": "5. August", "end_date": "10. August"}, "de"),
    
    TestCase("Ich möchte einen Flug von München nach Wien am 15. August buchen", 
             "flight_search", 
             {"origin": "München", "destination": "Wien", "start_date": "15. August"}, "de"),
    
    TestCase("Wie ist die Temperatur in Berlin nächste Woche?", 
             "weather", 
             {"city": "Berlin"}, "de"),
    
    TestCase("Gibt es günstige Flüge von Frankfurt nach Madrid im September?", 
             "flight_search", 
             {"origin": "Frankfurt", "destination": "Madrid", "start_date": "September"}, "de"),
    
    TestCase("Was kostet ein Flug von Düsseldorf nach Zürich am 20. Juli?", 
             "flight_search", 
             {"origin": "Düsseldorf", "destination": "Zürich", "start_date": "20. Juli"}, "de"),
    
    TestCase("Wettervorhersage für Köln vom 1. bis 3. März", 
             "weather", 
             {"city": "Köln", "start_date": "1. März", "end_date": "3. März"}, "de"),
    
    TestCase("Finde Flüge von Stuttgart nach Barcelona für 2 Erwachsene am 12. April", 
             "flight_search", 
             {"origin": "Stuttgart", "destination": "Barcelona", "adults": "2", "start_date": "12. April"}, "de"),
    
    TestCase("Hotel in München für 1 Erwachsenen und 2 Kinder vom 3. bis 7. Mai", 
             "hotel_booking", 
             {"city": "München", "adults": "1", "children": "2", "start_date": "3. Mai", "end_date": "7. Mai"}, "de"),
    
    TestCase("Wie ist das Wetter in Paris am 14. Februar?", 
             "weather", 
             {"city": "Paris", "start_date": "14. Februar"}, "de"),
    
    TestCase("Flug von Bremen nach Oslo am 22. Dezember gesucht", 
             "flight_search", 
             {"origin": "Bremen", "destination": "Oslo", "start_date": "22. Dezember"}, "de"),
    
    TestCase("Gibt es Hotels in Wien mit Parkmöglichkeit vom 8. bis 12. Juni?", 
             "hotel_booking", 
             {"city": "Wien", "start_date": "8. Juni", "end_date": "12. Juni"}, "de"),
    
    TestCase("Ich brauche einen Flug von Hannover nach Prag am 30. September", 
             "flight_search", 
             {"origin": "Hannover", "destination": "Prag", "start_date": "30. September"}, "de"),
    
    TestCase("Buche ein Hotel in Düsseldorf für 3 Nächte ab dem 5. November", 
             "hotel_booking", 
             {"city": "Düsseldorf", "start_date": "5. November"}, "de"),
]

def extract_debug_info(response: str) -> Tuple[str, Dict[str, str]]:
    """Extract intent and slots from debug output"""
    intent_match = re.search(r"DEBUG: intent=([^,\s]+)", response)
    slots_match = re.search(r"DEBUG: intent=[^,]+, slots=(\{[^}]*\})", response)
    
    intent = intent_match.group(1) if intent_match else "unknown"
    
    slots = {}
    if slots_match:
        try:
            slots_str = slots_match.group(1)
            # Clean up the slots string and parse it
            slots_str = slots_str.replace("'", '"')
            slots = json.loads(slots_str)
        except Exception as e:
            print(f"Debug: Could not parse slots '{slots_str}': {e}")
            pass
    
    print(f"Debug: Extracted intent='{intent}', slots={slots}")
    return intent, slots

def normalize_value(value: str) -> str:
    """Normalize values for comparison"""
    if not value:
        return ""
    return value.lower().strip()

def slots_match(expected: Dict[str, str], actual: Dict[str, str]) -> bool:
    """Check if slots match with flexible comparison"""
    for key, expected_val in expected.items():
        if key not in actual:
            return False
        
        actual_val = actual[key]
        
        # Normalize for comparison
        exp_norm = normalize_value(expected_val)
        act_norm = normalize_value(actual_val)
        
        # For cities, be flexible with variations (e.g., Rom vs Rome)
        if key in ['city', 'origin', 'destination']:
            if exp_norm == act_norm:
                continue
            # Check common variations
            city_variations = {
                'rom': 'rome', 'rome': 'rom',
                'münchen': 'munich', 'munich': 'münchen',
                'wien': 'vienna', 'vienna': 'wien',
                'hannover': 'hanover', 'hanover': 'hannover',
                'zürich': 'zurich', 'zurich': 'zürich',
                'köln': 'cologne', 'cologne': 'köln'
            }
            if exp_norm in city_variations and city_variations[exp_norm] == act_norm:
                continue
            
            return False
        else:
            if exp_norm != act_norm:
                return False
    
    return True

def run_test_analysis():
    from gradio_conversational_chatbot import chat_fn
    
    results = []
    
    for test_case in test_cases:
        try:
            response = chat_fn(test_case.query, history=None)
            actual_intent, actual_slots = extract_debug_info(response)
            
            intent_correct = actual_intent == test_case.expected_intent
            slots_correct = slots_match(test_case.expected_slots, actual_slots)
            overall_correct = intent_correct and slots_correct
            
            result = TestResult(
                query=test_case.query,
                expected_intent=test_case.expected_intent,
                actual_intent=actual_intent,
                expected_slots=test_case.expected_slots,
                actual_slots=actual_slots,
                intent_correct=intent_correct,
                slots_correct=slots_correct,
                overall_correct=overall_correct
            )
            results.append(result)
            
        except Exception as e:
            print(f"Error processing: {test_case.query}")
            print(f"Error: {e}")
            continue
    
    # Calculate accuracy metrics
    total_tests = len(results)
    intent_correct = sum(1 for r in results if r.intent_correct)
    slots_correct = sum(1 for r in results if r.slots_correct)
    overall_correct = sum(1 for r in results if r.overall_correct)
    
    intent_accuracy = intent_correct / total_tests * 100
    slot_accuracy = slots_correct / total_tests * 100
    overall_accuracy = overall_correct / total_tests * 100
    
    print("="*80)
    print("TEST ANALYSIS RESULTS")
    print("="*80)
    print(f"Total Test Cases: {total_tests}")
    print(f"Intent Classification Accuracy: {intent_accuracy:.1f}% ({intent_correct}/{total_tests})")
    print(f"Slot Extraction Accuracy: {slot_accuracy:.1f}% ({slots_correct}/{total_tests})")
    print(f"Overall Accuracy: {overall_accuracy:.1f}% ({overall_correct}/{total_tests})")
    print("="*80)
    
    # Show failed cases
    failed_cases = [r for r in results if not r.overall_correct]
    
    if failed_cases:
        print(f"\nFAILED CASES ({len(failed_cases)}):")
        print("-"*80)
        
        for i, result in enumerate(failed_cases, 1):
            print(f"{i}. Query: {result.query}")
            if not result.intent_correct:
                print(f"   Intent - Expected: {result.expected_intent}, Got: {result.actual_intent}")
            if not result.slots_correct:
                print(f"   Slots - Expected: {result.expected_slots}")
                print(f"           Got: {result.actual_slots}")
            print()
    
    return overall_accuracy >= 80.0, results

if __name__ == "__main__":
    success, results = run_test_analysis()
    if success:
        print("✅ PASSED: Accuracy target of 80% achieved!")
    else:
        print("❌ FAILED: Accuracy below 80% target")
