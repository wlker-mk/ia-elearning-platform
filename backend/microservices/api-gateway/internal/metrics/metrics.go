package metrics

import "sync"

type Metrics struct {
	requests  int64
	errors    int64
	latencies []int64
	mu        sync.RWMutex
}

func New() *Metrics {
	return &Metrics{
		latencies: make([]int64, 0),
	}
}

func (m *Metrics) IncrementRequests() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.requests++
}

func (m *Metrics) IncrementErrors() {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.errors++
}

func (m *Metrics) RecordLatency(latency int64) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.latencies = append(m.latencies, latency)
}
