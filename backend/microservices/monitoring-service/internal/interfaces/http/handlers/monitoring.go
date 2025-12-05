package handlers

import (
	"net/http"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/application/monitoring"
	"github.com/ai-elearning-platform/monitoring-service/pkg/errors"
	"github.com/ai-elearning-platform/monitoring-service/pkg/logger"
	"github.com/gin-gonic/gin"
)

type MonitoringHandler struct {
	service *monitoring.Service
}

func NewMonitoringHandler(service *monitoring.Service) *MonitoringHandler {
	return &MonitoringHandler{service: service}
}

// RegisterRoutes enregistre les routes de monitoring
func (h *MonitoringHandler) RegisterRoutes(r *gin.RouterGroup) {
	services := r.Group("/services")
	{
		services.POST("", h.RegisterService)
		services.GET("", h.GetAllServices)
		services.GET("/:serviceName", h.GetServiceHealth)
		services.POST("/:serviceName/check", h.CheckHealth)
		services.GET("/:serviceName/summary", h.GetServiceSummary)
	}
	
	metrics := r.Group("/metrics")
	{
		metrics.POST("", h.RecordMetric)
		metrics.POST("/batch", h.RecordMetricsBatch)
		metrics.GET("/:serviceName", h.GetMetrics)
	}
	
	performance := r.Group("/performance")
	{
		performance.POST("", h.RecordPerformance)
		performance.GET("/:serviceName/stats", h.GetPerformanceStats)
	}
	
	dashboard := r.Group("/dashboard")
	{
		dashboard.GET("/summary", h.GetDashboardSummary)
	}
}

// ===== Service Endpoints =====

// RegisterService godoc
// @Summary Register a new service
// @Tags monitoring
// @Accept json
// @Produce json
// @Param request body monitoring.RegisterServiceRequest true "Service registration"
// @Success 201 {object} monitoring.ServiceHealthResponse
// @Failure 400 {object} ErrorResponse
// @Failure 500 {object} ErrorResponse
// @Router /services [post]
func (h *MonitoringHandler) RegisterService(c *gin.Context) {
	var req monitoring.RegisterServiceRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		handleError(c, errors.BadRequest("invalid request body"))
		return
	}
	
	response, err := h.service.RegisterService(&req)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusCreated, response)
}

// GetServiceHealth godoc
// @Summary Get service health
// @Tags monitoring
// @Produce json
// @Param serviceName path string true "Service name"
// @Success 200 {object} monitoring.ServiceHealthResponse
// @Failure 404 {object} ErrorResponse
// @Router /services/{serviceName} [get]
func (h *MonitoringHandler) GetServiceHealth(c *gin.Context) {
	serviceName := c.Param("serviceName")
	
	response, err := h.service.GetServiceHealth(serviceName)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// GetAllServices godoc
// @Summary Get all services health
// @Tags monitoring
// @Produce json
// @Success 200 {array} monitoring.ServiceHealthResponse
// @Failure 500 {object} ErrorResponse
// @Router /services [get]
func (h *MonitoringHandler) GetAllServices(c *gin.Context) {
	responses, err := h.service.GetAllServicesHealth()
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"services": responses,
		"count":    len(responses),
	})
}

// CheckHealth godoc
// @Summary Perform health check on a service
// @Tags monitoring
// @Produce json
// @Param serviceName path string true "Service name"
// @Param url query string true "Service URL"
// @Success 200 {object} monitoring.HealthCheckResponse
// @Failure 400 {object} ErrorResponse
// @Router /services/{serviceName}/check [post]
func (h *MonitoringHandler) CheckHealth(c *gin.Context) {
	serviceName := c.Param("serviceName")
	url := c.Query("url")
	
	if url == "" {
		handleError(c, errors.BadRequest("url parameter is required"))
		return
	}
	
	response, err := h.service.CheckServiceHealth(serviceName, url)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// GetServiceSummary godoc
// @Summary Get service summary for dashboard
// @Tags monitoring
// @Produce json
// @Param serviceName path string true "Service name"
// @Success 200 {object} monitoring.ServiceSummaryResponse
// @Failure 404 {object} ErrorResponse
// @Router /services/{serviceName}/summary [get]
func (h *MonitoringHandler) GetServiceSummary(c *gin.Context) {
	serviceName := c.Param("serviceName")
	
	response, err := h.service.GetServiceSummary(serviceName)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// ===== Metrics Endpoints =====

// RecordMetric godoc
// @Summary Record a metric
// @Tags metrics
// @Accept json
// @Produce json
// @Param request body monitoring.RecordMetricRequest true "Metric data"
// @Success 201 {object} SuccessResponse
// @Failure 400 {object} ErrorResponse
// @Router /metrics [post]
func (h *MonitoringHandler) RecordMetric(c *gin.Context) {
	var req monitoring.RecordMetricRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		handleError(c, errors.BadRequest("invalid request body"))
		return
	}
	
	if err := h.service.RecordMetric(&req); err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"message": "metric recorded successfully",
	})
}

// RecordMetricsBatch godoc
// @Summary Record multiple metrics in batch
// @Tags metrics
// @Accept json
// @Produce json
// @Param request body monitoring.RecordMetricsBatchRequest true "Metrics batch"
// @Success 201 {object} SuccessResponse
// @Failure 400 {object} ErrorResponse
// @Router /metrics/batch [post]
func (h *MonitoringHandler) RecordMetricsBatch(c *gin.Context) {
	var req monitoring.RecordMetricsBatchRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		handleError(c, errors.BadRequest("invalid request body"))
		return
	}
	
	if err := h.service.RecordMetricsBatch(&req); err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"message": "metrics recorded successfully",
		"count":   len(req.Metrics),
	})
}

// GetMetrics godoc
// @Summary Get metrics for a service
// @Tags metrics
// @Produce json
// @Param serviceName path string true "Service name"
// @Param metricName query string false "Metric name filter"
// @Param from query string true "From timestamp (RFC3339)"
// @Param to query string true "To timestamp (RFC3339)"
// @Success 200 {object} monitoring.MetricsResponse
// @Failure 400 {object} ErrorResponse
// @Router /metrics/{serviceName} [get]
func (h *MonitoringHandler) GetMetrics(c *gin.Context) {
	serviceName := c.Param("serviceName")
	metricName := c.Query("metricName")
	fromStr := c.Query("from")
	toStr := c.Query("to")
	
	// Parse time parameters
	from, err := time.Parse(time.RFC3339, fromStr)
	if err != nil {
		handleError(c, errors.BadRequest("invalid 'from' timestamp format (use RFC3339)"))
		return
	}
	
	to, err := time.Parse(time.RFC3339, toStr)
	if err != nil {
		handleError(c, errors.BadRequest("invalid 'to' timestamp format (use RFC3339)"))
		return
	}
	
	req := &monitoring.GetMetricsRequest{
		ServiceName: serviceName,
		MetricName:  metricName,
		From:        from,
		To:          to,
	}
	
	response, err := h.service.GetMetrics(req)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// ===== Performance Endpoints =====

// RecordPerformance godoc
// @Summary Record performance metrics
// @Tags performance
// @Accept json
// @Produce json
// @Param request body monitoring.RecordPerformanceRequest true "Performance data"
// @Success 201 {object} SuccessResponse
// @Failure 400 {object} ErrorResponse
// @Router /performance [post]
func (h *MonitoringHandler) RecordPerformance(c *gin.Context) {
	var req monitoring.RecordPerformanceRequest
	
	if err := c.ShouldBindJSON(&req); err != nil {
		handleError(c, errors.BadRequest("invalid request body"))
		return
	}
	
	if err := h.service.RecordPerformance(&req); err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"message": "performance recorded successfully",
	})
}

// GetPerformanceStats godoc
// @Summary Get performance statistics
// @Tags performance
// @Produce json
// @Param serviceName path string true "Service name"
// @Param from query string true "From timestamp (RFC3339)"
// @Param to query string true "To timestamp (RFC3339)"
// @Success 200 {object} monitoring.PerformanceStatsResponse
// @Failure 400 {object} ErrorResponse
// @Router /performance/{serviceName}/stats [get]
func (h *MonitoringHandler) GetPerformanceStats(c *gin.Context) {
	serviceName := c.Param("serviceName")
	fromStr := c.Query("from")
	toStr := c.Query("to")
	
	from, err := time.Parse(time.RFC3339, fromStr)
	if err != nil {
		handleError(c, errors.BadRequest("invalid 'from' timestamp"))
		return
	}
	
	to, err := time.Parse(time.RFC3339, toStr)
	if err != nil {
		handleError(c, errors.BadRequest("invalid 'to' timestamp"))
		return
	}
	
	response, err := h.service.GetPerformanceStats(serviceName, from, to)
	if err != nil {
		handleError(c, err)
		return
	}
	
	c.JSON(http.StatusOK, response)
}

// ===== Dashboard Endpoints =====

// GetDashboardSummary godoc
// @Summary Get dashboard summary for all services
// @Tags dashboard
// @Produce json
// @Success 200 {object} DashboardResponse
// @Failure 500 {object} ErrorResponse
// @Router /dashboard/summary [get]
func (h *MonitoringHandler) GetDashboardSummary(c *gin.Context) {
	summaries, err := h.service.GetAllServicesSummary()
	if err != nil {
		handleError(c, err)
		return
	}
	
	// Calculer les statistiques globales
	totalServices := len(summaries)
	healthyServices := 0
	degradedServices := 0
	downServices := 0
	totalAlerts := 0
	
	for _, svc := range summaries {
		switch svc.Status {
		case "HEALTHY":
			healthyServices++
		case "DEGRADED":
			degradedServices++
		case "DOWN":
			downServices++
		}
		totalAlerts += svc.ActiveAlerts
	}
	
	c.JSON(http.StatusOK, gin.H{
		"services": summaries,
		"summary": gin.H{
			"total_services":    totalServices,
			"healthy_services":  healthyServices,
			"degraded_services": degradedServices,
			"down_services":     downServices,
			"total_alerts":      totalAlerts,
		},
		"timestamp": time.Now(),
	})
}

// ===== Helper Types =====

type SuccessResponse struct {
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
}

type ErrorResponse struct {
	Error   string                 `json:"error"`
	Code    string                 `json:"code,omitempty"`
	Details map[string]interface{} `json:"details,omitempty"`
}

type DashboardResponse struct {
	Services  interface{} `json:"services"`
	Summary   interface{} `json:"summary"`
	Timestamp time.Time   `json:"timestamp"`
}

// handleError gère les erreurs de manière centralisée
func handleError(c *gin.Context, err error) {
	appErr := errors.GetAppError(err)
	
	logger.Error("Request error",
		logger.String("path", c.Request.URL.Path),
		logger.String("method", c.Request.Method),
		logger.String("error", appErr.Message),
		logger.Err(err),
	)
	
	c.JSON(appErr.StatusCode, ErrorResponse{
		Error:   appErr.Message,
		Code:    string(appErr.Code),
		Details: appErr.Details,
	})
}