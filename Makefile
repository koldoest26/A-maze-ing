# Variables
PYTHON = python3
MAIN_SCRIPT = test_run.py

.PHONY: install run debug clean lint lint-strict

install:
	pip install flake8 mypy

run:
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE)


debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

lint:
	flake8 .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	flake8 .
	mypy --strict .

MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt

