#!/bin/bash

# 🚀 Quick Deployment Script for Automotive Service Scheduling System
# Author: Shivangi Rastogi
# This script prepares and deploys the app to Heroku

echo "🚀 Starting deployment preparation..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "❌ Error: Git repository not found. Please initialize git first."
    exit 1
fi

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo "❌ Error: Heroku CLI not found. Please install it first:"
    echo "   Visit: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Get app name from user
read -p "Enter your Heroku app name (e.g., automotive-service-app): " APP_NAME

if [ -z "$APP_NAME" ]; then
    echo "❌ Error: App name cannot be empty."
    exit 1
fi

echo "📦 Preparing deployment files..."

# Commit any changes
git add .
git status
read -p "Do you want to commit these changes? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Prepare for deployment - $(date)"
    echo "✅ Changes committed!"
fi

echo "🔧 Creating Heroku app..."
heroku create $APP_NAME

echo "⚙️ Setting environment variables..."
heroku config:set FLASK_APP=app.py --app $APP_NAME
heroku config:set FLASK_ENV=production --app $APP_NAME
heroku config:set SECRET_KEY=$(openssl rand -base64 32) --app $APP_NAME

echo "🚀 Deploying to Heroku..."
git push heroku main

echo "🗄️ Initializing database..."
heroku run python setup.py --app $APP_NAME

echo "✅ Deployment complete!"
echo "🌐 Your app is available at: https://$APP_NAME.herokuapp.com"
echo "📊 View logs: heroku logs --tail --app $APP_NAME"
echo "🔧 Open app: heroku open --app $APP_NAME"

# Open the app
read -p "Do you want to open the app now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    heroku open --app $APP_NAME
fi

echo "🎉 Deployment successful! Your automotive service scheduling system is now live!"
