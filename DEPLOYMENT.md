# Smart Locomotive Health Monitor - Complete Deployment & Development Guide

## 📋 Table of Contents
1. [Project Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Local Development Setup](#local-development-setup)
5. [Docker Deployment](#docker-deployment)
6. [Kubernetes Deployment](#kubernetes-deployment)
7. [API Documentation](#api-documentation)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)

## 🚀 Overview

Smart Locomotive Health Monitor is an enterprise-grade predictive maintenance system featuring:

- **AI/ML Capabilities**: Fuzzy logic, LSTM, CNN models for failure prediction
- **Real-time Monitoring**: WebSocket & MQTT support for live updates
- **Scalable Architecture**: Kubernetes-ready with Docker containerization
- **Secure API**: JWT authentication with role-based access control
- **Mobile App**: React Native cross-platform application
- **Production Ready**: Comprehensive testing, monitoring, and deployment configs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
├─────────────────────────────────────────────────────────┤
│  • React Native Mobile App (iOS/Android)                 │
│  • Web Dashboard (HTML/CSS/JS)                           │
│  • Real-time WebSocket Communication                     │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│               Nginx Reverse Proxy                        │
│    (Rate Limiting, SSL/TLS, Load Balancing)             │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│           Flask Backend API (Python)                    │
├─────────────────────────────────────────────────────────┤
│  • Authentication & Authorization (JWT)                 │
│  • RESTful API Endpoints                                │
│  • Real-time Service (WebSocket/MQTT)                   │
│  • ML/AI Analysis Engine                                │
│  • Alert Management System                              │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┬─────────────┐
        │              │              │             │
┌──────▼──┐   ┌──────▼──┐   ┌──────▼──┐   ┌──────▼──┐
│PostgreSQL│   │ Redis   │   │  MQTT   │   │  Cache  │
│ Database │   │ Cache   │   │  Broker │   │ Storage │
└──────────┘   └─────────┘   └─────────┘   └─────────┘
```

## ✅ Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows (WSL2)
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum (16GB+ for production)
- **Disk**: 20GB+ free space

### Software Requirements
- **Docker & Docker Compose** (latest)
- **Python 3.11+** (for local development)
- **Node.js 16+** (for frontend development)
- **PostgreSQL 14+** (for production)
- **Kubernetes 1.24+** (for K8s deployment)
- **Git** (for version control)

### Development Tools
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose

# Install Kubernetes (optional)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
```

## 🔧 Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/Bangladesh-Railways/locomotive-monitor.git
cd locomotive-monitor
```

### 2. Create Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Initialize Database (Local Development)
```bash
# For SQLite (testing only)
python backend/app_v2.py

# For PostgreSQL (production)
export DATABASE_URL="postgresql://user:password@localhost:5432/locomotive_monitor"
flask db init
flask db migrate
flask db upgrade
```

### 5. Run Backend Server
```bash
python backend/app_v2.py
# API available at http://localhost:5000
# Swagger docs at http://localhost:5000/docs
```

### 6. Run Frontend (in another terminal)
```bash
# Web Dashboard
cd frontend
python -m http.server 8000
# Open http://localhost:8000

# Mobile App
cd mobile
npm install
npm start
# Select "i" for iOS or "a" for Android
```

### 7. Run Tests
```bash
pytest backend/tests/ -v --cov=backend
```

## 🐳 Docker Deployment

### Quick Start (All Services)
```bash
# Clone & setup
git clone https://github.com/Bangladesh-Railways/locomotive-monitor.git
cd locomotive-monitor

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Deploy
chmod +x deploy.sh
./deploy.sh development

# Check services
docker-compose ps
```

### Service Management
```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f db

# Rebuild containers
docker-compose build --no-cache

# Stop services
docker-compose down

# Complete cleanup
docker-compose down -v  # Removes volumes!
```

### Access Services
- **API**: http://localhost:5000
- **API Docs**: http://localhost:5000/docs
- **Frontend**: http://localhost  (through Nginx)
- **PgAdmin**: http://localhost:5050
- **Database**: localhost:5432
- **Redis**: localhost:6379
- **MQTT**: localhost:1883

## ☸️ Kubernetes Deployment

### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/stable.txt"
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl

# Install Minikube (for local K8s)
curl -minikube https://github.com/kubernetes/minikube/releases/download/latest/minikube-linux-amd64
chmod +x minikube
./minikube start
```

### Deploy to Kubernetes
```bash
# Create namespace
kubectl create namespace locomotive-monitor

# Create secrets
kubectl create secret generic locomotive-secrets \
  --from-literal=jwt-secret-key=your-secret-key \
  --from-literal=db-password=your-db-password \
  -n locomotive-monitor

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Check deployment status
kubectl get pods -n locomotive-monitor
kubectl get services -n locomotive-monitor

# Port forward for local access
kubectl port-forward svc/locomotive-backend 5000:5000 -n locomotive-monitor
```

### Scaling & Management
```bash
# Scale replicas
kubectl scale deployment locomotive-backend --replicas=5 -n locomotive-monitor

# View logs
kubectl logs -f deployment/locomotive-backend -n locomotive-monitor

# Get deployment info
kubectl describe deployment locomotive-backend -n locomotive-monitor

# Update image
kubectl set image deployment/locomotive-backend \
  backend=localhost:5000/locomotive-monitor:v1.1.0 \
  -n locomotive-monitor

# Rollback
kubectl rollout undo deployment/locomotive-backend -n locomotive-monitor
```

## 📚 API Documentation

### Authentication
```bash
# Register
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "email": "user@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user",
    "password": "password123"
  }'
```

### Access API (with Token)
```bash
# Get locomotives
curl -X GET http://localhost:5000/api/locomotives \
  -H "Authorization: Bearer YOUR_TOKEN"

# Analyze locomotive health
curl -X POST http://localhost:5000/api/health/BR1001 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "temperature": 85.5,
    "vibration": 5.2,
    "pressure": 150,
    "oil_quality": 25,
    "mileage": 150000,
    "latitude": 23.7275,
    "longitude": 90.4086
  }'

# Get alerts
curl -X GET http://localhost:5000/api/alerts/BR1001 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Full API Documentation
Visit http://localhost:5000/docs (Swagger UI) for complete interactive documentation.

## 🧪 Testing

### Run All Tests
```bash
pytest backend/tests/ -v
```

### Run Specific Test Suite
```bash
pytest backend/tests/test_api.py::TestAuthentication -v
pytest backend/tests/test_api.py::TestHealthAnalysis -v
```

### Test Coverage
```bash
pytest backend/tests/ --cov=backend --cov-report=html
# Open htmlcov/index.html in browser
```

### Manual Testing
```bash
# Health check
curl http://localhost:5000

# Create test data
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User"
  }'
```

## 🔍 Monitoring & Logging

### View Application Logs
```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f db

# Kubernetes
kubectl logs -f deployment/locomotive-backend -n locomotive-monitor
```

### Monitor System Health
```bash
# CPU/Memory usage
docker stats

# Database connections
docker-compose exec db psql -U locomotive -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"

# Cache status
docker-compose exec redis redis-cli info
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```bash
# Check database is running
docker-compose ps db

# Check connection string in .env
grep DATABASE_URL .env

# Test connection
python -c "import psycopg2; psycopg2.connect('postgresql://user:password@localhost:5432/locomotive_monitor')"
```

#### 2. Port Already in Use
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>
```

#### 3. Docker Permissions
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### 4. Out of Memory
```bash
# Increase Docker memory limit
docker update --memory 4g <container_id>
```

### Debug Mode
```bash
# Enable debug logging
export FLASK_ENV=development
export FLASK_DEBUG=1
python backend/app_v2.py
```

##Contributing

### Development Workflow
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes and test: `pytest backend/tests/`
3. Commit: `git commit -am 'Add feature'`
4. Push: `git push origin feature/your-feature`
5. Create Pull Request

### Code Quality
```bash
# Format code
black backend/

# Lint code
pylint backend/

# Type checking
mypy backend/
```

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/Bangladesh-Railways/locomotive-monitor/issues
- Documentation: https://docs.example.com
- Email: support@railway.gov.bd

## 📄 License

Licensed under MIT License. See LICENSE file.

---

**Last Updated**: May 2025
**Version**: 2.0.0
**Status**: Production Ready ✅
