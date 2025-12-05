package errors

import (
	"fmt"
	"net/http"
)

// ErrorCode représente un code d'erreur application
type ErrorCode string

const (
	// Codes génériques
	ErrInternal       ErrorCode = "INTERNAL_ERROR"
	ErrNotFound       ErrorCode = "NOT_FOUND"
	ErrBadRequest     ErrorCode = "BAD_REQUEST"
	ErrUnauthorized   ErrorCode = "UNAUTHORIZED"
	ErrForbidden      ErrorCode = "FORBIDDEN"
	ErrConflict       ErrorCode = "CONFLICT"
	
	// Codes monitoring spécifiques
	ErrServiceNotFound     ErrorCode = "SERVICE_NOT_FOUND"
	ErrServiceUnavailable  ErrorCode = "SERVICE_UNAVAILABLE"
	ErrMetricNotFound      ErrorCode = "METRIC_NOT_FOUND"
	ErrAlertNotFound       ErrorCode = "ALERT_NOT_FOUND"
	ErrInvalidMetric       ErrorCode = "INVALID_METRIC"
	ErrInvalidAlert        ErrorCode = "INVALID_ALERT"
	ErrDatabaseConnection  ErrorCode = "DATABASE_CONNECTION_ERROR"
	ErrCacheConnection     ErrorCode = "CACHE_CONNECTION_ERROR"
	ErrInvalidTimeRange    ErrorCode = "INVALID_TIME_RANGE"
)

// AppError représente une erreur application avec contexte
type AppError struct {
	Code       ErrorCode              `json:"code"`
	Message    string                 `json:"message"`
	StatusCode int                    `json:"-"`
	Details    map[string]interface{} `json:"details,omitempty"`
	Err        error                  `json:"-"`
}

// Error implémente l'interface error
func (e *AppError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %s (%v)", e.Code, e.Message, e.Err)
	}
	return fmt.Sprintf("%s: %s", e.Code, e.Message)
}

// Unwrap retourne l'erreur wrappée
func (e *AppError) Unwrap() error {
	return e.Err
}

// New crée une nouvelle AppError
func New(code ErrorCode, message string) *AppError {
	return &AppError{
		Code:       code,
		Message:    message,
		StatusCode: getHTTPStatus(code),
		Details:    make(map[string]interface{}),
	}
}

// Wrap wrappe une erreur existante
func Wrap(err error, code ErrorCode, message string) *AppError {
	if err == nil {
		return nil
	}
	
	return &AppError{
		Code:       code,
		Message:    message,
		StatusCode: getHTTPStatus(code),
		Details:    make(map[string]interface{}),
		Err:        err,
	}
}

// WithDetail ajoute un détail à l'erreur
func (e *AppError) WithDetail(key string, value interface{}) *AppError {
	if e.Details == nil {
		e.Details = make(map[string]interface{})
	}
	e.Details[key] = value
	return e
}

// getHTTPStatus retourne le status HTTP correspondant au code d'erreur
func getHTTPStatus(code ErrorCode) int {
	switch code {
	case ErrNotFound, ErrServiceNotFound, ErrMetricNotFound, ErrAlertNotFound:
		return http.StatusNotFound
	case ErrBadRequest, ErrInvalidMetric, ErrInvalidAlert, ErrInvalidTimeRange:
		return http.StatusBadRequest
	case ErrUnauthorized:
		return http.StatusUnauthorized
	case ErrForbidden:
		return http.StatusForbidden
	case ErrConflict:
		return http.StatusConflict
	case ErrServiceUnavailable:
		return http.StatusServiceUnavailable
	default:
		return http.StatusInternalServerError
	}
}

// Constructeurs d'erreurs communes

// NotFound crée une erreur NotFound
func NotFound(resource, id string) *AppError {
	return New(ErrNotFound, fmt.Sprintf("%s not found: %s", resource, id))
}

// BadRequest crée une erreur BadRequest
func BadRequest(message string) *AppError {
	return New(ErrBadRequest, message)
}

// Internal crée une erreur Internal
func Internal(message string, err error) *AppError {
	return Wrap(err, ErrInternal, message)
}

// ServiceNotFound crée une erreur ServiceNotFound
func ServiceNotFound(serviceName string) *AppError {
	return New(ErrServiceNotFound, fmt.Sprintf("service not found: %s", serviceName)).
		WithDetail("service_name", serviceName)
}

// ServiceUnavailable crée une erreur ServiceUnavailable
func ServiceUnavailable(serviceName string) *AppError {
	return New(ErrServiceUnavailable, fmt.Sprintf("service unavailable: %s", serviceName)).
		WithDetail("service_name", serviceName)
}

// MetricNotFound crée une erreur MetricNotFound
func MetricNotFound(serviceName, metricName string) *AppError {
	return New(ErrMetricNotFound, fmt.Sprintf("metric not found: %s/%s", serviceName, metricName)).
		WithDetail("service_name", serviceName).
		WithDetail("metric_name", metricName)
}

// AlertNotFound crée une erreur AlertNotFound
func AlertNotFound(alertID string) *AppError {
	return New(ErrAlertNotFound, fmt.Sprintf("alert not found: %s", alertID)).
		WithDetail("alert_id", alertID)
}

// InvalidMetric crée une erreur InvalidMetric
func InvalidMetric(reason string) *AppError {
	return New(ErrInvalidMetric, fmt.Sprintf("invalid metric: %s", reason))
}

// InvalidAlert crée une erreur InvalidAlert
func InvalidAlert(reason string) *AppError {
	return New(ErrInvalidAlert, fmt.Sprintf("invalid alert: %s", reason))
}

// DatabaseError crée une erreur DatabaseConnection
func DatabaseError(err error) *AppError {
	return Wrap(err, ErrDatabaseConnection, "database connection error")
}

// CacheError crée une erreur CacheConnection
func CacheError(err error) *AppError {
	return Wrap(err, ErrCacheConnection, "cache connection error")
}

// InvalidTimeRange crée une erreur InvalidTimeRange
func InvalidTimeRange(reason string) *AppError {
	return New(ErrInvalidTimeRange, fmt.Sprintf("invalid time range: %s", reason))
}

// IsAppError vérifie si une erreur est une AppError
func IsAppError(err error) bool {
	_, ok := err.(*AppError)
	return ok
}

// GetAppError convertit une erreur en AppError (ou crée une erreur Internal)
func GetAppError(err error) *AppError {
	if appErr, ok := err.(*AppError); ok {
		return appErr
	}
	return Internal("unexpected error", err)
}