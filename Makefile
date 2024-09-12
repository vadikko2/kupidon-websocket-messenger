install:
	@echo "Copying requirements.txt to requirements.tmp.txt"
	@if [ -f ./requirements.txt ]; then \
	cp requirements.txt requirements.tmp.txt; \
	else \
	@echo "requirements.txt not found!"; \
	exit 1; \
	fi

	@echo "Replacing GitHub URL with token"
	@sed -i '' "s|https://github.com/vadikko2|https://$(GITHUB_TOKEN)@github.com/vadikko2|g" requirements.tmp.txt

	@echo "Installing requirements"
	@pip install --no-cache-dir -r requirements.tmp.txt --root-user-action=ignore

	@echo "Cleaning up temporary file"
	@rm -f requirements.tmp.txt

dev:
	@echo "Copying requirements.txt to requirements.tmp.txt"
	@if [ -f ./requirements.txt ]; then \
	cp requirements.txt requirements.tmp.txt; \
	else \
	@echo "requirements.txt not found!"; \
	exit 1; \
	fi

	@echo "Copying requirements-dev.txt to requirements-dev.tmp.txt"
	@if [ -f ./requirements-dev.txt ]; then \
	cp requirements-dev.txt requirements-dev.tmp.txt; \
	else \
	@echo "requirements-dev.txt not found!"; \
	exit 1; \
	fi

	@echo "Replacing GitHub URL with token"
	@sed -i '' "s|https://github.com/vadikko2|https://$(GITHUB_TOKEN)@github.com/vadikko2|g" requirements.tmp.txt
	@echo "Replacing requirements file path with token"
	@sed -i '' "s|requirements.txt|requirements.tmp.txt|g" requirements-dev.tmp.txt

	@echo "Installing requirements-dev"
	@pip install --no-cache-dir -r requirements-dev.tmp.txt --root-user-action=ignore

	@echo "Cleaning up temporary files"
	@rm -f requirements.tmp.txt
	@rm -f requirements-dev.tmp.txt

run:
	@echo "Starting the application"
	@bash -c "source ./venv/bin/activate; uvicorn --app-dir src/ presentation.api.main:app --workers 1 --host 0.0.0.0 --port 80"

run-fish:
	@echo "Starting the application"
	@fish -c "source ./venv/bin/activate.fish; uvicorn --app-dir src/ presentation.api.main:app --workers 1 --host 0.0.0.0 --port 80"

pre-commit:
	@echo "Starting pre-commit"
	@bash -c "source ./venv/bin/activate; pre-commit run --all-files --show-diff-on-failure"

pre-commit-fish:
	@echo "Starting pre-commit"
	@fish -c "source ./venv/bin/activate.fish; pre-commit run --all-files --show-diff-on-failure"

.PHONY: install run
