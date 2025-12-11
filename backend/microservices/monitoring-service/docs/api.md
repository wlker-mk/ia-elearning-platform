# API Documentation

## Base URL


[localhost:9090](http://localhost:9090/api/v1)

```

[localhost:9090](http://localhost:9090/api/v1)


## Endpoints

### Health Check

```http
GET /health


**Response:**

```


**Response:**
json
{
  "status": "ok",
  "service": "monitoring-service",
  "timestamp": 1234567890
}


### Get All Services


```


### Get All Services

http
GET /monitoring/services


**Response:**

```


**Response:**
json
{
  "services": [
    {
      "name": "api-gateway",
      "status": "up",
      "url": "[api-gateway:8000"](http://api-gateway:8000")
    }
  ]
}


### Get Service Details


```


### Get Service Details

http
GET /monitoring/services/:name


**Response:**

```


**Response:**
json
{
  "name": "api-gateway",
  "status": "up",
  "response_time": 25,
  "last_check": "2024-01-01T12:00:00Z"
}


### Get Metrics


```


### Get Metrics

http
GET /monitoring/metrics


**Response:**

```


**Response:**
json
{
  "total_requests": 1523,
  "error_rate": 2.3,
  "avg_response": 145,
  "uptime": 99.9
}


### Get Alerts


```


### Get Alerts

http
GET /alerts


### Create Alert


```


### Create Alert

http
POST /alerts
Content-Type: application/json

{
  "service": "user-service",
  "message": "High CPU usage",
  "severity": "warning"
}


### Get Alert


```


### Get Alert

http
GET /alerts/:id
```
