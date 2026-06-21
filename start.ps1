# Start vnd-api and vnd-ui in separate tabs of a single PowerShell/Windows Terminal window.
# Usage: .\start-vnd.ps1   (run from project root, or the script will use its own directory)

$ErrorActionPreference = "Stop"
$ProjectRoot = if ($PSScriptRoot) { $PSScriptRoot } else { Get-Location | Select-Object -ExpandProperty Path }

$apiScript = Join-Path $ProjectRoot "vnd-api.ps1"
$uiScript  = Join-Path $ProjectRoot "vnd-ui.ps1"

if (-not (Test-Path $apiScript)) { throw "vnd-api.ps1 not found at $apiScript" }
if (-not (Test-Path $uiScript))  { throw "vnd-ui.ps1 not found at $uiScript" }

# Prefer Windows Terminal (wt) for tabs in one window; fallback to two separate PowerShell windows
$wt = Get-Command wt -ErrorAction SilentlyContinue

if ($wt) {
    # Two tabs in one Windows Terminal window (semicolon separates wt commands)
    # Quote paths so spaces work
    $d = "`"$ProjectRoot`""
    $fApi = "`"$apiScript`""
    $fUi = "`"$uiScript`""
    Start-Process wt -ArgumentList @(
        "new-tab", "--title", "vnd-api", "-d", $d,
        "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $fApi
        ";",
        "new-tab", "--title", "vnd-ui", "-d", $d,
        "powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $fUi
    )
    Write-Host "Started vnd-api and vnd-ui in Windows Terminal tabs."
} else {
    # Fallback: two separate PowerShell windows
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $apiScript -WorkingDirectory $ProjectRoot
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $uiScript  -WorkingDirectory $ProjectRoot
    Write-Host "Started vnd-api and vnd-ui in two separate windows (install Windows Terminal for tabs in one window)."
}
