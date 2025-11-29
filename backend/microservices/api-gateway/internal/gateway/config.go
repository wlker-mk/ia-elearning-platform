package main

import (
	"fmt"
	"log"
	"time"
)

func (g *Gateway) registerAllServices() {
	services := []ServiceConfig{
		// Core Services
		{
			Name:      "user-service",
			BaseURL:   getEnv("USER_SERVICE_URL", "http://user-service:8001"),
			Timeout:   15 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "auth-service",
			BaseURL:   getEnv("AUTH_SERVICE_URL", "http://auth-service:8002"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},

		// Course & Learning Services
		{
			Name:      "courses-service",
			BaseURL:   getEnv("COURSES_SERVICE_URL", "http://courses-service:8003"),
			Timeout:   15 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "enrollment-service",
			BaseURL:   getEnv("ENROLLMENT_SERVICE_URL", "http://enrollment-service:8004"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "quizzes-service",
			BaseURL:   getEnv("QUIZZES_SERVICE_URL", "http://quizzes-service:8005"),
			Timeout:   15 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},

		// Payment & Booking Services
		{
			Name:      "payments-service",
			BaseURL:   getEnv("PAYMENTS_SERVICE_URL", "http://payments-service:8006"),
			Timeout:   20 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "bookings-service",
			BaseURL:   getEnv("BOOKINGS_SERVICE_URL", "http://bookings-service:8007"),
			Timeout:   15 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},

		// Communication Services
		{
			Name:      "notifications-service",
			BaseURL:   getEnv("NOTIFICATIONS_SERVICE_URL", "http://notifications-service:8008"),
			Timeout:   10 * time.Second,
			Retries:   2,
			HealthURL: "/health",
		},
		{
			Name:      "communications-service",
			BaseURL:   getEnv("COMMUNICATIONS_SERVICE_URL", "http://communications-service:8009"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "chatbot-service",
			BaseURL:   getEnv("CHATBOT_SERVICE_URL", "http://chatbot-service:8010"),
			Timeout:   15 * time.Second,
			Retries:   2,
			HealthURL: "/health",
		},

		// Analytics & Monitoring
		{
			Name:      "analytics-service",
			BaseURL:   getEnv("ANALYTICS_SERVICE_URL", "http://analytics-service:8011"),
			Timeout:   15 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "monitoring-service",
			BaseURL:   getEnv("MONITORING_SERVICE_URL", "http://monitoring-service:8012"),
			Timeout:   10 * time.Second,
			Retries:   2,
			HealthURL: "/health",
		},

		// Utility Services
		{
			Name:      "search-service",
			BaseURL:   getEnv("SEARCH_SERVICE_URL", "http://search-service:8013"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "cache-service",
			BaseURL:   getEnv("CACHE_SERVICE_URL", "http://cache-service:8014"),
			Timeout:   5 * time.Second,
			Retries:   2,
			HealthURL: "/health",
		},
		{
			Name:      "storage-service",
			BaseURL:   getEnv("STORAGE_SERVICE_URL", "http://storage-service:8015"),
			Timeout:   20 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},

		// Advanced Features
		{
			Name:      "gamification-service",
			BaseURL:   getEnv("GAMIFICATION_SERVICE_URL", "http://gamification-service:8016"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "reviews-service",
			BaseURL:   getEnv("REVIEWS_SERVICE_URL", "http://reviews-service:8017"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
		{
			Name:      "webinars-service",
			BaseURL:   getEnv("WEBINARS_SERVICE_URL", "http://webinars-service:8018"),
			Timeout:   15 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},

		// Business Services
		{
			Name:      "sponsors-service",
			BaseURL:   getEnv("SPONSORS_SERVICE_URL", "http://sponsors-service:8019"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},

		// Internationalization
		{
			Name:      "i18n-service",
			BaseURL:   getEnv("I18N_SERVICE_URL", "http://i18n-service:8020"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},

		// Security
		{
			Name:      "security-service",
			BaseURL:   getEnv("SECURITY_SERVICE_URL", "http://security-service:8021"),
			Timeout:   10 * time.Second,
			Retries:   3,
			HealthURL: "/health",
		},
	}

	for _, svc := range services {
		g.services[svc.Name] = &svc
		log.Printf("✅ Registered service: %s -> %s", svc.Name, svc.BaseURL)
	}

	log.Printf("📊 Total services registered: %d", len(g.services))
}

func (g *Gateway) ServiceHealthCheck(serviceName string) (bool, error) {
	service, exists := g.services[serviceName]
	if !exists {
		return false, fmt.Errorf("service not found: %s", serviceName)
	}

	healthURL := service.BaseURL + service.HealthURL
	resp, err := g.httpClient.Get(healthURL)
	if err != nil {
		return false, err
	}
	defer resp.Body.Close()

	return resp.StatusCode == 200, nil
}

func (g *Gateway) GetAllServicesHealth() map[string]bool {
	health := make(map[string]bool)

	for name := range g.services {
		isHealthy, _ := g.ServiceHealthCheck(name)
		health[name] = isHealthy
	}

	return health
}