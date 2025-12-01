package logger

import "log"

type Logger struct {
	level string
}

func New(level string) *Logger {
	return &Logger{level: level}
}

func (l *Logger) Info(msg string) {
	log.Printf("[INFO] %s", msg)
}

func (l *Logger) Error(msg string) {
	log.Printf("[ERROR] %s", msg)
}

func (l *Logger) Debug(msg string) {
	log.Printf("[DEBUG] %s", msg)
}
