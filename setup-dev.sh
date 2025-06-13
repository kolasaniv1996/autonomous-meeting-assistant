#!/bin/bash

# Development setup script for Autonomous Meeting Assistant
# This script sets up the development environment

set -e

echo "🛠️  Setting up development environment..."

# Check if Python 3.11+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 20+ first."
    exit 1
fi

# Setup backend
echo "🐍 Setting up backend..."
cd backend

# Install Python dependencies
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python3 reset_db.py

echo "✅ Backend setup completed!"

# Setup frontend
echo "⚛️  Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
npm install

echo "✅ Frontend setup completed!"

cd ..

echo "🎉 Development environment setup completed!"
echo ""
echo "🚀 To start development:"
echo "   Backend: cd backend && source venv/bin/activate && python3 app.py"
echo "   Frontend: cd frontend && npm run dev"
echo ""
echo "🌐 Development URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8080"
echo "   Default login: admin / admin123"

