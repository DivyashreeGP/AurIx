# 🐳 AurIx Docker Setup Guide

This guide explains how to run AurIx using Docker for complete platform independence.

## Prerequisites

- **Docker**: [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: [Install Docker Compose](https://docs.docker.com/compose/install/)
- Minimum 2GB RAM available for Docker

## Architecture

```
┌─────────────────────────────────────────────────────┐
│         VS Code Extension (Your Machine)            │
│  - Sends code to backend when saved/analyzed        │
└─────────────────────────┬───────────────────────────┘
                          │ HTTP (localhost:8000)
                          ▼
┌─────────────────────────────────────────────────────┐
│         Docker Network (aurix-network)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────────────┐  ┌────────────────┐  │
│  │  AurIx Backend          │  │  Ollama (LLM)  │  │
│  │  (FastAPI on 8000)      │  │  (11434)       │  │
│  │  - Vulnerability detect │  │  - AI Analysis │  │
│  │  - detect.py rules      │  │  - Qwen 2.5    │  │
│  │  - Results storage      │  │  [Optional]    │  │
│  └─────────────────────────┘  └────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Quick Start

### 1. **Start All Services**

```bash
cd AurIx
docker-compose up -d
```

This will:
- Build the AurIx backend image
- Start the backend on `http://localhost:8000`
- Start Ollama on `http://localhost:11434` (for AI analysis)
- Create volumes for data persistence

### 2. **Verify Services Are Running**

```bash
docker-compose ps
```

Expected output:
```
NAME               STATUS
aurix-backend      Up (healthy)
aurix-ollama       Up (healthy)
```

### 3. **View Logs**

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f aurix-backend
docker-compose logs -f aurix-ollama
```

### 4. **Test the Backend API**

```bash
curl http://localhost:8000/docs
```

Visit `http://localhost:8000/docs` in your browser to see the Swagger API documentation.

## Using with VS Code Extension

1. Keep Docker containers running
2. Open the AurIx VS Code extension
3. The extension automatically connects to `http://localhost:8000`
4. Analyze code as usual - it works exactly the same!

## Configuration

### Backend Only (Without AI)

If you don't need the Ollama AI service:

```bash
docker-compose up -d aurix-backend
```

### Custom Environment Variables

Create a `.env` file:

```bash
# .env
OLLAMA_ENDPOINT=http://ollama:11434
PYTHON_ENV=production
```

Then run:
```bash
docker-compose --env-file .env up -d
```

### Pull a Specific LLM Model (Optional)

If using Ollama for AI analysis:

```bash
# Start Ollama
docker-compose up -d aurix-ollama

# Pull a model (e.g., qwen2.5)
docker exec aurix-ollama ollama pull qwen2.5

# Verify available models
docker exec aurix-ollama ollama list
```

## Data Persistence

### Volumes

AurIx Docker setup automatically creates volumes for:

- **results/** - Vulnerability analysis reports
- **temp_files/** - Temporary analysis files
- **ollama_data** - LLM model cache (if using Ollama)

Data is automatically saved to your local machine.

### Access Results

```bash
# View results on host machine
ls ./results/

# Or inside the container
docker exec aurix-backend ls /app/results/
```

## Troubleshooting

### Backend won't start

Check logs:
```bash
docker-compose logs aurix-backend
```

Common issues:
- Port 8000 already in use: Change `ports: ["8001:8000"]` in docker-compose.yml
- Insufficient memory: Allocate more RAM to Docker

### Ollama not connecting

```bash
# Check if Ollama is running
docker-compose ps aurix-ollama

# View Ollama logs
docker-compose logs aurix-ollama

# Test connection
curl http://localhost:11434/api/tags
```

### Clean up everything

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Remove images
docker rmi aurix-backend ollama/ollama
```

## Building Custom Image

To rebuild after code changes:

```bash
# Rebuild image
docker-compose build

# Rebuild and restart
docker-compose up -d --build
```

## Performance Tips

### Increase Memory Limit

Edit `docker-compose.yml`:

```yaml
aurix-backend:
  mem_limit: 4g  # or your preferred limit
```

### Use Host Machine's Python (Advanced)

Skip Docker and run locally:

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

## Production Deployment

For production use:

1. Use `.env` file for secrets
2. Set `restart: always` in docker-compose.yml
3. Add logging driver (e.g., `json-file` with rotation)
4. Use Docker Swarm or Kubernetes for orchestration
5. Set resource limits and requests

Example production config:

```yaml
aurix-backend:
  restart: always
  mem_limit: 2g
  cpus: "1.0"
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

## Networking Issues?

If the VS Code extension can't reach the backend:

**Windows/Mac (Docker Desktop):**
```
http://localhost:8000        ✓ (Works natively)
http://host.docker.internal  ✓ (Alternative)
```

**Linux:**
```
http://localhost:8000        ✓ (Bridge network)
http://172.17.0.1:8000       ✓ (Docker gateway - if above fails)
```

## Support

For issues or questions:
1. Check `docker-compose logs`
2. Verify ports are not in use: `netstat -an | grep 8000`
3. Ensure Docker daemon is running
4. Check Docker documentation: https://docs.docker.com

Happy analyzing! 🔒
