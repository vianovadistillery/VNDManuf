# PowerShell script to launch the TPManuf Dash UI
# Run this script to start the web interface on port 8050

Write-Host "Starting TPManuf Modern UI..." -ForegroundColor Green
Write-Host "Make sure the API server is running on port 8000" -ForegroundColor Yellow
Write-Host ""

# Check if we're in a virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "Using virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Cyan
} else {
    Write-Host "Warning: No virtual environment detected" -ForegroundColor Yellow
    Write-Host "Consider activating your virtual environment first" -ForegroundColor Yellow
}

# Change to the project directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

Write-Host "Project directory: $projectDir" -ForegroundColor Cyan
Write-Host ""

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Cyan
try {
    $dashCheck = python -c "import dash; print('Dash version:', dash.__version__)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host $dashCheck -ForegroundColor Green
    } else {
        Write-Host "Dash not found. Installing..." -ForegroundColor Yellow
        pip install dash dash-bootstrap-components dash-table
    }
} catch {
    Write-Host "Error checking dependencies: $_" -ForegroundColor Red
}

# Check if API server is running
Write-Host "Checking API server..." -ForegroundColor Cyan
try {
    $apiCheck = Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($apiCheck.StatusCode -eq 200) {
        Write-Host "API server is running ✓" -ForegroundColor Green
    } else {
        Write-Host "API server check failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "API server not responding. Make sure to start it with:" -ForegroundColor Yellow
    Write-Host "  uvicorn app.api.main:app --reload" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting Dash UI on http://127.0.0.1:8050" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Dash application
try {
    python -c "from app.ui.app import app; app.run_server(debug=True, host='127.0.0.1', port=8050)"
} catch {
    Write-Host "Error starting UI: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "1. Make sure you're in the project directory" -ForegroundColor White
    Write-Host "2. Activate your virtual environment" -ForegroundColor White
    Write-Host "3. Install dependencies: pip install dash dash-bootstrap-components dash-table" -ForegroundColor White
    Write-Host "4. Make sure the API server is running on port 8000" -ForegroundColor White
}
