package alert

import (
	"fmt"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/domain/alert"
	"github.com/ai-elearning-platform/monitoring-service/pkg/errors"
)

// ===== Request DTOs =====

// CreateAlertRequest requête pour créer une alerte
type CreateAlertRequest struct {
	Title       string              `json:"title" binding:"required"`
	Description string              `json:"description" binding:"required"`
	Severity    alert.AlertSeverity `json:"severity" binding:"required"`
	ServiceName *string             `json:"serviceName,omitempty"`
	MetricName  *string             `json:"metricName,omitempty"`
	Threshold   *float64            `json:"threshold,omitempty"`
	ActualValue *float64            `json:"actualValue,omitempty"`
}

func (r *CreateAlertRequest) Validate() error {
	if r.Title == "" {
		return errors.BadRequest("title is required")
	}
	if r.Description == "" {
		return errors.BadRequest("description is required")
	}
	if !isValidSeverity(r.Severity) {
		return errors.InvalidAlert("invalid severity level")
	}
	return nil
}

// UpdateAlertRequest requête pour mettre à jour une alerte
type UpdateAlertRequest struct {
	Title       *string              `json:"title,omitempty"`
	Description *string              `json:"description,omitempty"`
	Severity    *alert.AlertSeverity `json:"severity,omitempty"`
}

func (r *UpdateAlertRequest) Validate() error {
	if r.Severity != nil && !isValidSeverity(*r.Severity) {
		return errors.InvalidAlert("invalid severity level")
	}
	return nil
}

// GetAlertsRequest requête pour récupérer des alertes
type GetAlertsRequest struct {
	Status      string `json:"status,omitempty"`
	Severity    string `json:"severity,omitempty"`
	ServiceName string `json:"serviceName,omitempty"`
	Limit       int    `json:"limit"`
	Offset      int    `json:"offset"`
}

func (r *GetAlertsRequest) Validate() error {
	if r.Limit <= 0 {
		r.Limit = 50 // Default
	}
	if r.Limit > 1000 {
		return errors.BadRequest("limit cannot exceed 1000")
	}
	if r.Offset < 0 {
		r.Offset = 0
	}

	if r.Status != "" && !isValidStatus(alert.AlertStatus(r.Status)) {
		return errors.InvalidAlert("invalid status")
	}
	if r.Severity != "" && !isValidSeverity(alert.AlertSeverity(r.Severity)) {
		return errors.InvalidAlert("invalid severity")
	}

	return nil
}

// CreateAlertRuleRequest requête pour créer une règle d'alerte
type CreateAlertRuleRequest struct {
	Name          string              `json:"name" binding:"required"`
	ServiceName   string              `json:"serviceName" binding:"required"`
	MetricName    string              `json:"metricName" binding:"required"`
	Condition     string              `json:"condition" binding:"required"`
	Threshold     float64             `json:"threshold" binding:"required"`
	Severity      alert.AlertSeverity `json:"severity" binding:"required"`
	WindowMinutes int                 `json:"windowMinutes" binding:"required"`
	Enabled       bool                `json:"enabled"`
}

func (r *CreateAlertRuleRequest) Validate() error {
	if r.Name == "" {
		return errors.BadRequest("rule name is required")
	}
	if r.ServiceName == "" {
		return errors.BadRequest("service name is required")
	}
	if r.MetricName == "" {
		return errors.BadRequest("metric name is required")
	}
	if !isValidCondition(r.Condition) {
		return errors.InvalidAlert("invalid condition (must be: gt, lt, eq, gte, lte)")
	}
	if !isValidSeverity(r.Severity) {
		return errors.InvalidAlert("invalid severity level")
	}
	if r.WindowMinutes <= 0 {
		return errors.BadRequest("window must be positive")
	}
	return nil
}

// ===== Response DTOs =====

// AlertResponse réponse pour une alerte
type AlertResponse struct {
	ID          string              `json:"id"`
	Title       string              `json:"title"`
	Description string              `json:"description"`
	Severity    alert.AlertSeverity `json:"severity"`
	Status      alert.AlertStatus   `json:"status"`
	ServiceName *string             `json:"serviceName,omitempty"`
	MetricName  *string             `json:"metricName,omitempty"`
	Threshold   *float64            `json:"threshold,omitempty"`
	ActualValue *float64            `json:"actualValue,omitempty"`
	TriggeredAt time.Time           `json:"triggeredAt"`
	Duration    string              `json:"duration"`
	IsActive    bool                `json:"isActive"`
	IsCritical  bool                `json:"isCritical"`
	CreatedAt   time.Time           `json:"createdAt"`
	UpdatedAt   time.Time           `json:"updatedAt"`
}

// AlertListResponse réponse pour une liste d'alertes
type AlertListResponse struct {
	Alerts []*AlertResponse `json:"alerts"`
	Total  int              `json:"total"`
	Limit  int              `json:"limit"`
	Offset int              `json:"offset"`
}

// AlertStatisticsResponse réponse pour les statistiques
type AlertStatisticsResponse struct {
	TotalAlerts           int                         `json:"totalAlerts"`
	OpenAlerts            int                         `json:"openAlerts"`
	AcknowledgedAlerts    int                         `json:"acknowledgedAlerts"`
	ResolvedAlerts        int                         `json:"resolvedAlerts"`
	BySeverity            map[alert.AlertSeverity]int `json:"bySeverity"`
	ByService             map[string]int              `json:"byService"`
	AverageResolutionTime string                      `json:"averageResolutionTime"`
}

// AlertSummaryResponse résumé des alertes
type AlertSummaryResponse struct {
	TotalOpen         int `json:"totalOpen"`
	TotalAcknowledged int `json:"totalAcknowledged"`
	TotalResolved     int `json:"totalResolved"`
	CriticalCount     int `json:"criticalCount"`
	ErrorCount        int `json:"errorCount"`
	WarningCount      int `json:"warningCount"`
	InfoCount         int `json:"infoCount"`
}

// AlertRuleResponse réponse pour une règle d'alerte
type AlertRuleResponse struct {
	ID          string              `json:"id"`
	Name        string              `json:"name"`
	ServiceName string              `json:"serviceName"`
	MetricName  string              `json:"metricName"`
	Condition   string              `json:"condition"`
	Threshold   float64             `json:"threshold"`
	Severity    alert.AlertSeverity `json:"severity"`
	Window      string              `json:"window"`
	Enabled     bool                `json:"enabled"`
	CreatedAt   time.Time           `json:"createdAt"`
	UpdatedAt   time.Time           `json:"updatedAt"`
}

// ===== Mapping Functions =====

func toAlertResponse(a *alert.Alert) *AlertResponse {
	duration := formatDuration(a.DurationSinceTriggered())

	return &AlertResponse{
		ID:          a.ID,
		Title:       a.Title,
		Description: a.Description,
		Severity:    a.Severity,
		Status:      a.Status,
		ServiceName: a.ServiceName,
		MetricName:  a.MetricName,
		Threshold:   a.Threshold,
		ActualValue: a.ActualValue,
		TriggeredAt: a.TriggeredAt,
		Duration:    duration,
		IsActive:    a.IsActive(),
		IsCritical:  a.IsCritical(),
		CreatedAt:   a.CreatedAt,
		UpdatedAt:   a.UpdatedAt,
	}
}

func toAlertStatisticsResponse(stats *alert.AlertStatistics) *AlertStatisticsResponse {
	return &AlertStatisticsResponse{
		TotalAlerts:           stats.TotalAlerts,
		OpenAlerts:            stats.OpenAlerts,
		AcknowledgedAlerts:    stats.AcknowledgedAlerts,
		ResolvedAlerts:        stats.ResolvedAlerts,
		BySeverity:            stats.BySeverity,
		ByService:             stats.ByService,
		AverageResolutionTime: formatDuration(stats.AverageResolutionTime),
	}
}

func toAlertRuleResponse(rule *alert.AlertRule) *AlertRuleResponse {
	return &AlertRuleResponse{
		ID:          rule.ID,
		Name:        rule.Name,
		ServiceName: rule.ServiceName,
		MetricName:  rule.MetricName,
		Condition:   rule.Condition,
		Threshold:   rule.Threshold,
		Severity:    rule.Severity,
		Window:      formatDuration(rule.Window),
		Enabled:     rule.Enabled,
	}
}

// ===== Validation Helpers =====

func isValidSeverity(severity alert.AlertSeverity) bool {
	switch severity {
	case alert.SeverityInfo, alert.SeverityWarning, alert.SeverityError, alert.SeverityCritical:
		return true
	default:
		return false
	}
}

func isValidStatus(status alert.AlertStatus) bool {
	switch status {
	case alert.StatusOpen, alert.StatusAcknowledged, alert.StatusResolved, alert.StatusClosed:
		return true
	default:
		return false
	}
}

func isValidCondition(condition string) bool {
	switch condition {
	case "gt", "lt", "eq", "gte", "lte":
		return true
	default:
		return false
	}
}

// ===== Format Helpers =====

func formatDuration(d time.Duration) string {
	if d < time.Minute {
		return "less than a minute"
	} else if d < time.Hour {
		minutes := int(d.Minutes())
		if minutes == 1 {
			return "1 minute"
		}
		return fmt.Sprintf("%d minutes", minutes)
	} else if d < 24*time.Hour {
		hours := int(d.Hours())
		if hours == 1 {
			return "1 hour"
		}
		return fmt.Sprintf("%d hours", hours)
	} else {
		days := int(d.Hours() / 24)
		if days == 1 {
			return "1 day"
		}
		return fmt.Sprintf("%d days", days)
	}
}
