#!/bin/bash
# NFT Analytics Engine - Production Deployment Script
# Generated: January 31, 2025

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_ENV=${DEPLOYMENT_ENV:-production}
APP_NAME="nft-analytics-engine"
BACKUP_DIR="/var/backups/nft-engine"
LOG_FILE="/var/log/nft-engine-deploy.log"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}" | tee -a "$LOG_FILE"
    exit 1
}

# Pre-deployment checks
check_requirements() {
    log "Checking deployment requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
    fi
    
    # Check if environment file exists
    if [[ ! -f "config/production.env" ]]; then
        error "Production environment file not found: config/production.env"
    fi
    
    # Check if required environment variables are set
    source config/production.env
    if [[ -z "${SECRET_KEY:-}" ]]; then
        error "SECRET_KEY not set in environment"
    fi
    
    success "All requirements met"
}

# Backup current deployment
backup_current() {
    log "Creating backup of current deployment..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)"
    BACKUP_PATH="$BACKUP_DIR/$(date +%Y%m%d_%H%M%S)"
    
    # Backup database
    if docker-compose ps postgres | grep -q "Up"; then
        log "Backing up database..."
        docker-compose exec -T postgres pg_dump -U nft_user nft_analytics > "$BACKUP_PATH/database.sql"
        success "Database backed up to $BACKUP_PATH/database.sql"
    fi
    
    # Backup volumes
    if docker volume ls | grep -q "${APP_NAME}_postgres_data"; then
        log "Backing up data volumes..."
        docker run --rm -v "${APP_NAME}_postgres_data:/source" -v "$BACKUP_PATH:/backup" alpine tar czf /backup/postgres_data.tar.gz -C /source .
        success "Volumes backed up"
    fi
}

# Build new images
build_images() {
    log "Building new Docker images..."
    
    # Build the main application image
    docker-compose build --no-cache nft-engine
    
    # Tag with version
    local version=$(grep "APP_VERSION" config/production.env | cut -d'=' -f2)
    docker tag "${APP_NAME}_nft-engine:latest" "${APP_NAME}_nft-engine:$version"
    
    success "Images built successfully"
}

# Deploy application
deploy() {
    log "Deploying NFT Analytics Engine..."
    
    # Stop current containers
    log "Stopping current containers..."
    docker-compose down --remove-orphans
    
    # Start new deployment
    log "Starting new deployment..."
    docker-compose --env-file config/production.env up -d
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    timeout 300 bash -c 'until docker-compose ps | grep -q "healthy"; do sleep 5; done'
    
    success "Deployment completed successfully"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Check if all services are running
    if ! docker-compose ps | grep -q "Up"; then
        error "Some services are not running"
    fi
    
    # Check API health endpoint
    if ! curl -f http://localhost:8001/health > /dev/null 2>&1; then
        error "API health check failed"
    fi
    
    # Check database connectivity
    if ! docker-compose exec -T postgres pg_isready -U nft_user > /dev/null 2>&1; then
        error "Database health check failed"
    fi
    
    # Check Redis connectivity
    if ! docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        error "Redis health check failed"
    fi
    
    success "All health checks passed"
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old images and containers..."
    
    # Remove old images (keep last 3 versions)
    docker images "${APP_NAME}_nft-engine" --format "table {{.Tag}}" | tail -n +4 | xargs -r docker rmi "${APP_NAME}_nft-engine:" || true
    
    # Remove unused volumes and networks
    docker system prune -f --volumes
    
    success "Cleanup completed"
}

# Main deployment process
main() {
    log "Starting NFT Analytics Engine deployment..."
    log "Environment: $DEPLOYMENT_ENV"
    
    check_requirements
    backup_current
    build_images
    deploy
    health_check
    cleanup
    
    success "🎉 NFT Analytics Engine deployed successfully!"
    log "Access the API at: http://localhost:8001"
    log "API Documentation: http://localhost:8001/docs"
    log "Health Status: http://localhost:8001/health"
}

# Run main function
main "$@"
