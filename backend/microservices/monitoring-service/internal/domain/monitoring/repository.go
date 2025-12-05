package monitoring

import "time"

// Repository définit les opérations de persistance pour le monitoring
type Repository interface {
	// ServiceHealth operations
	CreateServiceHealth(health *ServiceHealth) error
	UpdateServiceHealth(health *ServiceHealth) error
	GetServiceHealthByName(serviceName string) (*ServiceHealth, error)
	GetAllServiceHealth() ([]*ServiceHealth, error)
	DeleteServiceHealth(serviceName string) error
	
	// Metrics operations
	CreateMetric(metric *Metric) error
	CreateMetricsBatch(metrics []*Metric) error // Insertion batch pour performance
	GetMetricsByService(serviceName string, from, to time.Time) ([]*Metric, error)
	GetMetricsByName(serviceName, metricName string, from, to time.Time) ([]*Metric, error)
	GetLatestMetrics(serviceName string, limit int) ([]*Metric, error)
	DeleteOldMetrics(before time.Time) (int64, error) // Nettoyage des anciennes métriques
	
	// PerformanceLog operations
	CreatePerformanceLog(log *PerformanceLog) error
	CreatePerformanceLogsBatch(logs []*PerformanceLog) error
	GetPerformanceLogs(serviceName string, from, to time.Time, limit int) ([]*PerformanceLog, error)
	GetPerformanceByEndpoint(serviceName, endpoint string, from, to time.Time) ([]*PerformanceLog, error)
	GetAverageResponseTime(serviceName string, from, to time.Time) (float64, error)
	GetPercentileResponseTime(serviceName string, percentile float64, from, to time.Time) (float64, error)
	DeleteOldPerformanceLogs(before time.Time) (int64, error)
	
	// ErrorLog operations
	CreateErrorLog(log *ErrorLog) error
	UpdateErrorLogOccurrences(id string, occurrences int, lastSeenAt time.Time) error
	ResolveErrorLog(id string, resolvedAt time.Time) error
	GetErrorLogs(serviceName string, isResolved bool, limit int) ([]*ErrorLog, error)
	GetErrorLogsByType(serviceName, errorType string, limit int) ([]*ErrorLog, error)
	GetErrorLogStats(serviceName string, from, to time.Time) (map[string]int, error)
	DeleteOldResolvedErrors(before time.Time) (int64, error)
	
	// Uptime operations
	CreateOrUpdateUptime(uptime *Uptime) error
	GetUptimeByDate(serviceName string, date time.Time) (*Uptime, error)
	GetUptimeHistory(serviceName string, from, to time.Time) ([]*Uptime, error)
	CalculateUptimePercentage(serviceName string, from, to time.Time) (float64, error)
	
	// Aggregated queries pour dashboard
	GetServiceMetricsSummary(serviceName string) (*ServiceMetricsSummary, error)
	GetAllServicesMetricsSummary() ([]*ServiceMetricsSummary, error)
	GetAggregatedMetrics(serviceName string, from, to time.Time) (*AggregatedMetrics, error)
	
	// Health check
	HealthCheck() error
}