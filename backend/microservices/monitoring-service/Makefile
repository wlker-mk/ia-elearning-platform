.PHONY: help build run test clean docker-up docker-down migrate lint

# Variables
APP_NAME=monitoring-service
DOCKER_COMPOSE=docker-compose

help: ## Afficher l'aide
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Compiler l'application
	@echo "Building $(APP_NAME)..."
	go build -o bin/$(APP_NAME) ./cmd

run: ## Lancer l'application localement
	@echo "Running $(APP_NAME)..."
	go run ./cmd/main.go

test: ## Lancer les tests
	@echo "Running tests..."
	go test -v -race -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html

test-coverage: test ## Afficher la couverture de tests
	@echo "Test coverage:"
	go tool cover -func=coverage.out

lint: ## Lancer le linter
	@echo "Running linter..."
	golangci-lint run ./...

clean: ## Nettoyer les fichiers générés
	@echo "Cleaning..."
	rm -rf bin/
	rm -f coverage.out coverage.html

# Docker commands
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t $(APP_NAME):latest .

docker-up: ## Démarrer tous les services Docker
	@echo "Starting services..."
	$(DOCKER_COMPOSE) up -d

docker-up-tools: ## Démarrer avec les outils (pgAdmin, Redis Commander)
	@echo "Starting services with tools..."
	$(DOCKER_COMPOSE) --profile tools up -d

docker-down: ## Arrêter tous les services Docker
	@echo "Stopping services..."
	$(DOCKER_COMPOSE) down

docker-logs: ## Voir les logs Docker
	$(DOCKER_COMPOSE) logs -f

docker-ps: ## Lister les conteneurs
	$(DOCKER_COMPOSE) ps

docker-clean: ## Nettoyer les volumes Docker
	@echo "Cleaning Docker volumes..."
	$(DOCKER_COMPOSE) down -v

# Database commands
db-migrate: ## Créer les tables (via application)
	@echo "Running migrations..."
	go run ./cmd/main.go migrate

db-reset: ## Reset la base de données
	@echo "Resetting database..."
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d monitoring_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

db-shell: ## Ouvrir un shell PostgreSQL
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d monitoring_db

redis-cli: ## Ouvrir Redis CLI
	$(DOCKER_COMPOSE) exec redis redis-cli

# Development commands
dev: ## Lancer en mode développement avec hot reload
	@echo "Starting in development mode..."
	air

install-tools: ## Installer les outils de développement
	@echo "Installing development tools..."
	go install github.com/cosmtrek/air@latest
	go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

mod-tidy: ## Nettoyer go.mod
	go mod tidy

mod-download: ## Télécharger les dépendances
	go mod download

# API Testing
test-api: ## Tester l'API avec curl
	@echo "Testing health endpoint..."
	curl -X GET http://localhost:8080/health
	@echo "\nTesting service registration..."
	curl -X POST http://localhost:8080/api/v1/services \
		-H "Content-Type: application/json" \
		-d '{"serviceName":"test-service","url":"http://localhost:3000"}'

# Production
deploy: ## Build et deploy (à personnaliser)
	@echo "Building for production..."
	CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o bin/$(APP_NAME) ./cmd
	@echo "Ready for deployment!"

.DEFAULT_GOAL := help