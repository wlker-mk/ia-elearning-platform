# API Documentation

## Base URL
```
http://localhost:9090/api/v1
```

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "service": "monitoring-service",
  "timestamp": 1234567890
}
```

### Get All Services
```http
GET /monitoring/services
```

**Response:**
```json
{
  "services": [
    {
      "name": "api-gateway",
      "status": "up",
      "url": "http://api-gateway:8000"
    }
  ]
}
```

### Get Service Details
```http
GET /monitoring/services/:name
```

**Response:**
```json
{
  "name": "api-gateway",
  "status": "up",
  "response_time": 25,
  "last_check": "2024-01-01T12:00:00Z"
}
```

### Get Metrics
```http
GET /monitoring/metrics
```

**Response:**
```json
{
  "total_requests": 1523,
  "error_rate": 2.3,
  "avg_response": 145,
  "uptime": 99.9
}
```

### Get Alerts
```http
GET /alerts
```

### Create Alert
```http
POST /alerts
Content-Type: application/json

{
  "service": "user-service",
  "message": "High CPU usage",
  "severity": "warning"
}
```

### Get Alert
```http
GET /alerts/:id
```
