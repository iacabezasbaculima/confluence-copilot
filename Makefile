.PHONY: run run-pgvector clean-pgvector

run:
	@echo "Running the program..."
	poetry run streamlit run src/app.py --server.port 8787 --browser.serverAddress localhost

run-pgvector:
	@echo "Running postgres vector..."
	docker run -d --name pgvector -p 5432:5432 \
		-e POSTGRES_DB=pgvector \
		-e POSTGRES_USER=$${DB_USER:-pgvector} \
		-e POSTGRES_PASSWORD=$${DB_PASSWORD:-password} \
		pgvector/pgvector:pg17

clean-pgvector:
	@echo "Stopping and removing pgvector container..."
	docker stop pgvector 2>/dev/null || true
	docker rm pgvector 2>/dev/null || true

docker-up:
	@echo "Starting services with Docker Compose..."
	docker compose up -d

docker-down:
	@echo "Stopping services with Docker Compose..."
	docker compose down

docker-logs:
	@echo "Showing Docker Compose logs..."
	docker compose logs -f pgvector

run-cl:
	@echo "Running the chainlit app..."
	poetry run chainlit run src/cl_app.py
