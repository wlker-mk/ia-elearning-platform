package monitoring

import (
	"context"
	"net/http"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/domain/monitoring"
	"github.com/ai-elearning-platform/monitoring-service/internal/infrastructure/cache"
	"github.com/ai-elearning-platform/monitoring-service/pkg/errors"
	"github.com/ai-elearning-platform/monitoring-service/pkg/logger"
)

type Service struct {
	repo  monitoring.Repository
	cache *cache.RedisCache
}

func NewService(repo monitoring.Repository, cache *cache.RedisCache) *Service {
	return &Service{
		repo:  repo,
		cache: cache,
	}
}

// ===== ServiceHealth Operations =====

// RegisterService enregistre un nouveau service à monitorer
func (s *Service) RegisterService(req *RegisterServiceRequest) (*ServiceHealthResponse, error) {
	// Valider la requête
	if err := req.Validate(); err != nil {
		return nil, err
	}
	
	// Vérifier si le service existe déjà
	existing, _ := s.repo.GetServiceHealthByName(req.ServiceName)
	if existing != nil {
		return nil, errors.New(errors.ErrConflict, "service already registered")
	}
	
	// Créer l'entité
	health := &monitoring.ServiceHealth{
		ServiceName: req.ServiceName,
		Status:      monitoring.StatusHealthy,
		LastCheckAt: time.Now(),
	}
	
	if err := s.repo.CreateServiceHealth(health); err != nil {
		logger.Error("Failed to register service", logger.String("service", req.ServiceName), logger.Err(err))
		return nil, errors.Internal("failed to register service", err)
	}
	
	logger.Info("Service registered", logger.String("service", req.ServiceName))
	
	return toServiceHealthResponse(health), nil
}

// CheckServiceHealth effectue un health check sur un service
func (s *Service) CheckServiceHealth(serviceName, url string) (*HealthCheckResponse, error) {
	startTime := time.Now()
	
	// Effectuer le health check HTTP
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	req, err := http.NewRequestWithContext(ctx, "GET", url+"/health", nil)
	if err != nil {
		return s.handleUnhealthyService(serviceName, err, time.Since(startTime))
	}
	
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return s.handleUnhealthyService(serviceName, err, time.Since(startTime))
	}
	defer resp.Body.Close()
	
	responseTime := time.Since(startTime).Milliseconds()
	
	// Déterminer le statut
	var status monitoring.ServiceStatus
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		status = monitoring.StatusHealthy
	} else if resp.StatusCode >= 500 {
		status = monitoring.StatusDown
	} else {
		status = monitoring.StatusDegraded
	}
	
	// Mettre à jour la santé du service
	health, err := s.repo.GetServiceHealthByName(serviceName)
	if err != nil {
		// Si le service n'existe pas, le créer
		health = &monitoring.ServiceHealth{
			ServiceName: serviceName,
		}
	}
	
	health.Status = status
	health.LastCheckAt = time.Now()
	health.RequestCount++
	
	if status != monitoring.StatusHealthy {
		health.ErrorCount++
	}
	
	// Mettre à jour les temps de réponse (moyenne simple)
	if health.AvgResponseTime == nil {
		avgRT := float64(responseTime)
		health.AvgResponseTime = &avgRT
	} else {
		*health.AvgResponseTime = (*health.AvgResponseTime + float64(responseTime)) / 2
	}
	
	if err := s.repo.UpdateServiceHealth(health); err != nil {
		logger.Error("Failed to update service health", logger.String("service", serviceName), logger.Err(err))
	}
	
	// Mettre en cache le statut
	s.cache.SetServiceStatus(serviceName, string(status))
	s.cache.RecordResponseTime(serviceName, responseTime)
	
	// Incrémenter les métriques
	s.cache.IncrMetric(serviceName, "health_checks")
	
	logger.LogServiceHealth(serviceName, string(status), responseTime)
	
	return &HealthCheckResponse{
		ServiceName:  serviceName,
		Status:       status,
		ResponseTime: int(responseTime),
		CheckedAt:    time.Now(),
	}, nil
}

// handleUnhealthyService gère un service qui ne répond pas
func (s *Service) handleUnhealthyService(serviceName string, err error, elapsed time.Duration) (*HealthCheckResponse, error) {
	health, _ := s.repo.GetServiceHealthByName(serviceName)
	if health != nil {
		health.Status = monitoring.StatusDown
		health.LastCheckAt = time.Now()
		health.ErrorCount++
		s.repo.UpdateServiceHealth(health)
	}
	
	s.cache.SetServiceStatus(serviceName, string(monitoring.StatusDown))
	
	logger.Error("Service health check failed", 
		logger.String("service", serviceName), 
		logger.Err(err),
		logger.Duration("elapsed", elapsed),
	)
	
	return &HealthCheckResponse{
		ServiceName:  serviceName,
		Status:       monitoring.StatusDown,
		ResponseTime: int(elapsed.Milliseconds()),
		ErrorMessage: err.Error(),
		CheckedAt:    time.Now(),
	}, nil
}

// GetServiceHealth récupère la santé d'un service
func (s *Service) GetServiceHealth(serviceName string) (*ServiceHealthResponse, error) {
	// Essayer le cache d'abord
	var cachedHealth monitoring.ServiceHealth
	if err := s.cache.GetServiceHealth(serviceName, &cachedHealth); err == nil {
		return toServiceHealthResponse(&cachedHealth), nil
	}
	
	// Sinon chercher en DB
	health, err := s.repo.GetServiceHealthByName(serviceName)
	if err != nil {
		return nil, errors.ServiceNotFound(serviceName)
	}
	
	// Mettre en cache
	s.cache.SetServiceHealth(serviceName, health)
	
	return toServiceHealthResponse(health), nil
}

// GetAllServicesHealth récupère la santé de tous les services
func (s *Service) GetAllServicesHealth() ([]*ServiceHealthResponse, error) {
	services, err := s.repo.GetAllServiceHealth()
	if err != nil {
		logger.Error("Failed to get all services health", logger.Err(err))
		return nil, errors.Internal("failed to retrieve services", err)
	}
	
	responses := make([]*ServiceHealthResponse, len(services))
	for i, svc := range services {
		responses[i] = toServiceHealthResponse(svc)
	}
	
	return responses, nil
}

// ===== Metrics Operations =====

// RecordMetric enregistre une métrique
func (s *Service) RecordMetric(req *RecordMetricRequest) error {
	if err := req.Validate(); err != nil {
		return err
	}
	
	metric := &monitoring.Metric{
		ServiceName: req.ServiceName,
		MetricName:  req.MetricName,
		Value:       req.Value,
		Unit:        req.Unit,
		Labels:      req.Labels,
		Timestamp:   time.Now(),
	}
	
	// Enregistrer en DB (asynchrone si possible)
	if err := s.repo.CreateMetric(metric); err != nil {
		logger.Error("Failed to record metric", 
			logger.String("service", req.ServiceName),
			logger.String("metric", req.MetricName),
			logger.Err(err),
		)
		return errors.Internal("failed to record metric", err)
	}
	
	// Mettre à jour le cache
	s.cache.IncrMetric(req.ServiceName, req.MetricName)
	
	logger.LogMetric(req.ServiceName, req.MetricName, req.Value)
	
	return nil
}

// RecordMetricsBatch enregistre plusieurs métriques en batch
func (s *Service) RecordMetricsBatch(req *RecordMetricsBatchRequest) error {
	if err := req.Validate(); err != nil {
		return err
	}
	
	metrics := make([]*monitoring.Metric, len(req.Metrics))
	now := time.Now()
	
	for i, m := range req.Metrics {
		metrics[i] = &monitoring.Metric{
			ServiceName: m.ServiceName,
			MetricName:  m.MetricName,
			Value:       m.Value,
			Unit:        m.Unit,
			Labels:      m.Labels,
			Timestamp:   now,
		}
	}
	
	if err := s.repo.CreateMetricsBatch(metrics); err != nil {
		logger.Error("Failed to record metrics batch", logger.Err(err))
		return errors.Internal("failed to record metrics", err)
	}
	
	logger.Info("Metrics batch recorded", logger.Int("count", len(metrics)))
	
	return nil
}

// GetMetrics récupère les métriques d'un service
func (s *Service) GetMetrics(req *GetMetricsRequest) (*MetricsResponse, error) {
	if err := req.Validate(); err != nil {
		return nil, err
	}
	
	var metrics []*monitoring.Metric
	var err error
	
	if req.MetricName != "" {
		metrics, err = s.repo.GetMetricsByName(req.ServiceName, req.MetricName, req.From, req.To)
	} else {
		metrics, err = s.repo.GetMetricsByService(req.ServiceName, req.From, req.To)
	}
	
	if err != nil {
		logger.Error("Failed to get metrics", logger.Err(err))
		return nil, errors.Internal("failed to retrieve metrics", err)
	}
	
	return &MetricsResponse{
		ServiceName: req.ServiceName,
		Metrics:     toMetricDTOs(metrics),
		From:        req.From,
		To:          req.To,
		Count:       len(metrics),
	}, nil
}

// ===== Performance Operations =====

// RecordPerformance enregistre une performance log
func (s *Service) RecordPerformance(req *RecordPerformanceRequest) error {
	if err := req.Validate(); err != nil {
		return err
	}
	
	perfLog := &monitoring.PerformanceLog{
		ServiceName:  req.ServiceName,
		Endpoint:     req.Endpoint,
		Method:       req.Method,
		StatusCode:   req.StatusCode,
		ResponseTime: req.ResponseTime,
		UserID:       req.UserID,
		IPAddress:    req.IPAddress,
		Timestamp:    time.Now(),
	}
	
	if err := s.repo.CreatePerformanceLog(perfLog); err != nil {
		logger.Error("Failed to record performance", logger.Err(err))
		return errors.Internal("failed to record performance", err)
	}
	
	// Mettre à jour le cache pour calculs temps réel
	s.cache.RecordResponseTime(req.ServiceName, int64(req.ResponseTime))
	
	logger.LogPerformance(req.ServiceName, req.Endpoint, req.Method, req.StatusCode, req.ResponseTime)
	
	return nil
}

// GetPerformanceStats récupère les statistiques de performance
func (s *Service) GetPerformanceStats(serviceName string, from, to time.Time) (*PerformanceStatsResponse, error) {
	if serviceName == "" {
		return nil, errors.BadRequest("service name is required")
	}
	
	avg, err := s.repo.GetAverageResponseTime(serviceName, from, to)
	if err != nil {
		return nil, errors.Internal("failed to get average response time", err)
	}
	
	p95, _ := s.repo.GetPercentileResponseTime(serviceName, 95, from, to)
	p99, _ := s.repo.GetPercentileResponseTime(serviceName, 99, from, to)
	
	return &PerformanceStatsResponse{
		ServiceName:     serviceName,
		AvgResponseTime: avg,
		P95ResponseTime: p95,
		P99ResponseTime: p99,
		From:            from,
		To:              to,
	}, nil
}

// ===== Dashboard Operations =====

// GetServiceSummary récupère un résumé pour le dashboard
func (s *Service) GetServiceSummary(serviceName string) (*ServiceSummaryResponse, error) {
	summary, err := s.repo.GetServiceMetricsSummary(serviceName)
	if err != nil {
		return nil, errors.ServiceNotFound(serviceName)
	}
	
	return toServiceSummaryResponse(summary), nil
}

// GetAllServicesSummary récupère le résumé de tous les services
func (s *Service) GetAllServicesSummary() ([]*ServiceSummaryResponse, error) {
	summaries, err := s.repo.GetAllServicesMetricsSummary()
	if err != nil {
		return nil, errors.Internal("failed to retrieve summaries", err)
	}
	
	responses := make([]*ServiceSummaryResponse, len(summaries))
	for i, summary := range summaries {
		responses[i] = toServiceSummaryResponse(summary)
	}
	
	return responses, nil
}

// ===== Cleanup Operations =====

// CleanupOldData nettoie les anciennes données
func (s *Service) CleanupOldData(retentionDays int) error {
	before := time.Now().AddDate(0, 0, -retentionDays)
	
	// Nettoyer les métriques
	metricsDeleted, err := s.repo.DeleteOldMetrics(before)
	if err != nil {
		logger.Error("Failed to cleanup metrics", logger.Err(err))
	} else {
		logger.Info("Metrics cleaned up", logger.Int64("deleted", metricsDeleted))
	}
	
	// Nettoyer les performance logs
	perfDeleted, err := s.repo.DeleteOldPerformanceLogs(before)
	if err != nil {
		logger.Error("Failed to cleanup performance logs", logger.Err(err))
	} else {
		logger.Info("Performance logs cleaned up", logger.Int64("deleted", perfDeleted))
	}
	
	// Nettoyer les erreurs résolues
	errorsDeleted, err := s.repo.DeleteOldResolvedErrors(before)
	if err != nil {
		logger.Error("Failed to cleanup error logs", logger.Err(err))
	} else {
		logger.Info("Error logs cleaned up", logger.Int64("deleted", errorsDeleted))
	}
	
	return nil
}