package validation

import "regexp"

type Validator struct{}

func New() *Validator {
	return &Validator{}
}

func (v *Validator) ValidateEmail(email string) bool {
	re := regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)
	return re.MatchString(email)
}
