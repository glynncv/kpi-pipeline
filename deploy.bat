@echo off
REM Deployment Validation Script for KPI Pipeline (Windows)

echo ==================================================================
echo KPI PIPELINE - DEPLOYMENT VALIDATION
echo ==================================================================
echo.

set ERRORS=0
set WARNINGS=0

REM Check 1: Python version
echo [1/8] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python not found
    set /a ERRORS+=1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [OK] Python !PYTHON_VERSION!
)
echo.

REM Check 2: Required files
echo [2/8] Checking required files...
set FILE_ERRORS=0

if exist "main.py" (echo [OK] main.py) else (echo [X] main.py missing & set /a FILE_ERRORS+=1)
if exist "requirements.txt" (echo [OK] requirements.txt) else (echo [X] requirements.txt missing & set /a FILE_ERRORS+=1)
if exist "README.md" (echo [OK] README.md) else (echo [X] README.md missing & set /a FILE_ERRORS+=1)
if exist "LICENSE" (echo [OK] LICENSE) else (echo [X] LICENSE missing & set /a FILE_ERRORS+=1)
if exist ".gitignore" (echo [OK] .gitignore) else (echo [X] .gitignore missing & set /a FILE_ERRORS+=1)
if exist "src\__init__.py" (echo [OK] src\__init__.py) else (echo [X] src\__init__.py missing & set /a FILE_ERRORS+=1)
if exist "config\kpi_config.yaml" (echo [OK] config\kpi_config.yaml) else (echo [X] config\kpi_config.yaml missing & set /a FILE_ERRORS+=1)

if %FILE_ERRORS% gtr 0 set /a ERRORS+=%FILE_ERRORS%
echo.

REM Check 3: YAML validity
echo [3/8] Validating YAML configuration...
python -c "import yaml; yaml.safe_load(open('config/kpi_config.yaml'))" >nul 2>&1
if errorlevel 1 (
    echo [X] YAML configuration is invalid
    set /a ERRORS+=1
) else (
    echo [OK] YAML configuration is valid
)
echo.

REM Check 4: Python syntax
echo [4/8] Checking Python syntax...
set SYNTAX_ERRORS=0

for %%f in (src\*.py) do (
    python -m py_compile "%%f" >nul 2>&1
    if errorlevel 1 (
        echo [X] %%f has syntax errors
        set /a SYNTAX_ERRORS+=1
    ) else (
        echo [OK] %%f
    )
)

python -m py_compile main.py >nul 2>&1
if errorlevel 1 (
    echo [X] main.py has syntax errors
    set /a SYNTAX_ERRORS+=1
) else (
    echo [OK] main.py
)

if %SYNTAX_ERRORS% gtr 0 set /a ERRORS+=%SYNTAX_ERRORS%
echo.

REM Check 5: Git status
echo [5/8] Checking git repository...
git status >nul 2>&1
if errorlevel 1 (
    echo [!] Git repository not initialized
    echo     Run: git init
    set /a WARNINGS+=1
) else (
    echo [OK] Git repository initialized
    
    REM Check for remote
    git remote get-url origin >nul 2>&1
    if errorlevel 1 (
        echo [!] No remote repository configured
        set /a WARNINGS+=1
    ) else (
        echo [OK] Remote repository configured
    )
)
echo.

REM Check 6: Dependencies
echo [6/8] Checking Python dependencies...
set DEP_MISSING=0

python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo [!] pandas not installed
    set /a DEP_MISSING+=1
) else (
    echo [OK] pandas installed
)

python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo [!] pyyaml not installed
    set /a DEP_MISSING+=1
) else (
    echo [OK] pyyaml installed
)

python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo [!] openpyxl not installed
    set /a DEP_MISSING+=1
) else (
    echo [OK] openpyxl installed
)

if %DEP_MISSING% gtr 0 (
    echo [!] Run: pip install -r requirements.txt
    set /a WARNINGS+=1
)
echo.

REM Check 7: Run tests
echo [7/8] Running test suite...
if exist "tests\test_pipeline.py" (
    python tests\test_pipeline.py >nul 2>&1
    if errorlevel 1 (
        echo [!] Test suite failed
        echo     Run manually to see errors
        set /a WARNINGS+=1
    ) else (
        echo [OK] Test suite passed
    )
) else (
    echo [!] Test file not found
    set /a WARNINGS+=1
)
echo.

REM Check 8: Documentation
echo [8/8] Checking documentation...
if exist "docs\QUICKSTART.md" (echo [OK] docs\QUICKSTART.md) else (echo [!] docs\QUICKSTART.md missing & set /a WARNINGS+=1)
if exist "docs\TECHNICAL.md" (echo [OK] docs\TECHNICAL.md) else (echo [!] docs\TECHNICAL.md missing & set /a WARNINGS+=1)
if exist "docs\CONFIGURATION.md" (echo [OK] docs\CONFIGURATION.md) else (echo [!] docs\CONFIGURATION.md missing & set /a WARNINGS+=1)
echo.

REM Summary
echo ==================================================================
echo DEPLOYMENT VALIDATION SUMMARY
echo ==================================================================
echo.

if %ERRORS%==0 if %WARNINGS%==0 (
    echo [SUCCESS] READY TO DEPLOY
    echo.
    echo All checks passed! You can proceed with deployment.
    echo.
    echo Next steps:
    echo 1. git add .
    echo 2. git commit -m "Initial commit: KPI Pipeline v1.0.0"
    echo 3. git push -u origin main
    echo 4. Create release on GitHub
) else if %ERRORS%==0 (
    echo [WARNING] DEPLOY WITH CAUTION
    echo.
    echo Errors: %ERRORS%
    echo Warnings: %WARNINGS%
    echo.
    echo No critical errors, but there are warnings.
    echo Review warnings above before deploying.
) else (
    echo [ERROR] NOT READY TO DEPLOY
    echo.
    echo Errors: %ERRORS%
    echo Warnings: %WARNINGS%
    echo.
    echo Please fix errors above before deploying.
    exit /b 1
)

echo ==================================================================
pause

