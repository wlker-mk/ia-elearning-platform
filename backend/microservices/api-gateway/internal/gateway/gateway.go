package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

type Gateway struct {
	services       map[string]*ServiceConfig
	redisClient    *redis.Client
	rateLimiter    *RateLimiter
	jwtSecret      string
	circuitBreaker *CircuitBreaker
	httpClient     *http.Client
}

type ServiceConfig struct {
	Name      string
	BaseURL   string
	Timeout   time.Duration
	Retries   int
	HealthURL string
}

func NewGateway() *Gateway {
	// Initialize Redis
	redisClient := redis.NewClient(&redis.Options{
		Addr:     getEnv("REDIS_URL", "localhost:6379"),
		Password: getEnv("REDIS_PASSWORD", ""),
		DB:       0,
	})

	// Test Redis connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := redisClient.Ping(ctx).Err(); err != nil {
		log.Printf("⚠️  Redis connection failed: %v", err)
	} else {
		log.Println("✅ Redis connected")
	}

	gateway := &Gateway{
		services:       make(map[string]*ServiceConfig),
		redisClient:    redisClient,
		rateLimiter:    NewRateLimiter(redisClient),
		jwtSecret:      getEnv("JWT_SECRET", "your-secret-key-here"),
		circuitBreaker: NewCircuitBreaker(),
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}

	// Register services
	gateway.registerAllServices()

	return gateway
}

func (g *Gateway) ProxyHandler(serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		service, exists := g.services[serviceName]
		if !exists {
			c.JSON(http.StatusNotFound, gin.H{
				"error": "Service not found",
			})
			return
		}

		// Check circuit breaker
		if !g.circuitBreaker.AllowRequest(serviceName) {
			c.JSON(http.StatusServiceUnavailable, gin.H{
				"error": "Service temporarily unavailable",
			})
			return
		}

		// Parse target URL
		target, err := url.Parse(service.BaseURL)
		if err != nil {
			log.Printf("Error parsing service URL: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "Internal server error",
			})
			return
		}

		// Create reverse proxy
		proxy := httputil.NewSingleHostReverseProxy(target)

		// Custom director to modify the request
		originalDirector := proxy.Director
		proxy.Director = func(req *http.Request) {
			originalDirector(req)

			// Remove the service prefix from path
			req.URL.Path = strings.TrimPrefix(c.Request.URL.Path, "/api")
			req.URL.RawQuery = c.Request.URL.RawQuery

			// Forward headers
			req.Header.Set("X-Forwarded-Host", c.Request.Host)
			req.Header.Set("X-Origin-Host", target.Host)

			// Forward user context
			if userID, exists := c.Get("user_id"); exists {
				req.Header.Set("X-User-ID", fmt.Sprintf("%v", userID))
			}
			if userRole, exists := c.Get("user_role"); exists {
				req.Header.Set("X-User-Role", fmt.Sprintf("%v", userRole))
			}
		}

		// Custom error handler
		proxy.ErrorHandler = func(w http.ResponseWriter, req *http.Request, err error) {
			log.Printf("Proxy error for %s: %v", serviceName, err)
			g.circuitBreaker.RecordFailure(serviceName)

			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusBadGateway)
			fmt.Fprintf(w, `{"error": "Service unavailable", "service": "%s"}`, serviceName)
		}

		// Modify response
		proxy.ModifyResponse = func(resp *http.Response) error {
			// Record success for circuit breaker
			if resp.StatusCode < 500 {
				g.circuitBreaker.RecordSuccess(serviceName)
			} else {
				g.circuitBreaker.RecordFailure(serviceName)
			}

			// Add custom headers
			resp.Header.Set("X-Gateway", "api-gateway")
			resp.Header.Set("X-Service", serviceName)

			return nil
		}

		// Set timeout
		c.Request = c.Request.WithContext(
			contextWithTimeout(c.Request.Context(), service.Timeout),
		)

		// Serve the request
		proxy.ServeHTTP(c.Writer, c.Request)
	}
}

func (g *Gateway) Close() {
	if g.redisClient != nil {
		g.redisClient.Close()
		log.Println("✅ Redis connection closed")
	}
}

func contextWithTimeout(ctx context.Context, timeout time.Duration) context.Context {
	newCtx, _ := context.WithTimeout(ctx, timeout)
	return newCtx
}

func copyRequestBody(req *http.Request) ([]byte, error) {
	if req.Body == nil {
		return nil, nil
	}

	body, err := io.ReadAll(req.Body)
	if err != nil {
		return nil, err
	}

	req.Body = io.NopCloser(strings.NewReader(string(body)))

	return body, nil
}