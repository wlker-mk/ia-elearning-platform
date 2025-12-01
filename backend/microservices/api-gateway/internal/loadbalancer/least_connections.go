package loadbalancer

import "sync"

type LeastConnections struct {
	servers     []string
	connections map[string]int
	mu          sync.Mutex
}

func NewLeastConnections(servers []string) *LeastConnections {
	return &LeastConnections{
		servers:     servers,
		connections: make(map[string]int),
	}
}

func (lc *LeastConnections) Next() string {
	lc.mu.Lock()
	defer lc.mu.Unlock()

	if len(lc.servers) == 0 {
		return ""
	}

	minServer := lc.servers[0]
	minConn := lc.connections[minServer]

	for _, server := range lc.servers {
		if conn := lc.connections[server]; conn < minConn {
			minServer = server
			minConn = conn
		}
	}

	lc.connections[minServer]++
	return minServer
}
