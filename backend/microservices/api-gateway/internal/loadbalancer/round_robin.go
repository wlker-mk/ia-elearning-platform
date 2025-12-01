package loadbalancer

import "sync"

type RoundRobin struct {
	servers []string
	current int
	mu      sync.Mutex
}

func NewRoundRobin(servers []string) *RoundRobin {
	return &RoundRobin{
		servers: servers,
		current: 0,
	}
}

func (rr *RoundRobin) Next() string {
	rr.mu.Lock()
	defer rr.mu.Unlock()

	if len(rr.servers) == 0 {
		return ""
	}

	server := rr.servers[rr.current]
	rr.current = (rr.current + 1) % len(rr.servers)
	return server
}
