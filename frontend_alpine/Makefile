.PHONY: build watch dev deploy clean install

# Build single time
build:
	python build.py

# Watch mode for development
watch:
	python build.py --watch

# Install dependencies
install:
	pip install -r requirements.txt

# Build and copy to root for local testing
dev: build
	cp dist/index.html index.html

# Build Docker image and deploy
deploy:
	cd .. && docker compose -f docker-compose.test.yml build frontend-alpine
	cd .. && docker compose -f docker-compose.test.yml up frontend-alpine -d

# Clean generated files
clean:
	rm -rf dist/
	rm -f index.html

# Help
help:
	@echo "AdventureLog Frontend Build System"
	@echo ""
	@echo "Available commands:"
	@echo "  make install  - Install Python dependencies"
	@echo "  make build    - Build once"
	@echo "  make watch    - Watch mode (auto-rebuild)"
	@echo "  make dev      - Build and copy for local testing"
	@echo "  make deploy   - Build Docker and restart container"
	@echo "  make clean    - Remove generated files"
