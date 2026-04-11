@echo off
REM AurIx Docker Quick Start Script (Windows)

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  AurIx Docker Setup (Windows)
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed
    echo Install Docker from: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed
    echo Install Docker Compose from: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

echo ✓ Docker is installed
echo.

REM Ask about Ollama model
set /p PULL_MODEL="Do you want to pull the Ollama LLM model (qwen2.5)? (y/n): "

if /i "%PULL_MODEL%"=="y" (
    echo.
    echo Starting Ollama service...
    docker-compose up -d aurix-ollama
    
    echo Waiting for Ollama to be ready...
    timeout /t 5 /nobreak
    
    echo Pulling qwen2.5 model (this may take a few minutes)...
    docker exec aurix-ollama ollama pull qwen2.5
    
    echo ✓ Ollama model pulled
)

echo.
echo Starting AurIx backend...
docker-compose up -d aurix-backend

echo Waiting for backend to be healthy...
timeout /t 10 /nobreak

echo.
echo Checking services...
docker-compose ps

echo.
echo ========================================
echo  🎉 AurIx is ready!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo Ollama: http://localhost:11434
echo.
echo Next steps:
echo 1. Open your VS Code extension
echo 2. Analyze code as usual
echo 3. View logs: docker-compose logs -f
echo.
echo To stop services: docker-compose down
echo.
pause
