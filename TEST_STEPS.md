# Analysis Output Layer - Test Steps

## Quick Start

### Run All Tests
```bash
python tests/test_analysis_output.py
```

### Run with pytest (if installed)
```bash
pytest tests/test_analysis_output.py -v
```

## Test Categories

### 1. Unit Tests - Individual Table Creation Functions

#### 1.1 KPI Summary Table Tests
- **Test**: `test_create_kpi_summary_table_all_kpi_types`
  - Validates all KPI types (SM001, SM002, SM003, SM004) are handled
  - Verifies SM001 includes: p1_count, p2_count, total_major, p1_target, p2_target
  - Verifies SM002 includes: total_incidents, backlog_count, backlog_percentage, target_adherence
  - Verifies SM003 includes: total_requests, aged_count, aged_percentage, target_adherence
  - Verifies SM004 includes: total_resolved, fcr_count, fcr_percentage, target_rate
  - Verifies OVERALL is excluded from summary

- **Test**: `test_create_kpi_summary_table_empty`
  - Tests with empty kpi_results dictionary
  - Verifies returns empty DataFrame

- **Test**: `test_create_kpi_summary_table_missing_fields`
  - Tests graceful handling of missing optional fields
  - Verifies defaults are used appropriately

#### 1.2 Overall Score Table Tests
- **Test**: `test_create_overall_score_table`
  - Verifies columns: overall_score, overall_status, total_weight, timestamp
  - Tests with OVERALL present in kpi_results

- **Test**: `test_create_overall_score_table_missing`
  - Tests with missing OVERALL key
  - Verifies returns empty DataFrame

#### 1.3 OKR Scorecard Table Tests
- **Test**: `test_create_okr_scorecard_table`
  - Verifies columns: kr_id, kr_name, score, status, current_value, target_value, target_operator, gap_to_target, owner
  - Tests with all Key Results (KR3, KR4, KR5, KR6)
  - Verifies status values: On Track/At Risk/Off Track
  - Verifies score range: 0-100

- **Test**: `test_create_okr_scorecard_table_missing`
  - Tests with missing key_results
  - Verifies returns empty DataFrame

#### 1.4 Action Triggers Table Tests
- **Test**: `test_create_action_triggers_table`
  - Verifies columns: severity, kr_id, action, escalation
  - Tests with both critical and warning triggers
  - Verifies severity capitalization: Critical/Warning

- **Test**: `test_create_action_triggers_table_empty`
  - Tests with empty triggers dictionary
  - Verifies returns empty DataFrame

#### 1.5 Incident Detail Table Tests
- **Test**: `test_create_incident_detail_table`
  - Verifies required columns: number, priority, Priority_Number, opened_at, resolved_at, Days_Open, Is_Major_Incident, Is_Backlog, Is_First_Call_Resolution, country
  - Tests with Days_To_Resolve present (should be included)
  - Verifies copy() is used (independence from source)

- **Test**: `test_create_incident_detail_table_missing_columns`
  - Tests with missing optional columns
  - Verifies graceful handling

#### 1.6 Request Detail Table Tests
- **Test**: `test_create_request_detail_table`
  - Verifies required columns: number, opened_at, closed_at, Days_Open, Is_Aged, Is_Closed, country
  - Tests with Days_To_Close present (should be included)

- **Test**: `test_create_request_detail_table_empty`
  - Tests with empty DataFrame
  - Verifies returns empty DataFrame

#### 1.7 Geographic Summary Table Tests
- **Test**: `test_create_geographic_summary_table`
  - Verifies returns copy of location_summary DataFrame
  - Tests pass-through functionality

- **Test**: `test_create_geographic_summary_table_missing`
  - Tests with missing location_summary
  - Verifies returns empty DataFrame

### 2. Integration Tests - Main Entry Point

#### 2.1 Create All Output Tables Tests
- **Test**: `test_create_all_output_tables_complete`
  - Tests with complete valid inputs
  - Verifies all 7-8 table keys exist: kpi_summary, overall_score, okr_scorecard, action_triggers, incident_detail, request_detail, problem_detail (optional), geographic_summary
  - Verifies all tables are DataFrames

- **Test**: `test_create_all_output_tables_empty_requests`
  - Tests with empty requests DataFrame
  - Verifies request_detail is empty but other tables created

- **Test**: `test_create_all_output_tables_table_independence`
  - Verifies table independence (modifying one doesn't affect others)

### 3. File Persistence Tests

#### 3.1 Parquet Format Tests
- **Test**: `test_save_output_tables_parquet`
  - Tests saving all tables as Parquet
  - Verifies files created in correct directory
  - Verifies filename format: `{table_name}_{timestamp}.parquet`
  - Verifies timestamp format: YYYYMMDD_HHMMSS
  - Verifies files are readable (round-trip test)

#### 3.2 CSV Format Tests
- **Test**: `test_save_output_tables_csv`
  - Tests saving all tables as CSV
  - Verifies filename format: `{table_name}_{timestamp}.csv`
  - Verifies files are readable (round-trip test)
  - Verifies index=False (no index column)

#### 3.3 JSON Format Tests
- **Test**: `test_save_output_tables_json`
  - Tests saving all tables as JSON
  - Verifies filename format: `{table_name}_{timestamp}.json`
  - Verifies orient='records' format
  - Verifies date_format='iso' for timestamps

#### 3.4 Error Handling Tests
- **Test**: `test_save_output_tables_empty_tables`
  - Tests with empty tables (should be skipped)

- **Test**: `test_save_output_tables_invalid_format`
  - Tests with invalid format (should raise ValueError)

- **Test**: `test_save_output_tables_directory_creation`
  - Tests directory creation if doesn't exist

### 4. Data Contract Validation Tests

#### 4.1 KPI Summary Contract
- **Test**: `test_kpi_summary_data_contract`
  - Verifies column names match documentation
  - Verifies column types (kpi_code: string, adherence_rate: float, status: string, timestamp: datetime)
  - Verifies status values: ['Met', 'Warning', 'Critical']
  - Verifies adherence_rate range: 0-100

#### 4.2 OKR Scorecard Contract
- **Test**: `test_okr_scorecard_data_contract`
  - Verifies column names match documentation
  - Verifies column types (kr_id: string, score: float, status: string)
  - Verifies status values: ['On Track', 'At Risk', 'Off Track']
  - Verifies score range: 0-100
  - Verifies target_operator values: ≥, ≤

#### 4.3 Action Triggers Contract
- **Test**: `test_action_triggers_data_contract`
  - Verifies column names match documentation
  - Verifies severity values: ['Critical', 'Warning']
  - Verifies kr_id format (KR3, KR4, etc.)

#### 4.4 Other Tables Contracts
- **Test**: `test_incident_detail_data_contract`
  - Verifies incident_detail columns match documentation
  - Verifies data types

- **Test**: `test_request_detail_data_contract`
  - Verifies request_detail columns match documentation
  - Verifies data types

- **Test**: `test_geographic_summary_data_contract`
  - Verifies geographic_summary structure matches geo_results

### 5. CLI Integration Tests

#### 5.1 CLI Flag Tests
- **Test**: `test_cli_save_tables_flag`
  - Tests `--save-tables` flag simulation
  - Verifies files created in data/output/tables/
  - Verifies all 7-8 tables saved (problem_detail is optional)

- **Test**: `test_cli_tables_format_options`
  - Tests `--tables-format csv`
  - Tests `--tables-format json`
  - Tests `--tables-format parquet` (explicit)

#### 5.2 Pipeline Integration Tests
- **Test**: `test_cli_pipeline_integration`
  - Tests Step 5.75 execution (table creation)
  - Tests Step 5.8 execution when --save-tables provided
  - Tests Step 5.8 skipped when --save-tables not provided

- **Test**: `test_cli_console_output_simulation`
  - Verifies console output shows table creation progress
  - Verifies console output shows file paths when saved

### 6. Edge Cases and Error Handling

#### 6.1 Empty Data Tests
- **Test**: `test_edge_case_empty_kpi_results`
  - Tests with empty kpi_results

- **Test**: `test_edge_case_empty_dataframes`
  - Tests with empty incidents DataFrame
  - Tests with empty requests DataFrame

#### 6.2 Missing Fields Tests
- **Test**: `test_edge_case_missing_required_fields`
  - Tests with missing required fields in kpi_results
  - Tests with missing optional fields (should use defaults)

- **Test**: `test_edge_case_malformed_okr_results`
  - Tests with malformed okr_results structure

#### 6.3 Data Type Tests
- **Test**: `test_edge_case_timestamp_type`
  - Verifies timestamp is pd.Timestamp type

### 7. Performance and Scalability Tests

#### 7.1 Large Dataset Tests
- **Test**: `test_performance_large_dataset`
  - Tests with large incident DataFrame (10,000+ rows)
  - Verifies memory efficiency
  - Verifies performance acceptable

### 8. Round-Trip Tests

#### 8.1 Save and Reload Tests
- **Test**: `test_round_trip_parquet`
  - Saves tables as Parquet
  - Reloads and verifies data matches original
  - Verifies column types preserved

- **Test**: `test_round_trip_csv`
  - Saves tables as CSV
  - Reloads and verifies data matches original

- **Test**: `test_round_trip_json`
  - Saves tables as JSON
  - Reloads and verifies data matches original

- **Test**: `test_round_trip_column_types_preserved`
  - Verifies column types preserved (especially for Parquet)
  - Verifies timestamp columns preserved correctly

## Quick Test Script

A helper script is available to test reading saved tables:

```bash
python test_read_tables.py
```

This will:
- Find all saved tables (Parquet, CSV, JSON)
- Display their structure and first few rows
- Verify they're readable

## Manual Testing Steps

### Test CLI Integration Manually

1. **Test basic execution (no save)**
   ```bash
   python main.py --env dev
   ```
   - Verify Step 5.75 executes (table creation)
   - Verify Step 5.8 is skipped (no files created)

2. **Test with --save-tables (default Parquet)**
   ```bash
   python main.py --env dev --save-tables
   ```
   - Verify Step 5.75 executes
   - Verify Step 5.8 executes
   - Verify files created in `data/output/tables/`
   - Verify all 7-8 tables saved as `.parquet` files (problem_detail is optional if problems data available)
   - Verify console output shows file paths

3. **Test with --save-tables --tables-format csv**
   ```bash
   python main.py --env dev --save-tables --tables-format csv
   ```
   - Verify files created as `.csv` files
   - Verify files are readable

4. **Test with --save-tables --tables-format json**
   ```bash
   python main.py --env dev --save-tables --tables-format json
   ```
   - Verify files created as `.json` files
   - Verify files are readable

5. **Test invalid format**
   ```bash
   python main.py --env dev --save-tables --tables-format invalid
   ```
   - Verify error message displayed

### Verify File Outputs

1. **Check file locations**
   - Navigate to `data/output/tables/`
   - Verify files exist with timestamp format: `{table_name}_YYYYMMDD_HHMMSS.{format}`

2. **Verify file readability**
   
   **Option A: Use the test script (Recommended)**
   ```bash
   python test_read_tables.py
   ```
   This script will automatically find and read all saved tables in all formats.
   
   **Option B: Use Python interactively**
   ```bash
   python
   ```
   Then in Python:
   ```python
   import pandas as pd
   from pathlib import Path
   import glob
   
   # Find and read a specific parquet file
   files = list(Path('data/output/tables').glob('kpi_summary_*.parquet'))
   if files:
       df = pd.read_parquet(files[0])
       print(df.head())
   
   # Or read all parquet files
   for filepath in Path('data/output/tables').glob('*.parquet'):
       print(f"\n{filepath.name}:")
       df = pd.read_parquet(filepath)
       print(df.head())
   ```
   
   **Note**: Don't try to run Python code directly in PowerShell. Use `python` command first, or create a `.py` script file.

3. **Verify data integrity**
   - Compare saved data with console output
   - Verify all expected columns present
   - Verify data types correct

## Test Checklist

- [ ] Run all automated tests: `python tests/test_analysis_output.py`
- [ ] Verify all 44 tests pass
- [ ] Test CLI with --save-tables (Parquet)
- [ ] Test CLI with --save-tables --tables-format csv
- [ ] Test CLI with --save-tables --tables-format json
- [ ] Verify files created in correct location
- [ ] Verify files readable and data intact
- [ ] Test with empty/missing data (edge cases)
- [ ] Verify console output shows progress
- [ ] Verify console output shows file paths

## Expected Results

- **All 44 automated tests should pass**
- **CLI commands should execute without errors**
- **Files should be created in `data/output/tables/`**
- **Files should be readable and contain correct data**
- **Console output should show table creation and file paths**

## Troubleshooting

If tests fail:
1. Check Python version (3.9+ required)
2. Verify dependencies installed: `pip install -r requirements.txt`
3. Check that `src/analysis_output.py` exists and is importable
4. Verify test data fixtures are correct
5. Check file permissions for output directory

