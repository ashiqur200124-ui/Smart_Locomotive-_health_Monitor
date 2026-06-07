#!/bin/bash

# Deployment script for Smart Locomotive Health Monitor
# Supports Docker, Docker Compose, and Kubernetes deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-development}
VERSION=$(date +%Y%m%d_%H%M%S)
DOCKER_REGISTRY=${DOCKER_REGISTRY:-localhost:5000}
APP_NAME=locomotive-monitor

echo -e "${YELLOW}=== Smart Locomotive Health Monitor Deployment ===${NC}"
echo -e "${YELLOW}Environment: $ENVIRONMENT${NC}"
echo -e "${YELLOW}Version: $VERSION${NC}"

# Function to build Docker image
build_image() {
    echo -e "${YELLOW}Building Docker image...${NC}"
    docker build -t $DOCKER_REGISTRY/$APP_NAME:$VERSION .
    docker tag $DOCKER_REGISTRY/$APP_NAME:$VERSION $DOCKER_REGISTRY/$APP_NAME:latest
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
}

# Function to push Docker image
push_image() {
    echo -e "${YELLOW}Pushing Docker image to registry...${NC}"
    docker push $DOCKER_REGISTRY/$APP_NAME:$VERSION
    docker push $DOCKER_REGISTRY/$APP_NAME:latest
    echo -e "${GREEN}✓ Docker image pushed successfully${NC}"
}

# Function to deploy with Docker Compose
deploy_docker_compose() {
    echo -e "${YELLOW}Deploying with Docker Compose...${NC}"
    
    # Load environment variables
    if [ -f .env ]; then
        export $(cat .env | grep -v '#' | xargs)
    fi
    
    # Build and start containers
    docker-compose down
    docker-compose up -d
    
    # Wait for services to be ready
    echo -e "${YELLOW}Waiting for services to be ready...${NC}"
    sleep 10
    
    # Run migrations
    echo -e "${YELLOW}Running database migrations...${NC}"
    docker-compose exec -T backend flask init_db
    docker-compose exec -T backend flask load_initial_data
    
    echo -e "${GREEN}✓ Docker Compose deployment completed${NC}"
}

# Function to deploy with Kubernetes
deploy_kubernetes() {
    echo -e "${YELLOW}Deploying with Kubernetes...${NC}"
    
    # Create namespace
    kubectl create namespace locomotive-monitor || true
    
    # Create ConfigMap for environment variables
    kubectl create configmap locomotive-config \
        --from-file=.env \
        -n locomotive-monitor \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create secrets
    kubectl create secret generic locomotive-secrets \
        --from-literal=jwt-secret-key=$JWT_SECRET_KEY \
        --from-literal=db-password=$POSTGRES_PASSWORD \
        -n locomotive-monitor \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Kubernetes manifests
    kubectl apply -f k8s/ -n locomotive-monitor
    
    # Wait for deployment
    kubectl rollout status deployment/locomotive-backend -n locomotive-monitor
    
    echo -e "${GREEN}✓ Kubernetes deployment completed${NC}"
}

# Function to run health checks
health_check() {
    echo -e "${YELLOW}Running health checks...${NC}"
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        echo -n "Attempt $attempt/$max_attempts: "
        
        if curl -s http://localhost:5000 > /dev/null; then
            echo -e "${GREEN}✓ Backend is healthy${NC}"
            return 0
        fi
        
        echo "Backend not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}✗ Health check failed${NC}"
    return 1
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    
    if docker-compose ps | grep -q backend; then
        docker-compose exec backend pytest -v
    else
        pytest backend/tests/ -v
    fi
    
    echo -e "${GREEN}✓ Tests completed${NC}"
}

# Function to show deployment status
show_status() {
    echo -e "${YELLOW}Deployment Status:${NC}"
    
    if [ "$ENVIRONMENT" = "docker-compose" ]; then
        docker-compose ps
    elif [ "$ENVIRONMENT" = "kubernetes" ]; then
        kubectl get deployments -n locomotive-monitor
        kubectl get pods -n locomotive-monitor
        kubectl get services -n locomotive-monitor
    fi
}

# Main deployment flow
case $ENVIRONMENT in
    development)
        echo -e "${YELLOW}Setting up development environment...${NC}"
        build_image
        deploy_docker_compose
        health_check
        show_status
        ;;
    production)
        echo -e "${YELLOW}Setting up production environment...${NC}"
        build_image
        push_image
        deploy_kubernetes
        health_check
        show_status
        ;;
    docker-compose)
        deploy_docker_compose
        health_check
        show_status
        ;;
    kubernetes|k8s)
        deploy_kubernetes
        health_check
        show_status
        ;;
    test)
        build_image
        run_tests
        ;;
    build)
        build_image
        ;;
    *)
        echo -e "${RED}Usage: $0 [development|production|docker-compose|kubernetes|test|build]${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}=== Deployment Complete ===${NC}"
