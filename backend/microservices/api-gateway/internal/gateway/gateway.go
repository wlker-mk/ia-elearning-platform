package gateway

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

type Gateway struct {
	Services       map[string]*ServiceConfig
	RedisClient    *redis.Client
	RateLimiter    *RateLimiter
	JwtSecret      string
	CircuitBreaker *CircuitBreaker
	HttpClient     *http.Client
}

type ServiceConfig struct {
	Name      string
	BaseURL   string
	Timeout   time.Duration
	Retries   int
	HealthURL string
}

func NewGateway() *Gateway {
	redisClient := redis.NewClient(&redis.Options{
		Addr:     getEnv("REDIS_URL", "localhost:6379"),
		Password: getEnv("REDIS_PASSWORD", ""),
		DB:       0,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := redisClient.Ping(ctx).Err(); err != nil {
		log.Printf("⚠️  Redis connection failed: %v", err)
	} else {
		log.Println("✅ Redis connected")
	}

	gateway := &Gateway{
		Services:       make(map[string]*ServiceConfig),
		RedisClient:    redisClient,
		RateLimiter:    NewRateLimiter(redisClient),
		JwtSecret:      getEnv("JWT_SECRET", "your-secret-key-here"),
		CircuitBreaker: NewCircuitBreaker(),
		HttpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}

	gateway.registerAllServices()
	return gateway
}

func (g *Gateway) ProxyHandler(serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		service, exists := g.Services[serviceName]
		if !exists {
			c.JSON(http.StatusNotFound, gin.H{"error": "Service not found"})
			return
		}

		if !g.CircuitBreaker.AllowRequest(serviceName) {
			c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Service temporarily unavailable"})
			return
		}

		target, err := url.Parse(service.BaseURL)
		if err != nil {
			log.Printf("Error parsing service URL: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
			return
		}

		proxy := httputil.NewSingleHostReverseProxy(target)
		originalDirector := proxy.Director

		proxy.Director = func(req *http.Request) {
			originalDirector(req)
			req.URL.Path = strings.TrimPrefix(c.Request.URL.Path, "/api")
			req.URL.RawQuery = c.Request.URL.RawQuery
			req.Header.Set("X-Forwarded-Host", c.Request.Host)
			req.Header.Set("X-Origin-Host", target.Host)

			if userID, exists := c.Get("user_id"); exists {
				req.Header.Set("X-User-ID", fmt.Sprintf("%v", userID))
			}
			if userRole, exists := c.Get("user_role"); exists {
				req.Header.Set("X-User-Role", fmt.Sprintf("%v", userRole))
			}
		}

		proxy.ErrorHandler = func(w http.ResponseWriter, req *http.Request, err error) {
			log.Printf("Proxy error for %s: %v", serviceName, err)
			g.CircuitBreaker.RecordFailure(serviceName)
			w.Header().Set("Content-Type", "application/json")
			w.WriteHeader(http.StatusBadGateway)
			fmt.Fprintf(w, `{"error": "Service unavailable", "service": "%s"}`, serviceName)
		}

		proxy.ModifyResponse = func(resp *http.Response) error {
			if resp.StatusCode < 500 {
				g.CircuitBreaker.RecordSuccess(serviceName)
			} else {
				g.CircuitBreaker.RecordFailure(serviceName)
			}
			resp.Header.Set("X-Gateway", "api-gateway")
			resp.Header.Set("X-Service", serviceName)
			return nil
		}

		ctx, cancel := context.WithTimeout(c.Request.Context(), service.Timeout)
		defer cancel()
		c.Request = c.Request.WithContext(ctx)
		proxy.ServeHTTP(c.Writer, c.Request)
	}
}

func (g *Gateway) Close() {
	if g.RedisClient != nil {
		g.RedisClient.Close()
		log.Println("✅ Redis connection closed")
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
