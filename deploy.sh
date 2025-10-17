#!/bin/bash
# Deployment Validation Script for KPI Pipeline (Mac/Linux)

echo "=================================================================="
echo "KPI PIPELINE - DEPLOYMENT VALIDATION"
echo "=================================================================="
echo ""

ERRORS=0
WARNINGS=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# Check 1: Python version
echo "[1/8] Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
        success "Python $PYTHON_VERSION (requirement: 3.9+)"
    else
        error "Python $PYTHON_VERSION (requirement: 3.9+)"
    fi
else
    error "Python 3 not found"
fi
echo ""

# Check 2: Required files
echo "[2/8] Checking required files..."
REQUIRED_FILES=(
    "main.py"
    "requirements.txt"
    "README.md"
    "LICENSE"
    ".gitignore"
    "setup.sh"
    "setup.bat"
    "validate_project.py"
    "src/__init__.py"
    "src/config_loader.py"
    "src/load_data.py"
    "src/transform.py"
    "src/calculate_kpis.py"
    "config/kpi_config.yaml"
    "CONTRIBUTING.md"
    "CHANGELOG.md"
    "CODE_OF_CONDUCT.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "$file"
    else
        error "$file missing"
    fi
done
echo ""

# Check 3: YAML validity
echo "[3/8] Validating YAML configuration..."
if command -v python3 &> /dev/null; then
    python3 -c "import yaml; yaml.safe_load(open('config/kpi_config.yaml'))" 2>/dev/null
    if [ $? -eq 0 ]; then
        success "YAML configuration is valid"
    else
        error "YAML configuration is invalid"
    fi
else
    warning "Cannot validate YAML (Python not available)"
fi
echo ""

# Check 4: Python syntax
echo "[4/8] Checking Python syntax..."
SYNTAX_ERRORS=0
for file in src/*.py tests/*.py main.py validate_project.py; do
    if [ -f "$file" ]; then
        python3 -m py_compile "$file" 2>/dev/null
        if [ $? -eq 0 ]; then
            success "$file"
        else
            error "$file has syntax errors"
            ((SYNTAX_ERRORS++))
        fi
    fi
done

if [ $SYNTAX_ERRORS -eq 0 ]; then
    success "All Python files have valid syntax"
fi
echo ""

# Check 5: Git status
echo "[5/8] Checking git repository..."
if [ -d ".git" ]; then
    success "Git repository initialized"
    
    # Check for uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        success "No uncommitted changes"
    else
        warning "There are uncommitted changes"
    fi
    
    # Check current branch
    BRANCH=$(git branch --show-current 2>/dev/null)
    if [ ! -z "$BRANCH" ]; then
        success "Current branch: $BRANCH"
    fi
    
    # Check remote
    if git remote get-url origin &> /dev/null; then
        REMOTE=$(git remote get-url origin)
        success "Remote configured: $REMOTE"
    else
        warning "No remote repository configured"
    fi
else
    warning "Git repository not initialized (run: git init)"
fi
echo ""

# Check 6: Dependencies
echo "[6/8] Checking Python dependencies..."
MISSING_DEPS=0
for package in pandas pyyaml openpyxl dateutil; do
    python3 -c "import $package" 2>/dev/null
    if [ $? -eq 0 ]; then
        success "$package installed"
    else
        warning "$package not installed"
        ((MISSING_DEPS++))
    fi
done

if [ $MISSING_DEPS -gt 0 ]; then
    warning "Run: pip install -r requirements.txt"
fi
echo ""

# Check 7: Run tests
echo "[7/8] Running test suite..."
if [ -f "tests/test_pipeline.py" ]; then
    python3 tests/test_pipeline.py > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        success "Test suite passed"
    else
        warning "Test suite failed (run manually to see errors)"
    fi
else
    warning "Test file not found"
fi
echo ""

# Check 8: Documentation
echo "[8/8] Checking documentation..."
DOC_FILES=(
    "docs/QUICKSTART.md"
    "docs/TECHNICAL.md"
    "docs/CONFIGURATION.md"
    "docs/TROUBLESHOOTING.md"
)

DOC_MISSING=0
for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "$file"
    else
        warning "$file missing"
        ((DOC_MISSING++))
    fi
done
echo ""

# Summary
echo "=================================================================="
echo "DEPLOYMENT VALIDATION SUMMARY"
echo "=================================================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ READY TO DEPLOY${NC}"
    echo ""
    echo "All checks passed! You can proceed with deployment."
    echo ""
    echo "Next steps:"
    echo "1. git add ."
    echo "2. git commit -m \"Initial commit: KPI Pipeline v1.0.0\""
    echo "3. git push -u origin main"
    echo "4. Create release on GitHub"
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ DEPLOY WITH CAUTION${NC}"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "No critical errors, but there are warnings."
    echo "Review warnings above before deploying."
else
    echo -e "${RED}✗ NOT READY TO DEPLOY${NC}"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Please fix errors above before deploying."
    exit 1
fi

echo "=================================================================="

