# XSEMA Heroku Deployment Script (PowerShell)
Write-Host "🚀 Deploying XSEMA to Heroku..." -ForegroundColor Green

# Check if Heroku CLI is installed
try {
    $herokuVersion = heroku --version
    Write-Host "✅ Heroku CLI found: $herokuVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Heroku CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   Windows: winget install --id=Heroku.HerokuCLI" -ForegroundColor Yellow
    Write-Host "   Or download from: https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor Yellow
    exit 1
}

# Check if user is logged in to Heroku
try {
    $whoami = heroku auth:whoami
    Write-Host "✅ Logged in as: $whoami" -ForegroundColor Green
} catch {
    Write-Host "🔐 Please login to Heroku first:" -ForegroundColor Yellow
    Write-Host "   heroku login" -ForegroundColor Yellow
    exit 1
}

# Create Heroku app (if it doesn't exist)
$APP_NAME = "xsema-nft-api"
try {
    $appInfo = heroku apps:info $APP_NAME
    Write-Host "✅ Heroku app already exists: $APP_NAME" -ForegroundColor Green
} catch {
    Write-Host "📱 Creating Heroku app: $APP_NAME" -ForegroundColor Yellow
    heroku create $APP_NAME
}

# Set environment variables
Write-Host "⚙️ Setting environment variables..." -ForegroundColor Yellow
heroku config:set NODE_ENV=production
heroku config:set PYTHON_VERSION=3.11.7

# Add buildpacks
Write-Host "🔧 Adding buildpacks..." -ForegroundColor Yellow
heroku buildpacks:clear
heroku buildpacks:add heroku/python

# Deploy to Heroku
Write-Host "🚀 Deploying to Heroku..." -ForegroundColor Yellow
git add .
git commit -m "Deploy XSEMA to Heroku"
git push heroku main

# Open the app
Write-Host "🌐 Opening XSEMA on Heroku..." -ForegroundColor Yellow
heroku open

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "🌐 Your app URL: https://$APP_NAME.herokuapp.com" -ForegroundColor Cyan
Write-Host "📊 View logs: heroku logs --tail" -ForegroundColor Cyan
Write-Host "🔧 Run commands: heroku run python manage.py migrate" -ForegroundColor Cyan
