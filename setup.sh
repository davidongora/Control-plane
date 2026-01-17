#!/bin/bash

# Control Plane Setup Script

echo "=========================================="
echo "Control Plane Setup"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

echo "✓ Node.js found"

# Backend Setup
echo ""
echo "Setting up Backend..."
echo "----------------------"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser prompt
echo ""
echo "Would you like to create a superuser? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

# Frontend Setup
echo ""
echo "Setting up Frontend..."
echo "----------------------"

cd control-plane-frontend

# Install npm dependencies
echo "Installing npm dependencies..."
npm install

cd ..

# Success message
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To start the backend server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "To start the frontend server:"
echo "  cd control-plane-frontend"
echo "  npm start"
echo ""
echo "Backend API: http://localhost:8000/api/"
echo "Frontend App: http://localhost:4200/"
echo "Admin Panel: http://localhost:8000/admin/"
echo ""
