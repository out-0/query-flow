docker_start:
	docker compose up -d

docker_stop:
	docker compose down

docker_restart: docker_stop docker_start
	# This will run stop first, then start (sequential by default)

logs:
	docker compose logs -f


install:
	@echo "📦 Installing dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "✅ Using uv"; \
		uv sync; \
		uv pip install -e .; \
	elif command -v poetry >/dev/null 2>&1; then \
		echo "✅ Using poetry"; \
		poetry install; \
	elif command -v pip >/dev/null 2>&1; then \
		echo "✅ Using pip"; \
		if [ ! -d ".venv" ]; then \
			echo "Creating virtual environment..."; \
			python3 -m venv .venv; \
		fi; \
		echo "Activating and installing..."; \
		. .venv/bin/activate && pip install --upgrade pip && pip install -e .; \
		echo ""; \
		echo "⚠️  Remember to activate your virtual environment:"; \
		echo "   source .venv/bin/activate"; \
	else \
		echo "❌ No package manager found!"; \
		echo "Please install one of: uv, poetry, or pip"; \
		exit 1; \
	fi

run:
	@if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then \
		. .venv/bin/activate && python app.py; \
	elif command -v uv >/dev/null 2>&1 && [ -d ".venv" ]; then \
		uv run python app.py; \
	elif command -v poetry >/dev/null 2>&1 && [ -d ".venv" ]; then \
		poetry run python app.py; \
	else \
		python app.py; \
	fi