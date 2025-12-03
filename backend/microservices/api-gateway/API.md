# API Reference

Documentation complète des endpoints de l'API Gateway.

## Table des matières

- [Authentication](#authentication)
- [Users](#users)
- [Courses](#courses)
- [Enrollment](#enrollment)
- [Quizzes](#quizzes)
- [Payments](#payments)
- [Bookings](#bookings)
- [Notifications](#notifications)
- [Communications](#communications)
- [Chatbot](#chatbot)
- [Analytics](#analytics)
- [Monitoring](#monitoring)
- [Search](#search)
- [Storage](#storage)
- [Gamification](#gamification)
- [Reviews](#reviews)
- [Webinars](#webinars)
- [Sponsors](#sponsors)
- [I18n](#i18n)
- [Security](#security)
- [Admin](#admin)

## Base URL
```
Development: http://localhost:8000
Production: https://api.yourdomain.com
```

## Authentication

Tous les endpoints protégés nécessitent un token JWT dans le header Authorization:
```
Authorization: Bearer <token>
```

### POST /api/auth/login

Authentifier un utilisateur.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400,
  "user": {
    "id": "123",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "user"
  }
}
```

**Errors:**
- `400 Bad Request` - Données invalides
- `401 Unauthorized` - Identifiants incorrects

### POST /api/auth/register

Créer un nouveau compte utilisateur.

**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "name": "Jane Doe",
  "phone": "+1234567890"
}
```

**Response:** `201 Created`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "124",
    "email": "newuser@example.com",
    "name": "Jane Doe",
    "role": "user",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

**Errors:**
- `400 Bad Request` - Email déjà utilisé
- `422 Unprocessable Entity` - Validation échouée

### POST /api/auth/refresh

Rafraîchir le token d'accès.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 86400
}
```

## Users

### GET /api/users

Liste tous les utilisateurs (nécessite authentification).

**Query Parameters:**
- `page` (int) - Numéro de page (défaut: 1)
- `limit` (int) - Éléments par page (défaut: 20, max: 100)
- `search` (string) - Recherche par nom ou email
- `role` (string) - Filtrer par rôle (user, instructor, admin)
- `status` (string) - Filtrer par statut (active, inactive, suspended)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "status": "active",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8
  }
}
```

### POST /api/users

Créer un nouvel utilisateur (admin uniquement).

**Request:**
```json
{
  "email": "admin@example.com",
  "password": "SecurePass123!",
  "name": "Admin User",
  "role": "admin",
  "phone": "+1234567890"
}
```

**Response:** `201 Created`
```json
{
  "id": "125",
  "email": "admin@example.com",
  "name": "Admin User",
  "role": "admin",
  "created_at": "2024-01-20T14:00:00Z"
}
```

### GET /api/users/:id

Récupérer les détails d'un utilisateur.

**Response:** `200 OK`
```json
{
  "id": "123",
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user",
  "status": "active",
  "phone": "+1234567890",
  "avatar": "https://cdn.example.com/avatars/123.jpg",
  "bio": "Passionné de technologie",
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "stats": {
    "courses_enrolled": 5,
    "courses_completed": 2,
    "certificates": 2
  }
}
```

### PUT /api/users/:id

Mettre à jour un utilisateur.

**Request:**
```json
{
  "name": "John Updated",
  "phone": "+9876543210",
  "bio": "New bio"
}
```

**Response:** `200 OK`
```json
{
  "id": "123",
  "email": "user@example.com",
  "name": "John Updated",
  "phone": "+9876543210",
  "bio": "New bio",
  "updated_at": "2024-01-20T15:00:00Z"
}
```

### DELETE /api/users/:id

Supprimer un utilisateur (admin uniquement).

**Response:** `204 No Content`

## Courses

### GET /api/courses

Liste tous les cours disponibles.

**Query Parameters:**
- `page` (int) - Numéro de page
- `limit` (int) - Éléments par page
- `category` (string) - Filtrer par catégorie
- `level` (string) - Filtrer par niveau (beginner, intermediate, advanced)
- `price_min` (float) - Prix minimum
- `price_max` (float) - Prix maximum
- `instructor` (string) - ID de l'instructeur
- `sort` (string) - Tri (popular, recent, price_asc, price_desc)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "course-1",
      "title": "Introduction to Go Programming",
      "description": "Learn Go from scratch",
      "instructor": {
        "id": "inst-1",
        "name": "Jane Smith",
        "avatar": "https://cdn.example.com/avatars/inst-1.jpg"
      },
      "category": "Programming",
      "level": "beginner",
      "price": 49.99,
      "currency": "USD",
      "duration": 1200,
      "lessons_count": 24,
      "students_count": 1523,
      "rating": 4.8,
      "reviews_count": 342,
      "thumbnail": "https://cdn.example.com/courses/course-1.jpg",
      "is_published": true,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 250,
    "total_pages": 13
  }
}
```

### POST /api/courses

Créer un nouveau cours (instructeur uniquement).

**Request:**
```json
{
  "title": "Advanced Microservices Architecture",
  "description": "Build scalable microservices",
  "category": "Architecture",
  "level": "advanced",
  "price": 99.99,
  "currency": "USD",
  "duration": 3600,
  "prerequisites": ["Basic knowledge of Go", "Docker experience"],
  "learning_outcomes": [
    "Design microservices architecture",
    "Implement API Gateway",
    "Deploy on Kubernetes"
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": "course-251",
  "title": "Advanced Microservices Architecture",
  "slug": "advanced-microservices-architecture",
  "status": "draft",
  "created_at": "2024-01-20T16:00:00Z"
}
```

### GET /api/courses/:id

Récupérer les détails complets d'un cours.

**Response:** `200 OK`
```json
{
  "id": "course-1",
  "title": "Introduction to Go Programming",
  "description": "Learn Go from scratch with hands-on projects",
  "long_description": "Detailed course description...",
  "instructor": {
    "id": "inst-1",
    "name": "Jane Smith",
    "bio": "Senior Go Developer with 10+ years experience",
    "avatar": "https://cdn.example.com/avatars/inst-1.jpg",
    "courses_count": 12,
    "students_count": 45000
  },
  "category": "Programming",
  "subcategory": "Go",
  "level": "beginner",
  "language": "en",
  "price": 49.99,
  "discount_price": 39.99,
  "currency": "USD",
  "duration": 1200,
  "last_updated": "2024-01-15T00:00:00Z",
  "requirements": [
    "Basic programming knowledge",
    "Computer with internet connection"
  ],
  "learning_outcomes": [
    "Write Go programs",
    "Build REST APIs",
    "Work with databases"
  ],
  "sections": [
    {
      "id": "sec-1",
      "title": "Getting Started",
      "order": 1,
      "lessons": [
        {
          "id": "lesson-1",
          "title": "Introduction to Go",
          "type": "video",
          "duration": 600,
          "is_preview": true,
          "order": 1
        }
      ]
    }
  ],
  "students_count": 1523,
  "rating": 4.8,
  "reviews_count": 342,
  "is_bestseller": true,
  "is_published": true,
  "certificate_available": true,
  "thumbnail": "https://cdn.example.com/courses/course-1.jpg",
  "preview_video": "https://cdn.example.com/videos/course-1-preview.mp4"
}
```

### PUT /api/courses/:id

Mettre à jour un cours (instructeur/admin).

**Request:**
```json
{
  "title": "Updated Course Title",
  "price": 59.99,
  "is_published": true
}
```

**Response:** `200 OK`

### DELETE /api/courses/:id

Supprimer un cours (admin uniquement).

**Response:** `204 No Content`

## Enrollment

### POST /api/enrollment

S'inscrire à un cours.

**Request:**
```json
{
  "course_id": "course-1",
  "payment_method": "stripe"
}
```

**Response:** `201 Created`
```json
{
  "enrollment_id": "enr-123",
  "course_id": "course-1",
  "user_id": "123",
  "status": "active",
  "enrolled_at": "2024-01-20T17:00:00Z",
  "expires_at": "2025-01-20T17:00:00Z",
  "progress": 0,
  "payment": {
    "amount": 49.99,
    "currency": "USD",
    "status": "completed"
  }
}
```

### GET /api/enrollment/my-courses

Liste des cours auxquels l'utilisateur est inscrit.

**Query Parameters:**
- `status` (string) - Filtrer par statut (active, completed, expired)
- `sort` (string) - Tri (recent, progress, title)

**Response:** `200 OK`
```json
{
  "data": [
    {
      "enrollment_id": "enr-123",
      "course": {
        "id": "course-1",
        "title": "Introduction to Go Programming",
        "thumbnail": "https://cdn.example.com/courses/course-1.jpg",
        "instructor": "Jane Smith"
      },
      "progress": 45,
      "last_accessed": "2024-01-19T10:30:00Z",
      "enrolled_at": "2024-01-01T00:00:00Z",
      "completed_at": null,
      "certificate_url": null
    }
  ]
}
```

### GET /api/enrollment/:id

Détails d'une inscription.

**Response:** `200 OK`
```json
{
  "enrollment_id": "enr-123",
  "course": {
    "id": "course-1",
    "title": "Introduction to Go Programming"
  },
  "user_id": "123",
  "status": "active",
  "progress": 45,
  "completed_lessons": 11,
  "total_lessons": 24,
  "enrolled_at": "2024-01-01T00:00:00Z",
  "last_accessed": "2024-01-19T10:30:00Z",
  "time_spent": 3600,
  "quiz_scores": [
    {
      "quiz_id": "quiz-1",
      "score": 85,
      "completed_at": "2024-01-10T14:00:00Z"
    }
  ]
}
```

## Quizzes

### GET /api/quizzes

Liste des quiz d'un cours.

**Query Parameters:**
- `course_id` (string, required) - ID du cours

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "quiz-1",
      "title": "Go Basics Quiz",
      "description": "Test your knowledge of Go basics",
      "course_id": "course-1",
      "section_id": "sec-1",
      "questions_count": 10,
      "duration": 600,
      "passing_score": 70,
      "attempts_allowed": 3,
      "is_mandatory": true
    }
  ]
}
```

### POST /api/quizzes

Créer un nouveau quiz (instructeur).

**Request:**
```json
{
  "course_id": "course-1",
  "section_id": "sec-1",
  "title": "Advanced Go Concepts",
  "description": "Test advanced concepts",
  "questions": [
    {
      "type": "multiple_choice",
      "question": "What is a goroutine?",
      "options": [
        "A lightweight thread",
        "A Go function",
        "A package",
        "A variable type"
      ],
      "correct_answer": 0,
      "points": 10
    }
  ],
  "duration": 1200,
  "passing_score": 80
}
```

**Response:** `201 Created`

### GET /api/quizzes/:id

Détails d'un quiz.

**Response:** `200 OK`
```json
{
  "id": "quiz-1",
  "title": "Go Basics Quiz",
  "description": "Test your knowledge",
  "questions": [
    {
      "id": "q-1",
      "type": "multiple_choice",
      "question": "What is Go?",
      "options": [
        "A programming language",
        "A database",
        "An OS",
        "A framework"
      ],
      "points": 10
    }
  ],
  "duration": 600,
  "passing_score": 70,
  "attempts_allowed": 3,
  "user_attempts": 1,
  "best_score": 85
}
```

## Payments

### POST /api/payments

Initier un paiement.

**Request:**
```json
{
  "course_id": "course-1",
  "payment_method": "stripe",
  "amount": 49.99,
  "currency": "USD",
  "billing_details": {
    "name": "John Doe",
    "email": "john@example.com",
    "address": {
      "line1": "123 Main St",
      "city": "San Francisco",
      "state": "CA",
      "postal_code": "94111",
      "country": "US"
    }
  }
}
```

**Response:** `200 OK`
```json
{
  "payment_id": "pay-123",
  "status": "pending",
  "amount": 49.99,
  "currency": "USD",
  "client_secret": "pi_xxx_secret_xxx",
  "payment_url": "https://checkout.stripe.com/pay/xxx"
}
```

### GET /api/payments/:id

Statut d'un paiement.

**Response:** `200 OK`
```json
{
  "payment_id": "pay-123",
  "status": "completed",
  "amount": 49.99,
  "currency": "USD",
  "course_id": "course-1",
  "user_id": "123",
  "payment_method": "stripe",
  "transaction_id": "pi_xxx",
  "created_at": "2024-01-20T18:00:00Z",
  "completed_at": "2024-01-20T18:01:30Z"
}
```

### GET /api/payments/history

Historique des paiements.

**Response:** `200 OK`
```json
{
  "data": [
    {
      "payment_id": "pay-123",
      "course": {
        "id": "course-1",
        "title": "Introduction to Go Programming"
      },
      "amount": 49.99,
      "currency": "USD",
      "status": "completed",
      "created_at": "2024-01-20T18:00:00Z"
    }
  ],
  "total_spent": 149.97
}
```

## Bookings

### GET /api/bookings

Liste des réservations (sessions en direct, consultations).

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "booking-1",
      "type": "consultation",
      "instructor": {
        "id": "inst-1",
        "name": "Jane Smith"
      },
      "date": "2024-01-25T15:00:00Z",
      "duration": 3600,
      "status": "confirmed",
      "meeting_url": "https://zoom.us/j/xxx",
      "price": 50.00
    }
  ]
}
```

### POST /api/bookings

Créer une réservation.

**Request:**
```json
{
  "instructor_id": "inst-1",
  "type": "consultation",
  "date": "2024-01-25T15:00:00Z",
  "duration": 3600,
  "notes": "Need help with microservices design"
}
```

**Response:** `201 Created`

### GET /api/bookings/:id

Détails d'une réservation.

**Response:** `200 OK`

## Notifications

### GET /api/notifications

Liste des notifications de l'utilisateur.

**Query Parameters:**
- `unread` (boolean) - Filtrer non lues uniquement
- `type` (string) - Type de notification

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "notif-1",
      "type": "course_update",
      "title": "New lesson added",
      "message": "A new lesson has been added to Introduction to Go",
      "is_read": false,
      "created_at": "2024-01-20T10:00:00Z",
      "data": {
        "course_id": "course-1",
        "lesson_id": "lesson-25"
      }
    }
  ],
  "unread_count": 5
}
```

### PUT /api/notifications/:id/read

Marquer une notification comme lue.

**Response:** `200 OK`

## Admin

### GET /api/admin/users

Gestion complète des utilisateurs (admin uniquement).

**Response:** `200 OK`
```json
{
  "data": [
    {
      "id": "123",
      "email": "user@example.com",
      "name": "John Doe",
      "role": "user",
      "status": "active",
      "email_verified": true,
      "last_login": "2024-01-20T10:00:00Z",
      "created_at": "2024-01-01T00:00:00Z",
      "stats": {
        "courses_enrolled": 5,
        "total_spent": 249.95,
        "login_count": 127
      }
    }
  ]
}
```

### GET /api/admin/statistics

Statistiques globales de la plateforme.

**Response:** `200 OK`
```json
{
  "users": {
    "total": 15000,
    "active": 12500,
    "new_this_month": 450
  },
  "courses": {
    "total": 250,
    "published": 230,
    "drafts": 20
  },
  "revenue": {
    "total": 125000.00,
    "this_month": 15000.00,
    "currency": "USD"
  },
  "enrollments": {
    "total": 45000,
    "this_month": 1250,
    "completion_rate": 68.5
  }
}
```

### POST /api/admin/cache/clear

Vider le cache Redis.

**Response:** `200 OK`
```json
{
  "message": "Cache cleared successfully",
  "keys_deleted": 1523
}
```

## Rate Limiting

Toutes les requêtes sont soumises au rate limiting:

- **Endpoints publics**: 100 requêtes / minute
- **Endpoints authentifiés**: 200 requêtes / minute
- **Endpoints admin**: 500 requêtes / minute

**Headers de réponse:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1642771200
```

**Erreur 429:**
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 45
}
```

## Error Responses

Format standard des erreurs:
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "Validation message"
  },
  "request_id": "req-uuid-xxx"
}
```

**Codes d'erreur communs:**
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error
- `502` - Bad Gateway
- `503` - Service Unavailable
- `504` - Gateway Timeout