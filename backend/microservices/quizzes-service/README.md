# 📝 Quizzes Service

Service de gestion des quiz, questions, tentatives et proctoring pour la plateforme d'apprentissage.

## 🎯 Fonctionnalités

### Quiz Management

- ✅ Création et gestion de quiz
- ✅ Support de plusieurs types de questions
- ✅ Randomisation des questions
- ✅ Limite de tentatives configurables
- ✅ Score de passage personnalisable

### Types de Questions Supportés

- **MULTIPLE_CHOICE**: Questions à choix multiples
- **TRUE_FALSE**: Questions Vrai/Faux
- **SHORT_ANSWER**: Réponses courtes
- **ESSAY**: Questions de dissertation
- **CODING**: Questions de programmation
- **MATCHING**: Questions d'appariement
- **FILL_BLANK**: Compléter les blancs

### Proctoring

- 📹 Surveillance par webcam
- 🖥️ Capture d'écran
- 🔊 Enregistrement audio
- ⚠️ Détection d'activités suspectes:
  - Changements d'onglets
  - Détection de visages multiples
  - Absence de visage
  - Copier-coller
- 🚩 Signalement automatique pour révision

### Statistiques et Analytics

- 📊 Taux de réussite
- ⏱️ Temps moyen de complétion
- 📈 Score moyen
- 📉 Analyse par question

## 🏗️ Architecture

```q
quizzes-service/
├── apps/
│   └── quizzes/
│       ├── models.py          # Modèles Django
│       ├── serializers.py     # Serializers REST
│       ├── services.py        # Logique métier
│       ├── views.py           # API endpoints
│       ├── urls.py            # Routes
│       ├── admin.py           # Admin Django
│       ├── tasks.py           # Tâches Celery
│       ├── signals.py         # Signaux Django
│       └── permissions.py     # Permissions
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── prisma/
│   ├── schema.prisma
│   ├── migrations/
│   └── seed.py
└── shared/
    └── middleware/
```

## 📋 Prérequis

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- RabbitMQ 3.12+

## 🚀 Installation

### 1. Cloner et configurer l'environnement

```bash
cd backend/microservices/quizzes-service
cp .env.example .env
```

### 2. Configurer les variables d'environnement

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/quizzes_service_db
REDIS_URL=redis://redis:6379
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672
SERVICE_PORT=8004
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Générer le client Prisma

```bash
prisma generate
```

### 5. Exécuter les migrations

```bash
prisma migrate deploy
python manage.py migrate
```

### 6. Seed la base de données (optionnel)

```bash
python prisma/seed.py
```

### 7. Lancer le service

```bash
# Development
python manage.py runserver 0.0.0.0:8004

# Production
gunicorn config.wsgi:application --bind 0.0.0.0:8004 --workers 4
```

### 8. Lancer Celery Worker

```bash
celery -A config worker -l info
```

### 9. Lancer Celery Beat (tâches planifiées)

```bash
celery -A config beat -l info
```

## 🐳 Docker

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f quizzes-service
```

## 📡 API Endpoints

### Quiz Endpoints

#### Lister les quiz

```http
GET /api/quizzes/quizzes/?lesson_id={lesson_id}
GET /api/quizzes/quizzes/?course_id={course_id}
```

#### Créer un quiz

```http
POST /api/quizzes/quizzes/
Content-Type: application/json

{
  "lesson_id": "uuid",
  "course_id": "uuid",
  "title": "Quiz Title",
  "description": "Description",
  "duration": 30,
  "passing_score": 70.0,
  "max_attempts": 3,
  "randomize_questions": false,
  "questions": [...]
}
```

#### Obtenir un quiz

```http
GET /api/quizzes/quizzes/{quiz_id}/
```

#### Mettre à jour un quiz

```http
PUT /api/quizzes/quizzes/{quiz_id}/
Content-Type: application/json

{
  "title": "Updated Title",
  "passing_score": 80.0
}
```

#### Supprimer un quiz

```http
DELETE /api/quizzes/quizzes/{quiz_id}/
```

#### Ajouter une question

```http
POST /api/quizzes/quizzes/{quiz_id}/add_question/
Content-Type: application/json

{
  "type": "MULTIPLE_CHOICE",
  "question": "Question text",
  "order": 1,
  "points": 1.0,
  "options": ["Option 1", "Option 2", "Option 3"],
  "correct_answer": 1,
  "explanation": "Explanation text"
}
```

#### Obtenir les questions

```http
GET /api/quizzes/quizzes/{quiz_id}/questions/
GET /api/quizzes/quizzes/{quiz_id}/questions/?randomize=true
```

#### Statistiques du quiz

```http
GET /api/quizzes/quizzes/{quiz_id}/statistics/
```

#### Tentatives du quiz

```http
GET /api/quizzes/quizzes/{quiz_id}/attempts/
```

### Quiz Attempt Endpoints

#### Commencer une tentative

```http
POST /api/quizzes/attempts/start/
Content-Type: application/json

{
  "quiz_id": "uuid"
}
```

#### Soumettre une tentative

```http
POST /api/quizzes/attempts/{attempt_id}/submit/
Content-Type: application/json

{
  "answers": {
    "question_id_1": "answer_1",
    "question_id_2": "answer_2"
  }
}
```

#### Mes tentatives

```http
GET /api/quizzes/attempts/my_attempts/?quiz_id={quiz_id}
```

### Proctoring Endpoints

#### Enregistrer un événement

```http
POST /api/quizzes/proctoring/record_event/
Content-Type: application/json

{
  "quiz_attempt_id": "uuid",
  "event_type": "tab_switch",
  "details": {}
}
```

#### Sessions signalées (Instructeurs)

```http
GET /api/quizzes/proctoring/flagged/
```

#### Réviser une session (Instructeurs)

```http
POST /api/quizzes/proctoring/{session_id}/review/
Content-Type: application/json

{
  "notes": "Review notes"
}
```

## 🔐 Permissions

### Rôles

- **STUDENT**: Peut passer les quiz
- **INSTRUCTOR**: Peut créer et gérer les quiz
- **ADMIN**: Accès complet

### Permissions par endpoint

- Quiz CRUD: `IsInstructor`
- Démarrer tentative: `IsAuthenticated`
- Soumettre tentative: `IsAuthenticated` + Owner
- Proctoring review: `IsInstructor`

## 🔄 Tâches Celery

### Tâches planifiées

#### Auto-submit des tentatives expirées

- **Fréquence**: Toutes les 5 minutes
- **Description**: Soumet automatiquement les tentatives qui ont dépassé la durée limite

#### Signalement des tentatives anormales

- **Fréquence**: Toutes les 6 heures
- **Description**: Détecte et signale les tentatives avec des patterns suspects

#### Nettoyage des médias proctoring

- **Fréquence**: Quotidien à 2h du matin
- **Description**: Supprime les fichiers de proctoring de plus de 90 jours

### Tâches à la demande

- `calculate_quiz_statistics`: Calcule les statistiques d'un quiz
- `process_proctoring_data`: Analyse les données de proctoring
- `send_quiz_result_notification`: Envoie une notification de résultat
- `generate_quiz_report`: Génère un rapport complet

## 📊 Modèles de données

### Quiz

```python
{
  "id": "uuid",
  "lesson_id": "uuid",
  "course_id": "uuid",
  "title": "string",
  "description": "string",
  "duration": "int (minutes)",
  "passing_score": "float",
  "max_attempts": "int",
  "randomize_questions": "bool"
}
```

### Question

```python
{
  "id": "uuid",
  "quiz_id": "uuid",
  "type": "QuizType",
  "question": "string",
  "order": "int",
  "points": "float",
  "options": "json",
  "correct_answer": "json",
  "explanation": "string"
}
```

### QuizAttempt

```python
{
  "id": "uuid",
  "quiz_id": "uuid",
  "student_id": "uuid",
  "attempt_number": "int",
  "score": "float",
  "percentage": "float",
  "is_passed": "bool",
  "answers": "json",
  "started_at": "datetime",
  "submitted_at": "datetime",
  "time_spent": "int (seconds)"
}
```

### ProctoringSession

```python
{
  "id": "uuid",
  "quiz_attempt_id": "uuid",
  "webcam_url": "string",
  "screen_url": "string",
  "audio_url": "string",
  "tab_switches": "int",
  "multiple_faces": "bool",
  "no_face_detected": "bool",
  "copy_paste_detected": "bool",
  "flagged_for_review": "bool",
  "reviewed_by": "uuid",
  "reviewed_at": "datetime",
  "review_notes": "string"
}
```

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Lancer avec couverture
pytest --cov=apps.quizzes

# Lancer des tests spécifiques
pytest apps/quizzes/tests/test_services.py
pytest apps/quizzes/tests/test_views.py
```

## 📝 Logging

Les logs sont écrits dans:

- Console (stdout)
- Fichier: `/app/logs/app.log`

Niveaux de log:

- INFO: Opérations normales
- WARNING: Sessions proctoring signalées
- ERROR: Erreurs d'exécution

## 🔍 Monitoring

Le service expose:

- Health check: `GET /api/health/`
- Admin Django: `/admin/`

## 🤝 Contribution

1. Créer une branche feature
2. Implémenter les changements
3. Écrire des tests
4. Soumettre une PR

## 📄 Licence

Propriétaire - Tous droits réservés
