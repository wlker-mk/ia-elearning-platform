package monitoring

import (
	"encoding/json"
	"time"
)

// ServiceStatus représente l'état d'un service
type ServiceStatus string

const (
	StatusHealthy     ServiceStatus = "HEALTHY"
	StatusDegraded    ServiceStatus = "DEGRADED"
	StatusDown        ServiceStatus = "DOWN"
	StatusMaintenance ServiceStatus = "MAINTENANCE"
)

// ServiceHealth représente la santé complète d'un service
type ServiceHealth struct {
	ID              string        `json:"id" db:"id"`
	ServiceName     string        `json:"serviceName" db:"service_name"`
	Status          ServiceStatus `json:"status" db:"status"`
	AvgResponseTime *float64      `json:"avgResponseTime,omitempty" db:"avg_response_time"`
	P95ResponseTime *float64      `json:"p95ResponseTime,omitempty" db:"p95_response_time"`
	P99ResponseTime *float64      `json:"p99ResponseTime,omitempty" db:"p99_response_time"`
	Uptime          *float64      `json:"uptime,omitempty" db:"uptime"`
	Downtime        *int          `json:"downtime,omitempty" db:"downtime"`
	RequestCount    int           `json:"requestCount" db:"request_count"`
	ErrorCount      int           `json:"errorCount" db:"error_count"`
	CPUUsage        *float64      `json:"cpuUsage,omitempty" db:"cpu_usage"`
	MemoryUsage     *float64      `json:"memoryUsage,omitempty" db:"memory_usage"`
	DiskUsage       *float64      `json:"diskUsage,omitempty" db:"disk_usage"`
	LastCheckAt     time.Time     `json:"lastCheckAt" db:"last_check_at"`
	CreatedAt       time.Time     `json:"createdAt" db:"created_at"`
	UpdatedAt       time.Time     `json:"updatedAt" db:"updated_at"`
}

// Metric représente une métrique de monitoring
type Metric struct {
	ID          string                 `json:"id" db:"id"`
	ServiceName string                 `json:"serviceName" db:"service_name"`
	MetricName  string                 `json:"metricName" db:"metric_name"`
	Value       float64                `json:"value" db:"value"`
	Unit        *string                `json:"unit,omitempty" db:"unit"`
	Labels      map[string]interface{} `json:"labels,omitempty" db:"labels"`
	Timestamp   time.Time              `json:"timestamp" db:"timestamp"`
}

// MetricLabels gère la sérialisation JSON des labels
type MetricLabels map[string]interface{}

func (m MetricLabels) Value() (interface{}, error) {
	return json.Marshal(m)
}

func (m *MetricLabels) Scan(value interface{}) error {
	if value == nil {
		*m = make(map[string]interface{})
		return nil
	}
	
	bytes, ok := value.([]byte)
	if !ok {
		return nil
	}
	
	return json.Unmarshal(bytes, m)
}

// PerformanceLog enregistre les performances d'un endpoint
type PerformanceLog struct {
	ID           string    `json:"id" db:"id"`
	ServiceName  string    `json:"serviceName" db:"service_name"`
	Endpoint     string    `json:"endpoint" db:"endpoint"`
	Method       string    `json:"method" db:"method"`
	StatusCode   int       `json:"statusCode" db:"status_code"`
	ResponseTime int       `json:"responseTime" db:"response_time"` // en ms
	UserID       *string   `json:"userId,omitempty" db:"user_id"`
	IPAddress    *string   `json:"ipAddress,omitempty" db:"ip_address"`
	Timestamp    time.Time `json:"timestamp" db:"timestamp"`
}

// ErrorLog enregistre les erreurs applicatives
type ErrorLog struct {
	ID           string     `json:"id" db:"id"`
	ServiceName  string     `json:"serviceName" db:"service_name"`
	ErrorType    string     `json:"errorType" db:"error_type"`
	ErrorMessage string     `json:"errorMessage" db:"error_message"`
	StackTrace   *string    `json:"stackTrace,omitempty" db:"stack_trace"`
	Endpoint     *string    `json:"endpoint,omitempty" db:"endpoint"`
	Method       *string    `json:"method,omitempty" db:"method"`
	UserID       *string    `json:"userId,omitempty" db:"user_id"`
	Occurrences  int        `json:"occurrences" db:"occurrences"`
	FirstSeenAt  time.Time  `json:"firstSeenAt" db:"first_seen_at"`
	LastSeenAt   time.Time  `json:"lastSeenAt" db:"last_seen_at"`
	IsResolved   bool       `json:"isResolved" db:"is_resolved"`
	ResolvedAt   *time.Time `json:"resolvedAt,omitempty" db:"resolved_at"`
	CreatedAt    time.Time  `json:"createdAt" db:"created_at"`
}

// Uptime représente les statistiques d'uptime quotidiennes
type Uptime struct {
	ID              string        `json:"id" db:"id"`
	ServiceName     string        `json:"serviceName" db:"service_name"`
	Date            time.Time     `json:"date" db:"date"`
	Status          ServiceStatus `json:"status" db:"status"`
	UptimeSeconds   int           `json:"uptimeSeconds" db:"uptime_seconds"`
	DowntimeSeconds int           `json:"downtimeSeconds" db:"downtime_seconds"`
	IncidentCount   int           `json:"incidentCount" db:"incident_count"`
	CreatedAt       time.Time     `json:"createdAt" db:"created_at"`
}

// HealthCheckResult résultat d'un health check
type HealthCheckResult struct {
	ServiceName  string
	IsHealthy    bool
	ResponseTime int64 // en ms
	ErrorMessage string
	CheckedAt    time.Time
}

// AggregatedMetrics métriques agrégées pour dashboard
type AggregatedMetrics struct {
	ServiceName     string    `json:"serviceName"`
	TotalRequests   int64     `json:"totalRequests"`
	TotalErrors     int64     `json:"totalErrors"`
	ErrorRate       float64   `json:"errorRate"`
	AvgResponseTime float64   `json:"avgResponseTime"`
	P95ResponseTime float64   `json:"p95ResponseTime"`
	P99ResponseTime float64   `json:"p99ResponseTime"`
	UptimePercent   float64   `json:"uptimePercent"`
	Period          string    `json:"period"`
	Timestamp       time.Time `json:"timestamp"`
}

// ServiceMetricsSummary résumé des métriques d'un service
type ServiceMetricsSummary struct {
	ServiceName       string        `json:"serviceName"`
	Status            ServiceStatus `json:"status"`
	CurrentRequests   int64         `json:"currentRequests"`
	CurrentErrors     int64         `json:"currentErrors"`
	ResponseTimeAvg   float64       `json:"responseTimeAvg"`
	ResponseTimeP95   float64       `json:"responseTimeP95"`
	ResponseTimeP99   float64       `json:"responseTimeP99"`
	CPUUsage          float64       `json:"cpuUsage"`
	MemoryUsage       float64       `json:"memoryUsage"`
	DiskUsage         float64       `json:"diskUsage"`
	UptimePercentage  float64       `json:"uptimePercentage"`
	LastCheckAt       time.Time     `json:"lastCheckAt"`
	ActiveAlerts      int           `json:"activeAlerts"`
}

// IsHealthy vérifie si le service est en bonne santé
func (sh *ServiceHealth) IsHealthy() bool {
	return sh.Status == StatusHealthy
}

// ErrorRate calcule le taux d'erreur
func (sh *ServiceHealth) ErrorRate() float64 {
	if sh.RequestCount == 0 {
		return 0
	}
	return float64(sh.ErrorCount) / float64(sh.RequestCount) * 100
}

// UptimePercentage calcule le pourcentage d'uptime
func (u *Uptime) UptimePercentage() float64 {
	total := u.UptimeSeconds + u.DowntimeSeconds
	if total == 0 {
		return 100.0
	}
	return float64(u.UptimeSeconds) / float64(total) * 100
}