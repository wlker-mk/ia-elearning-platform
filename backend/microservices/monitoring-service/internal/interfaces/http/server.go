package http

import (
	"net/http"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/application/alert"
	"github.com/ai-elearning-platform/monitoring-service/internal/application/monitoring"
	"github.com/ai-elearning-platform/monitoring-service/internal/config"
	"github.com/ai-elearning-platform/monitoring-service/internal/interfaces/http/handlers"
	"github.com/ai-elearning-platform/monitoring-service/internal/interfaces/http/middleware"
	"github.com/gin-gonic/gin"
)

type Server struct {
	router             *gin.Engine
	config             *config.Config
	monitoringHandler  *handlers.MonitoringHandler
	alertHandler       *handlers.AlertHandler
}

func NewServer(cfg *config.Config, monitoringService *monitoring.Service, alertService *alert.Service) *Server {
	// Mode Gin basé sur l'environnement
	if cfg.Env == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.New()

	// Middlewares globaux
	router.Use(middleware.Logger())
	router.Use(middleware.CORS())
	router.Use(middleware.Recovery())
	router.Use(middleware.SecurityHeaders())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "ok",
			"service":   "monitoring-service",
			"timestamp": time.Now().Unix(),
		})
	})

	// Initialiser les handlers
	monitoringHandler := handlers.NewMonitoringHandler(monitoringService)
	alertHandler := handlers.NewAlertHandler(alertService)

	// Routes API v1
	v1 := router.Group("/api/v1")
	{
		// Monitoring routes
		monitoringHandler.RegisterRoutes(v1)

		// Alert routes
		alertHandler.RegisterRoutes(v1)
	}

	return &Server{
		router:            router,
		config:            cfg,
		monitoringHandler: monitoringHandler,
		alertHandler:      alertHandler,
	}
}

func (s *Server) Start(addr string) error {
	srv := &http.Server{
		Addr:         addr,
		Handler:      s.router,
		ReadTimeout:  15 * time.Second,
		WriteTimeout: 15 * time.Second,
		IdleTimeout:  60 * time.Second,
	}
	return srv.ListenAndServe()
}

func (s *Server) GetRouter() *gin.Engine {
	return s.router
}
