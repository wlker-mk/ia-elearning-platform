package monitoring

type Repository interface {
	FindAll() ([]*Service, error)
	FindByName(name string) (*Service, error)
	Create(service *Service) error
	Update(service *Service) error
	Delete(id int64) error
}
