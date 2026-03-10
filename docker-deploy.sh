#!/bin/bash

# Deforestation Detection System - Docker Deployment Script

echo "================================"
echo "🌍 Deforestation Detection System"
echo "Docker Deployment Helper"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/install/"
    exit 1
fi

print_success "Docker found"

# Check if .env file exists
if [ ! -f .env ]; then
    print_info "Creating .env file from .env.example"
    cp .env.example .env
    print_info "Please edit .env file with your Earth Engine credentials"
    read -p "Edit .env now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    fi
fi

print_success ".env file found"

# Build Docker image
print_info "Building Docker image..."
docker build -t deforestation-detection:latest .

if [ $? -eq 0 ]; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Run container
print_info "Starting Docker container..."
docker-compose up -d

if [ $? -eq 0 ]; then
    print_success "Container started successfully"
    echo ""
    print_info "Service is running at: http://localhost:5000"
    echo ""
    echo "Available commands:"
    echo "  docker-compose logs -f        # View logs"
    echo "  docker-compose stop           # Stop container"
    echo "  docker-compose down           # Stop and remove"
    echo "  docker-compose ps             # Show status"
else
    print_error "Failed to start container"
    exit 1
fi
