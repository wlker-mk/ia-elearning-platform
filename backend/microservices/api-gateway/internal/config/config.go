package config

import "os"

type Config struct {
	ServicePort string
	JWTSecret   string
	RedisURL    string
	Debug       bool
}

func Load() *Config {
	return &Config{
		ServicePort: getEnv("SERVICE_PORT", "8000"),
		JWTSecret:   getEnv("JWT_SECRET", "default-secret"),
		RedisURL:    getEnv("REDIS_URL", "localhost:6379"),
		Debug:       getEnv("DEBUG", "false") == "true",
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
