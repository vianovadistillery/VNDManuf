# TPManuf Development Script
# Usage: .\scripts\dev.ps1 <command>

param(
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("help")]
    [string]$Command
)

if ($Command -eq "help") {
    Write-Host "TPManuf Development Script Help"
    Write-Host "Available commands: setup, db, api, ui, test, clean, help"
}
