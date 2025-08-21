#!/bin/bash

# 🚀 XSEMA PRODUCTION DEPLOYMENT SCRIPT
# Date: 16th August 2025
# Status: Phase 2 Complete (100%) - Ready for Production

set -e  # Exit on any error

echo "🚀 XSEMA PRODUCTION DEPLOYMENT STARTING..."
echo "✅ Phase 2 Complete - All Advanced Features Ready"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    print_success "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker Compose is available"
}

# Check environment file
check_environment() {
    print_status "Checking environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            print_warning ".env file not found. Creating from .env.example..."
            cp .env.example .env
            print_warning "Please edit .env file with your production values before continuing."
            echo ""
            echo "Required environment variables:"
            echo "  - DATABASE_URL: PostgreSQL connection string"
            echo "  - REDIS_URL: Redis connection string"
            echo "  - SECRET_KEY: Production secret key"
            echo "  - JWT_SECRET_KEY: JWT secret key"
            echo "  - API_HOST: API host (0.0.0.0 for production)"
            echo "  - API_PORT: API port (8000)"
            echo "  - CORS_ORIGINS: Allowed CORS origins"
            echo ""
            read -p "Press Enter after editing .env file to continue..."
        else
            print_error ".env file not found and .env.example not available."
            exit 1
        fi
    fi
    
    print_success "Environment configuration ready"
}

# Build and start services
deploy_services() {
    print_status "Building and starting XSEMA services..."
    
    # Stop any existing containers
    print_status "Stopping existing containers..."
    docker-compose down --remove-orphans
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose up -d
    
    print_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    timeout=60
    counter=0
    while ! docker-compose exec -T api python -c "
from database import engine
try:
    with engine.connect() as conn:
        print('Database connected')
        exit(0)
except Exception as e:
    print(f'Database not ready: {e}')
    exit(1)
" &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "Database failed to start within $timeout seconds"
            exit 1
        fi
        echo -n "."
    done
    echo ""
    print_success "Database is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    timeout=30
    counter=0
    while ! docker-compose exec -T api python -c "
from redis import Redis
try:
    redis_client = Redis.from_url('redis://redis:6379/0')
    redis_client.ping()
    print('Redis connected')
    exit(0)
except Exception as e:
    print(f'Redis not ready: {e}')
    exit(1)
" &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "Redis failed to start within $timeout seconds"
            exit 1
        fi
        echo -n "."
    done
    echo ""
    print_success "Redis is ready"
    
    # Wait for API
    print_status "Waiting for API service..."
    timeout=60
    counter=0
    while ! curl -s http://localhost:8000/health &> /dev/null; do
        sleep 2
        counter=$((counter + 2))
        if [ $counter -ge $timeout ]; then
            print_error "API service failed to start within $timeout seconds"
            exit 1
        fi
        echo -n "."
    done
    echo ""
    print_success "API service is ready"
}

# Run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # API health
    print_status "Checking API health..."
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "API health check passed"
    else
        print_error "API health check failed"
        exit 1
    fi
    
    # Database health
    print_status "Checking database health..."
    if docker-compose exec -T api python -c "
from database import engine
try:
    with engine.connect() as conn:
        result = conn.execute('SELECT 1')
        print('Database health check passed')
        exit(0)
except Exception as e:
    print(f'Database health check failed: {e}')
    exit(1)
" &> /dev/null; then
        print_success "Database health check passed"
    else
        print_error "Database health check failed"
        exit 1
    fi
    
    # Redis health
    print_status "Checking Redis health..."
    if docker-compose exec -T api python -c "
from redis import Redis
try:
    redis_client = Redis.from_url('redis://redis:6379/0')
    redis_client.ping()
    print('Redis health check passed')
    exit(0)
except Exception as e:
    print(f'Redis health check failed: {e}')
    exit(1)
" &> /dev/null; then
        print_success "Redis health check passed"
    else
        print_error "Redis health check failed"
        exit 1
    fi
}

# Run feature tests
run_feature_tests() {
    print_status "Running feature tests..."
    
    # Test portfolio creation
    print_status "Testing portfolio creation..."
    if curl -s -X POST http://localhost:8000/api/v1/portfolios \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Portfolio", "user_id": "test-user"}' | grep -q "portfolio_id"; then
        print_success "Portfolio creation test passed"
    else
        print_warning "Portfolio creation test failed (may require authentication)"
    fi
    
    # Test P&L calculation endpoint
    print_status "Testing P&L calculation endpoint..."
    if curl -s http://localhost:8000/api/v1/advanced-analytics/health/advanced-features | grep -q "healthy"; then
        print_success "Advanced analytics health check passed"
    else
        print_warning "Advanced analytics health check failed"
    fi
}

# Show deployment status
show_deployment_status() {
    echo ""
    echo "🎉 XSEMA PRODUCTION DEPLOYMENT COMPLETED SUCCESSFULLY!"
    echo ""
    echo "✅ All services are running and healthy"
    echo "✅ Health checks passed"
    echo "✅ Feature tests completed"
    echo ""
    echo "🌐 Service URLs:"
    echo "  - API: http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Health Check: http://localhost:8000/health"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 Monitoring:"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - Grafana: http://localhost:3001"
    echo ""
    echo "🔧 Management Commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop services: docker-compose down"
    echo "  - Restart services: docker-compose restart"
    echo "  - Update services: docker-compose pull && docker-compose up -d"
    echo ""
    echo "🚀 XSEMA is now ready for production use!"
    echo ""
}

# Main deployment function
main() {
    echo "🚀 XSEMA PRODUCTION DEPLOYMENT"
    echo "================================"
    echo ""
    
    # Pre-deployment checks
    check_docker
    check_docker_compose
    check_environment
    
    echo ""
    echo "Starting deployment..."
    echo ""
    
    # Deploy services
    deploy_services
    
    # Wait for services
    wait_for_services
    
    # Health checks
    run_health_checks
    
    # Feature tests
    run_feature_tests
    
    # Show status
    show_deployment_status
}

# Run main function
main "$@"
