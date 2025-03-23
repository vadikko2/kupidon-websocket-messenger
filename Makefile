all: run

install:
	@echo "Installing requirements"
	@bash -c "source ./venv/bin/activate; pip install --no-cache-dir -r requirements.txt --root-user-action=ignore"

dev:
	@echo "Installing requirements-dev"
	@bash -c "source ./venv/bin/activate; pip install --no-cache-dir -r requirements-dev.txt --root-user-action=ignore; pre-commit install; pre-commit run --all-files --show-diff-on-failure"

run: install
	@echo "Starting the application"
	@bash -c "source ./venv/bin/activate; uvicorn --app-dir src/ presentation.api.main:app --workers 1 --host 0.0.0.0 --port 80"

docker-up:
	@echo "Starting the application in docker"
	@docker-compose up --build -d

docker-down:
	@echo "Stopping the docker containers application"
	@docker-compose down

pre-commit: dev
	@echo "Starting pre-commit"
	@bash -c "source ./venv/bin/activate; pre-commit run --all-files --show-diff-on-failure"

.PHONY: run install
