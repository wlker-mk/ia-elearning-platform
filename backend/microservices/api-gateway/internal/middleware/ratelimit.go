package middleware

import (
	"net/http"
	"time"

	"api-gateway/internal/gateway"

	"github.com/gin-gonic/gin"
)

func RateLimit(limiter *gateway.RateLimiter) gin.HandlerFunc {
	return func(c *gin.Context) {
		key := "ratelimit:" + c.ClientIP()
		allowed, err := limiter.Allow(key, 100, 60*time.Second)
		
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Rate limit check failed"})
			c.Abort()
			return
		}
		
		if !allowed {
			c.JSON(http.StatusTooManyRequests, gin.H{"error": "Rate limit exceeded"})
			c.Abort()
			return
		}
		
		c.Next()
	}
}
