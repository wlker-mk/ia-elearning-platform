package validation

type Rule interface {
	Validate(value interface{}) bool
}

type RequiredRule struct{}

func (r *RequiredRule) Validate(value interface{}) bool {
	return value != nil && value != ""
}
