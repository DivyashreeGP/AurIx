#!/bin/bash
# AurIx Docker Quick Start Script

set -e

echo "🐳 AurIx Docker Setup"
echo "===================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}❌ Docker is not installed${NC}"
    echo "Install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}❌ Docker Compose is not installed${NC}"
    echo "Install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker is installed${NC}"
echo ""

# Optionally pull Ollama model
read -p "Do you want to pull the Ollama LLM model (qwen2.5)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Starting Ollama service...${NC}"
    docker-compose up -d aurix-ollama
    
    echo -e "${BLUE}Waiting for Ollama to be ready...${NC}"
    sleep 5
    
    echo -e "${BLUE}Pulling qwen2.5 model (this may take a few minutes)...${NC}"
    docker exec aurix-ollama ollama pull qwen2.5
    
    echo -e "${GREEN}✓ Ollama model pulled${NC}"
fi

echo ""
echo -e "${BLUE}Starting AurIx backend...${NC}"
docker-compose up -d aurix-backend

echo -e "${BLUE}Waiting for backend to be healthy...${NC}"
sleep 10

# Check if backend is healthy
if docker-compose ps aurix-backend | grep -q "healthy\|Up"; then
    echo -e "${GREEN}✓ AurIx Backend is running${NC}"
else
    echo -e "${YELLOW}⚠ Backend status unknown, checking logs...${NC}"
    docker-compose logs aurix-backend | head -20
fi

echo ""
echo -e "${BLUE}Checking services...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 AurIx is ready!${NC}"
echo ""
echo "📍 Backend API: http://localhost:8000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Ollama: http://localhost:11434"
echo ""
echo "Next steps:"
echo "1. Open your VS Code extension"
echo "2. Analyze code as usual"
echo "3. View logs: docker-compose logs -f"
echo ""
echo -e "${BLUE}To stop services: docker-compose down${NC}"
