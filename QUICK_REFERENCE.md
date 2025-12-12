# KPI Pipeline - Quick Reference

## Daily Operations

### Run the Pipeline

**Option 1: Simple Batch File (Windows)**
```batch
# Production data (default) - generates both KPI Report and PM Dashboard
run.bat

# Development test data (fast)
run.bat dev

# Production data (explicit)
run.bat prod

# Service Management KPIs only
run.bat sm

# Problem Management KPIs only (standalone)
run.bat pm
```

**Option 1b: Batch File with Table Export (Windows)**
```batch
# Production data + save tables (CSV format)
run_with_tables.bat

# Development test data + save tables
run_with_tables.bat dev

# Save tables as Parquet format
run_with_tables.bat parquet

# Save tables as JSON format
run_with_tables.bat json
```

**Option 2: Direct Python Command**
```bash
# Activate environment first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run pipeline (generates both KPI Report and PM Dashboard)
python main.py

# With environment selection
python main.py --env dev     # Development data (fast)
python main.py --env prod    # Production data (full)

# Save output tables (CSV format)
python main.py --save-tables
```

### Check Output
Output files are saved to `data/output/`:
- **KPI Report**: `KPI_Report_[env]_YYYYMMDD_HHMMSS.xlsx`
  - Example: `KPI_Report_dev_20251020_120728.xlsx`
- **PM Dashboard**: `PM_Dashboard_YYYY-MM-DD_HHMMSS.xlsx` (if PM data available)
  - Example: `PM_Dashboard_2025-11-05_091641.xlsx`

## Common Tasks

### Update Input Data
1. Export fresh CSV from ServiceNow
2. Place in `data/input/`
3. Run `python main.py`

### Change KPI Targets
1. Edit `config/kpi_config.yaml`
2. Find KPI section (e.g., `SM001`)
3. Update `targets:` values
4. Save and run pipeline

### Enable/Disable KPIs
In `config/kpi_config.yaml`:
```yaml
kpis:
  SM003:
    enabled: false  # Change to true to enable
```

### View Column Mappings
```bash
python -c "from src.config_loader import load_config; config = load_config('config/kpi_config.yaml'); print(config['column_mappings'])"
```

## Troubleshooting

### "No module named 'src'"
**Solution**: Activate virtual environment first

### "FileNotFoundError: config/kpi_config.yaml"
**Solution**: Run from project root directory, not from `src/`

### "KeyError: 'column_name'"
**Solution**: Check column mappings in `config/kpi_config.yaml` match CSV headers

### Results Don't Match Power Query
1. Check `column_mappings` match your CSV
2. Verify `backlog_days: 10` in config
3. Check `u_resolved` mapped to `resolved_at`

### Problem Management Data Not Loading
1. Verify problem CSV file exists in `data/` directory
2. Check task CSV file exists in `data/` directory
3. Ensure `RCA001.enabled: true` in `config/kpi_config.yaml`
4. Verify column mappings in `problem_data` and `task_data` sections

## File Locations

| What | Where |
|------|-------|
| Input CSVs | `data/input/` |
| Output Excel | `data/output/` |
| Configuration | `config/kpi_config.yaml` |
| Main script | `main.py` |
| Source code | `src/*.py` |

## KPI Quick Reference

### Service Management KPIs
| KPI | Target | Backlog Threshold |
|-----|--------|------------------|
| SM001 | P1=0, P2≤5 | N/A |
| SM002 | 0 backlog, ≥90% | 10 days |
| SM003 | 0 aged, ≥90% | 30 days |
| SM004 | ≥80% FTF | N/A |

### Problem Management KPIs
| KPI | Target | Description |
|-----|--------|-------------|
| RCA001 | ≥95% completion | Root Cause Analysis completion rate for P1/P2 problems |

## Support

- README: `README.md`
- Deployment Guide: `DEPLOYMENT_CHECKLIST.md`
- Config Documentation: `docs/CONFIGURATION.md` and `config/kpi_config.yaml`
- Team Contact: IT Service Management Team

---
**Last Updated**: 2025-10-16
