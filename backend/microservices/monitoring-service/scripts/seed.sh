#!/bin/bash

echo "Seeding database..."

# TODO: Implémenter le seeding
go run internal/infrastructure/database/seed.go

echo "Seeding completed!"
