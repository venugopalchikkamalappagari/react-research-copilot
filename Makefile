.PHONY: install index run-api run-ui evaluate test

install:
	pip install -r requirements.txt

index:
	python scripts/ingest_corpus.py

run-api:
	uvicorn copilot.api.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	streamlit run frontend/app.py

evaluate:
	python scripts/run_eval.py

test:
	pytest tests/ -v