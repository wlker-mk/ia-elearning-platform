# Architecture du Monitoring Service

## Vue d'ensemble

Ce service suit une architecture hexagonale (Clean Architecture) avec une séparation claire des responsabilités.

## Couches

### Domain Layer (`internal/domain/`)
- Contient les entités métier pures
- Définit les interfaces des repositories
- Aucune dépendance externe

### Application Layer (`internal/application/`)
- Contient les cas d'usage
- Orchestre la logique métier
- Utilise les repositories via leurs interfaces

### Infrastructure Layer (`internal/infrastructure/`)
- Implémentations concrètes (Database, Cache)
- Dépendances externes
- Repositories concrets

### Interface Layer (`internal/interfaces/`)
- Adaptateurs HTTP, gRPC
- Handlers et middlewares
- Point d'entrée de l'application

## Flux de données

```
Request → HTTP Handler → Application Service → Domain Service → Repository → Database
```

## Technologies

- **Framework Web**: Gin
- **Database**: PostgreSQL
- **Cache**: Redis
- **Logging**: Zap
- **Config**: Viper/godotenv
