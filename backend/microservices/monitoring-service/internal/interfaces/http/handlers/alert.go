package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func GetAlerts(c *gin.Context) {
	// TODO: Implémenter la logique
	c.JSON(http.StatusOK, gin.H{
		"alerts": []map[string]interface{}{
			{
				"id":       1,
				"service":  "payment-service",
				"message":  "Service is down",
				"severity": "critical",
			},
		},
	})
}

func CreateAlert(c *gin.Context) {
	// TODO: Implémenter la logique
	c.JSON(http.StatusCreated, gin.H{
		"message": "alert created",
		"id":      123,
	})
}

func GetAlert(c *gin.Context) {
	id := c.Param("id")
	// TODO: Implémenter la logique
	c.JSON(http.StatusOK, gin.H{
		"id":       id,
		"service":  "user-service",
		"message":  "High CPU usage",
		"severity": "warning",
	})
}
