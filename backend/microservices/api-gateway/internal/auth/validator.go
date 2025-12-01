package auth

import (
	"errors"
	"strings"
)

func ValidateAuthHeader(header string) (string, error) {
	if header == "" {
		return "", errors.New("authorization header required")
	}

	parts := strings.Split(header, " ")
	if len(parts) != 2 || parts[0] != "Bearer" {
		return "", errors.New("invalid authorization format")
	}

	return parts[1], nil
}
