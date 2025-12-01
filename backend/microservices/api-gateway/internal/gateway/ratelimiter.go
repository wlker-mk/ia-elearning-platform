package gateway

import (
	"context"
	"time"

	"github.com/go-redis/redis/v8"
)

type RateLimiter struct {
	client *redis.Client
}

func NewRateLimiter(client *redis.Client) *RateLimiter {
	return &RateLimiter{client: client}
}

func (rl *RateLimiter) Allow(key string, max int, window time.Duration) (bool, error) {
	ctx := context.Background()
	
	pipe := rl.client.Pipeline()
	incr := pipe.Incr(ctx, key)
	pipe.Expire(ctx, key, window)
	
	_, err := pipe.Exec(ctx)
	if err != nil {
		return false, err
	}
	
	return incr.Val() <= int64(max), nil
}
