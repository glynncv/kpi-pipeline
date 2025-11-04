# Excel Export Module - Quick Reference Card

**Module:** `generate_pm_reports.py`  
**Purpose:** Export Problem Management KPIs to formatted Excel  
**Session:** 4 (Final)

---

## 📝 Quick Start (30 seconds)

```python
from src.generate_pm_reports import export_pm_dashboard

# Assuming you have kpis and transformed_df ready
dashboard_path = export_pm_dashboard(kpis, transformed_df)
print(f"Dashboard: {dashboard_path}")
```

**Output:** `data/PM_Dashboard_2025-11-04.xlsx`

---

## 🔧 Common Usage Patterns

### 1. Basic Export (Default Settings)

```python
export_pm_dashboard(kpi_results, transformed_df)
```

**Creates:**
- File: `data/PM_Dashboard_YYYY-MM-DD.xlsx`
- Sheets: Summary, RCA Details

---

### 2. Custom Location

```python
export_pm_dashboard(
    kpi_results, 
    transformed_df,
    output_dir='reports/monthly'
)
```

**Creates:**
- File: `reports/monthly/PM_Dashboard_YYYY-MM-DD.xlsx`

---

### 3. Custom Filename

```python
export_pm_dashboard(
    kpi_results,
    transformed_df,
    filename='PM_KPI_November.xlsx'
)
```

**Creates:**
- File: `data/PM_KPI_November.xlsx`

---

### 4. Full Customization

```python
export_pm_dashboard(
    kpi_results,
    transformed_df,
    output_dir='reports/archive',
    filename=f'PM_Dashboard_{region}_{date}.xlsx'
)
```

---

## 📊 Function Signatures

### Main Export Function

```python
export_pm_dashboard(
    kpi_results: Dict[str, Any],      # From calculate_all_pm_kpis()
    transformed_df: pd.DataFrame,      # From transform_all_problem_data()
    output_dir: str = 'data',          # Output directory
    filename: str = None               # Optional custom name
) -> str                               # Returns: file path
```

---

### Sheet Creation Functions

```python
create_summary_sheet(
    workbook: Workbook,               # openpyxl Workbook
    kpi_results: Dict[str, Any]       # KPI calculation results
) -> None
```

```python
create_detail_sheet(
    workbook: Workbook,               # openpyxl Workbook
    df: pd.DataFrame                  # Transformed DataFrame
) -> None
```

---

## 🎨 Styling Helpers

### Apply Status Color

```python
from src.generate_pm_reports import get_status_color

color = get_status_color('RED')     # Returns 'FFC7CE'
color = get_status_color('YELLOW')  # Returns 'FFEB9C'
color = get_status_color('GREEN')   # Returns 'C6EFCE'
```

---

### Apply Cell Formatting

```python
from src.generate_pm_reports import apply_cell_style

# Basic formatting
apply_cell_style(cell, bold=True, align='center')

# With background color
apply_cell_style(cell, bg_color='C6EFCE')

# With percentage format
apply_cell_style(cell, number_format='0.0%')
```

---

### Auto-Adjust Columns

```python
from src.generate_pm_reports import auto_adjust_column_width

auto_adjust_column_width(worksheet)
```

---

## 🎯 Expected Output

### Summary Sheet Structure

```
Row 1:  Problem Management KPI Dashboard
Row 2:  Report Date: 2025-11-04
Row 4:  [Headers]
Row 5:  RCA001 | 74.4% | 95.0% | 🔴 RED | -20.6% | 29/39
Row 8+: Detailed Breakdown
Row 14+: Status Thresholds
```

### Detail Sheet Structure

```
Row 1:  Problem Details - RCA Required
Row 2:  Total Problems: 39
Row 4:  [Headers]
Row 5+: [39 problem records]
```

---

## ✅ Validation Checklist

**Before running:**
- [ ] openpyxl installed
- [ ] KPI results calculated
- [ ] Data transformed
- [ ] Output directory exists (or will be created)

**After running:**
- [ ] File created successfully
- [ ] File size ~15-20 KB
- [ ] Summary sheet has metrics
- [ ] Detail sheet has 39 problems
- [ ] Formatting looks professional
- [ ] Status colors applied

---

## 🛠️ Troubleshooting Quick Fixes

### Problem: Import Error
```
ModuleNotFoundError: No module named 'openpyxl'
```
**Fix:** `pip install openpyxl`

---

### Problem: Permission Error
```
PermissionError: Permission denied
```
**Fix:** Close Excel file if open

---

### Problem: Missing Columns
```
ValueError: Missing required columns
```
**Fix:** Use transformed DataFrame:
```python
transformed = transform_all_problem_data(problems, tasks)
export_pm_dashboard(kpis, transformed)
```

---

### Problem: Empty Detail Sheet
```
Detail sheet created with 0 problems
```
**Fix:** Check RCA requirements:
```python
print(df['Requires_RCA'].value_counts())
```

---

## 🎨 Color Reference

```python
# Status Colors (Hex)
GREEN  = "C6EFCE"   # Light green
YELLOW = "FFEB9C"   # Light yellow  
RED    = "FFC7CE"   # Light red

# Header Colors
HEADER = "4472C4"   # Professional blue
WHITE  = "FFFFFF"   # White text

# Border
BORDER = "D0D0D0"   # Light gray
```

---

## 💡 Pro Tips

### 1. Check Results Before Export
```python
print(f"RCA: {kpis['RCA001']['completion_rate']}%")
print(f"Status: {kpis['RCA001']['status']}")
```

### 2. Verify Data is Transformed
```python
assert 'RCA_OnTime' in df.columns
assert 'Requires_RCA' in df.columns
```

### 3. Use Meaningful Filenames
```python
filename = f'PM_Dashboard_{region}_{month}.xlsx'
```

### 4. Archive Historical Reports
```python
output_dir = f'reports/archive/{year}/{month}'
```

---

## 📋 Complete Example

```python
"""
Complete export example
"""

# 1. Import everything
from src.config_loader import Config
from src.load_problem_data import load_all_problem_data
from src.transform_problems import transform_all_problem_data
from src.calculate_pm_kpis import calculate_all_pm_kpis
from src.generate_pm_reports import export_pm_dashboard

# 2. Run pipeline
config = Config()
problems, tasks = load_all_problem_data('data')
transformed = transform_all_problem_data(problems, tasks)
kpis = calculate_all_pm_kpis(transformed, config)

# 3. Export
dashboard = export_pm_dashboard(kpis, transformed)

# 4. Verify
print(f"Dashboard: {dashboard}")
print(f"RCA: {kpis['RCA001']['completion_rate']}%")
print(f"Status: {kpis['RCA001']['status']}")
```

---

## 🔍 Test Commands

### Test with Full Pipeline
```bash
python src/generate_pm_reports.py
```

### Test Standalone
```bash
python test_pm_export_quick.py
```

### Quick Validation
```python
import os
assert os.path.exists('data/PM_Dashboard_2025-11-04.xlsx')
```

---

## 📚 Need More Info?

- **Detailed docs:** SESSION_4_COMPLETE.md
- **Quick start:** SESSION_4_DELIVERY_SUMMARY.md
- **Code examples:** See function docstrings
- **Full reference:** Open the .py file

---

## ✨ Quick Wins

```python
# One-liner to run everything
from run_pipeline import run_kpi_pipeline; run_kpi_pipeline()

# Check status only
kpis['RCA001']['status']

# Get file path
export_pm_dashboard(kpis, df)  # Returns path

# Batch export
for region in ['EMEA', 'APAC', 'AMER']:
    # ... load data for region
    export_pm_dashboard(kpis, df, filename=f'PM_{region}.xlsx')
```

---

## 🎯 Common Use Cases

### Weekly Report
```python
# Run every Monday
dashboard = export_pm_dashboard(kpis, df)
email_to_stakeholders(dashboard)
```

### Monthly Archive
```python
# Keep historical versions
month = datetime.now().strftime('%Y-%m')
export_pm_dashboard(
    kpis, df,
    output_dir=f'reports/archive/{month}'
)
```

### Multi-Region Report
```python
# Generate for each region
regions = ['EMEA', 'APAC', 'AMER']
for region in regions:
    data = load_region_data(region)
    # ... process
    export_pm_dashboard(
        kpis, df,
        filename=f'PM_{region}.xlsx'
    )
```

---

**Remember:** Always transform data before exporting!

```python
# ❌ Wrong
export_pm_dashboard(kpis, problems_df)

# ✅ Right
transformed = transform_all_problem_data(problems, tasks)
export_pm_dashboard(kpis, transformed)
```

---

_Quick Reference Card - Session 4_  
_Problem Management KPI Pipeline_  
_Status: ✅ Production Ready_
