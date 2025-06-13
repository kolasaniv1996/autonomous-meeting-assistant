#!/bin/bash

<<<<<<< HEAD
# Autonomous Agent Framework Web Interface Deployment Script

set -e

echo "🚀 Starting deployment of Autonomous Agent Framework Web Interface..."

# Check if Docker is installed
=======
# Deployment script for Autonomous Meeting Assistant
# This script builds and deploys the application using Docker Compose

set -e

echo "🚀 Starting deployment of Autonomous Meeting Assistant..."

# Check if Docker and Docker Compose are installed
>>>>>>> develop
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

<<<<<<< HEAD
# Check if Docker Compose is installed
=======
>>>>>>> develop
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

<<<<<<< HEAD
# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment file from template..."
    cp .env.template .env
    echo "⚠️  Please edit .env file with your actual credentials before running the application."
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running successfully!"
    echo ""
    echo "🌐 Access the application:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:5001"
    echo ""
    echo "📚 Check the logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop the application:"
    echo "   docker-compose down"
else
    echo "❌ Failed to start services. Check the logs:"
    docker-compose logs
    exit 1
fi

=======
# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running again."
    exit 1
fi

# Load environment variables
source .env

echo "🔧 Building Docker images..."
docker-compose build

echo "🗄️  Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "🔍 Checking service health..."
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ Services are healthy!"
else
    echo "⚠️  Some services may not be fully ready yet. Check logs with: docker-compose logs"
fi

echo "🌐 Application URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8080"
echo "   Health Check: http://localhost:8080/api/health"

echo "📊 Service status:"
docker-compose ps

echo "🎉 Deployment completed successfully!"
echo ""
echo "📖 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose pull && docker-compose up -d"

>>>>>>> develop
