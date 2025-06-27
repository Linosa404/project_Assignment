#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from gradio_conversational_chatbot import chat_fn

# Test specific problematic cases
test_cases = [
    "Find flights from Berlin to Rome from July 1 to July 10",
    "Show me parks in Munich",
    "What's the weather in London from December 16 to 23, 2025?",
]

for msg in test_cases:
    print(f"\n{'='*60}")
    print(f"Input: {msg}")
    print("="*60)
    try:
        response = chat_fn(msg, history=None)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
