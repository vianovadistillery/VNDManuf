# Safe migration runner for Windows PowerShell
# Runs alembic upgrade head and safe check, always exits 0

$ErrorActionPreference = "Stop"

Write-Host "== alembic upgrade head =="
alembic upgrade head

Write-Host "`n== alembic check (safe) =="
python scripts/alembic_check_safe.py

Write-Host "`n== summary =="
if (Test-Path tmp\alembic_drift.txt) {
    $content = Get-Content tmp\alembic_drift.txt -Raw
    if ($content -match "New upgrade operations detected|Detected ") {
        Write-Host "Drift found → tmp\alembic_drift.txt"
    } else {
        Write-Host "No drift detected."
    }
} else {
    Write-Host "No drift file found."
}

exit 0
