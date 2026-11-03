# Write Python bytecode caches outside the working tree so the checkout stays
# clean. The entry point does the same on its own; this covers test runs.
export PYTHONPYCACHEPREFIX := $(HOME)/.cache/clipboard-picker/pycache

# Pulls in ruff and mypy on demand so no project virtualenv is needed. The
# versions are pinned so the gate does not change under the tree.
CHECK_PY := uv run --with ruff==0.17.3 --with mypy==2.4.1 python3

PY_FILES := $(shell find src/picker_lib tests -name '*.py') bin/clipboard

.DEFAULT_GOAL := help

.PHONY: help check lint format test

help:
	@echo "  check  - Lint, type check, and run the test suite"
	@echo "  lint   - Lint and format-check without modifying files"
	@echo "  format - Apply ruff fixes and formatting"
	@echo "  test   - Run the unit tests"

check: lint
	@$(MAKE) test
	@echo "all checks passed"

lint:
	$(CHECK_PY) -m ruff check --no-cache $(PY_FILES)
	$(CHECK_PY) -m ruff format --check --no-cache $(PY_FILES)
	$(CHECK_PY) -m mypy --cache-dir=/dev/null src/picker_lib

format:
	$(CHECK_PY) -m ruff check --fix --no-cache $(PY_FILES)
	$(CHECK_PY) -m ruff format --no-cache $(PY_FILES)

test:
	PYTHONPATH=src:. $(CHECK_PY) -m unittest discover -s tests -t .
