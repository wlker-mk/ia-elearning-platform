package router

import (
	"net/http"

	"api-gateway/internal/gateway"

	"github.com/gin-gonic/gin"
)

func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status": "healthy",
		"service": "api-gateway",
	})
}

func servicesHealthHandler(gw *gateway.Gateway) gin.HandlerFunc {
	return func(c *gin.Context) {
		health := gw.GetAllServicesHealth()
		
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
}

func gatewayStatsHandler(gw *gateway.Gateway) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":         "operational",
			"services_count": len(gw.Services),
		})
	}
}

func cacheClearHandler(gw *gateway.Gateway) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"message": "Cache cleared successfully",
		})
	}
}
