package monitoring

import "time"

type Service struct {
	ID           int64
	Name         string
	URL          string
	Status       string
	ResponseTime int
	LastCheck    time.Time
	CreatedAt    time.Time
	UpdatedAt    time.Time
}

type Metric struct {
	ID         int64
	ServiceID  int64
	Type       string
	Value      float64
	Timestamp  time.Time
}
