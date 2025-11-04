# How to Run the Problem Management KPI Feature

## Quick Start

### Prerequisites
1. ✅ Problem Management CSV files placed in `data/input/` directory
2. ✅ Configuration updated (already done - see `config/kpi_config.yaml`)
3. ✅ RCA001 KPI enabled (already enabled in config)

### Required Files
Make sure these files are in `data/input/`:
- `PYTHON EMEA PM P1P2 (This Year).csv` - Problem data
- `PYTHON EMEA TASK RCA (This Year).csv` - RCA Task data

## Option 1: Run Complete Pipeline (Recommended)

This runs the full pipeline including Service Management KPIs and Problem Management KPIs:

```bash
python main.py
```

**Output:**
- Service Management KPI report: `data/output/KPI_Report_[timestamp].xlsx`
- Problem Management dashboard: `output/PM_Dashboard_[date].xlsx` (if PM data available)

## Option 2: Run Problem Management Only

### Step 1: Load and Transform Data

```bash
python -c "from src import config_loader, load_problem_data, transform_problems; config = config_loader.load_config(); problems, tasks = load_problem_data.load_all_problem_data('data/input', config); transformed = transform_problems.transform_all_problem_data(problems, tasks); print(f'Transformed {len(transformed)} problems')"
```

### Step 2: Calculate KPIs

```bash
python -c "from src import config_loader, load_problem_data, transform_problems, calculate_pm_kpis; config = config_loader.load_config(); problems, tasks = load_problem_data.load_all_problem_data('data/input', config); transformed = transform_problems.transform_all_problem_data(problems, tasks); kpis = calculate_pm_kpis.calculate_all_pm_kpis(transformed, config); rca = kpis['RCA001']; print(f'RCA001: {rca[\"completion_rate\"]:.1f}% - Status: {rca[\"status\"]}')"
```

### Step 3: Generate Excel Dashboard

```bash
python -c "from src import config_loader, load_problem_data, transform_problems, calculate_pm_kpis, generate_pm_reports; config = config_loader.load_config(); problems, tasks = load_problem_data.load_all_problem_data('data/input', config); transformed = transform_problems.transform_all_problem_data(problems, tasks); kpis = calculate_pm_kpis.calculate_all_pm_kpis(transformed, config); filepath = generate_pm_reports.export_pm_dashboard(kpis, transformed); print(f'Dashboard created: {filepath}')"
```

## Option 3: Use Test Script (Easiest)

Create a simple script `run_pm.py`:

```python
"""Run Problem Management KPI Pipeline"""
from src import (
    config_loader,
    load_problem_data,
    transform_problems,
    calculate_pm_kpis,
    generate_pm_reports
)

print("=" * 60)
print("Problem Management KPI Pipeline")
print("=" * 60)

# Load configuration
print("\n1. Loading configuration...")
config = config_loader.load_config()

# Load data
print("\n2. Loading problem data...")
problems, tasks = load_problem_data.load_all_problem_data('data/input', config)

if problems is None or tasks is None:
    print("\n[ERROR] Problem Management data files not found!")
    print("Please ensure files are in data/input/ directory:")
    print("  - PYTHON EMEA PM P1P2 (This Year).csv")
    print("  - PYTHON EMEA TASK RCA (This Year).csv")
    exit(1)

# Transform data
print("\n3. Transforming data...")
transformed = transform_problems.transform_all_problem_data(problems, tasks)
print(f"   [OK] Transformed {len(transformed)} problems")

# Calculate KPIs
print("\n4. Calculating KPIs...")
kpis = calculate_pm_kpis.calculate_all_pm_kpis(transformed, config)
rca = kpis['RCA001']

print(f"\n   RCA001 Results:")
print(f"   - Completion Rate: {rca['completion_rate']:.1f}%")
print(f"   - Target: {rca['target']:.1f}%")
print(f"   - Status: {rca['status']}")
print(f"   - Completed: {rca['completed_ontime']}/{rca['total_requiring_rca']}")

# Generate Excel dashboard
print("\n5. Generating Excel dashboard...")
filepath = generate_pm_reports.export_pm_dashboard(kpis, transformed)

print("\n" + "=" * 60)
print("[SUCCESS] Problem Management KPI pipeline complete!")
print(f"Dashboard saved to: {filepath}")
print("=" * 60)
```

Then run:
```bash
python scripts/run_pm.py
```

## Option 4: Interactive Python Session

```python
# Start Python
python

# Then run:
from src import config_loader, load_problem_data, transform_problems, calculate_pm_kpis, generate_pm_reports

# Load config
config = config_loader.load_config()

# Load data
problems, tasks = load_problem_data.load_all_problem_data('data/input', config)

# Transform
transformed = transform_problems.transform_all_problem_data(problems, tasks)

# Calculate KPIs
kpis = calculate_pm_kpis.calculate_all_pm_kpis(transformed, config)

# View results
rca = kpis['RCA001']
print(f"Completion Rate: {rca['completion_rate']:.1f}%")
print(f"Status: {rca['status']}")

# Generate dashboard
filepath = generate_pm_reports.export_pm_dashboard(kpis, transformed)
print(f"Dashboard: {filepath}")
```

## Verify Files Are in Place

Before running, verify your files are correctly placed:

```bash
# Windows PowerShell
Get-ChildItem "data\input\*PM*"
Get-ChildItem "data\input\*TASK*"

# Or check if files exist
python -c "from pathlib import Path; print('PM file:', Path('data/input/PYTHON EMEA PM P1P2 (This Year).csv').exists()); print('Task file:', Path('data/input/PYTHON EMEA TASK RCA (This Year).csv').exists())"
```

## Expected Output

### Console Output
```
================================================================================
Loading Problem Management Data
================================================================================
[OK] Loaded 49 problems from PYTHON EMEA PM P1P2 (This Year).csv
[OK] Loaded 52 RCA tasks from PYTHON EMEA TASK RCA (This Year).csv

[OK] Data Quality Check:
  Problems in file: 49
  Tasks in file: 52
  Tasks matching problems: 38
  Coverage: 77.6%
================================================================================

RCA001 Results:
  Completion Rate: 48.7%
  Target: 95.0%
  Status: RED
  Completed: 19/39

[INFO] Creating Problem Management Dashboard...
[OK] Dashboard created successfully!
```

### Excel Dashboard
Location: `output/PM_Dashboard_YYYY-MM-DD.xlsx`

**Sheets:**
1. **Summary** - KPI overview with completion rate, status, and breakdown
2. **RCA Details** - Detailed list of all problems requiring RCA

## Troubleshooting

### "Problem file not found"
- Check files are in `data/input/` (not `data/`)
- Verify filenames match exactly (case-sensitive, including spaces)
- Check config: `config/kpi_config.yaml` → `data_files.problem_file`

### "RCA001 is disabled"
- Check `config/kpi_config.yaml`:
  ```yaml
  kpis:
    RCA001:
      enabled: true  # Should be true
  ```

### "No data loaded"
- Verify CSV files have required columns
- Check file encoding (should be Latin-1)
- Ensure files are readable (not locked by another program)

### Wrong completion rate
- Verify data files are current (not stale)
- Check that task `stage` values match expected formats
- Review task `has_breached` flags

## Quick Reference

| Step | Command |
|------|---------|
| Verify files | `python -c "from pathlib import Path; print(Path('data/input/PYTHON EMEA PM P1P2 (This Year).csv').exists())"` |
| Load data | `python -c "from src import config_loader, load_problem_data; config = config_loader.load_config(); problems, tasks = load_problem_data.load_all_problem_data('data/input', config); print(f'Loaded: {len(problems) if problems is not None else 0} problems')"` |
| Calculate KPIs | See Option 2, Step 2 |
| Generate dashboard | See Option 2, Step 3 |
| Full pipeline | `python main.py` |

## Next Steps

1. **Schedule regular runs**: Set up a scheduled task to run weekly/monthly
2. **Review results**: Open the Excel dashboard to review KPI performance
3. **Investigate issues**: Use the RCA Details sheet to identify problems with late/incomplete RCAs
4. **Update targets**: Adjust thresholds in `config/kpi_config.yaml` if needed

---

**Last Updated**: 2025-11-04

