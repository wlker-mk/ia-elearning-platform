package logger

type Fields map[string]interface{}

func (f Fields) Add(key string, value interface{}) Fields {
	f[key] = value
	return f
}
