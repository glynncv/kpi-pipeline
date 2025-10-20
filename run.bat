@echo off
REM ==========================================
REM KPI Pipeline - Quick Run Script
REM ==========================================
REM
REM Usage:
REM   run.bat              - Run with production data (default)
REM   run.bat dev          - Run with development test data
REM   run.bat prod         - Run with production data (explicit)
REM
REM ==========================================

echo.
echo ======================================================================
echo KPI PIPELINE - QUICK RUN
echo ======================================================================
echo.

REM Check if argument is provided
if "%1"=="" (
    echo Running with PRODUCTION data...
    echo.
    python main.py
    goto :end
)

if /i "%1"=="dev" (
    echo Running with DEVELOPMENT test data...
    echo.
    python main.py --env dev
    goto :end
)

if /i "%1"=="prod" (
    echo Running with PRODUCTION data...
    echo.
    python main.py --env prod
    goto :end
)

REM Invalid argument
echo ERROR: Invalid argument "%1"
echo.
echo Valid options:
echo   run.bat          - Production data (default)
echo   run.bat dev      - Development test data
echo   run.bat prod     - Production data (explicit)
echo.
goto :end

:end
echo.
echo ======================================================================
pause

