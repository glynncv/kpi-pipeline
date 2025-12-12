@echo off
REM ==========================================
REM KPI Pipeline - Run Script with Table Export
REM Runs Service Management KPIs and saves normalized output tables
REM ==========================================
REM
REM Usage:
REM   run_with_tables.bat              - Run with production data + save tables (CSV)
REM   run_with_tables.bat dev          - Run with development test data + save tables
REM   run_with_tables.bat prod         - Run with production data + save tables (explicit)
REM   run_with_tables.bat csv          - Explicitly save tables as CSV (default)
REM   run_with_tables.bat parquet      - Save tables as Parquet format
REM   run_with_tables.bat json         - Save tables as JSON format
REM
REM ==========================================

echo.
echo ======================================================================
echo KPI PIPELINE - RUN WITH TABLE EXPORT
echo ======================================================================
echo.

REM Determine table format (default: csv)
set TABLE_FORMAT=csv
if /i "%1"=="parquet" set TABLE_FORMAT=parquet
if /i "%1"=="json" set TABLE_FORMAT=json
if /i "%1"=="csv" set TABLE_FORMAT=csv

REM Check if argument is provided
if "%1"=="" goto default
if /i "%1"=="dev" goto dev
if /i "%1"=="prod" goto prod
if /i "%1"=="csv" goto csv
if /i "%1"=="parquet" goto parquet
if /i "%1"=="json" goto json
goto invalid

:default
echo Running ALL KPIs with PRODUCTION data + saving tables in CSV format...
echo.
echo ======================================================================
echo Running Complete KPI Pipeline (Service Management + Problem Management)...
echo ======================================================================
echo.
echo Note: main.py generates both KPI Report and PM Dashboard
echo       Tables will be saved to data\output\tables\ directory
echo.
python main.py --save-tables --tables-format csv
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
echo   Output Tables: data\output\tables\*.csv
echo ======================================================================
goto end

:dev
echo Running ALL KPIs with DEVELOPMENT test data + saving tables in CSV format...
echo.
echo Note: main.py generates both KPI Report and PM Dashboard
python main.py --env dev --save-tables --tables-format csv
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
echo.
echo Output Tables: data\output\tables\*.csv
goto end

:prod
echo Running ALL KPIs with PRODUCTION data + saving tables in CSV format...
echo.
echo Note: main.py generates both KPI Report and PM Dashboard
python main.py --env prod --save-tables --tables-format csv
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
echo.
echo Output Tables: data\output\tables\*.csv
goto end

:csv
echo Running ALL KPIs with PRODUCTION data + saving tables in CSV format...
echo.
python main.py --save-tables --tables-format csv
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
echo.
echo Output Tables: data\output\tables\*.csv
goto end

:parquet
echo Running ALL KPIs with PRODUCTION data + saving tables in Parquet format...
echo.
python main.py --save-tables --tables-format parquet
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
echo.
echo Output Tables: data\output\tables\*.parquet
goto end

:json
echo Running ALL KPIs with PRODUCTION data + saving tables in JSON format...
echo.
python main.py --save-tables --tables-format json
if errorlevel 1 (
    echo.
    echo ERROR: Pipeline failed
    goto end
)
echo.
echo Output Tables: data\output\tables\*.json
goto end

:invalid
echo ERROR: Invalid argument "%1"
echo.
echo Valid options:
echo   run_with_tables.bat          - Run ALL KPIs (production data, CSV tables)
echo   run_with_tables.bat dev      - Run ALL KPIs (development test data, CSV tables)
echo   run_with_tables.bat prod     - Run ALL KPIs (production data, CSV tables)
echo   run_with_tables.bat csv      - Run with CSV format tables (explicit)
echo   run_with_tables.bat parquet  - Run with Parquet format tables
echo   run_with_tables.bat json     - Run with JSON format tables
echo.
goto end

:end
echo.
echo ======================================================================
echo Complete!
echo ======================================================================
pause


