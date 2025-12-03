package http

import (
	"github.com/ai-elearning-platform/monitoring-service/internal/config"
	"github.com/ai-elearning-platform/monitoring-service/internal/interfaces/http/handlers"
	"github.com/ai-elearning-platform/monitoring-service/internal/interfaces/http/middleware"
	"github.com/gin-gonic/gin"
)

type Server struct {
	router *gin.Engine
	config *config.Config
}

func NewServer(cfg *config.Config) *Server {
	// Mode Gin basé sur l'environnement
	if cfg.Server.Mode == "production" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.Default()

	// Middlewares globaux
	router.Use(middleware.Logger())
	router.Use(middleware.CORS())

	// Routes
	v1 := router.Group("/api/v1")
	{
		// Health check
		v1.GET("/health", handlers.HealthCheck)

		// Monitoring routes
		monitoring := v1.Group("/monitoring")
		{
			monitoring.GET("/services", handlers.GetServices)
			monitoring.GET("/services/:name", handlers.GetServiceDetails)
			monitoring.GET("/metrics", handlers.GetMetrics)
		}

		// Alert routes
		alerts := v1.Group("/alerts")
		{
			alerts.GET("", handlers.GetAlerts)
			alerts.POST("", handlers.CreateAlert)
			alerts.GET("/:id", handlers.GetAlert)
		}
	}

	return &Server{
		router: router,
		config: cfg,
	}
}

func (s *Server) Start(addr string) error {
	return s.router.Run(addr)
}
