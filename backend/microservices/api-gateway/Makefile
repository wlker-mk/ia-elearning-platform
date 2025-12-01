.PHONY: build run dev test clean

build:
	@echo "🔨 Construction de l'API Gateway..."
	@go build -o bin/api-gateway ./cmd/api-gateway
	@echo "✅ Construction terminée!"

run: build
	@echo "🚀 Démarrage de l'API Gateway..."
	@./bin/api-gateway

dev:
	@echo "⚡ Mode développement..."
	@if command -v air > /dev/null; then 		air; 	else 		echo "⚠️  Air non installé, installation..."; 		go install github.com/cosmtrek/air@latest; 		air; 	fi

test:
	@echo "🧪 Exécution des tests..."
	@go test ./... -v

clean:
	@echo "🧹 Nettoyage..."
	@rm -rf bin/ tmp/

deps:
	@echo "📦 Installation des dépendances..."
	@go mod tidy
	@go mod download

docker-build:
	@echo "🐳 Construction de l'image Docker..."
	@docker build -t api-gateway .

docker-run:
	@echo "🐳 Démarrage du conteneur Docker..."
	@docker run -p 8000:8000 api-gateway
