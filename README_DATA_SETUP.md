# Data Setup Instructions

## Required CSV Files

To run the KPI pipeline, you need to place the following CSV files in the `data/` directory:

1. **PYTHON EMEA IM last 90 days_redacted_clean.csv** (2,132 incidents)
2. **PYTHON EMEA SCT last 90 days_redacted_clean.csv** (6,617 requests)

## File Structure

```
kpi_pipeline/
├── data/
│   ├── PYTHON EMEA IM last 90 days_redacted_clean.csv  <-- Place here
│   └── PYTHON EMEA SCT last 90 days_redacted_clean.csv <-- Place here
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
