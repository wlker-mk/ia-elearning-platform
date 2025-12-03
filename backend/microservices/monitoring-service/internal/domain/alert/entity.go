package alert

import "time"

type Alert struct {
	ID        int64
	ServiceID int64
	Message   string
	Severity  string
	Status    string
	CreatedAt time.Time
	ResolvedAt *time.Time
}

const (
	SeverityInfo     = "info"
	SeverityWarning  = "warning"
	SeverityCritical = "critical"
	
	StatusOpen     = "open"
	StatusResolved = "resolved"
)
