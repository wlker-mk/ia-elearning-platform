package main

import (
	"context"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/application/alert"
	"github.com/ai-elearning-platform/monitoring-service/internal/application/monitoring"
	"github.com/ai-elearning-platform/monitoring-service/internal/config"
	"github.com/ai-elearning-platform/monitoring-service/internal/infrastructure/cache"
	"github.com/ai-elearning-platform/monitoring-service/internal/infrastructure/database"
	"github.com/ai-elearning-platform/monitoring-service/internal/infrastructure/repository"
	"github.com/ai-elearning-platform/monitoring-service/internal/interfaces/http/handlers"
	"github.com/ai-elearning-platform/monitoring-service/internal/interfaces/http/middleware"
	"github.com/ai-elearning-platform/monitoring-service/pkg/logger"
	"github.com/gin-gonic/gin"
)

func main() {
	// Charger la configuration
	cfg, err := config.Load()
	if err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		os.Exit(1)
	}

	// Initialiser le logger
	if err := logger.Init(cfg.Env); err != nil {
		fmt.Printf("Failed to initialize logger: %v\n", err)
		os.Exit(1)
	}
	defer logger.Sync()

	logger.Info("Starting Monitoring Service",
		logger.String("env", cfg.Env),
		logger.String("port", cfg.Port),
	)

	// Connexion à PostgreSQL
	db, err := database.NewPostgresDB(&cfg.Database)
	if err != nil {
		logger.Fatal("Failed to connect to database", logger.Err(err))
	}
	defer db.Close()
	logger.Info("Connected to PostgreSQL")

	// Initialiser le schéma
	if err := db.InitSchema(); err != nil {
		logger.Fatal("Failed to initialize database schema", logger.Err(err))
	}
	logger.Info("Database schema initialized")

	// Connexion à Redis
	redisCache, err := cache.NewRedisCache(&cfg.Redis)
	if err != nil {
		logger.Fatal("Failed to connect to Redis", logger.Err(err))
	}
	defer redisCache.Close()
	logger.Info("Connected to Redis")

	// Initialiser les repositories
	monitoringRepo := repository.NewMonitoringRepository(db.DB)
	alertRepo := repository.NewAlertRepository(db.DB)

	// Initialiser les services
	monitoringService := monitoring.NewService(monitoringRepo, redisCache)
	alertService := alert.NewService(alertRepo, redisCache)

	// Initialiser les handlers
	monitoringHandler := handlers.NewMonitoringHandler(monitoringService)
	alertHandler := handlers.NewAlertHandler(alertService)

	// Configurer Gin
	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.New()

	// Middlewares globaux
	router.Use(middleware.RequestID())
	router.Use(middleware.Logger())
	router.Use(middleware.Recovery())
	router.Use(middleware.CORS())
	router.Use(middleware.SecurityHeaders())
	router.Use(middleware.MetricsCollector())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		// Vérifier DB
		dbHealth := "ok"
		if err := db.Health(); err != nil {
			dbHealth = "error"
		}

		// Vérifier Redis
		redisHealth := "ok"
		if err := redisCache.Health(); err != nil {
			redisHealth = "error"
		}

		status := http.StatusOK
		overallHealth := "healthy"
		if dbHealth != "ok" || redisHealth != "ok" {
			status = http.StatusServiceUnavailable
			overallHealth = "unhealthy"
		}

		c.JSON(status, gin.H{
			"status":    overallHealth,
			"timestamp": time.Now().Unix(),
			"service":   "monitoring-service",
			"checks": gin.H{
				"database": dbHealth,
				"cache":    redisHealth,
			},
		})
	})

	// Routes API v1
	v1 := router.Group("/api/v1")
	{
		// Monitoring routes
		monitoringHandler.RegisterRoutes(v1)

		// Alert routes
		alertHandler.RegisterRoutes(v1)
	}

	// Démarrer le serveur HTTP
	srv := &http.Server{
		Addr:         ":" + cfg.Port,
		Handler:      router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}

	// Démarrer les tâches en arrière-plan
	go startBackgroundTasks(monitoringService, alertService)

	// Démarrer le serveur dans une goroutine
	go func() {
		logger.Info("HTTP server listening", logger.String("port", cfg.Port))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Failed to start server", logger.Err(err))
		}
	}()

	// Attendre le signal d'arrêt
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")

	// Graceful shutdown avec timeout de 10 secondes
	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("Server forced to shutdown", logger.Err(err))
	}

	logger.Info("Server stopped gracefully")
}

// startBackgroundTasks démarre les tâches périodiques
func startBackgroundTasks(monitoringService *monitoring.Service, alertService *alert.Service) {
	// Ticker pour cleanup des anciennes données (tous les jours à 2h du matin)
	cleanupTicker := time.NewTicker(24 * time.Hour)
	defer cleanupTicker.Stop()

	// Ticker pour les métriques agrégées (toutes les 5 minutes)
	metricsTicker := time.NewTicker(5 * time.Minute)
	defer metricsTicker.Stop()

	logger.Info("Background tasks started")

	for {
		select {
		case <-cleanupTicker.C:
			logger.Info("Running data cleanup task")
			
			// Nettoyer les données de plus de 30 jours
			if err := monitoringService.CleanupOldData(30); err != nil {
				logger.Error("Data cleanup failed", logger.Err(err))
			}
			
			// Nettoyer les alertes résolues de plus de 90 jours
			if err := alertService.CleanupOldAlerts(90); err != nil {
				logger.Error("Alert cleanup failed", logger.Err(err))
			}
			
			logger.Info("Data cleanup completed")

		case <-metricsTicker.C:
			logger.Debug("Aggregating metrics")
			// Ici, vous pouvez ajouter des tâches d'agrégation de métriques
			// Par exemple, calculer les statistiques horaires/quotidiennes
		}
	}
}