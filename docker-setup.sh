#!/bin/bash
# AurIx Docker Setup Script - Cross-platform compatible

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

echo ""
echo "🐳 AurIx Docker Setup"
echo "===================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    echo ""
    echo "Please install Docker:"
    echo "  - Windows/macOS: https://docs.docker.com/get-docker/"
    echo "  - Linux: https://docs.docker.com/engine/install/"
    echo ""
    echo "After installation, restart your terminal and run this script again."
    exit 1
fi

# Check if Docker Compose is installed (try both v1 and v2)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
    print_status "Docker Compose (v1) found"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
    print_status "Docker Compose (v2) found"
else
    print_error "Docker Compose is not installed"
    echo ""
    echo "Please install Docker Compose:"
    echo "  - Usually included with Docker Desktop"
    echo "  - Or install separately: https://docs.docker.com/compose/install/"
    exit 1
fi

print_status "Docker is installed and running"

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    echo ""
    echo "Please start Docker Desktop or the Docker service and try again."
    exit 1
fi

echo ""

# Clean up any existing containers
print_info "Cleaning up existing containers..."
$DOCKER_COMPOSE_CMD down --remove-orphans 2>/dev/null || true

# Build the images
print_info "Building Docker images..."
$DOCKER_COMPOSE_CMD build --no-cache

echo ""

# Check for AI provider configuration
if [ -z "$AI_PROVIDER" ]; then
    AI_PROVIDER="gemini"
fi

echo "AI Provider: $AI_PROVIDER"

case $AI_PROVIDER in
    "gemini")
        if [ -z "$GEMINI_API_KEY" ]; then
            print_warning "GEMINI_API_KEY environment variable not set"
            echo ""
            echo "Please set your Gemini API key:"
            echo "  export GEMINI_API_KEY='your-api-key-here'"
            echo "  Or create a .env file with: GEMINI_API_KEY=your-api-key-here"
            echo ""
            echo "Get your API key from: https://makersuite.google.com/app/apikey"
            echo ""
            read -p "Do you want to continue anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_info "Setup cancelled. Please set your API key and try again."
                exit 1
            fi
        else
            print_status "Gemini API key found"
        fi
        ;;
    "openai")
        if [ -z "$OPENAI_API_KEY" ]; then
            print_warning "OPENAI_API_KEY environment variable not set"
            echo ""
            echo "Please set your OpenAI API key:"
            echo "  export OPENAI_API_KEY='your-api-key-here'"
            echo "  Or create a .env file with: OPENAI_API_KEY=your-api-key-here"
            echo ""
            echo "Get your API key from: https://platform.openai.com/api-keys"
            echo ""
            read -p "Do you want to continue anyway? (y/n): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_info "Setup cancelled. Please set your API key and try again."
                exit 1
            fi
        else
            print_status "OpenAI API key found"
        fi
        ;;
    *)
        print_error "Unknown AI provider: $AI_PROVIDER"
        echo "Supported providers: gemini, openai"
        exit 1
        ;;
esac

echo ""

# Start services

echo ""

# Wait for backend to be ready
print_info "Waiting for backend to be healthy..."
ATTEMPTS=0
MAX_ATTEMPTS=30

while [ $ATTEMPTS -lt $MAX_ATTEMPTS ]; do
    if $DOCKER_COMPOSE_CMD ps aurix-backend | grep -q "healthy\|running"; then
        break
    fi
    sleep 2
    ATTEMPTS=$((ATTEMPTS + 1))
done

# Check final status
if $DOCKER_COMPOSE_CMD ps aurix-backend | grep -q "healthy\|running"; then
    print_status "AurIx backend is running and healthy"
else
    print_warning "Backend status uncertain - checking logs..."
    $DOCKER_COMPOSE_CMD logs aurix-backend | tail -20
fi

echo ""
echo "🎉 AurIx Docker Setup Complete!"
echo "==============================="
echo ""
$DOCKER_COMPOSE_CMD ps

echo ""
echo "📍 Access Points:"
echo "   Backend API: http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   AI Provider: $AI_PROVIDER (configured)"

echo ""
echo "🔧 Management Commands:"
echo "   View logs:    $DOCKER_COMPOSE_CMD logs -f"
echo "   Stop all:     $DOCKER_COMPOSE_CMD down"
echo "   Restart:      $DOCKER_COMPOSE_CMD restart"
echo "   Rebuild:      $DOCKER_COMPOSE_CMD up --build"

echo ""
echo "📝 Next Steps:"
echo "   1. Test the API at http://localhost:8000/docs"
echo "   2. Use your VS Code extension or API client"
echo "   3. Check logs if you encounter issues"

echo ""
print_status "Setup completed successfully!"