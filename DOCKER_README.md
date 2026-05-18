# AurIx Docker Setup Guide

This guide will help you set up and run AurIx (vulnerability detection system) using Docker, ensuring consistent deployment across different systems.

## Prerequisites

- **Docker**: Install Docker Desktop for your platform
  - [Windows/macOS](https://docs.docker.com/get-docker/)
  - [Linux](https://docs.docker.com/engine/install/)
- **Docker Compose**: Usually included with Docker Desktop, or install separately
- **AI API Key**: Required for AI features (OpenAI)
  - [OpenAI](https://platform.openai.com/api-keys)

## Quick Start

### Linux/macOS
```bash
# Make the setup script executable
chmod +x docker-setup.sh

# Run the setup
./docker-setup.sh
```

### Windows
```cmd
# Run the setup script
docker-start.bat
```

## Manual Setup

If you prefer manual control:

```bash
# 1. Build and start services
docker-compose up --build -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f aurix-backend
```

## Access Points

Once running, access these endpoints:

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **OpenAI**: Integrated via API key (no direct endpoint)

## Configuration Options

### OpenAI Setup

The application uses OpenAI for advanced reasoning and code analysis features. You need to provide an OpenAI API key:

**Environment Variable:**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Or create a `.env` file:**
```
OPENAI_API_KEY=your-api-key-here
```

### Development Mode

For development with hot reload:

```bash
# Use development override
docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
```

### Production Mode

For production deployment:

```bash
# Build optimized images
docker-compose -f docker-compose.yml up --build --scale ollama=0
```

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Change port in docker-compose.yml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

2. **Permission issues on Linux**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Logout and login again
   ```

3. **Ollama model download fails**
   ```bash
   # Download manually after setup
   docker exec aurix-ollama ollama pull qwen2.5
   ```

4. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs aurix-backend

   # Rebuild without cache
   docker-compose build --no-cache
   ```

### Health Checks

The containers include health checks. Monitor status with:

```bash
docker-compose ps
```

### Logs

View logs for debugging:

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f aurix-backend
```

## Management Commands

```bash
# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose up --build

# Clean up (remove volumes)
docker-compose down -v
```

## File Structure

```
aurix-project/
├── docker-compose.yml          # Main compose file
├── docker-compose.override.yml # Development overrides
├── Dockerfile                  # Backend container definition
├── docker-setup.sh            # Linux/macOS setup script
├── docker-start.bat           # Windows setup script
├── .dockerignore              # Files to exclude from build
└── requirements.txt           # Python dependencies
```

## Environment Variables

Customize behavior with these environment variables in `docker-compose.yml`:

- `OPENAI_API_KEY`: Required for AI features (get from OpenAI)
- `GEMINI_API_KEY`: Optional backward-compatible fallback for older setup
- `PYTHONPATH`: Python path for imports
- `DEBUG`: Enable debug mode

## Volumes

Host-mounted volumes:
- `./results`: Scan results
- `./temp_files`: Temporary files
- `./Rule-Engine`: Rules directory (read-only)
- `./scanner`: Scanner directory (read-only)

## Security Notes

- CORS is configured to allow all origins (`*`) - restrict in production
- Health checks use HTTP endpoints - consider authentication for production
- Volumes mount host directories - ensure proper permissions
- **OpenAI API key is required** for AI features - keep it secure and never commit to version control

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify Docker is running: `docker info`
3. Test API: `curl http://localhost:8000/docs`
4. Check container status: `docker-compose ps`