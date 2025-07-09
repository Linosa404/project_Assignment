# Unit tests for unified training and inference scripts
import unittest
from src.infer import infer_intent, infer_ner

class TestUnifiedInference(unittest.TestCase):
    def test_intent_inference(self):
        text = "Book a hotel in Paris for 2 adults"
        intent = infer_intent(text)
        self.assertIsInstance(intent, str)
        self.assertIn(intent, ["hotel_booking", "flight_search", "weather", "attractions", "unknown"])

    def test_ner_inference(self):
        text = "Find flights from Berlin to Rome from July 1 to July 10"
        slots = infer_ner(text)
        self.assertIsInstance(slots, dict)
        self.assertTrue(any(slots.values()))

if __name__ == "__main__":
    unittest.main()
