.PHONY: setup simulate train evaluate reproduce demo-seed test

setup:
	pip install -r requirements.txt

simulate:
	PYTHONPATH="." python scripts/generate_data.py --num_customers 10000 --seed 42

train:
	PYTHONPATH="." python scripts/train_and_evaluate.py

evaluate: train

reproduce: simulate train

demo-seed:
	PYTHONPATH="." python scripts/seed_demo.py

test:
	PYTHONPATH="." python -m unittest discover -s tests
