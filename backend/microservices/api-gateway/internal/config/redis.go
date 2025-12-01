package config

type RedisConfig struct {
	URL      string
	Password string
	DB       int
}

func LoadRedisConfig() *RedisConfig {
	return &RedisConfig{
		URL:      getEnv("REDIS_URL", "localhost:6379"),
		Password: getEnv("REDIS_PASSWORD", ""),
		DB:       0,
	}
}
