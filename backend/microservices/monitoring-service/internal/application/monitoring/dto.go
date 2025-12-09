package monitoring

import (
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/domain/monitoring"
	"github.com/ai-elearning-platform/monitoring-service/pkg/errors"
)

// ===== Request DTOs =====

// RegisterServiceRequest requête pour enregistrer un service
type RegisterServiceRequest struct {
	ServiceName string `json:"serviceName" binding:"required"`
	URL         string `json:"url" binding:"required,url"`
	Description string `json:"description,omitempty"`
}

func (r *RegisterServiceRequest) Validate() error {
	if r.ServiceName == "" {
		return errors.BadRequest("service name is required")
	}
	if r.URL == "" {
		return errors.BadRequest("service URL is required")
	}
	return nil
}

// RecordMetricRequest requête pour enregistrer une métrique
type RecordMetricRequest struct {
	ServiceName string                 `json:"serviceName" binding:"required"`
	MetricName  string                 `json:"metricName" binding:"required"`
	Value       float64                `json:"value" binding:"required"`
	Unit        *string                `json:"unit,omitempty"`
	Labels      map[string]interface{} `json:"labels,omitempty"`
}

func (r *RecordMetricRequest) Validate() error {
	if r.ServiceName == "" {
		return errors.BadRequest("service name is required")
	}
	if r.MetricName == "" {
		return errors.BadRequest("metric name is required")
	}
	return nil
}

// RecordMetricsBatchRequest requête batch pour métriques
type RecordMetricsBatchRequest struct {
	Metrics []RecordMetricRequest `json:"metrics" binding:"required,dive"`
}

func (r *RecordMetricsBatchRequest) Validate() error {
	if len(r.Metrics) == 0 {
		return errors.BadRequest("at least one metric is required")
	}
	if len(r.Metrics) > 1000 {
		return errors.BadRequest("too many metrics (max 1000)")
	}
	
	for _, metric := range r.Metrics {
		if err := metric.Validate(); err != nil {
			return err
		}
	}
	return nil
}

// GetMetricsRequest requête pour récupérer des métriques
type GetMetricsRequest struct {
	ServiceName string    `json:"serviceName" binding:"required"`
	MetricName  string    `json:"metricName,omitempty"`
	From        time.Time `json:"from" binding:"required"`
	To          time.Time `json:"to" binding:"required"`
}

func (r *GetMetricsRequest) Validate() error {
	if r.ServiceName == "" {
		return errors.BadRequest("service name is required")
	}
	if r.From.IsZero() || r.To.IsZero() {
		return errors.BadRequest("time range is required")
	}
	if r.From.After(r.To) {
		return errors.InvalidTimeRange("from must be before to")
	}
	if r.To.Sub(r.From) > 30*24*time.Hour {
		return errors.InvalidTimeRange("time range cannot exceed 30 days")
	}
	return nil
}

// RecordPerformanceRequest requête pour enregistrer une performance
type RecordPerformanceRequest struct {
	ServiceName  string  `json:"serviceName" binding:"required"`
	Endpoint     string  `json:"endpoint" binding:"required"`
	Method       string  `json:"method" binding:"required"`
	StatusCode   int     `json:"statusCode" binding:"required"`
	ResponseTime int     `json:"responseTime" binding:"required"`
	UserID       *string `json:"userId,omitempty"`
	IPAddress    *string `json:"ipAddress,omitempty"`
}

func (r *RecordPerformanceRequest) Validate() error {
	if r.ServiceName == "" {
		return errors.BadRequest("service name is required")
	}
	if r.Endpoint == "" {
		return errors.BadRequest("endpoint is required")
	}
	if r.Method == "" {
		return errors.BadRequest("method is required")
	}
	if r.StatusCode < 100 || r.StatusCode > 599 {
		return errors.BadRequest("invalid status code")
	}
	if r.ResponseTime < 0 {
		return errors.BadRequest("response time cannot be negative")
	}
	return nil
}

// RecordErrorRequest requête pour enregistrer une erreur
type RecordErrorRequest struct {
	ServiceName  string  `json:"serviceName" binding:"required"`
	ErrorType    string  `json:"errorType" binding:"required"`
	ErrorMessage string  `json:"errorMessage" binding:"required"`
	StackTrace   *string `json:"stackTrace,omitempty"`
	Endpoint     *string `json:"endpoint,omitempty"`
	Method       *string `json:"method,omitempty"`
	UserID       *string `json:"userId,omitempty"`
}

func (r *RecordErrorRequest) Validate() error {
	if r.ServiceName == "" {
		return errors.BadRequest("service name is required")
	}
	if r.ErrorType == "" {
		return errors.BadRequest("error type is required")
	}
	if r.ErrorMessage == "" {
		return errors.BadRequest("error message is required")
	}
	return nil
}

// ===== Response DTOs =====

// ServiceHealthResponse réponse pour la santé d'un service
type ServiceHealthResponse struct {
	ID              string                  `json:"id"`
	ServiceName     string                  `json:"serviceName"`
	Status          monitoring.ServiceStatus `json:"status"`
	AvgResponseTime *float64                `json:"avgResponseTime,omitempty"`
	P95ResponseTime *float64                `json:"p95ResponseTime,omitempty"`
	P99ResponseTime *float64                `json:"p99ResponseTime,omitempty"`
	Uptime          *float64                `json:"uptime,omitempty"`
	RequestCount    int                     `json:"requestCount"`
	ErrorCount      int                     `json:"errorCount"`
	ErrorRate       float64                 `json:"errorRate"`
	CPUUsage        *float64                `json:"cpuUsage,omitempty"`
	MemoryUsage     *float64                `json:"memoryUsage,omitempty"`
	DiskUsage       *float64                `json:"diskUsage,omitempty"`
	LastCheckAt     time.Time               `json:"lastCheckAt"`
	CreatedAt       time.Time               `json:"createdAt"`
	UpdatedAt       time.Time               `json:"updatedAt"`
}

// HealthCheckResponse réponse d'un health check
type HealthCheckResponse struct {
	ServiceName  string                  `json:"serviceName"`
	Status       monitoring.ServiceStatus `json:"status"`
	ResponseTime int                     `json:"responseTime"`
	ErrorMessage string                  `json:"errorMessage,omitempty"`
	CheckedAt    time.Time               `json:"checkedAt"`
}

// MetricDTO DTO pour une métrique
type MetricDTO struct {
	ID          string                 `json:"id"`
	ServiceName string                 `json:"serviceName"`
	MetricName  string                 `json:"metricName"`
	Value       float64                `json:"value"`
	Unit        *string                `json:"unit,omitempty"`
	Labels      map[string]interface{} `json:"labels,omitempty"`
	Timestamp   time.Time              `json:"timestamp"`
}

// MetricsResponse réponse pour les métriques
type MetricsResponse struct {
	ServiceName string       `json:"serviceName"`
	Metrics     []*MetricDTO `json:"metrics"`
	From        time.Time    `json:"from"`
	To          time.Time    `json:"to"`
	Count       int          `json:"count"`
}

// PerformanceStatsResponse réponse pour les stats de performance
type PerformanceStatsResponse struct {
	ServiceName     string    `json:"serviceName"`
	AvgResponseTime float64   `json:"avgResponseTime"`
	P95ResponseTime float64   `json:"p95ResponseTime"`
	P99ResponseTime float64   `json:"p99ResponseTime"`
	From            time.Time `json:"from"`
	To              time.Time `json:"to"`
}

// ServiceSummaryResponse résumé d'un service pour le dashboard
type ServiceSummaryResponse struct {
	ServiceName       string                  `json:"serviceName"`
	Status            monitoring.ServiceStatus `json:"status"`
	CurrentRequests   int64                   `json:"currentRequests"`
	CurrentErrors     int64                   `json:"currentErrors"`
	ErrorRate         float64                 `json:"errorRate"`
	ResponseTimeAvg   float64                 `json:"responseTimeAvg"`
	ResponseTimeP95   float64                 `json:"responseTimeP95"`
	ResponseTimeP99   float64                 `json:"responseTimeP99"`
	CPUUsage          float64                 `json:"cpuUsage"`
	MemoryUsage       float64                 `json:"memoryUsage"`
	DiskUsage         float64                 `json:"diskUsage"`
	UptimePercentage  float64                 `json:"uptimePercentage"`
	LastCheckAt       time.Time               `json:"lastCheckAt"`
	ActiveAlerts      int                     `json:"activeAlerts"`
}

// ErrorLogResponse réponse pour un error log
type ErrorLogResponse struct {
	ID           string     `json:"id"`
	ServiceName  string     `json:"serviceName"`
	ErrorType    string     `json:"errorType"`
	ErrorMessage string     `json:"errorMessage"`
	Endpoint     *string    `json:"endpoint,omitempty"`
	Method       *string    `json:"method,omitempty"`
	Occurrences  int        `json:"occurrences"`
	FirstSeenAt  time.Time  `json:"firstSeenAt"`
	LastSeenAt   time.Time  `json:"lastSeenAt"`
	IsResolved   bool       `json:"isResolved"`
	ResolvedAt   *time.Time `json:"resolvedAt,omitempty"`
}

// UptimeResponse réponse pour l'uptime
type UptimeResponse struct {
	ServiceName       string                  `json:"serviceName"`
	Date              time.Time               `json:"date"`
	Status            monitoring.ServiceStatus `json:"status"`
	UptimeSeconds     int                     `json:"uptimeSeconds"`
	DowntimeSeconds   int                     `json:"downtimeSeconds"`
	UptimePercentage  float64                 `json:"uptimePercentage"`
	IncidentCount     int                     `json:"incidentCount"`
}

// ===== Mapping Functions =====

func toServiceHealthResponse(health *monitoring.ServiceHealth) *ServiceHealthResponse {
	return &ServiceHealthResponse{
		ID:              health.ID,
		ServiceName:     health.ServiceName,
		Status:          health.Status,
		AvgResponseTime: health.AvgResponseTime,
		P95ResponseTime: health.P95ResponseTime,
		P99ResponseTime: health.P99ResponseTime,
		Uptime:          health.Uptime,
		RequestCount:    health.RequestCount,
		ErrorCount:      health.ErrorCount,
		ErrorRate:       health.ErrorRate(),
		CPUUsage:        health.CPUUsage,
		MemoryUsage:     health.MemoryUsage,
		DiskUsage:       health.DiskUsage,
		LastCheckAt:     health.LastCheckAt,
		CreatedAt:       health.CreatedAt,
		UpdatedAt:       health.UpdatedAt,
	}
}

func toMetricDTO(metric *monitoring.Metric) *MetricDTO {
	return &MetricDTO{
		ID:          metric.ID,
		ServiceName: metric.ServiceName,
		MetricName:  metric.MetricName,
		Value:       metric.Value,
		Unit:        metric.Unit,
		Labels:      metric.Labels,
		Timestamp:   metric.Timestamp,
	}
}

func toMetricDTOs(metrics []*monitoring.Metric) []*MetricDTO {
	dtos := make([]*MetricDTO, len(metrics))
	for i, m := range metrics {
		dtos[i] = toMetricDTO(m)
	}
	return dtos
}

func toServiceSummaryResponse(summary *monitoring.ServiceMetricsSummary) *ServiceSummaryResponse {
	errorRate := float64(0)
	if summary.CurrentRequests > 0 {
		errorRate = float64(summary.CurrentErrors) / float64(summary.CurrentRequests) * 100
	}
	
	return &ServiceSummaryResponse{
		ServiceName:       summary.ServiceName,
		Status:            summary.Status,
		CurrentRequests:   summary.CurrentRequests,
		CurrentErrors:     summary.CurrentErrors,
		ErrorRate:         errorRate,
		ResponseTimeAvg:   summary.ResponseTimeAvg,
		ResponseTimeP95:   summary.ResponseTimeP95,
		ResponseTimeP99:   summary.ResponseTimeP99,
		CPUUsage:          summary.CPUUsage,
		MemoryUsage:       summary.MemoryUsage,
		DiskUsage:         summary.DiskUsage,
		UptimePercentage:  summary.UptimePercentage,
		LastCheckAt:       summary.LastCheckAt,
		ActiveAlerts:      summary.ActiveAlerts,
	}
}

func toErrorLogResponse(log *monitoring.ErrorLog) *ErrorLogResponse {
	return &ErrorLogResponse{
		ID:           log.ID,
		ServiceName:  log.ServiceName,
		ErrorType:    log.ErrorType,
		ErrorMessage: log.ErrorMessage,
		Endpoint:     log.Endpoint,
		Method:       log.Method,
		Occurrences:  log.Occurrences,
		FirstSeenAt:  log.FirstSeenAt,
		LastSeenAt:   log.LastSeenAt,
		IsResolved:   log.IsResolved,
		ResolvedAt:   log.ResolvedAt,
	}
}

func toUptimeResponse(uptime *monitoring.Uptime) *UptimeResponse {
	totalSeconds := uptime.UptimeSeconds + uptime.DowntimeSeconds
	uptimePercentage := 0.0
	if totalSeconds > 0 {
		uptimePercentage = float64(uptime.UptimeSeconds) / float64(totalSeconds) * 100
	}
	return &UptimeResponse{
		ServiceName:      uptime.ServiceName,
		Date:             uptime.Date,
		Status:           uptime.Status,
		UptimeSeconds:    uptime.UptimeSeconds,
		DowntimeSeconds:  uptime.DowntimeSeconds,
		UptimePercentage: uptimePercentage,
		IncidentCount:    uptime.IncidentCount,
	}
}