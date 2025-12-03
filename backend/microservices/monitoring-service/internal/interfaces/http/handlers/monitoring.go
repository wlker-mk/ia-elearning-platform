package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetServices(c *gin.Context) {
	// TODO: Implémenter la logique avec le service layer
	c.JSON(http.StatusOK, gin.H{
		"services": []map[string]interface{}{
			{
				"name":   "api-gateway",
				"status": "up",
				"url":    "http://api-gateway:8000",
			},
			{
				"name":   "user-service",
				"status": "up",
				"url":    "http://user-service:8001",
			},
		},
	})
}

func GetServiceDetails(c *gin.Context) {
	name := c.Param("name")
	// TODO: Implémenter la logique
	c.JSON(http.StatusOK, gin.H{
		"name":         name,
		"status":       "up",
		"response_time": 25,
		"last_check":   "2024-01-01T12:00:00Z",
	})
}

func GetMetrics(c *gin.Context) {
	// TODO: Implémenter la logique
	c.JSON(http.StatusOK, gin.H{
		"total_requests": 1523,
		"error_rate":     2.3,
		"avg_response":   145,
		"uptime":         99.9,
	})
}
