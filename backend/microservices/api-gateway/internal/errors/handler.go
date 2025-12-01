package errors

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
)

func HandleError(c *gin.Context, err error) {
	if gwErr, ok := err.(*GatewayError); ok {
		c.JSON(gwErr.Code, gin.H{"error": gwErr.Message})
		return
	}

	log.Printf("Unexpected error: %v", err)
	c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
}
