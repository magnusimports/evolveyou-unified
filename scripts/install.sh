#!/bin/bash

# EvolveYou - Installation Script
# Installs all dependencies for the monorepo

set -e

echo "🚀 EvolveYou - Installation Started"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root"
   exit 1
fi

# Check prerequisites
log_info "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    log_error "Node.js version 18+ required. Current version: $(node --version)"
    exit 1
fi

log_success "Node.js $(node --version) ✓"

# Check npm
if ! command -v npm &> /dev/null; then
    log_error "npm is not installed"
    exit 1
fi

log_success "npm $(npm --version) ✓"

# Check Docker
if ! command -v docker &> /dev/null; then
    log_warning "Docker is not installed. Some features may not work."
else
    log_success "Docker $(docker --version | cut -d' ' -f3 | cut -d',' -f1) ✓"
fi

# Check Flutter (optional)
if command -v flutter &> /dev/null; then
    log_success "Flutter $(flutter --version | head -n1 | cut -d' ' -f2) ✓"
else
    log_warning "Flutter is not installed. Mobile development will not be available."
fi

# Install root dependencies
log_info "Installing root dependencies..."
npm install

# Install workspace dependencies
log_info "Installing workspace dependencies..."

# Backend Services
log_info "Installing backend services..."
for service in services/*/; do
    if [ -f "$service/requirements.txt" ]; then
        log_info "Installing Python dependencies for $(basename "$service")"
        cd "$service"
        if command -v python3 &> /dev/null; then
            python3 -m pip install -r requirements.txt --user
        else
            log_warning "Python3 not found, skipping $(basename "$service")"
        fi
        cd - > /dev/null
    fi
done

# Frontend Applications
log_info "Installing frontend applications..."
for app in apps/*/; do
    if [ -f "$app/package.json" ]; then
        log_info "Installing dependencies for $(basename "$app")"
        cd "$app"
        npm install
        cd - > /dev/null
    fi
done

# Flutter Mobile App
if [ -f "apps/mobile/pubspec.yaml" ] && command -v flutter &> /dev/null; then
    log_info "Installing Flutter dependencies..."
    cd apps/mobile
    flutter pub get
    cd - > /dev/null
fi

# Setup environment
log_info "Setting up environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    log_success "Created .env file from template"
    log_warning "Please edit .env file with your actual configuration"
else
    log_info ".env file already exists"
fi

# Setup Git hooks (if in git repo)
if [ -d ".git" ]; then
    log_info "Setting up Git hooks..."
    if [ -f "scripts/git-hooks/pre-commit" ]; then
        cp scripts/git-hooks/pre-commit .git/hooks/
        chmod +x .git/hooks/pre-commit
        log_success "Pre-commit hook installed"
    fi
fi

# Create necessary directories
log_info "Creating necessary directories..."
mkdir -p logs
mkdir -p tmp
mkdir -p uploads
mkdir -p .cache

# Set permissions
chmod +x scripts/**/*.sh 2>/dev/null || true

log_success "Installation completed successfully!"
echo ""
echo "🎉 Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run 'docker-compose up -d' to start services"
echo "3. Run 'npm run dev' to start development"
echo ""
echo "📚 Documentation: docs/README.md"
echo "🆘 Support: suporte@evolveyou.com.br"

