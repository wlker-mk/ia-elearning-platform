package validator

import (
	"fmt"
	"regexp"
	"strings"
	"time"

	"github.com/ai-elearning-platform/monitoring-service/pkg/errors"
)

var (
	// Regex patterns
	emailRegex      = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	urlRegex        = regexp.MustCompile(`^https?://[a-zA-Z0-9.-]+(:[0-9]+)?(/.*)?$`)
	serviceNameRegex = regexp.MustCompile(`^[a-zA-Z0-9-_]+$`)
	metricNameRegex  = regexp.MustCompile(`^[a-zA-Z0-9-_.]+$`)
)

// ===== Service Validation =====

// ValidateServiceName valide un nom de service
func ValidateServiceName(name string) error {
	if name == "" {
		return errors.BadRequest("service name cannot be empty")
	}
	
	if len(name) > 100 {
		return errors.BadRequest("service name too long (max 100 characters)")
	}
	
	if !serviceNameRegex.MatchString(name) {
		return errors.BadRequest("service name can only contain alphanumeric characters, hyphens and underscores")
	}
	
	return nil
}

// ValidateURL valide une URL
func ValidateURL(url string) error {
	if url == "" {
		return errors.BadRequest("URL cannot be empty")
	}
	
	if !urlRegex.MatchString(url) {
		return errors.BadRequest("invalid URL format")
	}
	
	return nil
}

// ===== Metric Validation =====

// ValidateMetricName valide un nom de métrique
func ValidateMetricName(name string) error {
	if name == "" {
		return errors.BadRequest("metric name cannot be empty")
	}
	
	if len(name) > 200 {
		return errors.BadRequest("metric name too long (max 200 characters)")
	}
	
	if !metricNameRegex.MatchString(name) {
		return errors.BadRequest("metric name can only contain alphanumeric characters, hyphens, underscores and dots")
	}
	
	return nil
}

// ValidateMetricValue valide une valeur de métrique
func ValidateMetricValue(value float64) error {
	if value < 0 {
		return errors.InvalidMetric("metric value cannot be negative")
	}
	
	// Vérifier que la valeur n'est pas NaN ou Inf
	if value != value { // NaN check
		return errors.InvalidMetric("metric value cannot be NaN")
	}
	
	return nil
}

// ValidateMetricUnit valide une unité de métrique
func ValidateMetricUnit(unit string) error {
	if unit == "" {
		return nil // Unit is optional
	}
	
	validUnits := []string{
		"ms", "s", "m", "h",           // Time
		"bytes", "kb", "mb", "gb",     // Size
		"count", "percentage", "%",    // General
		"req/s", "qps",                // Rate
		"cpu", "memory", "disk",       // Resources
	}
	
	unitLower := strings.ToLower(unit)
	for _, valid := range validUnits {
		if unitLower == valid {
			return nil
		}
	}
	
	// Allow custom units but warn
	if len(unit) > 20 {
		return errors.InvalidMetric("metric unit too long (max 20 characters)")
	}
	
	return nil
}

// ===== Alert Validation =====

// ValidateAlertTitle valide un titre d'alerte
func ValidateAlertTitle(title string) error {
	if title == "" {
		return errors.BadRequest("alert title cannot be empty")
	}
	
	if len(title) > 200 {
		return errors.BadRequest("alert title too long (max 200 characters)")
	}
	
	return nil
}

// ValidateAlertDescription valide une description d'alerte
func ValidateAlertDescription(description string) error {
	if description == "" {
		return errors.BadRequest("alert description cannot be empty")
	}
	
	if len(description) > 2000 {
		return errors.BadRequest("alert description too long (max 2000 characters)")
	}
	
	return nil
}

// ValidateAlertSeverity valide une sévérité d'alerte
func ValidateAlertSeverity(severity string) error {
	validSeverities := []string{"INFO", "WARNING", "ERROR", "CRITICAL"}
	
	severityUpper := strings.ToUpper(severity)
	for _, valid := range validSeverities {
		if severityUpper == valid {
			return nil
		}
	}
	
	return errors.InvalidAlert(fmt.Sprintf("invalid severity: %s (must be: INFO, WARNING, ERROR, CRITICAL)", severity))
}

// ValidateAlertStatus valide un statut d'alerte
func ValidateAlertStatus(status string) error {
	validStatuses := []string{"OPEN", "ACKNOWLEDGED", "RESOLVED", "CLOSED"}
	
	statusUpper := strings.ToUpper(status)
	for _, valid := range validStatuses {
		if statusUpper == valid {
			return nil
		}
	}
	
	return errors.InvalidAlert(fmt.Sprintf("invalid status: %s", status))
}

// ===== Time Range Validation =====

// ValidateTimeRange valide une plage de temps
func ValidateTimeRange(from, to time.Time) error {
	if from.IsZero() {
		return errors.InvalidTimeRange("from time is required")
	}
	
	if to.IsZero() {
		return errors.InvalidTimeRange("to time is required")
	}
	
	if from.After(to) {
		return errors.InvalidTimeRange("from time must be before to time")
	}
	
	// Vérifier que la plage n'est pas trop grande (max 90 jours)
	if to.Sub(from) > 90*24*time.Hour {
		return errors.InvalidTimeRange("time range cannot exceed 90 days")
	}
	
	// Vérifier que from n'est pas dans le futur
	if from.After(time.Now()) {
		return errors.InvalidTimeRange("from time cannot be in the future")
	}
	
	return nil
}

// ValidateRetentionDays valide une période de rétention
func ValidateRetentionDays(days int) error {
	if days < 1 {
		return errors.BadRequest("retention days must be at least 1")
	}
	
	if days > 365 {
		return errors.BadRequest("retention days cannot exceed 365")
	}
	
	return nil
}

// ===== Performance Validation =====

// ValidateEndpoint valide un endpoint
func ValidateEndpoint(endpoint string) error {
	if endpoint == "" {
		return errors.BadRequest("endpoint cannot be empty")
	}
	
	if len(endpoint) > 500 {
		return errors.BadRequest("endpoint too long (max 500 characters)")
	}
	
	// Doit commencer par /
	if !strings.HasPrefix(endpoint, "/") {
		return errors.BadRequest("endpoint must start with /")
	}
	
	return nil
}

// ValidateHTTPMethod valide une méthode HTTP
func ValidateHTTPMethod(method string) error {
	validMethods := []string{"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
	
	methodUpper := strings.ToUpper(method)
	for _, valid := range validMethods {
		if methodUpper == valid {
			return nil
		}
	}
	
	return errors.BadRequest(fmt.Sprintf("invalid HTTP method: %s", method))
}

// ValidateStatusCode valide un code HTTP status
func ValidateStatusCode(code int) error {
	if code < 100 || code > 599 {
		return errors.BadRequest("invalid HTTP status code (must be between 100 and 599)")
	}
	
	return nil
}

// ValidateResponseTime valide un temps de réponse
func ValidateResponseTime(ms int) error {
	if ms < 0 {
		return errors.BadRequest("response time cannot be negative")
	}
	
	// Warning si temps de réponse > 1 minute (probablement une erreur)
	if ms > 60000 {
		return errors.BadRequest("response time seems too high (> 1 minute)")
	}
	
	return nil
}

// ===== Error Log Validation =====

// ValidateErrorType valide un type d'erreur
func ValidateErrorType(errorType string) error {
	if errorType == "" {
		return errors.BadRequest("error type cannot be empty")
	}
	
	if len(errorType) > 200 {
		return errors.BadRequest("error type too long (max 200 characters)")
	}
	
	return nil
}

// ValidateErrorMessage valide un message d'erreur
func ValidateErrorMessage(message string) error {
	if message == "" {
		return errors.BadRequest("error message cannot be empty")
	}
	
	if len(message) > 5000 {
		return errors.BadRequest("error message too long (max 5000 characters)")
	}
	
	return nil
}

// ===== Pagination Validation =====

// ValidateLimit valide une limite de pagination
func ValidateLimit(limit int) error {
	if limit < 1 {
		return errors.BadRequest("limit must be at least 1")
	}
	
	if limit > 1000 {
		return errors.BadRequest("limit cannot exceed 1000")
	}
	
	return nil
}

// ValidateOffset valide un offset de pagination
func ValidateOffset(offset int) error {
	if offset < 0 {
		return errors.BadRequest("offset cannot be negative")
	}
	
	return nil
}

// ===== General Validation =====

// ValidateEmail valide une adresse email
func ValidateEmail(email string) error {
	if email == "" {
		return errors.BadRequest("email cannot be empty")
	}
	
	if !emailRegex.MatchString(email) {
		return errors.BadRequest("invalid email format")
	}
	
	return nil
}

// ValidateIPAddress valide une adresse IP (basique)
func ValidateIPAddress(ip string) error {
	if ip == "" {
		return nil // IP is optional
	}
	
	// Simple validation - peut être améliorée
	parts := strings.Split(ip, ".")
	if len(parts) != 4 {
		// Peut-être IPv6
		if !strings.Contains(ip, ":") {
			return errors.BadRequest("invalid IP address format")
		}
	}
	
	return nil
}

// ValidateNotEmpty valide qu'une string n'est pas vide
func ValidateNotEmpty(value, fieldName string) error {
	if strings.TrimSpace(value) == "" {
		return errors.BadRequest(fmt.Sprintf("%s cannot be empty", fieldName))
	}
	return nil
}

// ValidateMaxLength valide la longueur maximale
func ValidateMaxLength(value string, maxLen int, fieldName string) error {
	if len(value) > maxLen {
		return errors.BadRequest(fmt.Sprintf("%s too long (max %d characters)", fieldName, maxLen))
	}
	return nil
}

// ValidateRange valide qu'une valeur est dans une plage
func ValidateRange(value, min, max float64, fieldName string) error {
	if value < min || value > max {
		return errors.BadRequest(fmt.Sprintf("%s must be between %.2f and %.2f", fieldName, min, max))
	}
	return nil
}

// ===== Batch Validation =====

// ValidateBatchSize valide la taille d'un batch
func ValidateBatchSize(size, maxSize int) error {
	if size < 1 {
		return errors.BadRequest("batch size must be at least 1")
	}
	
	if size > maxSize {
		return errors.BadRequest(fmt.Sprintf("batch size cannot exceed %d", maxSize))
	}
	
	return nil
}