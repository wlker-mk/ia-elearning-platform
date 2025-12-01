package loadbalancer

type LoadBalancer interface {
	Next() string
}
