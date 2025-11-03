# TPManuf Development Script
param([string]$Command)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Title)
    Write-Host ""
    Write-ColorOutput "=== $Title ===" -Color Magenta
    Write-Host ""
}

switch ($Command) {
    "setup" {
        Write-Header "Setting Up Development Environment"
        Set-Location $ProjectRoot

        if (Test-Path ".venv") {
            Write-ColorOutput "Removing existing virtual environment..." -Color Yellow
            Remove-Item -Path ".venv" -Recurse -Force
        }

        Write-ColorOutput "Creating virtual environment..." -Color Cyan
        python -m venv .venv

        Write-ColorOutput "Installing dependencies..." -Color Cyan
        & $PythonExe -m pip install --upgrade pip
        & $PythonExe -m pip install -r requirements.txt

        Write-ColorOutput "Installing pre-commit hooks..." -Color Cyan
        & $PythonExe -m pre_commit install

        Write-ColorOutput "Setup completed successfully" -Color Green
    }
    "db" {
        Write-Header "Database Operations"
        Set-Location $ProjectRoot

        if (-not (Test-Path "alembic.ini")) {
            Write-ColorOutput "Creating database tables directly..." -Color Yellow
            $cmd = 'from app.adapters.db import create_tables; create_tables(); print("Database tables created")'
            & $PythonExe -c $cmd
        } else {
            Write-ColorOutput "Running Alembic migrations..." -Color Cyan
            & $PythonExe -m alembic upgrade head
        }

        Write-ColorOutput "Database operations completed" -Color Green
    }
    "api" {
        Write-Header "Starting API Server"
        Set-Location $ProjectRoot

        Write-ColorOutput "Starting FastAPI server..." -Color Cyan
        Write-ColorOutput "API: http://127.0.0.1:8000" -Color Cyan
        Write-ColorOutput "Docs: http://127.0.0.1:8000/docs" -Color Cyan

        & $PythonExe -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
    }
    "ui" {
        Write-Header "Starting UI Server"
        Set-Location $ProjectRoot

        Write-ColorOutput "Starting Dash UI server..." -Color Cyan
        Write-ColorOutput "UI: http://127.0.0.1:8050" -Color Cyan

        # Use -c with properly escaped quotes for PowerShell
        $cmd = "from app.ui.app import app; app.run(debug=True, host='127.0.0.1', port=8050)"
        & $PythonExe -c $cmd
    }
    "test" {
        Write-Header "Running Tests"
        Set-Location $ProjectRoot

        Write-ColorOutput "Running tests..." -Color Cyan
        & $PythonExe -m pytest tests/ -v

        Write-ColorOutput "Running linting..." -Color Cyan
        & $PythonExe -m ruff check app/ --fix
        & $PythonExe -m ruff format app/ --check
    }
    "help" {
        Write-Header "TPManuf Development Script"
        Write-ColorOutput "Available commands:" -Color Cyan
        Write-Host "  setup  - Create virtual environment and install dependencies"
        Write-Host "  db     - Run database migrations"
        Write-Host "  api    - Start API server (http://127.0.0.1:8000)"
        Write-Host "  ui     - Start UI server (http://127.0.0.1:8050)"
        Write-Host "  test   - Run tests and linting"
        Write-Host "  help   - Show this help"
        Write-Host ""
        Write-ColorOutput "Quick start:" -Color Cyan
        Write-Host "  .\scripts\dev.ps1 setup"
        Write-Host "  .\scripts\dev.ps1 db"
        Write-Host "  .\scripts\dev.ps1 api   (Terminal 1)"
        Write-Host "  .\scripts\dev.ps1 ui    (Terminal 2)"
    }
    default {
        Write-ColorOutput "Unknown command: $Command" -Color Red
        Write-ColorOutput "Run '.\scripts\dev.ps1 help' for available commands" -Color Cyan
    }
}

Write-Host ""
