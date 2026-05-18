#!/bin/bash
# AurIx Docker Test Script

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🧪 Testing AurIx Docker Setup"
echo "============================"

# Check if services are running
echo "Checking service status..."
if docker-compose ps | grep -q "aurix-backend.*running\|aurix-backend.*healthy"; then
    echo -e "${GREEN}✓${NC} AurIx backend is running"
else
    echo -e "${RED}✗${NC} AurIx backend is not running"
    echo "Run 'docker-compose up -d' first"
    exit 1
fi

# Test API endpoint
echo "Testing API endpoint..."
if curl -f -s http://localhost:8000/docs > /dev/null; then
    echo -e "${GREEN}✓${NC} API is accessible"
else
    echo -e "${RED}✗${NC} API is not accessible"
    exit 1
fi

# Test vulnerability scan
echo "Testing vulnerability scan..."
TEST_CODE='import os; os.system("ls")'

RESPONSE=$(curl -s -X POST http://localhost:8000/analyze \
    -H "Content-Type: application/json" \
    -d "{\"code\": \"$TEST_CODE\"}")

if echo "$RESPONSE" | grep -q "issues"; then
    echo -e "${GREEN}✓${NC} Vulnerability scan working"
else
    echo -e "${RED}✗${NC} Vulnerability scan failed"
    echo "Response: $RESPONSE"
    exit 1
fi

# Check Ollama if available
if docker-compose ps | grep -q "aurix-ollama"; then
    echo "Testing Ollama service..."
    if curl -f -s http://localhost:11434/api/tags > /dev/null; then
        echo -e "${GREEN}✓${NC} Ollama is accessible"
    else
        echo -e "${YELLOW}⚠${NC} Ollama is running but not accessible"
    fi
else
    echo -e "${YELLOW}⚠${NC} Ollama not enabled (using Gemini AI instead)"
fi

echo ""
echo -e "${GREEN}🎉 All tests passed! AurIx is working correctly.${NC}"
echo ""
echo "📍 Access your application:"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"