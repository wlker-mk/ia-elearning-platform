package cache

import (
	"context"
	"time"

	"github.com/go-redis/redis/v8"
)

type RedisCache struct {
	client *redis.Client
}

func NewRedisCache(client *redis.Client) *RedisCache {
	return &RedisCache{client: client}
}

func (r *RedisCache) Get(key string) (string, error) {
	ctx := context.Background()
	return r.client.Get(ctx, key).Result()
}

func (r *RedisCache) Set(key string, value interface{}, expiration time.Duration) error {
	ctx := context.Background()
	return r.client.Set(ctx, key, value, expiration).Err()
}

func (r *RedisCache) Delete(key string) error {
	ctx := context.Background()
	return r.client.Del(ctx, key).Err()
}
