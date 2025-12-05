package alert

import "time"

// Repository définit les opérations de persistance pour les alertes
type Repository interface {
	// CRUD operations
	Create(alert *Alert) error
	Update(alert *Alert) error
	GetByID(id string) (*Alert, error)
	Delete(id string) error
	
	// Query operations
	GetAll(limit, offset int) ([]*Alert, error)
	GetByStatus(status AlertStatus, limit int) ([]*Alert, error)
	GetBySeverity(severity AlertSeverity, limit int) ([]*Alert, error)
	GetByService(serviceName string, limit int) ([]*Alert, error)
	GetActiveAlerts() ([]*Alert, error)
	GetCriticalAlerts() ([]*Alert, error)
	
	// Status management
	Acknowledge(id string) error
	Resolve(id string) error
	Close(id string) error
	
	// Statistics
	GetStatistics(from, to time.Time) (*AlertStatistics, error)
	CountByStatus(status AlertStatus) (int64, error)
	CountBySeverity(severity AlertSeverity) (int64, error)
	GetAverageResolutionTime(from, to time.Time) (time.Duration, error)
	
	// Cleanup
	DeleteOldResolvedAlerts(before time.Time) (int64, error)
	
	// Alert Rules (si nécessaire)
	CreateRule(rule *AlertRule) error
	GetRulesByService(serviceName string) ([]*AlertRule, error)
	GetEnabledRules() ([]*AlertRule, error)
	UpdateRule(rule *AlertRule) error
	DeleteRule(id string) error
}