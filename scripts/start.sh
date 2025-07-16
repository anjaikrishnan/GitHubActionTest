#!/bin/bash

# Enterprise Reporting Platform Startup Script

set -e

echo "🚀 Starting Enterprise Reporting Platform..."
echo "========================================"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding."
    echo "   Especially set your OPENAI_API_KEY for LLM functionality."
fi

# Pull latest images if needed
echo "📦 Pulling required Docker images..."
docker-compose pull

# Build services
echo "🔨 Building services..."
docker-compose build

# Start services
echo "🚀 Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

services=("postgres" "keycloak" "api-gateway" "llm-service" "analytics-service" "frontend")
for service in "${services[@]}"; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service failed to start"
    fi
done

echo ""
echo "🎉 Platform startup complete!"
echo "========================================"
echo "Access your services at:"
echo "🌐 Frontend:          http://localhost:3000"
echo "🔧 API Gateway:       http://localhost:8000"
echo "🧠 LLM Service:       http://localhost:8001"
echo "📊 Analytics Service: http://localhost:4000"
echo "🔐 Keycloak:          http://localhost:8080"
echo "🗄️  PostgreSQL:       localhost:5432"
echo ""
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🔍 Keycloak Admin:    http://localhost:8080 (admin/admin123)"
echo ""
echo "To stop all services, run: docker-compose down"
echo "To view logs, run: docker-compose logs -f [service-name]"
echo ""
echo "Happy reporting! 📈"