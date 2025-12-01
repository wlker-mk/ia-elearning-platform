package discovery

import "errors"

type StaticDiscovery struct {
	services map[string]string
}

func NewStaticDiscovery() *StaticDiscovery {
	return &StaticDiscovery{
		services: make(map[string]string),
	}
}

func (s *StaticDiscovery) Register(name string, address string) error {
	s.services[name] = address
	return nil
}

func (s *StaticDiscovery) Discover(name string) (string, error) {
	if addr, ok := s.services[name]; ok {
		return addr, nil
	}
	return "", errors.New("service not found")
}

func (s *StaticDiscovery) Deregister(name string) error {
	delete(s.services, name)
	return nil
}
