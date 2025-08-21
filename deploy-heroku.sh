#!/bin/bash

# XSEMA Heroku Deployment Script
echo "🚀 Deploying XSEMA to Heroku..."

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Heroku CLI not found. Please install it first:"
    echo "   Windows: winget install --id=Heroku.HerokuCLI"
    echo "   Or download from: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Check if user is logged in to Heroku
if ! heroku auth:whoami &> /dev/null; then
    echo "🔐 Please login to Heroku first:"
    echo "   heroku login"
    exit 1
fi

# Create Heroku app (if it doesn't exist)
APP_NAME="xsema-nft-api"
if ! heroku apps:info $APP_NAME &> /dev/null; then
    echo "📱 Creating Heroku app: $APP_NAME"
    heroku create $APP_NAME
else
    echo "✅ Heroku app already exists: $APP_NAME"
fi

# Set environment variables
echo "⚙️ Setting environment variables..."
heroku config:set NODE_ENV=production
heroku config:set PYTHON_VERSION=3.11.7

# Add buildpacks
echo "🔧 Adding buildpacks..."
heroku buildpacks:clear
heroku buildpacks:add heroku/python

# Deploy to Heroku
echo "🚀 Deploying to Heroku..."
git add .
git commit -m "Deploy XSEMA to Heroku"
git push heroku main

# Open the app
echo "🌐 Opening XSEMA on Heroku..."
heroku open

echo "✅ Deployment complete!"
echo "🌐 Your app URL: https://$APP_NAME.herokuapp.com"
echo "📊 View logs: heroku logs --tail"
echo "🔧 Run commands: heroku run python manage.py migrate"
