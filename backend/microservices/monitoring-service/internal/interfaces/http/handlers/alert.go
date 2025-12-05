package handlers

import (
	"net/http"
	"time"
	"strconv"

	"github.com/ai-elearning-platform/monitoring-service/internal/application/alert"
	"github.com/ai-elearning-platform/monitoring-service/pkg/errors"
	"github.com/gin-gonic/gin"
)

type AlertHandler struct {
	service *alert.Service
}

func NewAlertHandler(service *alert.Service) *AlertHandler {
	return &AlertHandler{service: service}
}

// RegisterRoutes enregistre les routes d'alertes
func (h *AlertHandler) RegisterRoutes(r *gin.RouterGroup) {
	alerts := r.Group("/alerts")
	{
		alerts.POST("", h.CreateAlert)
		alerts.GET("", h.GetAlerts)
		alerts.GET("/:id", h.GetAlert)
		alerts.PUT("/:id", h.UpdateAlert)
		alerts.DELETE("/:id", h.DeleteAlert)
		
		// Status management
		alerts.POST("/:id/acknowledge", h.AcknowledgeAlert)
		alerts.POST("/:id/resolve", h.ResolveAlert)
		alerts.POST("/:id/close", h.CloseAlert)
		
		// Special queries
		alerts.GET("/active", h.GetActiveAlerts)
		alerts.GET("/critical", h.GetCriticalAlerts)
		alerts.GET("/statistics", h.GetStatistics)
		alerts.GET("/summary", h.GetSummary)
	}
}

// ===== CRUD Operations =====

// CreateAlert godoc
// @Summary Create a new alert
// @Tags alerts
// @Accept json
// @Produce json
// @Param request body alert.CreateAlertRequest true "Alert data"
// @Success 201 {object} alert.AlertResponse
// @Failure 400 {object} ErrorResponse
// @Router /alerts [post]
func (h *AlertHandler) CreateAlert(c *gin.Context) {
	var req alert.CreateAlertRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		handleError(c, errors.BadRequest("invalid request body"))
		return
	}
	
	response, err := h.service.CreateAlert(&req)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusCreated, response)
}

// GetAlert godoc
// @Summary Get alert by ID
// @Tags alerts
// @Produce json
// @Param id path string true "Alert ID"
// @Success 200 {object} alert.AlertResponse
// @Failure 404 {object} ErrorResponse
// @Router /alerts/{id} [get]
func (h *AlertHandler) GetAlert(c *gin.Context) {
	id := c.Param("id")
	
	response, err := h.service.GetAlert(id)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// GetAlerts godoc
// @Summary Get alerts with filters
// @Tags alerts
// @Produce json
// @Param status query string false "Filter by status"
// @Param severity query string false "Filter by severity"
// @Param serviceName query string false "Filter by service"
// @Param limit query int false "Limit (default 50)"
// @Param offset query int false "Offset (default 0)"
// @Success 200 {object} alert.AlertListResponse
// @Failure 400 {object} ErrorResponse
// @Router /alerts [get]
func (h *AlertHandler) GetAlerts(c *gin.Context) {
	req := &alert.GetAlertsRequest{
		Status:      c.Query("status"),
		Severity:    c.Query("severity"),
		ServiceName: c.Query("serviceName"),
		Limit:       50,
		Offset:      0,
	}
	
	// Parse limit et offset
	if limit := c.Query("limit"); limit != "" {
		if l, err := strconv.Atoi(limit); err == nil {
			req.Limit = l
		}
	}
	
	if offset := c.Query("offset"); offset != "" {
		if o, err := strconv.Atoi(offset); err == nil {
			req.Offset = o
		}
	}
	
	response, err := h.service.GetAlerts(req)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// GetActiveAlerts godoc
// @Summary Get all active alerts
// @Tags alerts
// @Produce json
// @Success 200 {array} alert.AlertResponse
// @Failure 500 {object} ErrorResponse
// @Router /alerts/active [get]
func (h *AlertHandler) GetActiveAlerts(c *gin.Context) {
	responses, err := h.service.GetActiveAlerts()
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"alerts": responses,
		"count":  len(responses),
	})
}

// GetCriticalAlerts godoc
// @Summary Get all critical alerts
// @Tags alerts
// @Produce json
// @Success 200 {array} alert.AlertResponse
// @Failure 500 {object} ErrorResponse
// @Router /alerts/critical [get]
func (h *AlertHandler) GetCriticalAlerts(c *gin.Context) {
	responses, err := h.service.GetCriticalAlerts()
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"alerts": responses,
		"count":  len(responses),
	})
}

// UpdateAlert godoc
// @Summary Update an alert
// @Tags alerts
// @Accept json
// @Produce json
// @Param id path string true "Alert ID"
// @Param request body alert.UpdateAlertRequest true "Updated alert data"
// @Success 200 {object} alert.AlertResponse
// @Failure 400 {object} ErrorResponse
// @Failure 404 {object} ErrorResponse
// @Router /alerts/{id} [put]
func (h *AlertHandler) UpdateAlert(c *gin.Context) {
	id := c.Param("id")
	var req alert.UpdateAlertRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		handleError(c, errors.BadRequest("invalid request body"))
		return
	}
	
	response, err := h.service.UpdateAlert(id, &req)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// DeleteAlert godoc
// @Summary Delete an alert
// @Tags alerts
// @Produce json
// @Param id path string true "Alert ID"
// @Success 204
// @Failure 404 {object} ErrorResponse
// @Router /alerts/{id} [delete]
func (h *AlertHandler) DeleteAlert(c *gin.Context) {
	id := c.Param("id")
	
	if err := h.service.DeleteAlert(id); err != nil {
		handleError(c, err)
		return
	}
	
	c.Status(http.StatusNoContent)
}

// ===== Status Management =====

// AcknowledgeAlert godoc
// @Summary Acknowledge an alert
// @Tags alerts
// @Produce json
// @Param id path string true "Alert ID"
// @Success 200 {object} alert.AlertResponse
// @Failure 404 {object} ErrorResponse
// @Router /alerts/{id}/acknowledge [post]
func (h *AlertHandler) AcknowledgeAlert(c *gin.Context) {
	id := c.Param("id")
	
	response, err := h.service.AcknowledgeAlert(id)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// ResolveAlert godoc
// @Summary Resolve an alert
// @Tags alerts
// @Produce json
// @Param id path string true "Alert ID"
// @Success 200 {object} alert.AlertResponse
// @Failure 404 {object} ErrorResponse
// @Router /alerts/{id}/resolve [post]
func (h *AlertHandler) ResolveAlert(c *gin.Context) {
	id := c.Param("id")
	
	response, err := h.service.ResolveAlert(id)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// CloseAlert godoc
// @Summary Close an alert
// @Tags alerts
// @Produce json
// @Param id path string true "Alert ID"
// @Success 200 {object} alert.AlertResponse
// @Failure 404 {object} ErrorResponse
// @Router /alerts/{id}/close [post]
func (h *AlertHandler) CloseAlert(c *gin.Context) {
	id := c.Param("id")
	
	response, err := h.service.CloseAlert(id)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// ===== Statistics =====

// GetStatistics godoc
// @Summary Get alert statistics
// @Tags alerts
// @Produce json
// @Param from query string false "From timestamp (RFC3339)"
// @Param to query string false "To timestamp (RFC3339)"
// @Success 200 {object} alert.AlertStatisticsResponse
// @Failure 400 {object} ErrorResponse
// @Router /alerts/statistics [get]
func (h *AlertHandler) GetStatistics(c *gin.Context) {
	fromStr := c.Query("from")
	toStr := c.Query("to")
	
	// Default: dernières 24h
	from := time.Now().Add(-24 * time.Hour)
	to := time.Now()
	
	if fromStr != "" {
		if parsed, err := time.Parse(time.RFC3339, fromStr); err == nil {
			from = parsed
		}
	}
	
	if toStr != "" {
		if parsed, err := time.Parse(time.RFC3339, toStr); err == nil {
			to = parsed
		}
	}
	
	response, err := h.service.GetAlertStatistics(from, to)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// GetSummary godoc
// @Summary Get alert summary
// @Tags alerts
// @Produce json
// @Success 200 {object} alert.AlertSummaryResponse
// @Failure 500 {object} ErrorResponse
// @Router /alerts/summary [get]
func (h *AlertHandler) GetSummary(c *gin.Context) {
	response, err := h.service.GetAlertSummary()
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}