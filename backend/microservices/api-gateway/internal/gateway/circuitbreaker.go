package gateway

import (
	"sync"
	"time"
)

type CircuitState int

const (
	StateClosed CircuitState = iota
	StateOpen
	StateHalfOpen
)

type CircuitBreaker struct {
	services map[string]*ServiceCircuit
	mu       sync.RWMutex
}

type ServiceCircuit struct {
	state         CircuitState
	failures      int
	lastFailTime  time.Time
	threshold     int
	timeout       time.Duration
}

func NewCircuitBreaker() *CircuitBreaker {
	return &CircuitBreaker{
		services: make(map[string]*ServiceCircuit),
	}
}

func (cb *CircuitBreaker) AllowRequest(serviceName string) bool {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	circuit, exists := cb.services[serviceName]
	if !exists {
		circuit = &ServiceCircuit{
			state:     StateClosed,
			threshold: 5,
			timeout:   30 * time.Second,
		}
		cb.services[serviceName] = circuit
	}

	if circuit.state == StateOpen {
		if time.Since(circuit.lastFailTime) > circuit.timeout {
			circuit.state = StateHalfOpen
			return true
		}
		return false
	}

	return true
}

func (cb *CircuitBreaker) RecordSuccess(serviceName string) {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	if circuit, exists := cb.services[serviceName]; exists {
		circuit.failures = 0
		circuit.state = StateClosed
	}
}

func (cb *CircuitBreaker) RecordFailure(serviceName string) {
	cb.mu.Lock()
	defer cb.mu.Unlock()

	circuit, exists := cb.services[serviceName]
	if !exists {
		return
	}

	circuit.failures++
	circuit.lastFailTime = time.Now()

	if circuit.failures >= circuit.threshold {
		circuit.state = StateOpen
	}
}
