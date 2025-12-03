BINARY_NAME=monitoring-service
MAIN_PATH=cmd/server/main.go

.PHONY: all build run clean test docker-up docker-down help

all: build

## build: Compile le projet
build:
	@echo "Building..."
	@go build -o bin/$(BINARY_NAME) $(MAIN_PATH)

## run: Lance l'application
run:
	@echo "Running..."
	@go run $(MAIN_PATH)

## clean: Nettoie les fichiers de build
clean:
	@echo "Cleaning..."
	@rm -rf bin/
	@go clean

## test: Lance les tests
test:
	@echo "Testing..."
	@go test -v ./...

## test-coverage: Lance les tests avec couverture
test-coverage:
	@echo "Running tests with coverage..."
	@go test -coverprofile=coverage.out ./...
	@go tool cover -html=coverage.out

## docker-up: Démarre les containers Docker
docker-up:
	@echo "Starting Docker containers..."
	@docker-compose -f deployments/docker/docker-compose.yml up -d

## docker-down: Arrête les containers Docker
docker-down:
	@echo "Stopping Docker containers..."
	@docker-compose -f deployments/docker/docker-compose.yml down

## docker-logs: Affiche les logs Docker
docker-logs:
	@docker-compose -f deployments/docker/docker-compose.yml logs -f

## migrate: Lance les migrations de base de données
migrate:
	@echo "Running migrations..."
	@go run scripts/migrate.go

## seed: Remplit la base de données avec des données de test
seed:
	@echo "Seeding database..."
	@go run scripts/seed.go

## tidy: Nettoie et organise les dépendances
tidy:
	@echo "Tidying..."
	@go mod tidy

## help: Affiche cette aide
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' | sed -e 's/^/ /'
