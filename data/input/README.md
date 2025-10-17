# Data Input Directory

This directory is where you place your CSV data files for processing by the KPI Pipeline.

## Required Files

Place your exported CSV files here:

- **Incident data**: Required for SM001, SM002, and SM004
- **Request data**: Required only if SM003 (Request Aging) is enabled

## File Format Requirements

### Incident Data

**Required Columns:**
- `number` - Unique incident identifier
- `priority` - Priority level (e.g., "1 - High", "2 - Medium", or just "1", "2")
- `incident_state` or `state` - Current state (Resolved, Closed, In Progress, etc.)
- `opened_at` - Open timestamp
- `u_resolved` or `resolved_at` - Resolution timestamp (can be empty for open incidents)
- `reassignment_count` - Number of times reassigned

**Optional but Recommended:**
- `location_country` - Geographic location
- `contact_type` - Contact channel (Phone, Email, Self-service, etc.)
- `assignment_group` - Assigned team
- `category` - Incident category

**Example:**
```csv
number,priority,incident_state,opened_at,u_resolved,reassignment_count,location_country,contact_type
INC0010001,1 - High,Resolved,2025-10-01 09:00:00,2025-10-01 12:30:00,0,Germany,Phone
INC0010002,2 - Medium,Closed,2025-10-02 10:15:00,2025-10-03 14:00:00,1,UK,Email
INC0010003,3 - Low,In Progress,2025-10-15 08:00:00,,0,France,Self-service
```

### Request Data

**Required Columns:**
- `number` - Unique request identifier
- `state` - Current state
- `opened_at` - Open timestamp
- `u_resolved` or `resolved_at` - Resolution timestamp

**Optional but Recommended:**
- `location_country` - Geographic location
- `contact_type` - Contact channel

**Example:**
```csv
number,state,opened_at,u_resolved,location_country,contact_type
REQ0020001,Closed,2025-09-15 10:00:00,2025-09-16 15:00:00,Germany,Email
REQ0020002,In Progress,2025-10-01 09:00:00,,UK,Phone
```

## Column Mapping

If your CSV uses different column names, update the `column_mappings` section in `config/kpi_config.yaml`:

```yaml
column_mappings:
  number: "your_ticket_number_column"
  priority: "your_priority_column"
  state: "your_state_column"
  # ... etc
```

## Date Formats

The pipeline supports multiple date formats automatically:
- `2025-10-17 14:30:00` (ISO format)
- `10/17/2025 2:30 PM`
- `17-Oct-2025 14:30`

If your format isn't recognized, configure it in `config/kpi_config.yaml`:

```yaml
processing:
  date_parsing:
    formats:
      - "%Y-%m-%d %H:%M:%S"
      - "%d/%m/%Y %H:%M"
      # Add your format
```

## File Naming

You can name your CSV files anything, but update the paths in `main.py`:

```python
incidents = load_data.load_incidents(
    'data/input/YOUR_INCIDENT_FILE.csv',
    config
)
```

**Recommended naming**:
- `incidents_YYYYMMDD.csv`
- `requests_YYYYMMDD.csv`

## Data Privacy

⚠️ **Important**: This directory is excluded from git by `.gitignore` to protect sensitive data.

- CSV files in this directory will NOT be committed to version control
- Safe to place real data here
- Always anonymize data before sharing project

## File Size Considerations

**Recommended limits:**
- Small datasets: < 10,000 rows (instant processing)
- Medium datasets: 10,000 - 100,000 rows (5-30 seconds)
- Large datasets: > 100,000 rows (may require optimization)

For very large datasets (>500,000 rows), consider:
- Processing in chunks
- Using database instead of CSV
- Pre-filtering data before export

## Sample Data

To test the pipeline without real data:

```bash
# Generate sample data
python tests/generate_sample_data.py

# This creates:
# - tests/sample_data/sample_incidents.csv
# - tests/sample_data/sample_requests.csv
```

## Export Instructions

### From ServiceNow (Example)

1. Navigate to Incident or Request list
2. Apply filters (e.g., last 90 days, specific assignment group)
3. Right-click column header → Export → CSV
4. Save file to this directory

### From Other Systems

Export to CSV format with:
- UTF-8 encoding
- Comma-separated values
- Header row with column names
- Date/time in consistent format

## Troubleshooting

### Error: "File not found"

- Verify file is in `data/input/` directory
- Check file path in `main.py` matches actual filename
- Ensure you're running from project root: `python main.py`

### Error: "Column not found"

- Check CSV has all required columns
- Update `column_mappings` in config if using different names
- Open CSV in text editor to verify column headers

### Error: "Date parsing failed"

- Check date format in CSV
- Add your date format to config
- Enable auto-detection in config

### No Data Loaded

- Verify CSV is not empty
- Check file encoding (should be UTF-8)
- Verify delimiter is comma (not semicolon or tab)

## Need Help?

- See [`docs/QUICKSTART.md`](../../docs/QUICKSTART.md) for setup guide
- See [`docs/TROUBLESHOOTING.md`](../../docs/TROUBLESHOOTING.md) for common issues
- See [`docs/CONFIGURATION.md`](../../docs/CONFIGURATION.md) for column mapping

---

**Remember**: Place your CSV files here and update `main.py` with the correct filenames!

