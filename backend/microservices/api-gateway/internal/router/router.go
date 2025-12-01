package router

import (
	"api-gateway/internal/gateway"
	"api-gateway/internal/middleware"

	"github.com/gin-gonic/gin"
)

func SetupAllRoutes(gw *gateway.Gateway) *gin.Engine {
	router := gin.New()

	router.Use(gin.Recovery())
	router.Use(middleware.Logger())
	router.Use(middleware.CORS())
	router.Use(middleware.RequestID())
	router.Use(middleware.Security())

	router.GET("/health", healthCheck)
	router.GET("/api/health", healthCheck)
	router.GET("/api/services/health", servicesHealthHandler(gw))
	router.GET("/api/gateway/stats", gatewayStatsHandler(gw))

	public := router.Group("/api")
	{
		public.POST("/auth/login", gw.ProxyHandler("auth-service"))
		public.POST("/auth/register", gw.ProxyHandler("auth-service"))
		public.POST("/auth/refresh", gw.ProxyHandler("auth-service"))
		public.GET("/search/courses", gw.ProxyHandler("search-service"))
		public.GET("/courses/public", gw.ProxyHandler("courses-service"))
	}

	api := router.Group("/api")
	api.Use(middleware.Auth(gw.JwtSecret))
	api.Use(middleware.RateLimit(gw.RateLimiter))
	{
		setupUserRoutes(api, gw)
		setupCourseRoutes(api, gw)
		setupEnrollmentRoutes(api, gw)
		setupQuizRoutes(api, gw)
		setupPaymentRoutes(api, gw)
		setupBookingRoutes(api, gw)
		setupNotificationRoutes(api, gw)
		setupCommunicationRoutes(api, gw)
		setupChatbotRoutes(api, gw)
		setupAnalyticsRoutes(api, gw)
		setupMonitoringRoutes(api, gw)
		setupSearchRoutes(api, gw)
		setupStorageRoutes(api, gw)
		setupGamificationRoutes(api, gw)
		setupReviewRoutes(api, gw)
		setupWebinarRoutes(api, gw)
		setupSponsorRoutes(api, gw)
		setupI18nRoutes(api, gw)
		setupSecurityRoutes(api, gw)
		setupCacheRoutes(api, gw)
	}

	admin := router.Group("/api/admin")
	admin.Use(middleware.Auth(gw.JwtSecret))
	admin.Use(middleware.RateLimit(gw.RateLimiter))
	admin.Use(middleware.Admin())
	{
		admin.GET("/users", gw.ProxyHandler("user-service"))
		admin.GET("/statistics", gw.ProxyHandler("analytics-service"))
		admin.GET("/system-health", servicesHealthHandler(gw))
		admin.POST("/cache/clear", cacheClearHandler(gw))
	}

	return router
}

func setupUserRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	users := group.Group("/users")
	{
		users.GET("", gw.ProxyHandler("user-service"))
		users.POST("", gw.ProxyHandler("user-service"))
		users.GET("/:id", gw.ProxyHandler("user-service"))
		users.PUT("/:id", gw.ProxyHandler("user-service"))
		users.DELETE("/:id", gw.ProxyHandler("user-service"))
	}
}

func setupCourseRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	courses := group.Group("/courses")
	{
		courses.GET("", gw.ProxyHandler("courses-service"))
		courses.POST("", gw.ProxyHandler("courses-service"))
		courses.GET("/:id", gw.ProxyHandler("courses-service"))
		courses.PUT("/:id", gw.ProxyHandler("courses-service"))
		courses.DELETE("/:id", gw.ProxyHandler("courses-service"))
	}
}

func setupEnrollmentRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	enrollment := group.Group("/enrollment")
	{
		enrollment.POST("", gw.ProxyHandler("enrollment-service"))
		enrollment.GET("/my-courses", gw.ProxyHandler("enrollment-service"))
		enrollment.GET("/:id", gw.ProxyHandler("enrollment-service"))
	}
}

func setupQuizRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	quizzes := group.Group("/quizzes")
	{
		quizzes.GET("", gw.ProxyHandler("quizzes-service"))
		quizzes.POST("", gw.ProxyHandler("quizzes-service"))
		quizzes.GET("/:id", gw.ProxyHandler("quizzes-service"))
	}
}

func setupPaymentRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	payments := group.Group("/payments")
	{
		payments.POST("", gw.ProxyHandler("payments-service"))
		payments.GET("/:id", gw.ProxyHandler("payments-service"))
		payments.GET("/history", gw.ProxyHandler("payments-service"))
	}
}

func setupBookingRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	bookings := group.Group("/bookings")
	{
		bookings.GET("", gw.ProxyHandler("bookings-service"))
		bookings.POST("", gw.ProxyHandler("bookings-service"))
		bookings.GET("/:id", gw.ProxyHandler("bookings-service"))
	}
}

func setupNotificationRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	notifications := group.Group("/notifications")
	{
		notifications.GET("", gw.ProxyHandler("notifications-service"))
		notifications.PUT("/:id/read", gw.ProxyHandler("notifications-service"))
	}
}

func setupCommunicationRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	communications := group.Group("/communications")
	{
		communications.POST("/email", gw.ProxyHandler("communications-service"))
		communications.POST("/sms", gw.ProxyHandler("communications-service"))
	}
}

func setupChatbotRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	chatbot := group.Group("/chatbot")
	{
		chatbot.POST("/message", gw.ProxyHandler("chatbot-service"))
		chatbot.GET("/conversations", gw.ProxyHandler("chatbot-service"))
	}
}

func setupAnalyticsRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	analytics := group.Group("/analytics")
	{
		analytics.GET("/dashboard", gw.ProxyHandler("analytics-service"))
		analytics.GET("/reports", gw.ProxyHandler("analytics-service"))
	}
}

func setupMonitoringRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	monitoring := group.Group("/monitoring")
	{
		monitoring.GET("/metrics", gw.ProxyHandler("monitoring-service"))
		monitoring.GET("/logs", gw.ProxyHandler("monitoring-service"))
	}
}

func setupSearchRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	search := group.Group("/search")
	{
		search.GET("/courses", gw.ProxyHandler("search-service"))
		search.GET("/users", gw.ProxyHandler("search-service"))
	}
}

func setupStorageRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	storage := group.Group("/storage")
	{
		storage.POST("/upload", gw.ProxyHandler("storage-service"))
		storage.GET("/files/:id", gw.ProxyHandler("storage-service"))
	}
}

func setupGamificationRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	gamification := group.Group("/gamification")
	{
		gamification.GET("/badges", gw.ProxyHandler("gamification-service"))
		gamification.GET("/leaderboard", gw.ProxyHandler("gamification-service"))
	}
}

func setupReviewRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	reviews := group.Group("/reviews")
	{
		reviews.GET("", gw.ProxyHandler("reviews-service"))
		reviews.POST("", gw.ProxyHandler("reviews-service"))
	}
}

func setupWebinarRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	webinars := group.Group("/webinars")
	{
		webinars.GET("", gw.ProxyHandler("webinars-service"))
		webinars.POST("", gw.ProxyHandler("webinars-service"))
	}
}

func setupSponsorRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	sponsors := group.Group("/sponsors")
	{
		sponsors.GET("", gw.ProxyHandler("sponsors-service"))
		sponsors.POST("", gw.ProxyHandler("sponsors-service"))
	}
}

func setupI18nRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	i18n := group.Group("/translations")
	{
		i18n.GET("", gw.ProxyHandler("i18n-service"))
		i18n.GET("/:language", gw.ProxyHandler("i18n-service"))
	}
}

func setupSecurityRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	security := group.Group("/security")
	{
		security.GET("/audit-logs", gw.ProxyHandler("security-service"))
		security.POST("/report-issue", gw.ProxyHandler("security-service"))
	}
}

func setupCacheRoutes(group *gin.RouterGroup, gw *gateway.Gateway) {
	cache := group.Group("/cache")
	{
		cache.GET("/:key", gw.ProxyHandler("cache-service"))
		cache.POST("", gw.ProxyHandler("cache-service"))
	}
}
