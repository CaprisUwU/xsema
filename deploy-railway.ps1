# XSEMA Railway Deployment Script (PowerShell)
Write-Host "🚀 Deploying XSEMA to Railway..." -ForegroundColor Green

# Check if git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "❌ Git not initialized. Initializing git..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial XSEMA commit"
}

# Check git status
Write-Host "📋 Checking git status..." -ForegroundColor Blue
git status

# Add Railway configuration files
Write-Host "⚙️ Adding Railway configuration files..." -ForegroundColor Blue
git add railway.json railway.toml

# Commit Railway configuration
Write-Host "💾 Committing Railway configuration..." -ForegroundColor Blue
git commit -m "Add Railway deployment configuration"

# Check if remote origin exists
$remoteExists = git remote get-url origin 2>$null
if ($remoteExists) {
    Write-Host "✅ Remote origin already exists: $remoteExists" -ForegroundColor Green
} else {
    Write-Host "❌ No remote origin found. Please add your GitHub repository:" -ForegroundColor Red
    Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git" -ForegroundColor Yellow
    exit 1
}

# Push to GitHub
Write-Host "📤 Pushing to GitHub..." -ForegroundColor Blue
git push origin main

Write-Host "✅ XSEMA pushed to GitHub successfully!" -ForegroundColor Green
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Go to Railway dashboard" -ForegroundColor White
Write-Host "   2. Click 'New Project'" -ForegroundColor White
Write-Host "   3. Select 'Deploy from GitHub repo'" -ForegroundColor White
Write-Host "   4. Search for your repository" -ForegroundColor White
Write-Host "   5. Deploy XSEMA!" -ForegroundColor White
