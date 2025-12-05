package alert

import "time"
import "fmt"

// AlertSeverity niveaux de sévérité
type AlertSeverity string

const (
	SeverityInfo     AlertSeverity = "INFO"
	SeverityWarning  AlertSeverity = "WARNING"
	SeverityError    AlertSeverity = "ERROR"
	SeverityCritical AlertSeverity = "CRITICAL"
)

// AlertStatus états d'une alerte
type AlertStatus string

const (
	StatusOpen         AlertStatus = "OPEN"
	StatusAcknowledged AlertStatus = "ACKNOWLEDGED"
	StatusResolved     AlertStatus = "RESOLVED"
	StatusClosed       AlertStatus = "CLOSED"
)

// Alert représente une alerte système
type Alert struct {
	ID           string        `json:"id" db:"id"`
	Title        string        `json:"title" db:"title"`
	Description  string        `json:"description" db:"description"`
	Severity     AlertSeverity `json:"severity" db:"severity"`
	Status       AlertStatus   `json:"status" db:"status"`
	ServiceName  *string       `json:"serviceName,omitempty" db:"service_name"`
	MetricName   *string       `json:"metricName,omitempty" db:"metric_name"`
	Threshold    *float64      `json:"threshold,omitempty" db:"threshold"`
	ActualValue  *float64      `json:"actualValue,omitempty" db:"actual_value"`
	TriggeredAt  time.Time     `json:"triggeredAt" db:"triggered_at"`
	CreatedAt    time.Time     `json:"createdAt" db:"created_at"`
	UpdatedAt    time.Time     `json:"updatedAt" db:"updated_at"`
}

// AlertRule définit une règle de déclenchement d'alerte
type AlertRule struct {
	ID          string
	Name        string
	ServiceName string
	MetricName  string
	Condition   string  // "gt", "lt", "eq"
	Threshold   float64
	Severity    AlertSeverity
	Window      time.Duration // Fenêtre de temps pour évaluation
	Enabled     bool
}

// AlertStatistics statistiques des alertes
type AlertStatistics struct {
	TotalAlerts       int                      `json:"totalAlerts"`
	OpenAlerts        int                      `json:"openAlerts"`
	AcknowledgedAlerts int                     `json:"acknowledgedAlerts"`
	ResolvedAlerts    int                      `json:"resolvedAlerts"`
	BySeverity        map[AlertSeverity]int    `json:"bySeverity"`
	ByService         map[string]int           `json:"byService"`
	AverageResolutionTime time.Duration        `json:"averageResolutionTime"`
}

// IsActive vérifie si l'alerte est active
func (a *Alert) IsActive() bool {
	return a.Status == StatusOpen || a.Status == StatusAcknowledged
}

// IsCritical vérifie si l'alerte est critique
func (a *Alert) IsCritical() bool {
	return a.Severity == SeverityCritical
}

// DurationSinceTriggered retourne la durée depuis le déclenchement
func (a *Alert) DurationSinceTriggered() time.Duration {
	return time.Since(a.TriggeredAt)
}

// ShouldNotify détermine si une notification doit être envoyée
func (a *Alert) ShouldNotify() bool {
	// Notifier immédiatement les alertes critiques et erreurs
	if a.Severity == SeverityCritical || a.Severity == SeverityError {
		return true
	}
	
	// Pour les warnings, notifier si ouvert depuis plus de 5 minutes
	if a.Severity == SeverityWarning && a.DurationSinceTriggered() > 5*time.Minute {
		return true
	}
	
	return false
}

// EvaluateRule évalue si une règle doit déclencher une alerte
func (r *AlertRule) EvaluateRule(currentValue float64) bool {
	switch r.Condition {
	case "gt":
		return currentValue > r.Threshold
	case "lt":
		return currentValue < r.Threshold
	case "eq":
		return currentValue == r.Threshold
	case "gte":
		return currentValue >= r.Threshold
	case "lte":
		return currentValue <= r.Threshold
	default:
		return false
	}
}

// CreateAlertFromRule crée une alerte à partir d'une règle
func CreateAlertFromRule(rule *AlertRule, actualValue float64) *Alert {
	serviceName := rule.ServiceName
	metricName := rule.MetricName
	threshold := rule.Threshold
	
	return &Alert{
		Title:       rule.Name,
		Description: generateAlertDescription(rule, actualValue),
		Severity:    rule.Severity,
		Status:      StatusOpen,
		ServiceName: &serviceName,
		MetricName:  &metricName,
		Threshold:   &threshold,
		ActualValue: &actualValue,
		TriggeredAt: time.Now(),
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
}

func generateAlertDescription(rule *AlertRule, actualValue float64) string {
	return fmt.Sprintf(
		"Alert triggered for %s on service %s. Metric: %s %s %.2f (current: %.2f)",
		rule.Name,
		rule.ServiceName,
		rule.MetricName,
		rule.Condition,
		rule.Threshold,
		actualValue,
	)
}