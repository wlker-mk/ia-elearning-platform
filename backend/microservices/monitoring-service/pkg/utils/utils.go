package utils

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"math"
	"sort"
	"time"
)

// ===== ID Generation =====

// GenerateID génère un ID aléatoire hexadécimal
func GenerateID() string {
	bytes := make([]byte, 16)
	rand.Read(bytes)
	return hex.EncodeToString(bytes)
}

// ===== Time Utilities =====

// StartOfDay retourne le début de la journée
func StartOfDay(t time.Time) time.Time {
	year, month, day := t.Date()
	return time.Date(year, month, day, 0, 0, 0, 0, t.Location())
}

// EndOfDay retourne la fin de la journée
func EndOfDay(t time.Time) time.Time {
	year, month, day := t.Date()
	return time.Date(year, month, day, 23, 59, 59, 999999999, t.Location())
}

// StartOfMonth retourne le début du mois
func StartOfMonth(t time.Time) time.Time {
	year, month, _ := t.Date()
	return time.Date(year, month, 1, 0, 0, 0, 0, t.Location())
}

// EndOfMonth retourne la fin du mois
func EndOfMonth(t time.Time) time.Time {
	return StartOfMonth(t).AddDate(0, 1, 0).Add(-time.Nanosecond)
}

// DaysAgo retourne la date il y a N jours
func DaysAgo(days int) time.Time {
	return time.Now().AddDate(0, 0, -days)
}

// HoursAgo retourne la date il y a N heures
func HoursAgo(hours int) time.Time {
	return time.Now().Add(-time.Duration(hours) * time.Hour)
}

// FormatDuration formate une durée en string lisible
func FormatDuration(d time.Duration) string {
	if d < time.Second {
		return fmt.Sprintf("%dms", d.Milliseconds())
	} else if d < time.Minute {
		return fmt.Sprintf("%.1fs", d.Seconds())
	} else if d < time.Hour {
		return fmt.Sprintf("%.1fm", d.Minutes())
	} else if d < 24*time.Hour {
		return fmt.Sprintf("%.1fh", d.Hours())
	} else {
		return fmt.Sprintf("%.1fd", d.Hours()/24)
	}
}

// ===== Statistics Utilities =====

// CalculatePercentile calcule un percentile sur une série de valeurs
func CalculatePercentile(values []float64, percentile float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	sorted := make([]float64, len(values))
	copy(sorted, values)
	sort.Float64s(sorted)
	
	index := (percentile / 100.0) * float64(len(sorted)-1)
	lower := int(math.Floor(index))
	upper := int(math.Ceil(index))
	
	if lower == upper {
		return sorted[lower]
	}
	
	// Interpolation linéaire
	weight := index - float64(lower)
	return sorted[lower]*(1-weight) + sorted[upper]*weight
}

// CalculateAverage calcule la moyenne
func CalculateAverage(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	sum := 0.0
	for _, v := range values {
		sum += v
	}
	
	return sum / float64(len(values))
}

// CalculateMedian calcule la médiane
func CalculateMedian(values []float64) float64 {
	return CalculatePercentile(values, 50)
}

// CalculateStdDev calcule l'écart-type
func CalculateStdDev(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	avg := CalculateAverage(values)
	variance := 0.0
	
	for _, v := range values {
		diff := v - avg
		variance += diff * diff
	}
	
	variance /= float64(len(values))
	return math.Sqrt(variance)
}

// CalculateMin retourne le minimum
func CalculateMin(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	min := values[0]
	for _, v := range values {
		if v < min {
			min = v
		}
	}
	
	return min
}

// CalculateMax retourne le maximum
func CalculateMax(values []float64) float64 {
	if len(values) == 0 {
		return 0
	}
	
	max := values[0]
	for _, v := range values {
		if v > max {
			max = v
		}
	}
	
	return max
}

// ===== Rate Calculations =====

// CalculateErrorRate calcule le taux d'erreur en pourcentage
func CalculateErrorRate(errors, total int64) float64 {
	if total == 0 {
		return 0
	}
	return float64(errors) / float64(total) * 100
}

// CalculateUptimePercentage calcule le pourcentage d'uptime
func CalculateUptimePercentage(uptimeSeconds, totalSeconds int) float64 {
	if totalSeconds == 0 {
		return 100.0
	}
	return float64(uptimeSeconds) / float64(totalSeconds) * 100
}

// ===== Conversion Utilities =====

// BytesToMB convertit bytes en MB
func BytesToMB(bytes uint64) float64 {
	return float64(bytes) / (1024 * 1024)
}

// BytesToGB convertit bytes en GB
func BytesToGB(bytes uint64) float64 {
	return float64(bytes) / (1024 * 1024 * 1024)
}

// MsToSeconds convertit millisecondes en secondes
func MsToSeconds(ms int64) float64 {
	return float64(ms) / 1000.0
}

// ===== Validation Utilities =====

// IsValidURL vérifie si une URL est valide
func IsValidURL(url string) bool {
	// Simple validation - peut être améliorée
	return len(url) > 0 && (
		len(url) > 7 && url[:7] == "http://" ||
		len(url) > 8 && url[:8] == "https://")
}

// IsValidEmail vérifie si un email est valide (basique)
func IsValidEmail(email string) bool {
	// Validation basique - à améliorer avec regex si nécessaire
	if len(email) < 3 {
		return false
	}
	atIndex := -1
	dotIndex := -1
	for i, c := range email {
		if c == '@' {
			if atIndex != -1 {
				return false // Multiple @
			}
			atIndex = i
		}
		if c == '.' && atIndex != -1 {
			dotIndex = i
		}
	}
	return atIndex > 0 && dotIndex > atIndex+1 && dotIndex < len(email)-1
}

// ===== String Utilities =====

// TruncateString tronque une string à une longueur maximale
func TruncateString(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	if maxLen <= 3 {
		return s[:maxLen]
	}
	return s[:maxLen-3] + "..."
}

// ContainsString vérifie si une slice contient une string
func ContainsString(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

// RemoveDuplicateStrings supprime les doublons d'une slice
func RemoveDuplicateStrings(slice []string) []string {
	seen := make(map[string]bool)
	result := []string{}
	
	for _, item := range slice {
		if !seen[item] {
			seen[item] = true
			result = append(result, item)
		}
	}
	
	return result
}

// ===== Numeric Utilities =====

// RoundToDecimal arrondit à N décimales
func RoundToDecimal(value float64, decimals int) float64 {
	multiplier := math.Pow(10, float64(decimals))
	return math.Round(value*multiplier) / multiplier
}

// Clamp limite une valeur entre min et max
func Clamp(value, min, max float64) float64 {
	if value < min {
		return min
	}
	if value > max {
		return max
	}
	return value
}

// ===== Batch Processing =====

// ChunkSlice divise une slice en chunks de taille maximale
func ChunkSlice(slice []interface{}, chunkSize int) [][]interface{} {
	var chunks [][]interface{}
	
	for i := 0; i < len(slice); i += chunkSize {
		end := i + chunkSize
		if end > len(slice) {
			end = len(slice)
		}
		chunks = append(chunks, slice[i:end])
	}
	
	return chunks
}

// ===== Retry Logic =====

// Retry exécute une fonction avec retry
func Retry(attempts int, sleep time.Duration, fn func() error) error {
	var err error
	
	for i := 0; i < attempts; i++ {
		err = fn()
		if err == nil {
			return nil
		}
		
		if i < attempts-1 {
			time.Sleep(sleep)
			sleep *= 2 // Exponential backoff
		}
	}
	
	return fmt.Errorf("after %d attempts, last error: %w", attempts, err)
}

// ===== Monitoring Specific =====

// CalculateAvailability calcule la disponibilité en pourcentage
func CalculateAvailability(uptime, downtime int) float64 {
	total := uptime + downtime
	if total == 0 {
		return 100.0
	}
	return float64(uptime) / float64(total) * 100
}

// CalculateSLA calcule si le SLA est respecté
func CalculateSLA(availability float64, slaTarget float64) bool {
	return availability >= slaTarget
}

// GetHealthStatus détermine le statut de santé basé sur des métriques
func GetHealthStatus(errorRate, responseTime float64) string {
	if errorRate > 10 || responseTime > 5000 {
		return "DOWN"
	} else if errorRate > 5 || responseTime > 2000 {
		return "DEGRADED"
	} else if errorRate > 1 || responseTime > 1000 {
		return "HEALTHY"
	}
	return "HEALTHY"
}

// CalculateThroughput calcule le throughput (requêtes par seconde)
func CalculateThroughput(requests int64, durationSeconds float64) float64 {
	if durationSeconds == 0 {
		return 0
	}
	return float64(requests) / durationSeconds
}