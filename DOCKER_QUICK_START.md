# 🐳 AurIx Docker - Quick Reference

## 🚀 One-Command Start (Recommended)

### Windows
```powershell
cd c:\Major_Project\Integration\vulnerability-detection-bhavani
.\docker-start.bat
```

### macOS/Linux
```bash
cd vulnerability-detection-bhavani
chmod +x docker-start.sh
./docker-start.sh
```

## Manual Setup

### Start Everything
```bash
docker-compose up -d
```

### Start Backend Only (No AI)
```bash
docker-compose up -d aurix-backend
```

### View Logs
```bash
docker-compose logs -f aurix-backend
```

### Stop Services
```bash
docker-compose down
```

## Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | http://localhost:8000 | Vulnerability detection |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Ollama** | http://localhost:11434 | Local LLM (optional) |

## Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Backend Not Starting
```bash
docker-compose logs aurix-backend
```

### Clean Everything
```bash
docker-compose down -v
docker system prune -a
```

## VS Code Extension Integration

1. Start Docker: `docker-compose up -d`
2. Open VS Code
3. Use extension normally - it works exactly the same!
4. Backend automatically connects to http://localhost:8000

## Performance

- **Memory**: 2GB minimum (4GB recommended)
- **CPU**: 1 core minimum (2+ cores for AI)
- **Disk**: 2GB for images, 5GB+ for Ollama models

## Environment Variables

Edit `.env`:
```
OLLAMA_ENDPOINT=http://ollama:11434
PYTHONUNBUFFERED=1
```

Then run:
```bash
docker-compose --env-file .env up -d
```

For detailed guide, see: **DOCKER_SETUP.md**
