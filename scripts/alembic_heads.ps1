$ErrorActionPreference = "Stop"

Write-Host "== alembic heads (verbose) =="
alembic heads --verbose

exit $LASTEXITCODE
