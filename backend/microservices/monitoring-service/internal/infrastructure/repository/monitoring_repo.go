package repository

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/domain/monitoring"
	"github.com/google/uuid"
)

type MonitoringRepository struct {
	db *sql.DB
}

func NewMonitoringRepository(db *sql.DB) *MonitoringRepository {
	return &MonitoringRepository{db: db}
}

// ===== ServiceHealth Operations =====

func (r *MonitoringRepository) CreateServiceHealth(health *monitoring.ServiceHealth) error {
	if health.ID == "" {
		health.ID = uuid.New().String()
	}
	
	query := `
		INSERT INTO service_health (
			id, service_name, status, avg_response_time, p95_response_time, 
			p99_response_time, uptime, downtime, request_count, error_count,
			cpu_usage, memory_usage, disk_usage, last_check_at, created_at, updated_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
	`
	
	now := time.Now()
	_, err := r.db.Exec(query,
		health.ID, health.ServiceName, health.Status, health.AvgResponseTime,
		health.P95ResponseTime, health.P99ResponseTime, health.Uptime, health.Downtime,
		health.RequestCount, health.ErrorCount, health.CPUUsage, health.MemoryUsage,
		health.DiskUsage, health.LastCheckAt, now, now,
	)
	
	return err
}

func (r *MonitoringRepository) UpdateServiceHealth(health *monitoring.ServiceHealth) error {
	query := `
		UPDATE service_health SET
			status = $2, avg_response_time = $3, p95_response_time = $4,
			p99_response_time = $5, uptime = $6, downtime = $7,
			request_count = $8, error_count = $9, cpu_usage = $10,
			memory_usage = $11, disk_usage = $12, last_check_at = $13,
			updated_at = $14
		WHERE service_name = $1
	`
	
	_, err := r.db.Exec(query,
		health.ServiceName, health.Status, health.AvgResponseTime,
		health.P95ResponseTime, health.P99ResponseTime, health.Uptime,
		health.Downtime, health.RequestCount, health.ErrorCount,
		health.CPUUsage, health.MemoryUsage, health.DiskUsage,
		health.LastCheckAt, time.Now(),
	)
	
	return err
}

func (r *MonitoringRepository) GetServiceHealthByName(serviceName string) (*monitoring.ServiceHealth, error) {
	query := `
		SELECT id, service_name, status, avg_response_time, p95_response_time,
			   p99_response_time, uptime, downtime, request_count, error_count,
			   cpu_usage, memory_usage, disk_usage, last_check_at, created_at, updated_at
		FROM service_health
		WHERE service_name = $1
	`
	
	health := &monitoring.ServiceHealth{}
	err := r.db.QueryRow(query, serviceName).Scan(
		&health.ID, &health.ServiceName, &health.Status, &health.AvgResponseTime,
		&health.P95ResponseTime, &health.P99ResponseTime, &health.Uptime,
		&health.Downtime, &health.RequestCount, &health.ErrorCount,
		&health.CPUUsage, &health.MemoryUsage, &health.DiskUsage,
		&health.LastCheckAt, &health.CreatedAt, &health.UpdatedAt,
	)
	
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("service not found: %s", serviceName)
	}
	
	return health, err
}

func (r *MonitoringRepository) GetAllServiceHealth() ([]*monitoring.ServiceHealth, error) {
	query := `
		SELECT id, service_name, status, avg_response_time, p95_response_time,
			   p99_response_time, uptime, downtime, request_count, error_count,
			   cpu_usage, memory_usage, disk_usage, last_check_at, created_at, updated_at
		FROM service_health
		ORDER BY service_name
	`
	
	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	var services []*monitoring.ServiceHealth
	for rows.Next() {
		health := &monitoring.ServiceHealth{}
		err := rows.Scan(
			&health.ID, &health.ServiceName, &health.Status, &health.AvgResponseTime,
			&health.P95ResponseTime, &health.P99ResponseTime, &health.Uptime,
			&health.Downtime, &health.RequestCount, &health.ErrorCount,
			&health.CPUUsage, &health.MemoryUsage, &health.DiskUsage,
			&health.LastCheckAt, &health.CreatedAt, &health.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		services = append(services, health)
	}
	
	return services, rows.Err()
}

func (r *MonitoringRepository) DeleteServiceHealth(serviceName string) error {
	query := `DELETE FROM service_health WHERE service_name = $1`
	_, err := r.db.Exec(query, serviceName)
	return err
}

// ===== Metrics Operations =====

func (r *MonitoringRepository) CreateMetric(metric *monitoring.Metric) error {
	if metric.ID == "" {
		metric.ID = uuid.New().String()
	}
	
	query := `
		INSERT INTO metrics (id, service_name, metric_name, value, unit, labels, timestamp)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`
	
	_, err := r.db.Exec(query,
		metric.ID, metric.ServiceName, metric.MetricName, metric.Value,
		metric.Unit, metric.Labels, metric.Timestamp,
	)
	
	return err
}

func (r *MonitoringRepository) CreateMetricsBatch(metrics []*monitoring.Metric) error {
	if len(metrics) == 0 {
		return nil
	}
	
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer tx.Rollback()
	
	stmt, err := tx.Prepare(`
		INSERT INTO metrics (id, service_name, metric_name, value, unit, labels, timestamp)
		VALUES ($1, $2, $3, $4, $5, $6, $7)
	`)
	if err != nil {
		return err
	}
	defer stmt.Close()
	
	for _, metric := range metrics {
		if metric.ID == "" {
			metric.ID = uuid.New().String()
		}
		
		_, err := stmt.Exec(
			metric.ID, metric.ServiceName, metric.MetricName, metric.Value,
			metric.Unit, metric.Labels, metric.Timestamp,
		)
		if err != nil {
			return err
		}
	}
	
	return tx.Commit()
}

func (r *MonitoringRepository) GetMetricsByService(serviceName string, from, to time.Time) ([]*monitoring.Metric, error) {
	query := `
		SELECT id, service_name, metric_name, value, unit, labels, timestamp
		FROM metrics
		WHERE service_name = $1 AND timestamp BETWEEN $2 AND $3
		ORDER BY timestamp DESC
		LIMIT 1000
	`
	
	rows, err := r.db.Query(query, serviceName, from, to)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanMetrics(rows)
}

func (r *MonitoringRepository) GetMetricsByName(serviceName, metricName string, from, to time.Time) ([]*monitoring.Metric, error) {
	query := `
		SELECT id, service_name, metric_name, value, unit, labels, timestamp
		FROM metrics
		WHERE service_name = $1 AND metric_name = $2 AND timestamp BETWEEN $3 AND $4
		ORDER BY timestamp DESC
		LIMIT 1000
	`
	
	rows, err := r.db.Query(query, serviceName, metricName, from, to)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanMetrics(rows)
}

func (r *MonitoringRepository) GetLatestMetrics(serviceName string, limit int) ([]*monitoring.Metric, error) {
	query := `
		SELECT id, service_name, metric_name, value, unit, labels, timestamp
		FROM metrics
		WHERE service_name = $1
		ORDER BY timestamp DESC
		LIMIT $2
	`
	
	rows, err := r.db.Query(query, serviceName, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanMetrics(rows)
}

func (r *MonitoringRepository) DeleteOldMetrics(before time.Time) (int64, error) {
	query := `DELETE FROM metrics WHERE timestamp < $1`
	result, err := r.db.Exec(query, before)
	if err != nil {
		return 0, err
	}
	return result.RowsAffected()
}

// ===== PerformanceLog Operations =====

func (r *MonitoringRepository) CreatePerformanceLog(log *monitoring.PerformanceLog) error {
	if log.ID == "" {
		log.ID = uuid.New().String()
	}
	
	query := `
		INSERT INTO performance_logs (id, service_name, endpoint, method, status_code, 
									  response_time, user_id, ip_address, timestamp)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
	`
	
	_, err := r.db.Exec(query,
		log.ID, log.ServiceName, log.Endpoint, log.Method, log.StatusCode,
		log.ResponseTime, log.UserID, log.IPAddress, log.Timestamp,
	)
	
	return err
}

func (r *MonitoringRepository) CreatePerformanceLogsBatch(logs []*monitoring.PerformanceLog) error {
	if len(logs) == 0 {
		return nil
	}
	
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	tx, err := r.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer tx.Rollback()
	
	stmt, err := tx.Prepare(`
		INSERT INTO performance_logs (id, service_name, endpoint, method, status_code,
									  response_time, user_id, ip_address, timestamp)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
	`)
	if err != nil {
		return err
	}
	defer stmt.Close()
	
	for _, log := range logs {
		if log.ID == "" {
			log.ID = uuid.New().String()
		}
		
		_, err := stmt.Exec(
			log.ID, log.ServiceName, log.Endpoint, log.Method, log.StatusCode,
			log.ResponseTime, log.UserID, log.IPAddress, log.Timestamp,
		)
		if err != nil {
			return err
		}
	}
	
	return tx.Commit()
}

func (r *MonitoringRepository) GetPerformanceLogs(serviceName string, from, to time.Time, limit int) ([]*monitoring.PerformanceLog, error) {
	query := `
		SELECT id, service_name, endpoint, method, status_code, response_time,
			   user_id, ip_address, timestamp
		FROM performance_logs
		WHERE service_name = $1 AND timestamp BETWEEN $2 AND $3
		ORDER BY timestamp DESC
		LIMIT $4
	`
	
	rows, err := r.db.Query(query, serviceName, from, to, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanPerformanceLogs(rows)
}

func (r *MonitoringRepository) GetPerformanceByEndpoint(serviceName, endpoint string, from, to time.Time) ([]*monitoring.PerformanceLog, error) {
	query := `
		SELECT id, service_name, endpoint, method, status_code, response_time,
			   user_id, ip_address, timestamp
		FROM performance_logs
		WHERE service_name = $1 AND endpoint = $2 AND timestamp BETWEEN $3 AND $4
		ORDER BY timestamp DESC
		LIMIT 1000
	`
	
	rows, err := r.db.Query(query, serviceName, endpoint, from, to)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanPerformanceLogs(rows)
}

func (r *MonitoringRepository) GetAverageResponseTime(serviceName string, from, to time.Time) (float64, error) {
	query := `
		SELECT COALESCE(AVG(response_time), 0)
		FROM performance_logs
		WHERE service_name = $1 AND timestamp BETWEEN $2 AND $3
	`
	
	var avg float64
	err := r.db.QueryRow(query, serviceName, from, to).Scan(&avg)
	return avg, err
}

func (r *MonitoringRepository) GetPercentileResponseTime(serviceName string, percentile float64, from, to time.Time) (float64, error) {
	query := `
		SELECT PERCENTILE_CONT($1) WITHIN GROUP (ORDER BY response_time)
		FROM performance_logs
		WHERE service_name = $2 AND timestamp BETWEEN $3 AND $4
	`
	
	var result float64
	err := r.db.QueryRow(query, percentile/100, serviceName, from, to).Scan(&result)
	return result, err
}

func (r *MonitoringRepository) DeleteOldPerformanceLogs(before time.Time) (int64, error) {
	query := `DELETE FROM performance_logs WHERE timestamp < $1`
	result, err := r.db.Exec(query, before)
	if err != nil {
		return 0, err
	}
	return result.RowsAffected()
}

// ===== Helper functions =====

func (r *MonitoringRepository) scanMetrics(rows *sql.Rows) ([]*monitoring.Metric, error) {
	var metrics []*monitoring.Metric
	
	for rows.Next() {
		metric := &monitoring.Metric{}
		err := rows.Scan(
			&metric.ID, &metric.ServiceName, &metric.MetricName,
			&metric.Value, &metric.Unit, &metric.Labels, &metric.Timestamp,
		)
		if err != nil {
			return nil, err
		}
		metrics = append(metrics, metric)
	}
	
	return metrics, rows.Err()
}

func (r *MonitoringRepository) scanPerformanceLogs(rows *sql.Rows) ([]*monitoring.PerformanceLog, error) {
	var logs []*monitoring.PerformanceLog
	
	for rows.Next() {
		log := &monitoring.PerformanceLog{}
		err := rows.Scan(
			&log.ID, &log.ServiceName, &log.Endpoint, &log.Method,
			&log.StatusCode, &log.ResponseTime, &log.UserID,
			&log.IPAddress, &log.Timestamp,
		)
		if err != nil {
			return nil, err
		}
		logs = append(logs, log)
	}
	
	return logs, rows.Err()
}

func (r *MonitoringRepository) HealthCheck() error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	
	return r.db.PingContext(ctx)
}