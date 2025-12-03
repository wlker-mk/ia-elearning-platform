package main

import (
	"log"
	"os"

	"github.com/ai-elearning-platform/monitoring-service/internal/config"
	"github.com/ai-elearning-platform/monitoring-service/internal/interfaces/http"
)

func main() {
	// Charger la configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Démarrer le serveur HTTP
	server := http.NewServer(cfg)
	
	port := os.Getenv("PORT")
	if port == "" {
		port = "9090"
	}

	log.Printf("🚀 Starting monitoring service on port %s", port)
	if err := server.Start(":" + port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
