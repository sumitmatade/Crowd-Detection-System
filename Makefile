.PHONY: install models sample test lint demo clean

install:
	pip install -e ".[dev]"

models:
	python scripts/download_models.py

sample:
	python scripts/download_sample.py

test:
	pytest

lint:
	ruff check .

demo: models sample
	crowd-detection --config examples/demo.yaml

clean:
	rm -rf output .pytest_cache .ruff_cache build dist *.egg-info src/*.egg-info
