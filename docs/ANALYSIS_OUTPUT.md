# Analysis Output Layer

The analysis output layer provides an intermediate data format between KPI calculation and report presentation. It normalizes analysis results into structured DataFrames that can be used for multiple output formats.

## Architecture

```
Analysis (Dicts) → Normalization (DataFrames) → Presentation (Excel/JSON/CSV)
```

**Before**: Analysis results were tightly coupled to Excel generation.

**After**: Normalized tables serve as a clean interface between analysis and any presentation format.

## Pipeline Integration

The analysis output layer runs as **Step 5.75** in the pipeline:

```
1. Load configuration
2. Load data
3. Transform data
4. Calculate KPIs
5. Calculate OKRs
5.5. Geographic analysis
5.75. Create normalized output tables  ← NEW
5.8. Save output tables (optional)     ← NEW
6. Display results
7. Generate Excel report
```

## Usage

### Basic (Logical Layer Only)

Tables exist in memory during execution:

```bash
python main.py
```

### With Physical Persistence

Save tables to disk for auditing or historical analysis:

```bash
# Save as Parquet (default, recommended)
python main.py --save-tables

# Save as CSV
python main.py --save-tables --tables-format csv

# Save as JSON
python main.py --save-tables --tables-format json
```

## Output Tables

The layer produces 7-9 normalized tables (problem_detail and sdm_summary are optional):

| Table Name | Description | Key Columns |
|------------|-------------|-------------|
| `kpi_summary` | KPI-level metrics | kpi_code, status, adherence_rate |
| `overall_score` | Overall performance | overall_score, overall_status |
| `okr_scorecard` | Key Results tracking | kr_id, score, status, gap_to_target |
| `action_triggers` | Required actions | severity, kr_id, action, escalation |
| `incident_detail` | Incident drill-down | number, priority, Is_Backlog, Days_Open |
| `request_detail` | Request drill-down | number, Is_Aged, Days_Open |
| `problem_detail` | Problem drill-down (optional) | number, priority, Is_Major_Problem, Requires_RCA, RCA_OnTime |
| `geographic_summary` | Location analysis (all KPIs/OKRs) | Location, Country, Incident/Request/Problem metrics, OKR scores |
| `sdm_summary` | SDM analysis (optional) | SDM, Total_Volume, Backlog_Pct, FCR_Rate, OKR scores |

## File Locations

When using `--save-tables`, files are saved to:

```
data/output/tables/
├── kpi_summary_20251109_143022.parquet
├── overall_score_20251109_143022.parquet
├── okr_scorecard_20251109_143022.parquet
├── action_triggers_20251109_143022.parquet
├── incident_detail_20251109_143022.parquet
├── request_detail_20251109_143022.parquet
├── problem_detail_20251109_143022.parquet  (optional, if problems data available)
├── geographic_summary_20251109_143022.parquet
└── sdm_summary_20251109_143022.parquet     (optional, if SDM data available)
```

Files are timestamped to support historical trending.

## Module Reference

### Main Entry Point

```python
from src import analysis_output

output_tables = analysis_output.create_all_output_tables(
    kpi_results=kpi_results,
    okr_results=okr_results,
    action_triggers=action_triggers,
    incidents=incidents,
    requests=requests,
    geo_results=geo_results,
    problems=problems  # Optional: include if problem management data available
)
```

### Individual Table Functions

```python
# KPI summary
kpi_df = analysis_output.create_kpi_summary_table(kpi_results)

# OKR scorecard
okr_df = analysis_output.create_okr_scorecard_table(okr_results)

# Action triggers
actions_df = analysis_output.create_action_triggers_table(action_triggers)

# Incident details
incidents_df = analysis_output.create_incident_detail_table(incidents)

# Request details
requests_df = analysis_output.create_request_detail_table(requests)

# Problem details (optional)
problems_df = analysis_output.create_problem_detail_table(problems)  # If problems available

# Geographic summary
geo_df = analysis_output.create_geographic_summary_table(geo_results)

# SDM summary (optional, requires SDM data)
sdm_df = analysis_output.create_sdm_summary_table(sdm_results)
```

### Saving Tables

```python
saved_files = analysis_output.save_output_tables(
    output_tables,
    output_dir='data/output/tables',
    format='parquet'  # or 'csv' or 'json'
)

# Returns: {'kpi_summary': 'data/output/tables/kpi_summary_20251109_143022.parquet', ...}
```

## Benefits

### 1. Multiple Output Formats

Same analytical data can produce different presentations:

```python
# Excel report
generate_excel_report(output_tables)

# JSON API response
output_tables['kpi_summary'].to_json()

# CSV export
output_tables['kpi_summary'].to_csv('kpi_export.csv')

# Database load
output_tables['kpi_summary'].to_sql('kpi_summary', engine)
```

### 2. Audit Trail

Save analytical snapshots for compliance:

```python
python main.py --save-tables
# Creates timestamped files that prove what was calculated and when
```

### 3. Historical Trending

Compare metrics over time:

```python
import pandas as pd

# Load historical snapshots
nov_data = pd.read_parquet('data/output/tables/kpi_summary_20251101_090000.parquet')
dec_data = pd.read_parquet('data/output/tables/kpi_summary_20251201_090000.parquet')

# Compare
trend = pd.merge(nov_data, dec_data, on='kpi_code', suffixes=['_nov', '_dec'])
```

### 4. Separate Testing

Test analysis logic independently from formatting:

```python
def test_kpi_summary():
    result = create_kpi_summary_table(mock_results)
    assert 'adherence_rate' in result.columns
    assert result['status'].isin(['Met', 'Warning', 'Critical']).all()

def test_excel_formatting():
    # Test separately with mock data
    excel = generate_excel_report(mock_tables)
```

### 5. Reprocessing

Regenerate reports without recalculating:

```python
# Load saved analytical output
tables = {
    'kpi_summary': pd.read_parquet('data/output/tables/kpi_summary_20251109.parquet'),
    # ... load other tables
}

# Generate new report format
generate_powerpoint(tables)  # Future capability
```

## Format Recommendations

| Format | Use Case | Pros | Cons |
|--------|----------|------|------|
| **Parquet** | Default, archiving | Compact, typed, fast | Requires pyarrow |
| **CSV** | Sharing, Excel import | Universal | No types, larger |
| **JSON** | API responses, web | Structured | Verbose |

**Recommendation**: Use Parquet for archiving, CSV for ad-hoc sharing.

## Data Contracts

### kpi_summary Table

| Column | Type | Description |
|--------|------|-------------|
| kpi_code | string | KPI identifier (SM001, SM002, etc.) |
| kpi_name | string | Full KPI name |
| status | string | Met, Warning, or Critical |
| adherence_rate | float | Percentage adherence (0-100) |
| business_impact | string | Impact description |
| timestamp | datetime | When calculated |
| p1_count | int | (SM001 only) P1 incident count |
| p2_count | int | (SM001 only) P2 incident count |
| backlog_count | int | (SM002 only) Backlog count |
| fcr_count | int | (SM004 only) FCR count |

### okr_scorecard Table

| Column | Type | Description |
|--------|------|-------------|
| kr_id | string | Key Result identifier (KR3, KR4, etc.) |
| kr_name | string | Key Result name |
| score | float | Achievement score (0-100) |
| status | string | On Track, At Risk, Off Track |
| current_value | float | Current metric value |
| target_value | float | Target value |
| target_operator | string | Comparison operator (≥, ≤) |
| gap_to_target | string | Gap description |
| owner | string | Responsible owner |

### action_triggers Table

| Column | Type | Description |
|--------|------|-------------|
| severity | string | Critical or Warning |
| kr_id | string | Associated Key Result |
| action | string | Required action description |
| escalation | string | Escalation path |

### problem_detail Table

| Column | Type | Description |
|--------|------|-------------|
| number | string | Problem ticket number |
| priority | string | Priority level (1 - Critical, 2 - High, etc.) |
| state | string | Problem state (Open, Closed, etc.) |
| opened_at | datetime | When problem was opened |
| closed_at | datetime | When problem was closed (if applicable) |
| Days_Open | int | Number of days problem has been open |
| Is_Major_Problem | bool | True if priority 1 or 2 |
| Requires_RCA | bool | True if RCA is required for this problem |
| RCA_OnTime | bool | True if RCA was completed on time (if required) |
| country | string | Country location (if available) |
| location | string | Location name (if available) |

**Note**: This table is only created when problem management data is available and `RCA001` KPI is enabled.

### sdm_summary Table

| Column | Type | Description |
|--------|------|-------------|
| SDM | string | Service Delivery Manager name |
| Total_Volume | int | Total tickets (incidents + requests + problems) |
| Incident_Volume | int | Number of incidents |
| Request_Volume | int | Number of requests |
| Problem_Volume | int | Number of problems |
| Backlog_Count | int | Number of backlog incidents |
| Backlog_Pct | float | Backlog percentage |
| Major_Incident_Count | int | Number of major incidents |
| FCR_Count | int | Number of first call resolutions |
| FCR_Rate | float | First call resolution rate (0-100) |
| Aged_Request_Count | int | Number of aged requests |
| Aged_Request_Pct | float | Aged request percentage |
| Request_Adherence_Rate | float | Request adherence rate (0-100) |
| KR3_Score | float | KR3 (Major Incidents) score (0-100) |
| KR4_Score | float | KR4 (Backlog) score (0-100) |
| KR5_Score | float | KR5 (Request Aging) score (0-100) |
| KR6_Score | float | KR6 (FCR) score (0-100) |
| Overall_OKR_Score | float | Weighted overall OKR score |
| Overall_OKR_Status | string | On Track, At Risk, Off Track |
| Overall_KPI_Score | float | Weighted overall KPI score |
| Overall_KPI_Status | string | Excellent, Good, Needs Improvement, Poor |
| Volume_Tier | string | Volume tier (tier_1 to tier_4) |
| Volume_Tier_Name | string | Tier description (High Volume, etc.) |
| Intervention_Priority | string | Critical, High, Monitor, Standard |

**Note**: This table is only created when SDM data is available (columns containing 'it_operations_manager' are found).

## Future Extensions

The normalized table format enables future capabilities:

1. **REST API**: Serve tables as JSON endpoints
2. **PowerPoint**: Generate slide decks from tables
3. **Email Reports**: HTML summaries with embedded tables
4. **Data Warehouse**: Direct SQL loading
5. **Dashboards**: Feed web visualization tools

## Related Documentation

- [Technical Architecture](TECHNICAL.md) - Overall system design
- [Configuration Guide](CONFIGURATION.md) - YAML configuration options
- [Quick Start](QUICKSTART.md) - Getting started guide
