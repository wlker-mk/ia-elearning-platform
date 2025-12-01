package errors

import "fmt"

type GatewayError struct {
	Code    int
	Message string
	Err     error
}

func (e *GatewayError) Error() string {
	if e.Err != nil {
		return fmt.Sprintf("%s: %v", e.Message, e.Err)
	}
	return e.Message
}

func NewError(code int, message string, err error) *GatewayError {
	return &GatewayError{
		Code:    code,
		Message: message,
		Err:     err,
	}
}
