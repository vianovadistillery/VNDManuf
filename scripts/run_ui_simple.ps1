# Simple PowerShell script to launch the TPManuf Dash UI
Write-Host "Starting TPManuf Modern UI..." -ForegroundColor Green
Write-Host "Access the UI at: http://127.0.0.1:8050" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Dash application
python -c "from app.ui.app import app; app.run(debug=True, host='127.0.0.1', port=8050)"
