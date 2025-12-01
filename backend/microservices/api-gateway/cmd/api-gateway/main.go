package main

import (
	"log"

	"api-gateway/internal/config"
	"api-gateway/internal/gateway"
	"api-gateway/internal/router"
)

func main() {
	cfg := config.Load()

	gw := gateway.NewGateway()

	r := router.SetupAllRoutes(gw)

	log.Printf("🚀 API Gateway démarré sur le port %s", cfg.ServicePort)

	if err := r.Run(":" + cfg.ServicePort); err != nil {
		log.Fatal("❌ Erreur lors du démarrage du serveur:", err)
	}
}
