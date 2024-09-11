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

run:
	@echo "Starting the application"
	@uvicorn --app-dir src/ presentation.api.main:app --workers 4 --host 0.0.0.0 --port 80

.PHONY: install run
