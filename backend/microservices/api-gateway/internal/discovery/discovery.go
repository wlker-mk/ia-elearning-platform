package discovery

type ServiceDiscovery interface {
	Register(name string, address string) error
	Discover(name string) (string, error)
	Deregister(name string) error
}
