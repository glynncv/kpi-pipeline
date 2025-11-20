# Data Setup Instructions

## Required CSV Files

To run the KPI pipeline, you need to place the following CSV files in the `data/input/` directory (or `data/input/test_data/` for dev environment):

### Core Files (Required)
1. **PYTHON EMEA IM (2025)_redacted_clean.csv** - Incident data
2. **PYTHON EMEA SCT (2025)_redacted_clean.csv** - Service Request data

### Problem Management Files (Optional - Required for RCA001 KPI)
3. **PYTHON EMEA PM P1P2 (This Year).csv** - Problem data (P1/P2 problems)
4. **PYTHON EMEA TASK RCA (This Year).csv** - RCA Task data

**Note**: If Problem Management files are missing, the pipeline will skip PM processing and continue with Service Management KPIs only.

## File Structure

```
kpi_pipeline/
├── data/
│   └── input/
│       ├── PYTHON EMEA IM (2025)_redacted_clean.csv          <-- Incidents
│       ├── PYTHON EMEA SCT (2025)_redacted_clean.csv          <-- Requests
│       ├── PYTHON EMEA PM P1P2 (This Year).csv                <-- Problems (optional)
│       └── PYTHON EMEA TASK RCA (This Year).csv               <-- RCA Tasks (optional)
├── config/
│   └── kpi_config.yaml
└── ... (other files)
```

## CSV Column Requirements

### Incidents CSV (PYTHON EMEA IM)
Must contain these columns:
- number
- priority (e.g., "1 - Critical")
- incident_state
- opened_at
- u_resolved (resolved date)
- reassignment_count
- location_country
- contact_type (optional, for FCR calculation)

### Requests CSV (PYTHON EMEA SCT)
Must contain these columns:
- number
- opened_at
- closed_at
- request_item_u_opened_on_behalf_of_location_country

### Problems CSV (PYTHON EMEA PM P1P2)
Required for RCA001 KPI. Must contain these columns:
- number
- opened_at
- closed_at
- priority (e.g., "1 - Critical", "2 - High")
- state
- u_rca_required
- location.country
- location.name
- location.u_region
- location.u_site_name

### Tasks CSV (PYTHON EMEA TASK RCA)
Required for RCA001 KPI. Must contain these columns:
- task (task ID)
- task.parent.number (parent problem ID)
- stage (e.g., "Achieved", "Breached", "In progress")
- has_breached (boolean)
- task.due_date
- start_time
- planned_end_time
- end_time
- duration
- business_duration
- time_left

## Data Validation

After placing the files, run:
```bash
python load_data.py
```

This will validate that:
- Files exist
- Required columns are present
- Dates parse correctly
- Priority extraction works
