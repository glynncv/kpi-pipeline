@echo off
REM ==========================================
REM KPI Pipeline - Complete Run Script
REM Runs both Service Management and Problem Management KPIs
REM ==========================================

echo.
echo ======================================================================
echo KPI PIPELINE - COMPLETE RUN
echo ======================================================================
echo.

REM Check if argument is provided
if "%1"=="" goto default
if /i "%1"=="dev" goto dev
if /i "%1"=="prod" goto prod
if /i "%1"=="sm" goto sm
if /i "%1"=="pm" goto pm
goto invalid

:default
echo Running ALL KPIs with PRODUCTION data...
echo.
echo ======================================================================
echo Running Complete KPI Pipeline
echo ======================================================================
echo.
echo Note: main.py generates both KPI Report and PM Dashboard
echo.
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
echo.
echo ======================================================================
echo ALL KPIs COMPLETE - Check output files:
echo   Service Management: data\output\KPI_Report_*.xlsx
echo   Problem Management: data\output\PM_Dashboard_*.xlsx
echo ======================================================================
goto end

:dev
echo Running ALL KPIs with DEVELOPMENT test data...
echo.
echo Note: main.py generates both KPI Report and PM Dashboard
python main.py --env dev
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
goto end

:prod
echo Running ALL KPIs with PRODUCTION data...
echo.
echo Note: main.py generates both KPI Report and PM Dashboard
python main.py --env prod
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
goto end

:sm
echo Running Service Management KPIs only...
echo.
python main.py
goto end

:pm
echo Running Problem Management KPIs only...
echo.
python scripts\run_pm.py
goto end

:invalid
echo ERROR: Invalid argument "%1"
echo.
echo Valid options:
echo   run.bat          - Run ALL KPIs (production data, default)
echo   run.bat dev      - Run ALL KPIs (development test data)
echo   run.bat prod     - Run ALL KPIs (production data, explicit)
echo   run.bat sm       - Run Service Management KPIs only
echo   run.bat pm       - Run Problem Management KPIs only
echo.
goto end

:end
echo.
echo ======================================================================
echo Complete!
echo ======================================================================
pause
