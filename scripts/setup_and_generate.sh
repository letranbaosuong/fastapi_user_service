#!/bin/bash

# Setup and Generate Dummy Data Script
#
# CHỨC NĂNG:
# - Check dependencies
# - Install missing packages
# - Start Docker services
# - Generate dummy data
#
# USAGE (từ project root):
# chmod +x scripts/setup_and_generate.sh
# ./scripts/setup_and_generate.sh
#
# Hoặc từ bất kỳ đâu:
# cd /path/to/project
# ./scripts/setup_and_generate.sh

set -e  # Exit on error

# Get script directory và project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"

# Change to project root
cd "$PROJECT_ROOT"
echo "📁 Working directory: $PROJECT_ROOT"
echo ""

echo ""
echo "============================================================"
echo "🚀 SETUP & GENERATE DUMMY DATA"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "${YELLOW}📋 Step 1: Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✅ Found: $PYTHON_VERSION${NC}"
echo ""

# Step 2: Check Docker
echo -e "${YELLOW}📋 Step 2: Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker${NC}"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✅ Found: $DOCKER_VERSION${NC}"
echo ""

# Step 3: Install Python dependencies
echo -e "${YELLOW}📦 Step 3: Installing Python dependencies...${NC}"
echo "Installing: bcrypt, faker, tqdm..."

# Check if venv exists and activate it
if [ -d "$PROJECT_ROOT/venv" ]; then
    echo "🐍 Activating virtual environment..."
    source "$PROJECT_ROOT/venv/bin/activate"
    PYTHON_CMD="python"
    PIP_CMD="pip"
else
    echo "⚠️  No venv found, using global Python"
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
fi

# Install bcrypt 4.0.1 first (fix passlib compatibility)
echo "Installing bcrypt 4.0.1 (passlib compatibility fix)..."
$PIP_CMD install bcrypt==4.0.1 > /dev/null 2>&1

# Install other dependencies
if $PIP_CMD install faker==22.0.0 tqdm==4.66.1; then
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Step 4: Start Docker services
echo -e "${YELLOW}🐳 Step 4: Starting Docker services...${NC}"
echo "Starting PostgreSQL, Redis, and pgAdmin4..."

if docker-compose up -d; then
    echo -e "${GREEN}✅ Docker services started${NC}"
else
    echo -e "${RED}❌ Failed to start Docker services${NC}"
    exit 1
fi
echo ""

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
sleep 5

MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker exec user_service_postgres pg_isready -U postgres > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
        break
    fi

    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 1
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    echo -e "${RED}❌ PostgreSQL failed to start within 30 seconds${NC}"
    exit 1
fi
echo ""

# Step 5: Generate dummy data
echo -e "${YELLOW}🎲 Step 5: Generating dummy data...${NC}"
echo "This will create 175,000+ rows (takes ~2-3 minutes)"
echo ""

# Run from project root (already cd'd there)
# Use $PYTHON_CMD from Step 3 (venv python or python3)
if $PYTHON_CMD "$PROJECT_ROOT/scripts/generate_dummy_data.py"; then
    echo ""
    echo -e "${GREEN}✅ Dummy data generated successfully!${NC}"
else
    echo -e "${RED}❌ Failed to generate dummy data${NC}"
    exit 1
fi
echo ""

# Step 6: Show next steps
echo "============================================================"
echo "🎉 SETUP COMPLETE!"
echo "============================================================"
echo ""
echo "📊 Access Tools:"
echo "  - pgAdmin4:  http://localhost:5050"
echo "    Login: admin@admin.com / admin"
echo ""
echo "  - PostgreSQL Direct:"
echo "    docker exec -it user_service_postgres psql -U postgres -d user_service_db"
echo ""
echo "  - Redis CLI:"
echo "    docker exec -it user_service_redis redis-cli"
echo ""
echo "🚀 Next Steps:"
echo "  1. Start API server: uvicorn app.main:app --reload"
echo "  2. Open Swagger UI: http://localhost:8000/docs"
echo "  3. Test with 20,000+ users!"
echo ""
echo "📚 Documentation:"
echo "  - DUMMY_DATA_GUIDE.md"
echo "  - REDIS_CACHE_GUIDE.md"
echo "  - PROJECT_MANAGEMENT_GUIDE.md"
echo ""
echo "============================================================"
echo ""
