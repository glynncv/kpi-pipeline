# KPI Pipeline - Quick Reference

## Daily Operations

### Run the Pipeline
```bash
# Activate environment first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run pipeline
python main.py
```

### Check Output
Output location: `data/outputs/KPI_Dashboard_YYYY-MM-DD_HHMMSS.xlsx`

## Common Tasks

### Update Input Data
1. Export fresh CSV from ServiceNow
2. Place in `data/inputs/`
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

## File Locations

| What | Where |
|------|-------|
| Input CSVs | `data/inputs/` |
| Output Excel | `data/outputs/` |
| Configuration | `config/kpi_config.yaml` |
| Main script | `main.py` |
| Source code | `src/*.py` |

## KPI Quick Reference

| KPI | Target | Backlog Threshold |
|-----|--------|------------------|
| SM001 | P1=0, P2≤5 | N/A |
| SM002 | 0 backlog, ≥90% | 10 days |
| SM003 | 0 aged, ≥90% | 30 days |
| SM004 | ≥80% FTF | N/A |

## Support

- README: `README.md`
- Deployment Guide: `DEPLOYMENT_CHECKLIST.md`
- Full Config Reference: `complete_kpi_config.yaml`
- Team Contact: IT Service Management Team

---
**Last Updated**: 2025-10-16
