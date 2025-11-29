.PHONY: help build run test clean docker-build docker-run docker-stop logs

# Variables
APP_NAME=api-gateway
DOCKER_IMAGE=$(APP_NAME):latest
GO_FILES=$(shell find . -name '*.go')

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

build: ## Build the Go application
	@echo "🔨 Building $(APP_NAME)..."
	@go build -o bin/$(APP_NAME) ./cmd/api-gateway
	@echo "✅ Build complete!"

run: ## Run the application locally
	@echo "🚀 Running $(APP_NAME)..."
	@go run ./cmd/api-gateway

test: ## Run tests
	@echo "🧪 Running tests..."
	@go test -v ./...

test-coverage: ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	@go test -v -coverprofile=coverage.out ./...
	@go tool cover -html=coverage.out -o coverage.html
	@echo "✅ Coverage report generated: coverage.html"

clean: ## Clean build artifacts
	@echo "🧹 Cleaning..."
	@rm -rf bin/
	@rm -f coverage.out coverage.html
	@echo "✅ Clean complete!"

deps: ## Download dependencies
	@echo "📦 Downloading dependencies..."
	@go mod download
	@go mod tidy
	@echo "✅ Dependencies updated!"

format: ## Format Go code
	@echo "💅 Formatting code..."
	@go fmt ./...
	@echo "✅ Format complete!"

lint: ## Run linter
	@echo "🔍 Running linter..."
	@golangci-lint run ./...
	@echo "✅ Lint complete!"

docker-build: ## Build Docker image
	@echo "🐳 Building Docker image..."
	@docker build -t $(DOCKER_IMAGE) .
	@echo "✅ Docker image built!"

docker-run: ## Run Docker container
	@echo "🐳 Starting Docker container..."
	@docker-compose up -d
	@echo "✅ Container started!"
	@echo "📊 Access the gateway at http://localhost:8000"

docker-stop: ## Stop Docker container
	@echo "🛑 Stopping Docker container..."
	@docker-compose down
	@echo "✅ Container stopped!"

docker-logs: ## Show Docker logs
	@docker-compose logs -f api-gateway

docker-restart: docker-stop docker-run ## Restart Docker container

docker-clean: ## Remove Docker containers and volumes
	@echo "🧹 Cleaning Docker resources..."
	@docker-compose down -v
	@docker rmi $(DOCKER_IMAGE) || true
	@echo "✅ Docker cleanup complete!"

dev: ## Run in development mode with hot reload
	@echo "🔥 Starting development mode..."
	@air || go run ./cmd/api-gateway

health: ## Check gateway health
	@echo "🏥 Checking gateway health..."
	@curl -s http://localhost:8000/health | jq .

benchmark: ## Run benchmarks
	@echo "⚡ Running benchmarks..."
	@go test -bench=. -benchmem ./...

install-tools: ## Install development tools
	@echo "🔧 Installing development tools..."
	@go install github.com/cosmtrek/air@latest
	@go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
	@echo "✅ Tools installed!"

init: deps install-tools ## Initialize project for development
	@echo "✅ Project initialized!"

prod-build: ## Build optimized production binary
	@echo "🚀 Building production binary..."
	@CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -ldflags="-w -s" -o bin/$(APP_NAME) ./cmd/api-gateway
	@echo "✅ Production build complete!"

all: clean format lint test build ## Run all checks and build
	@echo "✅ All tasks complete!"