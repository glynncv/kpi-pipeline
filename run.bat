@echo off
REM ==========================================
REM KPI Pipeline - Complete Run Script
REM Runs both Service Management and Problem Management KPIs
REM ==========================================
REM
REM Usage:
REM   run.bat              - Run all KPIs with production data (default)
REM   run.bat dev          - Run all KPIs with development test data
REM   run.bat prod         - Run all KPIs with production data (explicit)
REM   run.bat sm           - Run Service Management KPIs only
REM   run.bat pm           - Run Problem Management KPIs only
REM
REM ==========================================

echo.
echo ======================================================================
echo KPI PIPELINE - COMPLETE RUN
echo ======================================================================
echo.

REM Check if argument is provided
if "%1"=="" (
    echo Running ALL KPIs with PRODUCTION data...
    echo.
    echo ======================================================================
    echo [1/2] Running Service Management KPIs...
    echo ======================================================================
    python main.py
    if errorlevel 1 (
        echo.
        echo ERROR: Service Management pipeline failed
        goto :end
    )
    echo.
    echo ======================================================================
    echo [2/2] Running Problem Management KPIs...
    echo ======================================================================
    python scripts\run_pm.py
    if errorlevel 1 (
        echo.
        echo WARNING: Problem Management pipeline failed (may be missing data files)
        echo This is OK if PM data files are not available
    )
    echo.
    echo ======================================================================
    echo ALL KPIs COMPLETE - Check output files:
    echo   Service Management: data\output\KPI_Report_*.xlsx
    echo   Problem Management: data\output\PM_Dashboard_*.xlsx
    echo ======================================================================
    goto :end
)

if /i "%1"=="dev" (
    echo Running ALL KPIs with DEVELOPMENT test data...
    echo.
    echo [1/2] Running Service Management KPIs...
    python main.py --env dev
    if errorlevel 1 (
        echo.
        echo ERROR: Service Management pipeline failed
        goto :end
    )
    echo.
    echo [2/2] Running Problem Management KPIs...
    python scripts\run_pm.py
    if errorlevel 1 (
        echo.
        echo WARNING: Problem Management pipeline failed (may be missing data files)
        echo This is OK if PM data files are not available
    )
    goto :end
)

if /i "%1"=="prod" (
    echo Running ALL KPIs with PRODUCTION data...
    echo.
    echo [1/2] Running Service Management KPIs...
    python main.py --env prod
    if errorlevel 1 (
        echo.
        echo ERROR: Service Management pipeline failed
        goto :end
    )
    echo.
    echo [2/2] Running Problem Management KPIs...
    python scripts\run_pm.py
    if errorlevel 1 (
        echo.
        echo WARNING: Problem Management pipeline failed (may be missing data files)
        echo This is OK if PM data files are not available
    )
    goto :end
)

if /i "%1"=="sm" (
    echo Running Service Management KPIs only...
    echo.
    python main.py
    goto :end
)

if /i "%1"=="pm" (
    echo Running Problem Management KPIs only...
    echo.
    python scripts\run_pm.py
    goto :end
)

REM Invalid argument
echo ERROR: Invalid argument "%1"
echo.
echo Valid options:
echo   run.bat          - Run ALL KPIs (production data, default)
echo   run.bat dev      - Run ALL KPIs (development test data)
echo   run.bat prod     - Run ALL KPIs (production data, explicit)
echo   run.bat sm       - Run Service Management KPIs only
echo   run.bat pm       - Run Problem Management KPIs only
echo.
goto :end

:end
echo.
echo ======================================================================
echo Complete!
echo ======================================================================
pause


