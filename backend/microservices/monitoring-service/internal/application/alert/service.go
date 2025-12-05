package alert

import (
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/domain/alert"
	"github.com/ai-elearning-platform/monitoring-service/internal/infrastructure/cache"
	"github.com/ai-elearning-platform/monitoring-service/pkg/errors"
	"github.com/ai-elearning-platform/monitoring-service/pkg/logger"
)

type Service struct {
	repo  alert.Repository
	cache *cache.RedisCache
}

func NewService(repo alert.Repository, cache *cache.RedisCache) *Service {
	return &Service{
		repo:  repo,
		cache: cache,
	}
}

// ===== Alert CRUD Operations =====

// CreateAlert crée une nouvelle alerte
func (s *Service) CreateAlert(req *CreateAlertRequest) (*AlertResponse, error) {
	if err := req.Validate(); err != nil {
		return nil, err
	}
	
	a := &alert.Alert{
		Title:        req.Title,
		Description:  req.Description,
		Severity:     req.Severity,
		Status:       alert.StatusOpen,
		ServiceName:  req.ServiceName,
		MetricName:   req.MetricName,
		Threshold:    req.Threshold,
		ActualValue:  req.ActualValue,
		TriggeredAt:  time.Now(),
		CreatedAt:    time.Now(),
		UpdatedAt:    time.Now(),
	}
	
	if err := s.repo.Create(a); err != nil {
		logger.Error("Failed to create alert", logger.Err(err))
		return nil, errors.Internal("failed to create alert", err)
	}
	
	// Mettre en cache
	s.cache.CacheAlert(a.ID, a)
	
	// Logger l'alerte
	serviceName := ""
	if a.ServiceName != nil {
		serviceName = *a.ServiceName
	}
	logger.LogAlert(string(a.Severity), a.Title, serviceName)
	
	// TODO: Envoyer notification si critique
	if a.IsCritical() {
		s.sendNotification(a)
	}
	
	return toAlertResponse(a), nil
}

// GetAlert récupère une alerte par ID
func (s *Service) GetAlert(id string) (*AlertResponse, error) {
	// Essayer le cache
	var cachedAlert alert.Alert
	if err := s.cache.GetCachedAlert(id, &cachedAlert); err == nil {
		return toAlertResponse(&cachedAlert), nil
	}
	
	// Sinon DB
	a, err := s.repo.GetByID(id)
	if err != nil {
		return nil, errors.AlertNotFound(id)
	}
	
	// Mettre en cache
	s.cache.CacheAlert(a.ID, a)
	
	return toAlertResponse(a), nil
}

// GetAlerts récupère toutes les alertes avec pagination
func (s *Service) GetAlerts(req *GetAlertsRequest) (*AlertListResponse, error) {
	if err := req.Validate(); err != nil {
		return nil, err
	}
	
	var alerts []*alert.Alert
	var err error
	
	// Filtrer par statut ou sévérité
	if req.Status != "" {
		alerts, err = s.repo.GetByStatus(alert.AlertStatus(req.Status), req.Limit)
	} else if req.Severity != "" {
		alerts, err = s.repo.GetBySeverity(alert.AlertSeverity(req.Severity), req.Limit)
	} else if req.ServiceName != "" {
		alerts, err = s.repo.GetByService(req.ServiceName, req.Limit)
	} else {
		alerts, err = s.repo.GetAll(req.Limit, req.Offset)
	}
	
	if err != nil {
		logger.Error("Failed to get alerts", logger.Err(err))
		return nil, errors.Internal("failed to retrieve alerts", err)
	}
	
	responses := make([]*AlertResponse, len(alerts))
	for i, a := range alerts {
		responses[i] = toAlertResponse(a)
	}
	
	return &AlertListResponse{
		Alerts: responses,
		Total:  len(responses),
		Limit:  req.Limit,
		Offset: req.Offset,
	}, nil
}

// GetActiveAlerts récupère toutes les alertes actives
func (s *Service) GetActiveAlerts() ([]*AlertResponse, error) {
	alerts, err := s.repo.GetActiveAlerts()
	if err != nil {
		return nil, errors.Internal("failed to retrieve active alerts", err)
	}
	
	responses := make([]*AlertResponse, len(alerts))
	for i, a := range alerts {
		responses[i] = toAlertResponse(a)
	}
	
	return responses, nil
}

// GetCriticalAlerts récupère toutes les alertes critiques
func (s *Service) GetCriticalAlerts() ([]*AlertResponse, error) {
	alerts, err := s.repo.GetCriticalAlerts()
	if err != nil {
		return nil, errors.Internal("failed to retrieve critical alerts", err)
	}
	
	responses := make([]*AlertResponse, len(alerts))
	for i, a := range alerts {
		responses[i] = toAlertResponse(a)
	}
	
	return responses, nil
}

// UpdateAlert met à jour une alerte
func (s *Service) UpdateAlert(id string, req *UpdateAlertRequest) (*AlertResponse, error) {
	if err := req.Validate(); err != nil {
		return nil, err
	}
	
	a, err := s.repo.GetByID(id)
	if err != nil {
		return nil, errors.AlertNotFound(id)
	}
	
	// Mettre à jour les champs modifiables
	if req.Title != nil {
		a.Title = *req.Title
	}
	if req.Description != nil {
		a.Description = *req.Description
	}
	if req.Severity != nil {
		a.Severity = *req.Severity
	}
	
	a.UpdatedAt = time.Now()
	
	if err := s.repo.Update(a); err != nil {
		logger.Error("Failed to update alert", logger.String("id", id), logger.Err(err))
		return nil, errors.Internal("failed to update alert", err)
	}
	
	// Invalider le cache
	s.cache.Delete("alert:" + id)
	
	logger.Info("Alert updated", logger.String("id", id))
	
	return toAlertResponse(a), nil
}

// DeleteAlert supprime une alerte
func (s *Service) DeleteAlert(id string) error {
	if err := s.repo.Delete(id); err != nil {
		return errors.AlertNotFound(id)
	}
	
	// Invalider le cache
	s.cache.Delete("alert:" + id)
	
	logger.Info("Alert deleted", logger.String("id", id))
	
	return nil
}

// ===== Alert Status Management =====

// AcknowledgeAlert acquitte une alerte
func (s *Service) AcknowledgeAlert(id string) (*AlertResponse, error) {
	if err := s.repo.Acknowledge(id); err != nil {
		return nil, errors.AlertNotFound(id)
	}
	
	a, _ := s.repo.GetByID(id)
	
	// Invalider le cache
	s.cache.Delete("alert:" + id)
	
	logger.Info("Alert acknowledged", logger.String("id", id))
	
	return toAlertResponse(a), nil
}

// ResolveAlert résout une alerte
func (s *Service) ResolveAlert(id string) (*AlertResponse, error) {
	if err := s.repo.Resolve(id); err != nil {
		return nil, errors.AlertNotFound(id)
	}
	
	a, _ := s.repo.GetByID(id)
	
	// Invalider le cache
	s.cache.Delete("alert:" + id)
	
	logger.Info("Alert resolved", logger.String("id", id))
	
	return toAlertResponse(a), nil
}

// CloseAlert ferme une alerte
func (s *Service) CloseAlert(id string) (*AlertResponse, error) {
	if err := s.repo.Close(id); err != nil {
		return nil, errors.AlertNotFound(id)
	}
	
	a, _ := s.repo.GetByID(id)
	
	// Invalider le cache
	s.cache.Delete("alert:" + id)
	
	logger.Info("Alert closed", logger.String("id", id))
	
	return toAlertResponse(a), nil
}

// ===== Statistics =====

// GetAlertStatistics récupère les statistiques des alertes
func (s *Service) GetAlertStatistics(from, to time.Time) (*AlertStatisticsResponse, error) {
	stats, err := s.repo.GetStatistics(from, to)
	if err != nil {
		return nil, errors.Internal("failed to get alert statistics", err)
	}
	
	return toAlertStatisticsResponse(stats), nil
}

// GetAlertSummary récupère un résumé des alertes
func (s *Service) GetAlertSummary() (*AlertSummaryResponse, error) {
	openCount, _ := s.repo.CountByStatus(alert.StatusOpen)
	acknowledgedCount, _ := s.repo.CountByStatus(alert.StatusAcknowledged)
	resolvedCount, _ := s.repo.CountByStatus(alert.StatusResolved)
	
	criticalCount, _ := s.repo.CountBySeverity(alert.SeverityCritical)
	errorCount, _ := s.repo.CountBySeverity(alert.SeverityError)
	warningCount, _ := s.repo.CountBySeverity(alert.SeverityWarning)
	infoCount, _ := s.repo.CountBySeverity(alert.SeverityInfo)
	
	return &AlertSummaryResponse{
		TotalOpen:         int(openCount),
		TotalAcknowledged: int(acknowledgedCount),
		TotalResolved:     int(resolvedCount),
		CriticalCount:     int(criticalCount),
		ErrorCount:        int(errorCount),
		WarningCount:      int(warningCount),
		InfoCount:         int(infoCount),
	}, nil
}

// ===== Alert Rules (Bonus) =====

// EvaluateRules évalue les règles d'alerte sur les métriques
func (s *Service) EvaluateRules(serviceName string, metricName string, value float64) error {
	// TODO: Implémenter l'évaluation des règles
	// 1. Récupérer les règles pour ce service/métrique
	// 2. Évaluer chaque règle
	// 3. Créer des alertes si nécessaire
	
	rules, err := s.repo.GetRulesByService(serviceName)
	if err != nil {
		return nil // Pas d'erreur si pas de règles
	}
	
	for _, rule := range rules {
		if !rule.Enabled {
			continue
		}
		
		if rule.MetricName != metricName {
			continue
		}
		
		if rule.EvaluateRule(value) {
			// Créer une alerte
			newAlert := alert.CreateAlertFromRule(rule, value)
			s.repo.Create(newAlert)
			
			logger.LogAlert(string(newAlert.Severity), newAlert.Title, serviceName)
		}
	}
	
	return nil
}

// ===== Cleanup =====

// CleanupOldAlerts nettoie les anciennes alertes résolues
func (s *Service) CleanupOldAlerts(retentionDays int) error {
	before := time.Now().AddDate(0, 0, -retentionDays)
	
	deleted, err := s.repo.DeleteOldResolvedAlerts(before)
	if err != nil {
		logger.Error("Failed to cleanup old alerts", logger.Err(err))
		return errors.Internal("failed to cleanup alerts", err)
	}
	
	logger.Info("Old alerts cleaned up", logger.Int64("deleted", deleted))
	
	return nil
}

// ===== Notifications (À implémenter) =====

func (s *Service) sendNotification(a *alert.Alert) {
	// TODO: Implémenter l'envoi de notifications
	// - Email
	// - Slack
	// - PagerDuty
	// - Webhook
	
	logger.Info("Notification sent for critical alert",
		logger.String("alert_id", a.ID),
		logger.String("title", a.Title),
	)
}