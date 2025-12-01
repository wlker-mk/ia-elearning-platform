package ratelimit

type Store interface {
	Increment(key string) (int64, error)
	Expire(key string, seconds int) error
}
