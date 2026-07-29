# Variables
PYTHON = python3
MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt

.PHONY: build install run debug clean lint lint-strict venv

build:
	python3 -m pip install --upgrade build
	python3 -m build --outdir .

install:
	pip3 install flake8 mypy

run:
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache mypy_cache
	rm -rf dist build *.egg-info mazegen.egg-info
	rm -f *.whl *.tar.gz

lint:
	flake8 .
	mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs .

lint-strict:
	flake8 .
	mypy --strict .

venv:
	python3 -m venv venv
	@echo "Virtual Environment created. To activate it run: source venv/bin/activate"