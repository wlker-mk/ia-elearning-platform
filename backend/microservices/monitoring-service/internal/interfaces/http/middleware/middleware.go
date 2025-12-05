package middleware

import (
	"time"
	"context"

	"github.com/ai-elearning-platform/monitoring-service/pkg/logger"
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
)

// RequestID ajoute un ID unique à chaque requête
func RequestID() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = uuid.New().String()
		}
		
		c.Set("request_id", requestID)
		c.Header("X-Request-ID", requestID)
		
		c.Next()
	}
}

// Logger middleware pour logging des requêtes HTTP
func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery
		
		c.Next()
		
		latency := time.Since(start)
		statusCode := c.Writer.Status()
		
		// Log avec contexte
		fields := []interface{}{
			logger.String("method", c.Request.Method),
			logger.String("path", path),
			logger.String("query", query),
			logger.Int("status", statusCode),
			logger.Duration("latency", latency),
			logger.String("ip", c.ClientIP()),
			logger.String("user_agent", c.Request.UserAgent()),
		}
		
		if requestID, exists := c.Get("request_id"); exists {
			fields = append(fields, logger.String("request_id", requestID.(string)))
		}
		
		// Logger selon le statut
		if statusCode >= 500 {
			logger.Error("Server error", fields...)
		} else if statusCode >= 400 {
			logger.Warn("Client error", fields...)
		} else {
			logger.Info("Request completed", fields...)
		}
	}
}

// Recovery middleware pour récupérer des panics
func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				logger.Error("Panic recovered",
					logger.String("error", err.(error).Error()),
					logger.String("path", c.Request.URL.Path),
					logger.String("method", c.Request.Method),
				)
				
				c.JSON(500, gin.H{
					"error": "Internal server error",
					"code":  "INTERNAL_ERROR",
				})
				c.Abort()
			}
		}()
		
		c.Next()
	}
}

// CORS middleware
func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With, X-Request-ID")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE, PATCH")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	}
}

// RateLimiter middleware basique (peut être amélioré avec Redis)
func RateLimiter(requestsPerMinute int) gin.HandlerFunc {
	// Simple in-memory rate limiter
	type client struct {
		lastSeen time.Time
		count    int
	}
	
	clients := make(map[string]*client)
	
	return func(c *gin.Context) {
		ip := c.ClientIP()
		
		now := time.Now()
		
		if cl, exists := clients[ip]; exists {
			// Reset si plus d'une minute
			if now.Sub(cl.lastSeen) > time.Minute {
				cl.count = 1
				cl.lastSeen = now
			} else {
				cl.count++
				if cl.count > requestsPerMinute {
					c.JSON(429, gin.H{
						"error": "Too many requests",
						"code":  "RATE_LIMIT_EXCEEDED",
					})
					c.Abort()
					return
				}
			}
		} else {
			clients[ip] = &client{
				lastSeen: now,
				count:    1,
			}
		}
		
		c.Next()
	}
}

// Timeout middleware
func Timeout(timeout time.Duration) gin.HandlerFunc {
	return func(c *gin.Context) {
		// Wrap dans un contexte avec timeout
		ctx, cancel := context.WithTimeout(c.Request.Context(), timeout)
		defer cancel()
		
		c.Request = c.Request.WithContext(ctx)
		
		finished := make(chan struct{})
		go func() {
			c.Next()
			finished <- struct{}{}
		}()
		
		select {
		case <-finished:
			return
		case <-ctx.Done():
			c.JSON(504, gin.H{
				"error": "Request timeout",
				"code":  "TIMEOUT",
			})
			c.Abort()
		}
	}
}

// HealthCheck endpoint simple
func HealthCheck() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":    "healthy",
			"timestamp": time.Now().Unix(),
			"service":   "monitoring-service",
		})
	}
}

// MetricsCollector middleware pour collecter des métriques sur les requêtes
func MetricsCollector() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		
		c.Next()
		
		duration := time.Since(start)
		
		// Incrémenter les métriques (peut utiliser Prometheus)
		statusCode := c.Writer.Status()
		method := c.Request.Method
		path := c.Request.URL.Path
		
		// Log des métriques
		logger.Debug("Request metrics",
			logger.String("method", method),
			logger.String("path", path),
			logger.Int("status", statusCode),
			logger.Int64("duration_ms", duration.Milliseconds()),
		)
	}
}

// Security headers
func SecurityHeaders() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("X-Content-Type-Options", "nosniff")
		c.Header("X-Frame-Options", "DENY")
		c.Header("X-XSS-Protection", "1; mode=block")
		c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
		
		c.Next()
	}
}

// APIKeyAuth middleware pour authentification par API key (basique)
func APIKeyAuth(validAPIKey string) gin.HandlerFunc {
	return func(c *gin.Context) {
		apiKey := c.GetHeader("X-API-Key")
		
		if apiKey == "" {
			c.JSON(401, gin.H{
				"error": "API key required",
				"code":  "UNAUTHORIZED",
			})
			c.Abort()
			return
		}
		
		if apiKey != validAPIKey {
			c.JSON(401, gin.H{
				"error": "Invalid API key",
				"code":  "UNAUTHORIZED",
			})
			c.Abort()
			return
		}
		
		c.Next()
	}
}