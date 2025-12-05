package database

import (
	"context"
	"database/sql"
	"fmt"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/config"
	_ "github.com/lib/pq"
)

type PostgresDB struct {
	DB *sql.DB
}

// NewPostgresDB crée une nouvelle connexion à PostgreSQL optimisée pour monitoring
func NewPostgresDB(cfg *config.DatabaseConfig) (*PostgresDB, error) {
	dsn := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		cfg.Host, cfg.Port, cfg.User, cfg.Password, cfg.DBName,
	)

	db, err := sql.Open("postgres", dsn)
	if err != nil {
		return nil, fmt.Errorf("failed to open database: %w", err)
	}

	// Configuration optimisée pour monitoring (faible overhead)
	db.SetMaxOpenConns(20)              // Limite pour éviter saturation
	db.SetMaxIdleConns(5)               // Connexions idle pour réactivité
	db.SetConnMaxLifetime(5 * time.Minute)
	db.SetConnMaxIdleTime(10 * time.Minute)

	// Vérifier la connexion
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	
	if err := db.PingContext(ctx); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return &PostgresDB{DB: db}, nil
}

// Close ferme la connexion
func (p *PostgresDB) Close() error {
	return p.DB.Close()
}

// Health vérifie l'état de la connexion (monitoring du monitoring!)
func (p *PostgresDB) Health() error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	
	return p.DB.PingContext(ctx)
}

// InitSchema initialise le schéma basé sur Prisma
func (p *PostgresDB) InitSchema() error {
	schema := `
	-- Types ENUM
	CREATE TYPE service_status AS ENUM ('HEALTHY', 'DEGRADED', 'DOWN', 'MAINTENANCE');
	CREATE TYPE alert_severity AS ENUM ('INFO', 'WARNING', 'ERROR', 'CRITICAL');
	CREATE TYPE alert_status AS ENUM ('OPEN', 'ACKNOWLEDGED', 'RESOLVED', 'CLOSED');

	-- Table service_health
	CREATE TABLE IF NOT EXISTS service_health (
		id VARCHAR(36) PRIMARY KEY,
		service_name VARCHAR(255) UNIQUE NOT NULL,
		status service_status DEFAULT 'HEALTHY',
		avg_response_time FLOAT,
		p95_response_time FLOAT,
		p99_response_time FLOAT,
		uptime FLOAT,
		downtime INTEGER,
		request_count INTEGER DEFAULT 0,
		error_count INTEGER DEFAULT 0,
		cpu_usage FLOAT,
		memory_usage FLOAT,
		disk_usage FLOAT,
		last_check_at TIMESTAMP NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Table metrics (optimisée pour insertion rapide)
	CREATE TABLE IF NOT EXISTS metrics (
		id VARCHAR(36) PRIMARY KEY,
		service_name VARCHAR(255) NOT NULL,
		metric_name VARCHAR(255) NOT NULL,
		value FLOAT NOT NULL,
		unit VARCHAR(50),
		labels JSONB,
		timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	-- Index pour requêtes temporelles rapides
	CREATE INDEX IF NOT EXISTS idx_metrics_service_name_timestamp 
		ON metrics(service_name, metric_name, timestamp DESC);
	CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
		ON metrics(timestamp DESC);

	-- Table alerts
	CREATE TABLE IF NOT EXISTS alerts (
		id VARCHAR(36) PRIMARY KEY,
		title VARCHAR(500) NOT NULL,
		description TEXT NOT NULL,
		severity alert_severity NOT NULL,
		status alert_status DEFAULT 'OPEN',
		service_name VARCHAR(255),
		metric_name VARCHAR(255),
		threshold FLOAT,
		actual_value FLOAT,
		triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
	CREATE INDEX IF NOT EXISTS idx_alerts_service ON alerts(service_name, status);

	-- Table performance_logs (optimisée pour volume élevé)
	CREATE TABLE IF NOT EXISTS performance_logs (
		id VARCHAR(36) PRIMARY KEY,
		service_name VARCHAR(255) NOT NULL,
		endpoint VARCHAR(500) NOT NULL,
		method VARCHAR(10) NOT NULL,
		status_code INTEGER NOT NULL,
		response_time INTEGER NOT NULL,
		user_id VARCHAR(36),
		ip_address VARCHAR(45),
		timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_perf_service_endpoint_timestamp 
		ON performance_logs(service_name, endpoint, timestamp DESC);
	CREATE INDEX IF NOT EXISTS idx_perf_timestamp 
		ON performance_logs(timestamp DESC);

	-- Table error_logs
	CREATE TABLE IF NOT EXISTS error_logs (
		id VARCHAR(36) PRIMARY KEY,
		service_name VARCHAR(255) NOT NULL,
		error_type VARCHAR(255) NOT NULL,
		error_message TEXT NOT NULL,
		stack_trace TEXT,
		endpoint VARCHAR(500),
		method VARCHAR(10),
		user_id VARCHAR(36),
		occurrences INTEGER DEFAULT 1,
		first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		is_resolved BOOLEAN DEFAULT FALSE,
		resolved_at TIMESTAMP,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_error_service_type 
		ON error_logs(service_name, error_type, is_resolved);

	-- Table uptime
	CREATE TABLE IF NOT EXISTS uptime (
		id VARCHAR(36) PRIMARY KEY,
		service_name VARCHAR(255) NOT NULL,
		date DATE NOT NULL,
		status service_status NOT NULL,
		uptime_seconds INTEGER DEFAULT 0,
		downtime_seconds INTEGER DEFAULT 0,
		incident_count INTEGER DEFAULT 0,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		UNIQUE(service_name, date)
	);

	CREATE INDEX IF NOT EXISTS idx_uptime_service_date 
		ON uptime(service_name, date DESC);

	-- Trigger pour updated_at automatique
	CREATE OR REPLACE FUNCTION update_updated_at_column()
	RETURNS TRIGGER AS $$
	BEGIN
		NEW.updated_at = CURRENT_TIMESTAMP;
		RETURN NEW;
	END;
	$$ language 'plpgsql';

	DROP TRIGGER IF EXISTS update_service_health_updated_at ON service_health;
	CREATE TRIGGER update_service_health_updated_at
		BEFORE UPDATE ON service_health
		FOR EACH ROW
		EXECUTE FUNCTION update_updated_at_column();

	DROP TRIGGER IF EXISTS update_alerts_updated_at ON alerts;
	CREATE TRIGGER update_alerts_updated_at
		BEFORE UPDATE ON alerts
		FOR EACH ROW
		EXECUTE FUNCTION update_updated_at_column();
	`

	_, err := p.DB.Exec(schema)
	return err
}

// Stats retourne les statistiques de la connexion
func (p *PostgresDB) Stats() sql.DBStats {
	return p.DB.Stats()
}