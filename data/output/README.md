# Data Output Directory

This directory is where generated reports and output files are saved by the KPI Pipeline.

## Generated Files

Currently, the pipeline outputs results to the console. Future versions will generate files here:

### Planned Output Files (v1.1.0+)

- **Excel Reports**: `kpi_report_YYYYMMDD_HHMMSS.xlsx`
  - Summary sheet with all KPIs
  - Detailed breakdowns per KPI
  - Charts and visualizations
  - Formatted tables

- **CSV Exports**: `kpi_results_YYYYMMDD.csv`
  - Raw KPI calculations
  - Suitable for further analysis

- **JSON Data**: `kpi_data_YYYYMMDD.json`
  - Structured KPI results
  - For API integrations

## File Naming Convention

Generated files follow this pattern:
```
kpi_report_20251017_143000.xlsx
kpi_results_20251017.csv
kpi_data_20251017.json
```

Format: `{type}_{date}_{time}.{extension}`

## Output Directory Management

### Automatic Cleanup

The pipeline does NOT automatically delete old files. You should:

**Weekly**: Review and archive old reports
```bash
# Example: Move to archive
mkdir -p data/output/archive/2025-10
mv data/output/kpi_report_202510*.xlsx data/output/archive/2025-10/
```

**Monthly**: Delete very old files
```bash
# Delete files older than 90 days (example)
find data/output/ -name "*.xlsx" -mtime +90 -delete
```

### Manual Cleanup

```bash
# List all output files
ls -lh data/output/

# Remove all CSV files (keep Excel)
rm data/output/*.csv

# Remove all files
rm data/output/*
```

**Windows**:
```cmd
dir data\output\
del data\output\*.csv
```

## Git Ignore

⚠️ **Important**: This directory's output files are excluded from git by `.gitignore`

Files excluded:
- `*.xlsx` - Excel reports
- `*.csv` - CSV exports
- `*.json` - JSON data
- `*.log` - Log files

This prevents:
- Large binary files in repository
- Merge conflicts on generated files
- Sensitive data committed to git

## Storage Considerations

### File Sizes

Typical output file sizes:
- **Excel reports**: 100KB - 5MB (depending on data volume)
- **CSV exports**: 50KB - 2MB
- **JSON data**: 10KB - 500KB

### Disk Space Management

Monitor disk usage:
```bash
# Check output directory size
du -sh data/output/

# Find largest files
du -h data/output/* | sort -rh | head -5
```

**Recommendations**:
- Keep last 30 days of reports: ~150MB
- Keep last 90 days of reports: ~450MB
- Archive older reports to network drive or cloud storage

## Accessing Output Files

### Excel Reports (Future)

Open in:
- Microsoft Excel 2016+
- LibreOffice Calc
- Google Sheets (upload)

Features will include:
- Summary dashboard
- KPI detail sheets
- Charts and graphs
- Conditional formatting

### CSV Exports

Open in:
- Excel
- Text editor
- pandas: `pd.read_csv('data/output/kpi_results_20251017.csv')`
- Any data analysis tool

### JSON Data

Use in:
- Python: `json.load(open('data/output/kpi_data_20251017.json'))`
- JavaScript applications
- API integrations
- Database imports

## Current Output (v1.0.0)

Currently, all output goes to console:

```bash
python main.py

# Redirect to file if needed
python main.py > results.txt 2>&1

# Or just the output
python main.py | tee results.txt
```

## Backup Strategy

### Important Reports

For critical reports, create backups:

```bash
# Copy to backup location
cp data/output/kpi_report_20251017.xlsx ~/backups/

# Or create archive
tar -czf kpi_reports_2025-10.tar.gz data/output/kpi_report_202510*.xlsx
```

### Automated Backup

Add to monthly maintenance:

```bash
#!/bin/bash
# Backup last month's reports
LAST_MONTH=$(date -d "last month" +%Y%m)
tar -czf "backups/kpi_reports_${LAST_MONTH}.tar.gz" data/output/kpi_report_${LAST_MONTH}*.xlsx
```

## Security Considerations

### Sensitive Data

Output files may contain:
- Incident counts and details
- Team performance metrics
- Geographic information

**Best practices**:
- Limit access to output directory
- Don't share reports publicly
- Sanitize before sharing externally
- Follow your organization's data policy

### File Permissions

**Linux/Mac**:
```bash
# Restrict access to owner only
chmod 700 data/output/
chmod 600 data/output/*.xlsx
```

**Windows**:
- Right-click directory → Properties → Security
- Limit access to authorized users only

## Troubleshooting

### Issue: "Permission denied" when writing

**Cause**: No write permissions to directory

**Solution**:
```bash
# Linux/Mac
chmod u+w data/output/

# Windows: Check folder permissions
```

### Issue: Output file already open

**Cause**: File open in Excel or another program

**Solution**: Close the file before running pipeline

### Issue: Disk full

**Cause**: No space left on device

**Solution**: Clean up old files or increase disk space

## Integration

### Power BI

Import output files:
1. Power BI → Get Data → CSV/Excel
2. Select output file
3. Transform and model as needed

### Tableau

1. Connect to Data → Excel/Text file
2. Navigate to data/output/
3. Select report file

### Python Analysis

```python
import pandas as pd

# Read CSV output
df = pd.read_csv('data/output/kpi_results_20251017.csv')

# Read Excel output (future)
df = pd.read_excel('data/output/kpi_report_20251017.xlsx', sheet_name='Summary')
```

## Future Enhancements (Roadmap)

**Version 1.1.0**:
- Excel dashboard with charts
- Formatted tables
- Multiple sheets per KPI

**Version 1.2.0**:
- Email report distribution
- Automated report scheduling
- PDF export

**Version 2.0.0**:
- Real-time dashboard
- Historical trend analysis
- Interactive web reports

## Need Help?

- See [`docs/QUICKSTART.md`](../../docs/QUICKSTART.md) for usage
- See [`docs/MAINTENANCE.md`](../../docs/MAINTENANCE.md) for cleanup procedures
- See [`docs/TROUBLESHOOTING.md`](../../docs/TROUBLESHOOTING.md) for issues

---

**Note**: This directory is ready for future output files. Currently outputs display in console.

