# Makefile for common project tasks

.PHONY: train-intent train-ner infer-intent infer-ner test clean

train-intent:
	python src/train.py --task intent

train-ner:
	python src/train.py --task ner

infer-intent:
	python src/infer.py --task intent --text "Book a hotel in Paris for 2 adults"

infer-ner:
	python src/infer.py --task ner --text "Find flights from Berlin to Rome from July 1 to July 10"

test:
	python -m unittest discover -s test

clean:
	rm -rf __pycache__ */__pycache__ *.pyc *.pyo .pytest_cache
