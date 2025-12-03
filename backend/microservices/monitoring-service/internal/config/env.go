package config

import "os"

// Env represents the application environment
type Env string

const (
	Development Env = "development"
	Production  Env = "production"
	Test        Env = "test"
)

// GetEnv returns the current environment
func GetEnv() Env {
	env := os.Getenv("MODE")
	switch env {
	case "production":
		return Production
	case "test":
		return Test
	default:
		return Development
	}
}

// IsDevelopment checks if running in development mode
func IsDevelopment() bool {
	return GetEnv() == Development
}

// IsProduction checks if running in production mode
func IsProduction() bool {
	return GetEnv() == Production
}
