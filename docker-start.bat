@echo off
REM AurIx Docker Setup Script (Windows) - Enhanced Version

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
    echo.
    echo Install Docker from: https://docs.docker.com/get-docker/
    echo.
    pause
    exit /b 1
)

REM Check Docker Compose (try both v1 and v2)
docker-compose --version >nul 2>&1
if not errorlevel 1 (
    set DOCKER_COMPOSE_CMD=docker-compose
    echo ✓ Docker Compose (v1) found
    goto :compose_found
)

docker compose version >nul 2>&1
if not errorlevel 1 (
    set DOCKER_COMPOSE_CMD=docker compose
    echo ✓ Docker Compose (v2) found
    goto :compose_found
)

echo ❌ Docker Compose is not installed
echo.
echo Install Docker Compose from: https://docs.docker.com/compose/install/
echo.
pause
exit /b 1

:compose_found
echo ✓ Docker is installed and running
echo.

REM Clean up existing containers
echo Cleaning up existing containers...
%DOCKER_COMPOSE_CMD% down --remove-orphans >nul 2>&1

REM Build images
echo Building Docker images...
%DOCKER_COMPOSE_CMD% build --no-cache

echo.

REM Check for AI provider configuration
if "%AI_PROVIDER%"=="" (
    set AI_PROVIDER=gemini
)

echo AI Provider: %AI_PROVIDER%

if /i "%AI_PROVIDER%"=="gemini" (
    if "%GEMINI_API_KEY%"=="" (
        echo.
        echo WARNING: GEMINI_API_KEY environment variable not set
        echo.
        echo Please set your Gemini API key:
        echo   set GEMINI_API_KEY=your-api-key-here
        echo   Or create a .env file with: GEMINI_API_KEY=your-api-key-here
        echo.
        echo Get your API key from: https://makersuite.google.com/app/apikey
        echo.
        set /p CONTINUE="Do you want to continue anyway? (y/n): "
        if /i not "!CONTINUE!"=="y" (
            echo Setup cancelled. Please set your API key and try again.
            pause
            exit /b 1
        )
    ) else (
        echo ✓ Gemini API key found
    )
) else if /i "%AI_PROVIDER%"=="openai" (
    if "%OPENAI_API_KEY%"=="" (
        echo.
        echo WARNING: OPENAI_API_KEY environment variable not set
        echo.
        echo Please set your OpenAI API key:
        echo   set OPENAI_API_KEY=your-api-key-here
        echo   Or create a .env file with: OPENAI_API_KEY=your-api-key-here
        echo.
        echo Get your API key from: https://platform.openai.com/api-keys
        echo.
        set /p CONTINUE="Do you want to continue anyway? (y/n): "
        if /i not "!CONTINUE!"=="y" (
            echo Setup cancelled. Please set your API key and try again.
            pause
            exit /b 1
        )
    ) else (
        echo ✓ OpenAI API key found
    )
) else (
    echo ERROR: Unknown AI provider: %AI_PROVIDER%
    echo Supported providers: gemini, openai
    pause
    exit /b 1
)

echo.

REM Start services
echo Starting AurIx backend...
%DOCKER_COMPOSE_CMD% up -d aurix-backend
echo Checking services...
%DOCKER_COMPOSE_CMD% ps

echo.
echo ========================================
echo  🎉 AurIx is ready!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo AI Provider: %AI_PROVIDER% (configured)
echo.
echo Management Commands:
echo   View logs:    %DOCKER_COMPOSE_CMD% logs -f
echo   Stop all:     %DOCKER_COMPOSE_CMD% down
echo   Restart:      %DOCKER_COMPOSE_CMD% restart
echo   Rebuild:      %DOCKER_COMPOSE_CMD% up --build
echo.
echo Next Steps:
echo 1. Test the API at http://localhost:8000/docs
echo 2. Use your VS Code extension or API client
echo 3. Check logs if you encounter issues
echo.
pause
