# Problem Management KPI Testing Setup Guide

## Required Data Files

To test the Problem Management KPI functionality (RCA001), you need **two CSV files** exported from ServiceNow.

### 1. Problem Data File

**Location**: `data/` directory (project root)

**Expected Filename**: As configured in `config/kpi_config.yaml` under `data_files.problem_file`

Default expected name: `PYTHON_EMEA_PM_P1P2__This_Year_.csv`

**Required Columns**:
- `number` - Problem ID (e.g., PRB0050848)
- `opened_at` - Problem opened datetime
- `closed_at` - Problem closed datetime (may be null)
- `priority` - Priority text (e.g., "2 - High", "1 - Critical")
- `state` - Problem state
- `u_rca_required` - Yes/No flag indicating if RCA is required
- `location.country` - Country (optional)

**File Characteristics**:
- Should contain P1 and P2 problems only (filtered in ServiceNow export)
- Encoding: Latin-1 (to handle special characters)
- Date format: Standard datetime format

### 2. Task Data File (RCA Tasks)

**Location**: `data/` directory (project root)

**Expected Filename**: As configured in `config/kpi_config.yaml` under `data_files.task_file`

Default expected name: `PYTHON_EMEA_TASK_RCA__This_Year_.csv`

**Required Columns**:
- `task` - Task ID (e.g., PTASK001)
- `task.parent.number` - Parent Problem ID (links to Problem.number)
- `stage` - Task stage (e.g., "Achieved", "Breached", "In progress", "Paused")
- `has_breached` - Boolean flag (True/False)
- `task.due_date` - RCA due date
- `end_time` - Task completion time (if completed)

**File Characteristics**:
- Should contain RCA tasks linked to problems
- Encoding: Latin-1
- Date format: Standard datetime format

## Configuration Check

Before testing, verify the filenames in `config/kpi_config.yaml`:

```yaml
data_files:
  problem_file: "PYTHON_EMEA_PM_P1P2__This_Year_.csv"
  task_file: "PYTHON_EMEA_TASK_RCA__This_Year_.csv"
```

If your files have different names, update these values in the config file.

## File Structure

```
kpi_pipeline/
├── data/
│   ├── PYTHON_EMEA_PM_P1P2__This_Year_.csv      ← Problem file here
│   ├── PYTHON_EMEA_TASK_RCA__This_Year_.csv     ← Task file here
│   └── input/
│       └── (incident and request files)
├── config/
│   └── kpi_config.yaml                          ← Check filenames here
└── src/
    └── (source code)
```

## Quick Test

### Test 1: Verify Files Are Detected

```bash
python -c "from src import config_loader, load_problem_data; config = config_loader.load_config(); problems, tasks = load_problem_data.load_all_problem_data('data', config); print(f'Problems: {len(problems) if problems is not None else 0}'); print(f'Tasks: {len(tasks) if tasks is not None else 0}')"
```

**Expected Output**:
```
✓ Loaded X problems from PYTHON_EMEA_PM_P1P2__This_Year_.csv
✓ Loaded Y tasks from PYTHON_EMEA_TASK_RCA__This_Year_.csv
Problems: X
Tasks: Y
```

### Test 2: Run Full Pipeline

```bash
python -c "from src import config_loader, load_problem_data, transform_problems, calculate_pm_kpis; config = config_loader.load_config(); problems, tasks = load_problem_data.load_all_problem_data('data', config); transformed = transform_problems.transform_all_problem_data(problems, tasks); kpis = calculate_pm_kpis.calculate_all_pm_kpis(transformed, config); rca = kpis['RCA001']; print(f'RCA001: {rca[\"completion_rate\"]:.1f}% (Target: {rca[\"target\"]:.1f}%) - {rca[\"status\"]}')"
```

### Test 3: Generate Excel Dashboard

```bash
python -c "from src import config_loader, load_problem_data, transform_problems, calculate_pm_kpis, generate_pm_reports; config = config_loader.load_config(); problems, tasks = load_problem_data.load_all_problem_data('data', config); transformed = transform_problems.transform_all_problem_data(problems, tasks); kpis = calculate_pm_kpis.calculate_all_pm_kpis(transformed, config); filepath = generate_pm_reports.export_pm_dashboard(kpis, transformed); print(f'Dashboard created: {filepath}')"
```

**Expected Output**:
```
[INFO] Creating Problem Management Dashboard...
[INFO] Creating Summary sheet...
[OK] Summary sheet created successfully
[INFO] Creating Detail sheet...
[OK] Detail sheet created with X problems
[OK] Dashboard created successfully!
Dashboard created: output/PM_Dashboard_2025-11-04.xlsx
```

## Troubleshooting

### "Problem file not found"
- Check the file is in the `data/` directory (not `data/input/`)
- Verify the filename matches `data_files.problem_file` in config
- Check file permissions (readable)

### "Task file not found"
- Check the file is in the `data/` directory
- Verify the filename matches `data_files.task_file` in config
- Check file permissions (readable)

### "Missing required columns"
- Verify your CSV has the required columns listed above
- Check column names match exactly (case-sensitive)
- For `task.parent.number`, ensure the column name includes the dot notation

### "RCA001 is disabled"
- Check `config/kpi_config.yaml`:
  ```yaml
  kpis:
    RCA001:
      enabled: true  # Should be true
  ```

### "Encoding errors"
- Ensure files are saved with Latin-1 encoding
- If exporting from ServiceNow, use the default export encoding
- Special characters in descriptions should be preserved

## Expected Results (EMEA Data)

Based on Session 3 testing with EMEA data:
- **Problems**: 53 P1/P2 problems
- **Requiring RCA**: 39 problems
- **RCA Completion Rate**: 74.4% (29/39)
- **Status**: RED (below 95% target)
- **Gap**: -20.6 percentage points

## Next Steps

Once files are in place and tests pass:
1. Run the full pipeline: `python main.py`
2. Check output: `output/PM_Dashboard_YYYY-MM-DD.xlsx`
3. Review KPI summary and problem details sheets

---

**Last Updated**: 2025-11-04

