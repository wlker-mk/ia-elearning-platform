package repository

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/domain/monitoring"
	"github.com/google/uuid"
)

// ===== ErrorLog Operations =====

func (r *MonitoringRepository) CreateErrorLog(log *monitoring.ErrorLog) error {
	if log.ID == "" {
		log.ID = uuid.New().String()
	}
	
	query := `
		INSERT INTO error_logs (id, service_name, error_type, error_message, stack_trace,
								endpoint, method, user_id, occurrences, first_seen_at,
								last_seen_at, is_resolved, resolved_at, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
	`
	
	now := time.Now()
	_, err := r.db.Exec(query,
		log.ID, log.ServiceName, log.ErrorType, log.ErrorMessage, log.StackTrace,
		log.Endpoint, log.Method, log.UserID, log.Occurrences, log.FirstSeenAt,
		log.LastSeenAt, log.IsResolved, log.ResolvedAt, now,
	)
	
	return err
}

func (r *MonitoringRepository) UpdateErrorLogOccurrences(id string, occurrences int, lastSeenAt time.Time) error {
	query := `
		UPDATE error_logs 
		SET occurrences = $2, last_seen_at = $3
		WHERE id = $1
	`
	
	_, err := r.db.Exec(query, id, occurrences, lastSeenAt)
	return err
}

func (r *MonitoringRepository) ResolveErrorLog(id string, resolvedAt time.Time) error {
	query := `
		UPDATE error_logs 
		SET is_resolved = true, resolved_at = $2
		WHERE id = $1
	`
	
	_, err := r.db.Exec(query, id, resolvedAt)
	return err
}

func (r *MonitoringRepository) GetErrorLogs(serviceName string, isResolved bool, limit int) ([]*monitoring.ErrorLog, error) {
	query := `
		SELECT id, service_name, error_type, error_message, stack_trace,
			   endpoint, method, user_id, occurrences, first_seen_at,
			   last_seen_at, is_resolved, resolved_at, created_at
		FROM error_logs
		WHERE service_name = $1 AND is_resolved = $2
		ORDER BY last_seen_at DESC
		LIMIT $3
	`
	
	rows, err := r.db.Query(query, serviceName, isResolved, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanErrorLogs(rows)
}

func (r *MonitoringRepository) GetErrorLogsByType(serviceName, errorType string, limit int) ([]*monitoring.ErrorLog, error) {
	query := `
		SELECT id, service_name, error_type, error_message, stack_trace,
			   endpoint, method, user_id, occurrences, first_seen_at,
			   last_seen_at, is_resolved, resolved_at, created_at
		FROM error_logs
		WHERE service_name = $1 AND error_type = $2
		ORDER BY last_seen_at DESC
		LIMIT $3
	`
	
	rows, err := r.db.Query(query, serviceName, errorType, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanErrorLogs(rows)
}

func (r *MonitoringRepository) GetErrorLogStats(serviceName string, from, to time.Time) (map[string]int, error) {
	query := `
		SELECT error_type, COUNT(*) as count
		FROM error_logs
		WHERE service_name = $1 AND last_seen_at BETWEEN $2 AND $3
		GROUP BY error_type
		ORDER BY count DESC
	`
	
	rows, err := r.db.Query(query, serviceName, from, to)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	stats := make(map[string]int)
	for rows.Next() {
		var errorType string
		var count int
		if err := rows.Scan(&errorType, &count); err != nil {
			return nil, err
		}
		stats[errorType] = count
	}
	
	return stats, rows.Err()
}

func (r *MonitoringRepository) DeleteOldResolvedErrors(before time.Time) (int64, error) {
	query := `DELETE FROM error_logs WHERE is_resolved = true AND resolved_at < $1`
	result, err := r.db.Exec(query, before)
	if err != nil {
		return 0, err
	}
	return result.RowsAffected()
}

// ===== Uptime Operations =====

func (r *MonitoringRepository) CreateOrUpdateUptime(uptime *monitoring.Uptime) error {
	if uptime.ID == "" {
		uptime.ID = uuid.New().String()
	}
	
	query := `
		INSERT INTO uptime (id, service_name, date, status, uptime_seconds, 
							downtime_seconds, incident_count, created_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		ON CONFLICT (service_name, date) 
		DO UPDATE SET 
			status = EXCLUDED.status,
			uptime_seconds = EXCLUDED.uptime_seconds,
			downtime_seconds = EXCLUDED.downtime_seconds,
			incident_count = EXCLUDED.incident_count
	`
	
	_, err := r.db.Exec(query,
		uptime.ID, uptime.ServiceName, uptime.Date, uptime.Status,
		uptime.UptimeSeconds, uptime.DowntimeSeconds, uptime.IncidentCount,
		time.Now(),
	)
	
	return err
}

func (r *MonitoringRepository) GetUptimeByDate(serviceName string, date time.Time) (*monitoring.Uptime, error) {
	query := `
		SELECT id, service_name, date, status, uptime_seconds,
			   downtime_seconds, incident_count, created_at
		FROM uptime
		WHERE service_name = $1 AND date = $2
	`
	
	uptime := &monitoring.Uptime{}
	err := r.db.QueryRow(query, serviceName, date).Scan(
		&uptime.ID, &uptime.ServiceName, &uptime.Date, &uptime.Status,
		&uptime.UptimeSeconds, &uptime.DowntimeSeconds, &uptime.IncidentCount,
		&uptime.CreatedAt,
	)
	
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("uptime not found for %s on %s", serviceName, date.Format("2006-01-02"))
	}
	
	return uptime, err
}

func (r *MonitoringRepository) GetUptimeHistory(serviceName string, from, to time.Time) ([]*monitoring.Uptime, error) {
	query := `
		SELECT id, service_name, date, status, uptime_seconds,
			   downtime_seconds, incident_count, created_at
		FROM uptime
		WHERE service_name = $1 AND date BETWEEN $2 AND $3
		ORDER BY date DESC
	`
	
	rows, err := r.db.Query(query, serviceName, from, to)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanUptimes(rows)
}

func (r *MonitoringRepository) CalculateUptimePercentage(serviceName string, from, to time.Time) (float64, error) {
	query := `
		SELECT 
			COALESCE(SUM(uptime_seconds), 0) as total_uptime,
			COALESCE(SUM(uptime_seconds + downtime_seconds), 0) as total_time
		FROM uptime
		WHERE service_name = $1 AND date BETWEEN $2 AND $3
	`
	
	var totalUptime, totalTime float64
	err := r.db.QueryRow(query, serviceName, from, to).Scan(&totalUptime, &totalTime)
	if err != nil {
		return 0, err
	}
	
	if totalTime == 0 {
		return 100.0, nil
	}
	
	return (totalUptime / totalTime) * 100, nil
}

// ===== Aggregated Queries =====

func (r *MonitoringRepository) GetServiceMetricsSummary(serviceName string) (*monitoring.ServiceMetricsSummary, error) {
	// Récupérer les données de santé
	health, err := r.GetServiceHealthByName(serviceName)
	if err != nil {
		return nil, err
	}
	
	// Compter les alertes actives
	var activeAlerts int
	alertQuery := `
		SELECT COUNT(*) 
		FROM alerts 
		WHERE service_name = $1 AND status IN ('OPEN', 'ACKNOWLEDGED')
	`
	_ = r.db.QueryRow(alertQuery, serviceName).Scan(&activeAlerts)
	
	// Calculer l'uptime des dernières 24h
	uptimePercent, _ := r.CalculateUptimePercentage(
		serviceName,
		time.Now().Add(-24*time.Hour),
		time.Now(),
	)
	
	summary := &monitoring.ServiceMetricsSummary{
		ServiceName:       health.ServiceName,
		Status:            health.Status,
		CurrentRequests:   int64(health.RequestCount),
		CurrentErrors:     int64(health.ErrorCount),
		ResponseTimeAvg:   *health.AvgResponseTime,
		ResponseTimeP95:   *health.P95ResponseTime,
		ResponseTimeP99:   *health.P99ResponseTime,
		UptimePercentage:  uptimePercent,
		LastCheckAt:       health.LastCheckAt,
		ActiveAlerts:      activeAlerts,
	}
	
	if health.CPUUsage != nil {
		summary.CPUUsage = *health.CPUUsage
	}
	if health.MemoryUsage != nil {
		summary.MemoryUsage = *health.MemoryUsage
	}
	if health.DiskUsage != nil {
		summary.DiskUsage = *health.DiskUsage
	}
	
	return summary, nil
}

func (r *MonitoringRepository) GetAllServicesMetricsSummary() ([]*monitoring.ServiceMetricsSummary, error) {
	services, err := r.GetAllServiceHealth()
	if err != nil {
		return nil, err
	}
	
	summaries := make([]*monitoring.ServiceMetricsSummary, 0, len(services))
	for _, svc := range services {
		summary, err := r.GetServiceMetricsSummary(svc.ServiceName)
		if err != nil {
			continue
		}
		summaries = append(summaries, summary)
	}
	
	return summaries, nil
}

func (r *MonitoringRepository) GetAggregatedMetrics(serviceName string, from, to time.Time) (*monitoring.AggregatedMetrics, error) {
	// Requêtes d'agrégation
	query := `
		SELECT 
			COUNT(*) as total_requests,
			COUNT(CASE WHEN status_code >= 400 THEN 1 END) as total_errors,
			AVG(response_time) as avg_response_time
		FROM performance_logs
		WHERE service_name = $1 AND timestamp BETWEEN $2 AND $3
	`
	
	var totalRequests, totalErrors int64
	var avgResponseTime float64
	
	err := r.db.QueryRow(query, serviceName, from, to).Scan(
		&totalRequests, &totalErrors, &avgResponseTime,
	)
	if err != nil {
		return nil, err
	}
	
	// Calculer le taux d'erreur
	var errorRate float64
	if totalRequests > 0 {
		errorRate = float64(totalErrors) / float64(totalRequests) * 100
	}
	
	// Récupérer les percentiles
	p95, _ := r.GetPercentileResponseTime(serviceName, 95, from, to)
	p99, _ := r.GetPercentileResponseTime(serviceName, 99, from, to)
	
	// Calculer l'uptime
	uptimePercent, _ := r.CalculateUptimePercentage(serviceName, from, to)
	
	return &monitoring.AggregatedMetrics{
		ServiceName:     serviceName,
		TotalRequests:   totalRequests,
		TotalErrors:     totalErrors,
		ErrorRate:       errorRate,
		AvgResponseTime: avgResponseTime,
		P95ResponseTime: p95,
		P99ResponseTime: p99,
		UptimePercent:   uptimePercent,
		Period:          fmt.Sprintf("%s to %s", from.Format("2006-01-02"), to.Format("2006-01-02")),
		Timestamp:       time.Now(),
	}, nil
}

// ===== Helper Scan Functions =====

func (r *MonitoringRepository) scanErrorLogs(rows *sql.Rows) ([]*monitoring.ErrorLog, error) {
	var logs []*monitoring.ErrorLog
	
	for rows.Next() {
		log := &monitoring.ErrorLog{}
		err := rows.Scan(
			&log.ID, &log.ServiceName, &log.ErrorType, &log.ErrorMessage,
			&log.StackTrace, &log.Endpoint, &log.Method, &log.UserID,
			&log.Occurrences, &log.FirstSeenAt, &log.LastSeenAt,
			&log.IsResolved, &log.ResolvedAt, &log.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		logs = append(logs, log)
	}
	
	return logs, rows.Err()
}

func (r *MonitoringRepository) scanUptimes(rows *sql.Rows) ([]*monitoring.Uptime, error) {
	var uptimes []*monitoring.Uptime
	
	for rows.Next() {
		uptime := &monitoring.Uptime{}
		err := rows.Scan(
			&uptime.ID, &uptime.ServiceName, &uptime.Date, &uptime.Status,
			&uptime.UptimeSeconds, &uptime.DowntimeSeconds, &uptime.IncidentCount,
			&uptime.CreatedAt,
		)
		if err != nil {
			return nil, err
		}
		uptimes = append(uptimes, uptime)
	}
	
	return uptimes, rows.Err()
}