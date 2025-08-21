#!/bin/bash
# NFT Analytics Engine - Health Check Script
# Generated: January 31, 2025

set -euo pipefail

# Configuration
API_BASE_URL=${API_BASE_URL:-"http://localhost:8001"}
TIMEOUT=${TIMEOUT:-30}
LOG_FILE="/var/log/nft-engine-health.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
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
}

# Health check functions
check_api_health() {
    log "Checking API health endpoint..."
    
    if response=$(curl -s -f --max-time "$TIMEOUT" "$API_BASE_URL/health"); then
        local status=$(echo "$response" | jq -r '.status' 2>/dev/null || echo "unknown")
        if [[ "$status" == "healthy" ]]; then
            success "API health check passed"
            return 0
        else
            error "API health check failed: status=$status"
            return 1
        fi
    else
        error "API health endpoint unreachable"
        return 1
    fi
}

check_database() {
    log "Checking database connectivity..."
    
    if docker-compose exec -T postgres pg_isready -U nft_user -d nft_analytics >/dev/null 2>&1; then
        success "Database connectivity check passed"
        return 0
    else
        error "Database connectivity check failed"
        return 1
    fi
}

check_redis() {
    log "Checking Redis connectivity..."
    
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        success "Redis connectivity check passed"
        return 0
    else
        error "Redis connectivity check failed"
        return 1
    fi
}

check_websocket() {
    log "Checking WebSocket connectivity..."
    
    # Use a simple WebSocket test
    if timeout 10 bash -c "exec 3<>/dev/tcp/localhost/8001 && echo 'GET /ws HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: test\r\nSec-WebSocket-Version: 13\r\n\r\n' >&3" >/dev/null 2>&1; then
        success "WebSocket connectivity check passed"
        return 0
    else
        warning "WebSocket connectivity check failed (may be normal if no active connections)"
        return 0  # Don't fail on WebSocket issues
    fi
}

check_api_endpoints() {
    log "Checking critical API endpoints..."
    
    local endpoints=(
        "/api/v1/nfts"
        "/api/v1/wallets"
        "/api/v1/markets"
        "/api/v1/collections"
        "/api/v1/traits"
    )
    
    local failed=0
    for endpoint in "${endpoints[@]}"; do
        if curl -s -f --max-time "$TIMEOUT" -o /dev/null "$API_BASE_URL$endpoint" >/dev/null 2>&1; then
            success "Endpoint $endpoint is responsive"
        else
            error "Endpoint $endpoint is not responsive"
            ((failed++))
        fi
    done
    
    if [[ $failed -eq 0 ]]; then
        success "All critical endpoints are responsive"
        return 0
    else
        error "$failed critical endpoints are not responsive"
        return 1
    fi
}

check_disk_space() {
    log "Checking disk space..."
    
    local usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $usage -lt 90 ]]; then
        success "Disk space usage: ${usage}% (OK)"
        return 0
    elif [[ $usage -lt 95 ]]; then
        warning "Disk space usage: ${usage}% (WARNING)"
        return 0
    else
        error "Disk space usage: ${usage}% (CRITICAL)"
        return 1
    fi
}

check_memory() {
    log "Checking memory usage..."
    
    local memory_info=$(free | grep '^Mem:')
    local total=$(echo "$memory_info" | awk '{print $2}')
    local used=$(echo "$memory_info" | awk '{print $3}')
    local usage=$((used * 100 / total))
    
    if [[ $usage -lt 85 ]]; then
        success "Memory usage: ${usage}% (OK)"
        return 0
    elif [[ $usage -lt 95 ]]; then
        warning "Memory usage: ${usage}% (WARNING)"
        return 0
    else
        error "Memory usage: ${usage}% (CRITICAL)"
        return 1
    fi
}

check_docker_containers() {
    log "Checking Docker container status..."
    
    local containers=$(docker-compose ps --services)
    local failed=0
    
    for container in $containers; do
        if docker-compose ps "$container" | grep -q "Up"; then
            success "Container $container is running"
        else
            error "Container $container is not running"
            ((failed++))
        fi
    done
    
    if [[ $failed -eq 0 ]]; then
        success "All containers are running"
        return 0
    else
        error "$failed containers are not running"
        return 1
    fi
}

# Generate health report
generate_report() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    local report_file="/tmp/nft-engine-health-report-$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" <<EOF
{
    "timestamp": "$timestamp",
    "checks": {
        "api_health": $1,
        "database": $2,
        "redis": $3,
        "websocket": $4,
        "api_endpoints": $5,
        "disk_space": $6,
        "memory": $7,
        "docker_containers": $8
    },
    "overall_status": "$9"
}
EOF
    
    log "Health report generated: $report_file"
}

# Main health check
main() {
    log "Starting NFT Analytics Engine health check..."
    
    local checks=()
    local overall_status="healthy"
    
    # Run all checks
    check_api_health && checks+=(true) || { checks+=(false); overall_status="unhealthy"; }
    check_database && checks+=(true) || { checks+=(false); overall_status="unhealthy"; }
    check_redis && checks+=(true) || { checks+=(false); overall_status="unhealthy"; }
    check_websocket && checks+=(true) || { checks+=(false); overall_status="degraded"; }
    check_api_endpoints && checks+=(true) || { checks+=(false); overall_status="unhealthy"; }
    check_disk_space && checks+=(true) || { checks+=(false); overall_status="unhealthy"; }
    check_memory && checks+=(true) || { checks+=(false); overall_status="degraded"; }
    check_docker_containers && checks+=(true) || { checks+=(false); overall_status="unhealthy"; }
    
    # Generate report
    generate_report "${checks[@]}" "$overall_status"
    
    # Final status
    if [[ "$overall_status" == "healthy" ]]; then
        success "🎉 All health checks passed - System is healthy!"
        exit 0
    elif [[ "$overall_status" == "degraded" ]]; then
        warning "⚠️ System is running but with some issues"
        exit 1
    else
        error "💥 System is unhealthy - Immediate attention required!"
        exit 2
    fi
}

# Run main function
main "$@"
