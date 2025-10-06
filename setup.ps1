# My ZSH Setup Script for Windows/WSL
# PowerShell version of the setup script

Write-Host "🚀 Setting up ZSH configuration..." -ForegroundColor Blue
Write-Host ""

# Get the directory where this script is located
$SCRIPT_DIR = $PSScriptRoot

# Detect if running in WSL or native PowerShell
$IsWSL = $false
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    $IsWSL = $true
    Write-Host "✓ WSL detected. Will configure ZSH in WSL environment." -ForegroundColor Green
} else {
    Write-Host "⚠️  This script is designed for WSL (Windows Subsystem for Linux)." -ForegroundColor Yellow
    Write-Host "   If you're using Git Bash or similar, please run setup.sh instead." -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne 'y') {
        exit
    }
}

# Convert Windows path to WSL path
$WSL_PATH = $SCRIPT_DIR -replace '\\', '/' -replace 'C:', '/mnt/c'

Write-Host "📝 Configuring .zshrc in WSL" -ForegroundColor Green

# Create the setup command for WSL
$setupCommand = @"
cd '$WSL_PATH' && chmod +x setup.sh && ./setup.sh
"@

if ($IsWSL) {
    wsl bash -c $setupCommand
    Write-Host ""
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "To apply changes in your WSL terminal, run:" -ForegroundColor Blue
    Write-Host "  source ~/.zshrc" -ForegroundColor Green
} else {
    Write-Host "Command to run in your Unix-like shell:" -ForegroundColor Yellow
    Write-Host $setupCommand -ForegroundColor Cyan
}

