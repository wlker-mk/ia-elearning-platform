package metrics

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func Handler(metrics *Metrics) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"requests": metrics.requests,
			"errors":   metrics.errors,
		})
	}
}
