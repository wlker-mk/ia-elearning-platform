---
description: Repository Information Overview
alwaysApply: true
---

# AI E-Learning Platform - Repository Information

## Repository Summary

Advanced AI-powered e-learning platform built as a multi-project monorepo combining a modern React frontend with a comprehensive microservices backend architecture. The platform features 21 microservices supporting courses, payments, analytics, gamification, communications, and more, utilizing Django, Spring Boot, and Go across different services.

## Repository Structure

- **frontend/**: React + Vite web application (Node.js/TypeScript)
- **backend/**: Microservices architecture with multiple independent services
  - **microservices/**: Individual service directories (21 services)
  - **docker/**: Infrastructure Docker configurations
  - **scripts/**: Deployment and migration scripts
  - **k8s/**: Kubernetes deployment configurations
  - **terraform/**: Infrastructure-as-Code configurations
  - **infrastructure/**: Supporting infrastructure setup

### Main Repository Components

- **Frontend Application**: React-based user interface with Vite build system
- **API Gateway**: Go-based request routing and service orchestration
- **Python Microservices** (18): Django REST Framework services handling core business logic
- **Java Payments Service**: Spring Boot service for payment processing
- **Infrastructure Layer**: PostgreSQL, Redis, RabbitMQ, Elasticsearch, Nginx
- **Supporting Tools**: Monitoring, CI/CD scripts, health checks, database migrations

## Projects

### Frontend Application

**Configuration File**: `frontend/package.json`

#### Language & Runtime

**Language**: JavaScript/JSX  
**Runtime**: Node.js (ES modules)  
**Build System**: Vite (rolldown-vite@7.2.5)  
**Package Manager**: npm

#### Dependencies

**Main Dependencies**:
- react@19.2.0, react-dom@19.2.0
- react-router-dom@7.9.6
- @reduxjs/toolkit@2.10.1, react-redux@9.2.0
- @tanstack/react-query@5.90.10 (data fetching)
- axios@1.13.2 (HTTP client)
- tailwindcss@4.1.17 (CSS framework)
- framer-motion@12.23.24 (animations)
- socket.io-client@4.8.1 (WebSocket)
- react-hook-form@7.66.1 (form management)
- recharts@3.4.1 (charting)

**Development Dependencies**:
- @vitejs/plugin-react@5.1.1
- eslint@9.39.1, eslint-plugin-react-hooks@7.0.1
- postcss@8.5.6, autoprefixer@10.4.22

#### Build & Installation

```bash
npm install
npm run dev          # Development server with HMR
npm run build        # Production build
npm run lint         # Code linting
npm run preview      # Preview production build
```

#### Entry Point

**Main File**: `frontend/index.html`  
**App Source**: `frontend/src/` (React components and application logic)

### Backend - API Gateway (Go)

**Configuration File**: `backend/microservices/api-gateway/go.mod`

#### Language & Runtime

**Language**: Go  
**Package Manager**: Go modules  
**Linting**: golangci-yml configuration present

#### Build & Installation

```bash
go mod download      # Download dependencies
go build            # Build executable
```

#### Docker

**Dockerfile**: `backend/microservices/api-gateway/Dockerfile`

### Backend - Python Microservices (18 services)

**Primary Configuration Files**: `backend/requirements.txt` (root) + `backend/microservices/[service]/requirements.txt` (per-service)

#### Language & Runtime

**Language**: Python 3.x  
**Framework**: Django 5.0.1, Django REST Framework 3.14.0  
**Build System**: Django setuptools  
**Package Manager**: pip

#### Microservices

- **auth-service**: JWT authentication and user authorization (8001)
- **user-service**: User profile and account management (8002)
- **courses-service**: Course content and enrollment management (8003)
- **payments-service**: Payment processing and subscription management (8006)
- **quizzes-service**: Quiz creation and assessment
- **bookings-service**: Session and appointment bookings
- **notifications-service**: Email and push notifications
- **webinars-service**: Live webinar management
- **gamification-service**: Badges, points, and leaderboards
- **chatbot-service**: AI-powered chatbot interactions
- **analytics-service**: Learning analytics and reporting
- **communications-service**: Messaging and collaboration
- **search-service**: Full-text search integration
- **storage-service**: File storage and management
- **security-service**: Security and compliance
- **monitoring-service**: System health monitoring
- **ai-gateway**: AI model integration and inference
- **cache-service**: Caching layer management
- **i18n-service**: Internationalization support
- **sponsors-service**: Sponsor and partnership management
- **Additional services**: enrollment-service, reviews-service

#### Dependencies

**Core Dependencies**:
- Django==5.0.1, djangorestframework==3.14.0
- django-cors-headers==4.3.1, django-filter==23.3
- psycopg2-binary==2.9.9 (PostgreSQL driver)
- prisma==0.11.0 (ORM)
- redis==5.0.1, django-redis==5.3.0 (caching)
- celery==5.3.4, django-celery-beat==2.5.0 (task queue)
- requests==2.31.0, httpx==0.25.2 (HTTP clients)

**Authentication & Security**:
- djangorestframework-simplejwt==5.3.0
- PyJWT==2.8.0
- bcrypt==4.1.2, argon2-cffi==23.1.0
- pyotp==2.9.0, qrcode==7.4.2

**Storage & Cloud**:
- boto3==1.34.23, django-storages==1.14.2 (AWS S3)
- stripe==7.10.0 (payment processing)

**Development & Testing**:
- pytest==7.4.4, pytest-django==4.7.0, pytest-cov==4.1.0
- factory-boy==3.3.0 (test fixtures)
- black==23.12.1 (code formatting)
- flake8==7.0.0 (linting)
- isort==5.13.2 (import sorting)

#### Build & Installation

```bash
pip install -r requirements.txt              # Install dependencies
pip install -r backend/requirements.txt      # Root dependencies
./scripts/migrate_all.sh                    # Run Prisma migrations
docker-compose up -d                        # Start all services
```

#### Testing

**Framework**: Pytest  
**Configuration File**: `backend/pytest.ini`  
**Test Location**: `backend/tests/` directory  
**Naming Convention**: `test_*.py` or `*_tests.py`  
**Test Markers**: unit, integration, e2e

**Run Command**:

```bash
make test                          # Run all tests
pytest tests/unit                 # Unit tests
pytest tests/integration          # Integration tests
pytest --cov=. --cov-report=html # With coverage report
```

### Backend - Payments Service (Java/Spring Boot)

**Configuration File**: `backend/microservices/payments-service/pom.xml`

#### Language & Runtime

**Language**: Java  
**Version**: Java 21  
**Framework**: Spring Boot 3.5.8  
**Build System**: Maven  
**Package Manager**: Maven Central Repository

#### Dependencies

**Core Spring Framework**:
- spring-boot-starter-web
- spring-boot-starter-data-jpa
- spring-boot-starter-validation
- spring-boot-starter-security

**Payment Processing**:
- stripe@24.16.0 (Stripe SDK)

**Database & ORM**:
- spring-boot-starter-data-jpa
- Database driver (PostgreSQL recommended)

**Utilities**:
- springdoc-openapi@2.6.0 (OpenAPI/Swagger)
- flyway@10.0.0 (database migration)

#### Build & Installation

```bash
mvn clean install                 # Build and install
mvn spring-boot:run              # Run the application
mvn test                         # Run tests
```

#### Docker

**Dockerfile**: `backend/microservices/payments-service/Dockerfile`  
**Build Command**: `docker build -t payments-service .`

## Infrastructure & Docker

### Main Docker Compose Setup

**File**: `backend/docker-compose.yml`

**Services**:
- **PostgreSQL 15 Alpine**: Database (port 5432)
- **Redis 7 Alpine**: Cache and session store (port 6379)
- **RabbitMQ 3 Management**: Message queue (ports 5672, 15672)
- **Elasticsearch 8.11.0**: Full-text search (port 9200)
- **Nginx**: Reverse proxy and load balancing (ports 80, 443)
- **All Microservices**: Python and Java services
- **API Gateway**: Go routing service

### Build & Operations

```bash
make build                        # Build all containers
make up                          # Start all services
make down                        # Stop all services
make restart                     # Restart all services
make logs                        # View service logs
make ps                          # List active services
make health                      # Health check services
make clean                       # Clean volumes and containers
```

## Main Entry Points & Configuration

**Frontend**:
- **HTML Entry**: `frontend/index.html`
- **App Root**: `frontend/src/main.jsx`
- **Config**: `frontend/vite.config.js`, `frontend/tailwind.config.js`

**Backend**:
- **Environment**: `.env` (root level, see `.env.example`)
- **Celery App**: `backend/celery_app/`
- **Shared Code**: `backend/shared/`
- **Static Files**: `backend/static/`
- **Media Files**: `backend/media/`

## Testing & Quality

**Python Testing**:
- pytest framework with coverage reporting
- Pytest markers for test categorization
- Coverage thresholds configured in pytest.ini
- Test fixtures via factory-boy

**Code Quality Tools**:
- Black (code formatting)
- Flake8 (style checking)
- isort (import ordering)
- ESLint (frontend JavaScript)

**Build & CI**:
- Makefile for common operations
- GitHub Actions workflows (`.github/workflows/`)
- Health check scripts for service monitoring

## Deployment

**Kubernetes**: K8s manifests in `backend/k8s/` directory  
**Infrastructure as Code**: Terraform configurations in `backend/terraform/`  
**Environment Configuration**: 
- `.env.example` for template
- `.env` for local development
- Docker Compose files: standard, development (`docker-compose.dev.yml`), production (`docker-compose.prod.yml`)
