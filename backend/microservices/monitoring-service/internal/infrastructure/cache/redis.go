package cache

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/internal/config"
	"github.com/redis/go-redis/v9"
)

const (
	// Préfixes pour organisation des clés
	PrefixServiceStatus  = "svc:status:"
	PrefixServiceMetrics = "svc:metrics:"
	PrefixAlert          = "alert:"
	PrefixCounter        = "counter:"
	PrefixHealth         = "health:"
	
	// TTL par défaut pour monitoring (court pour fraîcheur)
	DefaultTTL = 30 * time.Second
	MetricTTL  = 60 * time.Second
	HealthTTL  = 15 * time.Second
)

type RedisCache struct {
	client *redis.Client
	ctx    context.Context
}

// NewRedisCache crée une instance Redis optimisée pour monitoring
func NewRedisCache(cfg *config.RedisConfig) (*RedisCache, error) {
	client := redis.NewClient(&redis.Options{
		Addr:         fmt.Sprintf("%s:%s", cfg.Host, cfg.Port),
		Password:     cfg.Password,
		DB:           0,
		PoolSize:     15,           // Pool adapté au monitoring
		MinIdleConns: 3,
		MaxRetries:   2,            // Retry limité (faible latence prioritaire)
		DialTimeout:  3 * time.Second,
		ReadTimeout:  2 * time.Second,
		WriteTimeout: 2 * time.Second,
	})

	ctx := context.Background()

	// Vérification connexion
	if err := client.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("redis connection failed: %w", err)
	}

	return &RedisCache{
		client: client,
		ctx:    ctx,
	}, nil
}

// === Opérations de base ===

// Set stocke une valeur avec expiration
func (r *RedisCache) Set(key string, value interface{}, expiration time.Duration) error {
	data, err := json.Marshal(value)
	if err != nil {
		return fmt.Errorf("marshal failed: %w", err)
	}

	return r.client.Set(r.ctx, key, data, expiration).Err()
}

// Get récupère une valeur
func (r *RedisCache) Get(key string, dest interface{}) error {
	data, err := r.client.Get(r.ctx, key).Bytes()
	if err != nil {
		if err == redis.Nil {
			return fmt.Errorf("key not found: %s", key)
		}
		return err
	}

	return json.Unmarshal(data, dest)
}

// Delete supprime une ou plusieurs clés
func (r *RedisCache) Delete(keys ...string) error {
	if len(keys) == 0 {
		return nil
	}
	return r.client.Del(r.ctx, keys...).Err()
}

// === Opérations monitoring spécifiques ===

// SetServiceHealth stocke l'état de santé d'un service
func (r *RedisCache) SetServiceHealth(serviceName string, health interface{}) error {
	key := PrefixHealth + serviceName
	return r.Set(key, health, HealthTTL)
}

// GetServiceHealth récupère l'état de santé
func (r *RedisCache) GetServiceHealth(serviceName string, dest interface{}) error {
	key := PrefixHealth + serviceName
	return r.Get(key, dest)
}

// SetServiceStatus stocke le statut rapide d'un service
func (r *RedisCache) SetServiceStatus(serviceName, status string) error {
	key := PrefixServiceStatus + serviceName
	return r.client.Set(r.ctx, key, status, DefaultTTL).Err()
}

// GetServiceStatus récupère le statut
func (r *RedisCache) GetServiceStatus(serviceName string) (string, error) {
	key := PrefixServiceStatus + serviceName
	return r.client.Get(r.ctx, key).Result()
}

// === Métriques en temps réel ===

// IncrMetric incrémente un compteur de métrique
func (r *RedisCache) IncrMetric(serviceName, metricName string) (int64, error) {
	key := fmt.Sprintf("%s%s:%s", PrefixCounter, serviceName, metricName)
	val, err := r.client.Incr(r.ctx, key).Result()
	if err != nil {
		return 0, err
	}
	
	// Définir expiration si nouvelle clé
	r.client.Expire(r.ctx, key, MetricTTL)
	return val, nil
}

// IncrMetricBy incrémente d'une valeur spécifique
func (r *RedisCache) IncrMetricBy(serviceName, metricName string, value int64) (int64, error) {
	key := fmt.Sprintf("%s%s:%s", PrefixCounter, serviceName, metricName)
	val, err := r.client.IncrBy(r.ctx, key, value).Result()
	if err != nil {
		return 0, err
	}
	
	r.client.Expire(r.ctx, key, MetricTTL)
	return val, nil
}

// GetMetric récupère la valeur d'un compteur
func (r *RedisCache) GetMetric(serviceName, metricName string) (int64, error) {
	key := fmt.Sprintf("%s%s:%s", PrefixCounter, serviceName, metricName)
	val, err := r.client.Get(r.ctx, key).Int64()
	if err == redis.Nil {
		return 0, nil
	}
	return val, err
}

// ResetMetric remet un compteur à zéro
func (r *RedisCache) ResetMetric(serviceName, metricName string) error {
	key := fmt.Sprintf("%s%s:%s", PrefixCounter, serviceName, metricName)
	return r.client.Del(r.ctx, key).Err()
}

// === Métriques de performance (moyenne mobile) ===

// RecordResponseTime enregistre un temps de réponse (liste pour calcul p95/p99)
func (r *RedisCache) RecordResponseTime(serviceName string, responseTime int64) error {
	key := fmt.Sprintf("%s%s:response_times", PrefixServiceMetrics, serviceName)
	
	pipe := r.client.Pipeline()
	pipe.LPush(r.ctx, key, responseTime)
	pipe.LTrim(r.ctx, key, 0, 99) // Garder les 100 dernières valeurs
	pipe.Expire(r.ctx, key, 5*time.Minute)
	
	_, err := pipe.Exec(r.ctx)
	return err
}

// GetResponseTimes récupère les temps de réponse récents
func (r *RedisCache) GetResponseTimes(serviceName string) ([]int64, error) {
	key := fmt.Sprintf("%s%s:response_times", PrefixServiceMetrics, serviceName)
	
	vals, err := r.client.LRange(r.ctx, key, 0, -1).Result()
	if err != nil {
		return nil, err
	}
	
	times := make([]int64, 0, len(vals))
	for _, v := range vals {
		var t int64
		if err := json.Unmarshal([]byte(v), &t); err == nil {
			times = append(times, t)
		}
	}
	
	return times, nil
}

// === Alertes ===

// CacheAlert stocke une alerte temporairement
func (r *RedisCache) CacheAlert(alertID string, alert interface{}) error {
	key := PrefixAlert + alertID
	return r.Set(key, alert, 10*time.Minute)
}

// GetCachedAlert récupère une alerte
func (r *RedisCache) GetCachedAlert(alertID string, dest interface{}) error {
	key := PrefixAlert + alertID
	return r.Get(key, dest)
}

// === Pattern matching ===

// GetKeysByPattern récupère les clés par pattern
func (r *RedisCache) GetKeysByPattern(pattern string) ([]string, error) {
	return r.client.Keys(r.ctx, pattern).Result()
}

// DeleteByPattern supprime toutes les clés correspondant au pattern
func (r *RedisCache) DeleteByPattern(pattern string) error {
	keys, err := r.GetKeysByPattern(pattern)
	if err != nil {
		return err
	}
	
	if len(keys) == 0 {
		return nil
	}
	
	return r.Delete(keys...)
}

// === Utilitaires ===

// Health vérifie la santé de Redis
func (r *RedisCache) Health() error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	
	return r.client.Ping(ctx).Err()
}

// Close ferme la connexion
func (r *RedisCache) Close() error {
	return r.client.Close()
}

// FlushDB nettoie la base (DEV uniquement)
func (r *RedisCache) FlushDB() error {
	return r.client.FlushDB(r.ctx).Err()
}

// Stats retourne les statistiques de pool
func (r *RedisCache) Stats() *redis.PoolStats {
	return r.client.PoolStats()
}

// Exists vérifie si une clé existe
func (r *RedisCache) Exists(keys ...string) (int64, error) {
	return r.client.Exists(r.ctx, keys...).Result()
}

// Expire définit une expiration
func (r *RedisCache) Expire(key string, expiration time.Duration) error {
	return r.client.Expire(r.ctx, key, expiration).Err()
}

// TTL récupère le temps restant avant expiration
func (r *RedisCache) TTL(key string) (time.Duration, error) {
	return r.client.TTL(r.ctx, key).Result()
}