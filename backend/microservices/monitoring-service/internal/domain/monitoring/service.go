package monitoring

type Service interface {
	CheckHealth(service *Service) error
	GetAllServices() ([]*Service, error)
	GetServiceByName(name string) (*Service, error)
}
