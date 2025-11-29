package main

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func setupAllRoutes(gateway *Gateway) *gin.Engine {
	if getEnv("DEBUG", "false") == "false" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.New()

	// Global Middleware
	router.Use(gin.Recovery())
	router.Use(LoggerMiddleware())
	router.Use(CORSMiddleware())
	router.Use(RequestIDMiddleware())
	router.Use(SecurityMiddleware())

	// Health & Monitoring
	router.GET("/health", HealthCheck)
	router.GET("/api/health", HealthCheck)
	router.GET("/api/services/health", gateway.ServicesHealthHandler)
	router.GET("/api/gateway/stats", gateway.GatewayStatsHandler)

	// Public routes (no auth required)
	public := router.Group("/api")
	{
		// Auth routes
		public.POST("/auth/login", gateway.ProxyHandler("auth-service"))
		public.POST("/auth/register", gateway.ProxyHandler("auth-service"))
		public.POST("/auth/refresh", gateway.ProxyHandler("auth-service"))
		public.POST("/auth/forgot-password", gateway.ProxyHandler("auth-service"))
		public.POST("/auth/reset-password", gateway.ProxyHandler("auth-service"))
		
		// Public search
		public.GET("/search/courses", gateway.ProxyHandler("search-service"))
		public.GET("/courses/public", gateway.ProxyHandler("courses-service"))
	}

	// Protected routes (auth required)
	api := router.Group("/api")
	api.Use(AuthMiddleware(gateway.jwtSecret))
	api.Use(RateLimitMiddleware(gateway.rateLimiter))
	{
		// User Service Routes
		users := api.Group("/users")
		{
			users.GET("", gateway.ProxyHandler("user-service"))
			users.POST("", gateway.ProxyHandler("user-service"))
			users.GET("/:id", gateway.ProxyHandler("user-service"))
			users.PUT("/:id", gateway.ProxyHandler("user-service"))
			users.DELETE("/:id", gateway.ProxyHandler("user-service"))
			users.GET("/:id/profile", gateway.ProxyHandler("user-service"))
			users.PUT("/:id/profile", gateway.ProxyHandler("user-service"))
		}

		// Course Service Routes
		courses := api.Group("/courses")
		{
			courses.GET("", gateway.ProxyHandler("courses-service"))
			courses.POST("", gateway.ProxyHandler("courses-service"))
			courses.GET("/:id", gateway.ProxyHandler("courses-service"))
			courses.PUT("/:id", gateway.ProxyHandler("courses-service"))
			courses.DELETE("/:id", gateway.ProxyHandler("courses-service"))
			courses.GET("/:id/modules", gateway.ProxyHandler("courses-service"))
			courses.POST("/:id/modules", gateway.ProxyHandler("courses-service"))
			courses.GET("/:id/lessons", gateway.ProxyHandler("courses-service"))
		}

		// Enrollment Service Routes
		enrollment := api.Group("/enrollment")
		{
			enrollment.POST("", gateway.ProxyHandler("enrollment-service"))
			enrollment.GET("/my-courses", gateway.ProxyHandler("enrollment-service"))
			enrollment.GET("/:id", gateway.ProxyHandler("enrollment-service"))
			enrollment.DELETE("/:id", gateway.ProxyHandler("enrollment-service"))
			enrollment.PUT("/:id/progress", gateway.ProxyHandler("enrollment-service"))
		}

		// Quiz Service Routes
		quizzes := api.Group("/quizzes")
		{
			quizzes.GET("", gateway.ProxyHandler("quizzes-service"))
			quizzes.POST("", gateway.ProxyHandler("quizzes-service"))
			quizzes.GET("/:id", gateway.ProxyHandler("quizzes-service"))
			quizzes.PUT("/:id", gateway.ProxyHandler("quizzes-service"))
			quizzes.DELETE("/:id", gateway.ProxyHandler("quizzes-service"))
			quizzes.POST("/:id/submit", gateway.ProxyHandler("quizzes-service"))
			quizzes.GET("/:id/results", gateway.ProxyHandler("quizzes-service"))
		}

		// Payment Service Routes
		payments := api.Group("/payments")
		{
			payments.POST("", gateway.ProxyHandler("payments-service"))
			payments.GET("/:id", gateway.ProxyHandler("payments-service"))
			payments.GET("/history", gateway.ProxyHandler("payments-service"))
			payments.POST("/:id/refund", gateway.ProxyHandler("payments-service"))
		}

		// Subscription Routes
		subscriptions := api.Group("/subscriptions")
		{
			subscriptions.GET("", gateway.ProxyHandler("payments-service"))
			subscriptions.POST("", gateway.ProxyHandler("payments-service"))
			subscriptions.GET("/:id", gateway.ProxyHandler("payments-service"))
			subscriptions.PUT("/:id", gateway.ProxyHandler("payments-service"))
			subscriptions.DELETE("/:id", gateway.ProxyHandler("payments-service"))
		}

		// Booking Service Routes
		bookings := api.Group("/bookings")
		{
			bookings.GET("", gateway.ProxyHandler("bookings-service"))
			bookings.POST("", gateway.ProxyHandler("bookings-service"))
			bookings.GET("/:id", gateway.ProxyHandler("bookings-service"))
			bookings.PUT("/:id", gateway.ProxyHandler("bookings-service"))
			bookings.DELETE("/:id", gateway.ProxyHandler("bookings-service"))
		}

		// Notification Service Routes
		notifications := api.Group("/notifications")
		{
			notifications.GET("", gateway.ProxyHandler("notifications-service"))
			notifications.GET("/:id", gateway.ProxyHandler("notifications-service"))
			notifications.PUT("/:id/read", gateway.ProxyHandler("notifications-service"))
			notifications.DELETE("/:id", gateway.ProxyHandler("notifications-service"))
			notifications.POST("/mark-all-read", gateway.ProxyHandler("notifications-service"))
		}

		// Communication Service Routes
		communications := api.Group("/communications")
		{
			communications.POST("/email", gateway.ProxyHandler("communications-service"))
			communications.POST("/sms", gateway.ProxyHandler("communications-service"))
			communications.GET("/messages", gateway.ProxyHandler("communications-service"))
		}

		// Chatbot Service Routes
		chatbot := api.Group("/chatbot")
		{
			chatbot.POST("/message", gateway.ProxyHandler("chatbot-service"))
			chatbot.GET("/conversations", gateway.ProxyHandler("chatbot-service"))
			chatbot.GET("/conversations/:id", gateway.ProxyHandler("chatbot-service"))
		}

		// Analytics Service Routes
		analytics := api.Group("/analytics")
		{
			analytics.GET("/dashboard", gateway.ProxyHandler("analytics-service"))
			analytics.GET("/reports", gateway.ProxyHandler("analytics-service"))
			analytics.GET("/user-activity", gateway.ProxyHandler("analytics-service"))
			analytics.GET("/course-stats", gateway.ProxyHandler("analytics-service"))
			analytics.POST("/events", gateway.ProxyHandler("analytics-service"))
		}

		// Monitoring Service Routes
		monitoring := api.Group("/monitoring")
		{
			monitoring.GET("/metrics", gateway.ProxyHandler("monitoring-service"))
			monitoring.GET("/logs", gateway.ProxyHandler("monitoring-service"))
			monitoring.GET("/alerts", gateway.ProxyHandler("monitoring-service"))
		}

		// Search Service Routes
		search := api.Group("/search")
		{
			search.GET("/courses", gateway.ProxyHandler("search-service"))
			search.GET("/users", gateway.ProxyHandler("search-service"))
			search.POST("/index", gateway.ProxyHandler("search-service"))
		}

		// Storage Service Routes
		storage := api.Group("/storage")
		{
			storage.POST("/upload", gateway.ProxyHandler("storage-service"))
			storage.GET("/files/:id", gateway.ProxyHandler("storage-service"))
			storage.DELETE("/files/:id", gateway.ProxyHandler("storage-service"))
			storage.GET("/files", gateway.ProxyHandler("storage-service"))
		}

		// Gamification Service Routes
		gamification := api.Group("/gamification")
		{
			gamification.GET("/badges", gateway.ProxyHandler("gamification-service"))
			gamification.GET("/leaderboard", gateway.ProxyHandler("gamification-service"))
			gamification.GET("/my-achievements", gateway.ProxyHandler("gamification-service"))
			gamification.POST("/claim-reward", gateway.ProxyHandler("gamification-service"))
		}

		// Review Service Routes
		reviews := api.Group("/reviews")
		{
			reviews.GET("", gateway.ProxyHandler("reviews-service"))
			reviews.POST("", gateway.ProxyHandler("reviews-service"))
			reviews.GET("/:id", gateway.ProxyHandler("reviews-service"))
			reviews.PUT("/:id", gateway.ProxyHandler("reviews-service"))
			reviews.DELETE("/:id", gateway.ProxyHandler("reviews-service"))
			reviews.POST("/:id/helpful", gateway.ProxyHandler("reviews-service"))
		}

		// Webinar Service Routes
		webinars := api.Group("/webinars")
		{
			webinars.GET("", gateway.ProxyHandler("webinars-service"))
			webinars.POST("", gateway.ProxyHandler("webinars-service"))
			webinars.GET("/:id", gateway.ProxyHandler("webinars-service"))
			webinars.PUT("/:id", gateway.ProxyHandler("webinars-service"))
			webinars.DELETE("/:id", gateway.ProxyHandler("webinars-service"))
			webinars.POST("/:id/join", gateway.ProxyHandler("webinars-service"))
			webinars.POST("/:id/leave", gateway.ProxyHandler("webinars-service"))
		}

		// Sponsor Service Routes
		sponsors := api.Group("/sponsors")
		{
			sponsors.GET("", gateway.ProxyHandler("sponsors-service"))
			sponsors.POST("", gateway.ProxyHandler("sponsors-service"))
			sponsors.GET("/:id", gateway.ProxyHandler("sponsors-service"))
			sponsors.PUT("/:id", gateway.ProxyHandler("sponsors-service"))
			sponsors.DELETE("/:id", gateway.ProxyHandler("sponsors-service"))
		}

		// I18n Service Routes
		i18n := api.Group("/translations")
		{
			i18n.GET("", gateway.ProxyHandler("i18n-service"))
			i18n.GET("/:language", gateway.ProxyHandler("i18n-service"))
			i18n.POST("", gateway.ProxyHandler("i18n-service"))
		}

		// Security Service Routes
		security := api.Group("/security")
		{
			security.GET("/audit-logs", gateway.ProxyHandler("security-service"))
			security.POST("/report-issue", gateway.ProxyHandler("security-service"))
			security.GET("/permissions", gateway.ProxyHandler("security-service"))
		}

		// Cache Service Routes (internal use mostly)
		cache := api.Group("/cache")
		{
			cache.GET("/:key", gateway.ProxyHandler("cache-service"))
			cache.POST("", gateway.ProxyHandler("cache-service"))
			cache.DELETE("/:key", gateway.ProxyHandler("cache-service"))
		}
	}

	// Admin routes (requires admin role)
	admin := router.Group("/api/admin")
	admin.Use(AuthMiddleware(gateway.jwtSecret))
	admin.Use(RateLimitMiddleware(gateway.rateLimiter))
	admin.Use(AdminMiddleware())
	{
		admin.GET("/users", gateway.ProxyHandler("user-service"))
		admin.GET("/statistics", gateway.ProxyHandler("analytics-service"))
		admin.GET("/system-health", gateway.ServicesHealthHandler)
		admin.POST("/cache/clear", gateway.CacheClearHandler)
	}

	return router
}

// ServicesHealthHandler returns health status of all services
func (g *Gateway) ServicesHealthHandler(c *gin.Context) {
	health := g.GetAllServicesHealth()
	
	allHealthy := true
	for _, isHealthy := range health {
		if !isHealthy {
			allHealthy = false
			break
		}
	}

	status := http.StatusOK
	if !allHealthy {
		status = http.StatusServiceUnavailable
	}

	c.JSON(status, gin.H{
		"status":   allHealthy,
		"services": health,
	})
}

// GatewayStatsHandler returns gateway statistics
func (g *Gateway) GatewayStatsHandler(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":           "operational",
		"services_count":   len(g.services),
		"circuit_breakers": g.circuitBreaker.GetAllStats(),
		"rate_limiter":     g.rateLimiter.GetLimitInfo(),
	})
}

// CacheClearHandler clears the cache
func (g *Gateway) CacheClearHandler(c *gin.Context) {
	// Clear Redis cache logic here
	c.JSON(http.StatusOK, gin.H{
		"message": "Cache cleared successfully",
	})
}

// AdminMiddleware checks if user is admin
func AdminMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		role, exists := c.Get("user_role")
		if !exists || role != "admin" {
			c.JSON(http.StatusForbidden, gin.H{
				"error": "Admin access required",
			})
			c.Abort()
			return
		}
		c.Next()
	}
}