package logger

import (
	"os"
	"time"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

var Log *zap.Logger

// Init initialise le logger global
func Init(env string) error {
	var config zap.Config
	
	if env == "production" {
		config = zap.NewProductionConfig()
		config.EncoderConfig.TimeKey = "timestamp"
		config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
	} else {
		config = zap.NewDevelopmentConfig()
		config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
	}
	
	// Configuration optimisée pour monitoring (faible overhead)
	config.DisableCaller = false
	config.DisableStacktrace = false
	config.Sampling = &zap.SamplingConfig{
		Initial:    100,
		Thereafter: 100,
	}
	
	logger, err := config.Build(
		zap.AddCallerSkip(1),
		zap.AddStacktrace(zapcore.ErrorLevel),
	)
	if err != nil {
		return err
	}
	
	Log = logger
	return nil
}

// Sync flush les logs bufferisés
func Sync() {
	if Log != nil {
		_ = Log.Sync()
	}
}

// Info log niveau info
func Info(msg string, fields ...zap.Field) {
	if Log != nil {
		Log.Info(msg, fields...)
	}
}

// Debug log niveau debug
func Debug(msg string, fields ...zap.Field) {
	if Log != nil {
		Log.Debug(msg, fields...)
	}
}

// Warn log niveau warning
func Warn(msg string, fields ...zap.Field) {
	if Log != nil {
		Log.Warn(msg, fields...)
	}
}

// Error log niveau error
func Error(msg string, fields ...zap.Field) {
	if Log != nil {
		Log.Error(msg, fields...)
	}
}

// Fatal log niveau fatal (termine le programme)
func Fatal(msg string, fields ...zap.Field) {
	if Log != nil {
		Log.Fatal(msg, fields...)
	}
	os.Exit(1)
}

// With crée un logger avec des champs contextuels
func With(fields ...zap.Field) *zap.Logger {
	if Log != nil {
		return Log.With(fields...)
	}
	return zap.NewNop()
}

// Fields helpers pour logging structuré

// String crée un champ string
func String(key, val string) zap.Field {
	return zap.String(key, val)
}

// Int crée un champ int
func Int(key string, val int) zap.Field {
	return zap.Int(key, val)
}

// Int64 crée un champ int64
func Int64(key string, val int64) zap.Field {
	return zap.Int64(key, val)
}

// Float64 crée un champ float64
func Float64(key string, val float64) zap.Field {
	return zap.Float64(key, val)
}

// Bool crée un champ bool
func Bool(key string, val bool) zap.Field {
	return zap.Bool(key, val)
}

// Err crée un champ error
func Err(err error) zap.Field {
	return zap.Error(err)
}

// Duration crée un champ duration
func Duration(key string, val time.Duration) zap.Field {
	return zap.Duration(key, val)
}

// Time crée un champ time
func Time(key string, val time.Time) zap.Field {
	return zap.Time(key, val)
}

// Any crée un champ de type quelconque
func Any(key string, val interface{}) zap.Field {
	return zap.Any(key, val)
}

// Monitoring specific loggers

// LogServiceHealth log les informations de santé d'un service
func LogServiceHealth(serviceName, status string, responseTime int64) {
	Info("Service health check",
		String("service", serviceName),
		String("status", status),
		Int64("response_time_ms", responseTime),
	)
}

// LogMetric log une métrique
func LogMetric(serviceName, metricName string, value float64) {
	Debug("Metric recorded",
		String("service", serviceName),
		String("metric", metricName),
		Float64("value", value),
	)
}

// LogAlert log une alerte
func LogAlert(severity, title, serviceName string) {
	Warn("Alert triggered",
		String("severity", severity),
		String("title", title),
		String("service", serviceName),
	)
}

// LogError log une erreur applicative
func LogError(serviceName, errorType, errorMsg string) {
	Error("Application error",
		String("service", serviceName),
		String("error_type", errorType),
		String("error_message", errorMsg),
	)
}

// LogPerformance log les performances d'un endpoint
func LogPerformance(serviceName, endpoint, method string, statusCode, responseTime int) {
	Debug("Request performance",
		String("service", serviceName),
		String("endpoint", endpoint),
		String("method", method),
		Int("status_code", statusCode),
		Int("response_time_ms", responseTime),
	)
}

// LogCacheOperation log une opération cache
func LogCacheOperation(operation, key string, hit bool) {
	Debug("Cache operation",
		String("operation", operation),
		String("key", key),
		Bool("hit", hit),
	)
}

// LogDatabaseOperation log une opération base de données
func LogDatabaseOperation(operation, table string, duration time.Duration, err error) {
	if err != nil {
		Error("Database operation failed",
			String("operation", operation),
			String("table", table),
			Duration("duration", duration),
			Err(err),
		)
	} else {
		Debug("Database operation",
			String("operation", operation),
			String("table", table),
			Duration("duration", duration),
		)
	}
}