# Simple PowerShell script to launch the TPManuf FastAPI backend
Write-Host "Starting TPManuf API Server..." -ForegroundColor Green
Write-Host "API: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Docs: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "ReDoc: http://127.0.0.1:8000/redoc" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the FastAPI application with uvicorn
python -m uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000

