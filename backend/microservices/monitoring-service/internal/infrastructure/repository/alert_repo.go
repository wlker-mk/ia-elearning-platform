package repository

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/domain/alert"
	"github.com/google/uuid"
)

type AlertRepository struct {
	db *sql.DB
}

func NewAlertRepository(db *sql.DB) *AlertRepository {
	return &AlertRepository{db: db}
}

// ===== CRUD Operations =====

func (r *AlertRepository) Create(a *alert.Alert) error {
	if a.ID == "" {
		a.ID = uuid.New().String()
	}
	
	query := `
		INSERT INTO alerts (id, title, description, severity, status, service_name,
							metric_name, threshold, actual_value, triggered_at, 
							created_at, updated_at)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
	`
	
	now := time.Now()
	_, err := r.db.Exec(query,
		a.ID, a.Title, a.Description, a.Severity, a.Status, a.ServiceName,
		a.MetricName, a.Threshold, a.ActualValue, a.TriggeredAt,
		now, now,
	)
	
	return err
}

func (r *AlertRepository) Update(a *alert.Alert) error {
	query := `
		UPDATE alerts SET
			title = $2, description = $3, severity = $4, status = $5,
			service_name = $6, metric_name = $7, threshold = $8,
			actual_value = $9, updated_at = $10
		WHERE id = $1
	`
	
	_, err := r.db.Exec(query,
		a.ID, a.Title, a.Description, a.Severity, a.Status, a.ServiceName,
		a.MetricName, a.Threshold, a.ActualValue, time.Now(),
	)
	
	return err
}

func (r *AlertRepository) GetByID(id string) (*alert.Alert, error) {
	query := `
		SELECT id, title, description, severity, status, service_name,
			   metric_name, threshold, actual_value, triggered_at,
			   created_at, updated_at
		FROM alerts
		WHERE id = $1
	`
	
	a := &alert.Alert{}
	err := r.db.QueryRow(query, id).Scan(
		&a.ID, &a.Title, &a.Description, &a.Severity, &a.Status,
		&a.ServiceName, &a.MetricName, &a.Threshold, &a.ActualValue,
		&a.TriggeredAt, &a.CreatedAt, &a.UpdatedAt,
	)
	
	if err == sql.ErrNoRows {
		return nil, fmt.Errorf("alert not found: %s", id)
	}
	
	return a, err
}

func (r *AlertRepository) Delete(id string) error {
	query := `DELETE FROM alerts WHERE id = $1`
	result, err := r.db.Exec(query, id)
	if err != nil {
		return err
	}
	
	rows, _ := result.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("alert not found: %s", id)
	}
	
	return nil
}

// ===== Query Operations =====

func (r *AlertRepository) GetAll(limit, offset int) ([]*alert.Alert, error) {
	query := `
		SELECT id, title, description, severity, status, service_name,
			   metric_name, threshold, actual_value, triggered_at,
			   created_at, updated_at
		FROM alerts
		ORDER BY triggered_at DESC
		LIMIT $1 OFFSET $2
	`
	
	rows, err := r.db.Query(query, limit, offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanAlerts(rows)
}

func (r *AlertRepository) GetByStatus(status alert.AlertStatus, limit int) ([]*alert.Alert, error) {
	query := `
		SELECT id, title, description, severity, status, service_name,
			   metric_name, threshold, actual_value, triggered_at,
			   created_at, updated_at
		FROM alerts
		WHERE status = $1
		ORDER BY triggered_at DESC
		LIMIT $2
	`
	
	rows, err := r.db.Query(query, status, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanAlerts(rows)
}

func (r *AlertRepository) GetBySeverity(severity alert.AlertSeverity, limit int) ([]*alert.Alert, error) {
	query := `
		SELECT id, title, description, severity, status, service_name,
			   metric_name, threshold, actual_value, triggered_at,
			   created_at, updated_at
		FROM alerts
		WHERE severity = $1
		ORDER BY triggered_at DESC
		LIMIT $2
	`
	
	rows, err := r.db.Query(query, severity, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanAlerts(rows)
}

func (r *AlertRepository) GetByService(serviceName string, limit int) ([]*alert.Alert, error) {
	query := `
		SELECT id, title, description, severity, status, service_name,
			   metric_name, threshold, actual_value, triggered_at,
			   created_at, updated_at
		FROM alerts
		WHERE service_name = $1
		ORDER BY triggered_at DESC
		LIMIT $2
	`
	
	rows, err := r.db.Query(query, serviceName, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanAlerts(rows)
}

func (r *AlertRepository) GetActiveAlerts() ([]*alert.Alert, error) {
	query := `
		SELECT id, title, description, severity, status, service_name,
			   metric_name, threshold, actual_value, triggered_at,
			   created_at, updated_at
		FROM alerts
		WHERE status IN ('OPEN', 'ACKNOWLEDGED')
		ORDER BY severity DESC, triggered_at DESC
	`
	
	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanAlerts(rows)
}

func (r *AlertRepository) GetCriticalAlerts() ([]*alert.Alert, error) {
	query := `
		SELECT id, title, description, severity, status, service_name,
			   metric_name, threshold, actual_value, triggered_at,
			   created_at, updated_at
		FROM alerts
		WHERE severity = 'CRITICAL' AND status IN ('OPEN', 'ACKNOWLEDGED')
		ORDER BY triggered_at DESC
	`
	
	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	
	return r.scanAlerts(rows)
}

// ===== Status Management =====

func (r *AlertRepository) Acknowledge(id string) error {
	query := `
		UPDATE alerts 
		SET status = 'ACKNOWLEDGED', updated_at = $2
		WHERE id = $1 AND status = 'OPEN'
	`
	
	result, err := r.db.Exec(query, id, time.Now())
	if err != nil {
		return err
	}
	
	rows, _ := result.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("alert not found or already acknowledged: %s", id)
	}
	
	return nil
}

func (r *AlertRepository) Resolve(id string) error {
	query := `
		UPDATE alerts 
		SET status = 'RESOLVED', updated_at = $2
		WHERE id = $1 AND status IN ('OPEN', 'ACKNOWLEDGED')
	`
	
	result, err := r.db.Exec(query, id, time.Now())
	if err != nil {
		return err
	}
	
	rows, _ := result.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("alert not found or already resolved: %s", id)
	}
	
	return nil
}

func (r *AlertRepository) Close(id string) error {
	query := `
		UPDATE alerts 
		SET status = 'CLOSED', updated_at = $2
		WHERE id = $1
	`
	
	result, err := r.db.Exec(query, id, time.Now())
	if err != nil {
		return err
	}
	
	rows, _ := result.RowsAffected()
	if rows == 0 {
		return fmt.Errorf("alert not found: %s", id)
	}
	
	return nil
}

// ===== Statistics =====

func (r *AlertRepository) GetStatistics(from, to time.Time) (*alert.AlertStatistics, error) {
	// Total alerts
	var totalAlerts int
	_ = r.db.QueryRow(`
		SELECT COUNT(*) FROM alerts 
		WHERE triggered_at BETWEEN $1 AND $2
	`, from, to).Scan(&totalAlerts)
	
	// By status
	var openAlerts, acknowledgedAlerts, resolvedAlerts int
	_ = r.db.QueryRow(`
		SELECT COUNT(*) FROM alerts 
		WHERE status = 'OPEN' AND triggered_at BETWEEN $1 AND $2
	`, from, to).Scan(&openAlerts)
	
	_ = r.db.QueryRow(`
		SELECT COUNT(*) FROM alerts 
		WHERE status = 'ACKNOWLEDGED' AND triggered_at BETWEEN $1 AND $2
	`, from, to).Scan(&acknowledgedAlerts)
	
	_ = r.db.QueryRow(`
		SELECT COUNT(*) FROM alerts 
		WHERE status = 'RESOLVED' AND triggered_at BETWEEN $1 AND $2
	`, from, to).Scan(&resolvedAlerts)
	
	// By severity
	bySeverity := make(map[alert.AlertSeverity]int)
	rows, _ := r.db.Query(`
		SELECT severity, COUNT(*) 
		FROM alerts 
		WHERE triggered_at BETWEEN $1 AND $2
		GROUP BY severity
	`, from, to)
	defer rows.Close()
	
	for rows.Next() {
		var severity alert.AlertSeverity
		var count int
		rows.Scan(&severity, &count)
		bySeverity[severity] = count
	}
	
	// By service
	byService := make(map[string]int)
	rows2, _ := r.db.Query(`
		SELECT service_name, COUNT(*) 
		FROM alerts 
		WHERE triggered_at BETWEEN $1 AND $2 AND service_name IS NOT NULL
		GROUP BY service_name
	`, from, to)
	defer rows2.Close()
	
	for rows2.Next() {
		var service string
		var count int
		rows2.Scan(&service, &count)
		byService[service] = count
	}
	
	// Average resolution time
	var avgResolutionSeconds sql.NullFloat64
	_ = r.db.QueryRow(`
		SELECT AVG(EXTRACT(EPOCH FROM (updated_at - triggered_at)))
		FROM alerts 
		WHERE status = 'RESOLVED' AND triggered_at BETWEEN $1 AND $2
	`, from, to).Scan(&avgResolutionSeconds)
	
	var avgResolution time.Duration
	if avgResolutionSeconds.Valid {
		avgResolution = time.Duration(avgResolutionSeconds.Float64) * time.Second
	}
	
	return &alert.AlertStatistics{
		TotalAlerts:           totalAlerts,
		OpenAlerts:            openAlerts,
		AcknowledgedAlerts:    acknowledgedAlerts,
		ResolvedAlerts:        resolvedAlerts,
		BySeverity:            bySeverity,
		ByService:             byService,
		AverageResolutionTime: avgResolution,
	}, nil
}

func (r *AlertRepository) CountByStatus(status alert.AlertStatus) (int64, error) {
	query := `SELECT COUNT(*) FROM alerts WHERE status = $1`
	
	var count int64
	err := r.db.QueryRow(query, status).Scan(&count)
	return count, err
}

func (r *AlertRepository) CountBySeverity(severity alert.AlertSeverity) (int64, error) {
	query := `SELECT COUNT(*) FROM alerts WHERE severity = $1`
	
	var count int64
	err := r.db.QueryRow(query, severity).Scan(&count)
	return count, err
}

func (r *AlertRepository) GetAverageResolutionTime(from, to time.Time) (time.Duration, error) {
	query := `
		SELECT AVG(EXTRACT(EPOCH FROM (updated_at - triggered_at)))
		FROM alerts 
		WHERE status = 'RESOLVED' AND triggered_at BETWEEN $1 AND $2
	`
	
	var avgSeconds sql.NullFloat64
	err := r.db.QueryRow(query, from, to).Scan(&avgSeconds)
	if err != nil || !avgSeconds.Valid {
		return 0, err
	}
	
	return time.Duration(avgSeconds.Float64) * time.Second, nil
}

// ===== Cleanup =====

func (r *AlertRepository) DeleteOldResolvedAlerts(before time.Time) (int64, error) {
	query := `
		DELETE FROM alerts 
		WHERE status = 'RESOLVED' AND updated_at < $1
	`
	
	result, err := r.db.Exec(query, before)
	if err != nil {
		return 0, err
	}
	
	return result.RowsAffected()
}

// ===== Alert Rules (Bonus) =====

func (r *AlertRepository) CreateRule(rule *alert.AlertRule) error {
	// TODO: Implémenter si table alert_rules existe
	return fmt.Errorf("not implemented yet")
}

func (r *AlertRepository) GetRulesByService(serviceName string) ([]*alert.AlertRule, error) {
	// TODO: Implémenter si table alert_rules existe
	return nil, fmt.Errorf("not implemented yet")
}

func (r *AlertRepository) GetEnabledRules() ([]*alert.AlertRule, error) {
	// TODO: Implémenter si table alert_rules existe
	return nil, fmt.Errorf("not implemented yet")
}

func (r *AlertRepository) UpdateRule(rule *alert.AlertRule) error {
	// TODO: Implémenter si table alert_rules existe
	return fmt.Errorf("not implemented yet")
}

func (r *AlertRepository) DeleteRule(id string) error {
	// TODO: Implémenter si table alert_rules existe
	return fmt.Errorf("not implemented yet")
}

// ===== Helper Functions =====

func (r *AlertRepository) scanAlerts(rows *sql.Rows) ([]*alert.Alert, error) {
	var alerts []*alert.Alert
	
	for rows.Next() {
		a := &alert.Alert{}
		err := rows.Scan(
			&a.ID, &a.Title, &a.Description, &a.Severity, &a.Status,
			&a.ServiceName, &a.MetricName, &a.Threshold, &a.ActualValue,
			&a.TriggeredAt, &a.CreatedAt, &a.UpdatedAt,
		)
		if err != nil {
			return nil, err
		}
		alerts = append(alerts, a)
	}
	
	return alerts, rows.Err()
}