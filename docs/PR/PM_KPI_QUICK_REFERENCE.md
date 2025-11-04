# Problem Management KPI - Quick Reference

**Module:** `calculate_pm_kpis.py`  
**Version:** 1.0  
**Date:** 2025-11-03

---

## 🚀 Quick Start

```python
# Import
from src.config_loader import Config
from src.load_problem_data import load_all_problem_data
from src.transform_problems import transform_all_problem_data
from src.calculate_pm_kpis import calculate_all_pm_kpis

# Calculate
config = Config()
problems, tasks = load_all_problem_data('data')
transformed = transform_all_problem_data(problems, tasks)
kpis = calculate_all_pm_kpis(transformed, config)

# View
print(kpis['RCA001'])
```

---

## 📊 Functions

### `calculate_rca_completion(df, config=None)`

**What it does:** Calculates RCA completion rate for P1/P2 problems

**Input:**
- `df` - Transformed DataFrame (from transform_problems.py)
- `config` - Config object (optional)

**Output:**
```python
{
    'kpi_id': 'RCA001',
    'completion_rate': 74.4,
    'target': 95.0,
    'status': 'RED',
    'gap': -20.6,
    'completed_ontime': 29,
    'total_requiring_rca': 39,
    'total_problems': 49,
    'calculation_date': '2025-11-03'
}
```

**Example:**
```python
result = calculate_rca_completion(transformed_df)
print(f"RCA Completion: {result['completion_rate']}%")
# Output: RCA Completion: 74.4%
```

---

### `calculate_rca_kpi_status(df, config)`

**What it does:** Same as above, but requires config (for consistency)

**Input:**
- `df` - Transformed DataFrame
- `config` - Config object (required)

**Output:** Same as `calculate_rca_completion()`

**Example:**
```python
from src.config_loader import Config
config = Config()
result = calculate_rca_kpi_status(transformed_df, config)
```

---

### `calculate_all_pm_kpis(df, config)`

**What it does:** Calculates all PM KPIs (currently just RCA001)

**Input:**
- `df` - Transformed DataFrame
- `config` - Config object

**Output:**
```python
{
    'RCA001': {
        'kpi_id': 'RCA001',
        'completion_rate': 74.4,
        ...
    },
    # Future KPIs will appear here
}
```

**Example:**
```python
all_kpis = calculate_all_pm_kpis(transformed_df, config)

# Access specific KPI
rca_result = all_kpis['RCA001']
print(f"Status: {rca_result['status']}")
# Output: Status: RED

# Iterate through all KPIs
for kpi_id, result in all_kpis.items():
    print(f"{kpi_id}: {result['completion_rate']}% ({result['status']})")
```

---

## 🎯 Status Rules

| Completion Rate | Status | Color |
|----------------|---------|-------|
| ≥ 95% | GREEN | 🟢 |
| 85% - 95% | YELLOW | 🟡 |
| < 85% | RED | 🔴 |

**Your Data:** 74.4% = RED 🔴

---

## 🧮 Calculation Logic

### RCA Completion Rate

```
Completion Rate = (RCA Completed On-time / Total Requiring RCA) × 100
```

**Filters:**
- `Is_Major_Problem == True` (P1 or P2)
- `Requires_RCA == True`

**On-time criteria:**
- `RCA_OnTime == True` (task stage = 'Achieved')

**Your Data:**
```
Completion Rate = (29 / 39) × 100 = 74.4%
```

---

## 📁 Required Columns (from transform_problems.py)

Input DataFrame must have:
- `Is_Major_Problem` (bool) - P1/P2 problems
- `Requires_RCA` (bool) - RCA required flag
- `RCA_OnTime` (bool) - RCA completed on-time

These are added by `transform_all_problem_data()` in Session 2.

---

## 🧪 Testing

### Built-in Test:
```bash
python src/calculate_pm_kpis.py
```

### Quick Test:
```bash
python test_pm_kpis_quick.py
```

### Manual Test:
```python
result = calculate_rca_completion(df)
assert result['completion_rate'] == 74.4
assert result['status'] == 'RED'
assert result['completed_ontime'] == 29
```

---

## 🔢 Your Data Summary

| Metric | Value |
|--------|-------|
| Total Problems | 49 |
| Requiring RCA | 39 (79.6%) |
| Completed On-time | 29 |
| Completion Rate | **74.4%** |
| Target | 95.0% |
| Status | **RED** 🔴 |
| Gap | -20.6% |
| Problems without RCA | 10 |

---

## 💡 Common Use Cases

### 1. Calculate and Display:
```python
result = calculate_rca_completion(df)
print(f"{result['kpi_name']}")
print(f"Rate: {result['completion_rate']}%")
print(f"Status: {result['status']}")
print(f"Gap: {result['gap']}%")
```

### 2. Check if Meeting Target:
```python
result = calculate_rca_completion(df)
if result['status'] == 'GREEN':
    print("✓ Meeting RCA completion target!")
else:
    print(f"✗ Need {95.0 - result['completion_rate']:.1f}% improvement")
```

### 3. Calculate All KPIs:
```python
all_kpis = calculate_all_pm_kpis(df, config)
for kpi_id, result in all_kpis.items():
    status_emoji = {'GREEN': '🟢', 'YELLOW': '🟡', 'RED': '🔴'}
    print(f"{kpi_id}: {result['completion_rate']}% {status_emoji[result['status']]}")
```

### 4. Export to Dictionary for JSON:
```python
import json
kpis = calculate_all_pm_kpis(df, config)
json_output = json.dumps(kpis, indent=2)
print(json_output)
```

---

## ⚠️ Common Mistakes

### ❌ Wrong:
```python
# Don't calculate directly on unfiltered data
rate = df['RCA_OnTime'].sum() / len(df)  # WRONG!
```

### ✅ Right:
```python
# Use the function which handles filtering
result = calculate_rca_completion(df)
rate = result['completion_rate']
```

---

### ❌ Wrong:
```python
# Don't forget to transform data first
result = calculate_rca_completion(problems_df)  # Missing transforms!
```

### ✅ Right:
```python
# Always transform before calculating
transformed = transform_all_problem_data(problems, tasks)
result = calculate_rca_completion(transformed)
```

---

### ❌ Wrong:
```python
# Don't hardcode thresholds
if rate >= 95:
    status = 'GREEN'  # Hardcoded!
```

### ✅ Right:
```python
# Use the function which gets thresholds from config
result = calculate_rca_kpi_status(df, config)
status = result['status']
```

---

## 🔗 Dependencies

**Requires these modules (from Sessions 1 & 2):**
- `config_loader.py` - Config management
- `load_problem_data.py` - Data loading
- `transform_problems.py` - Data transformation

**External libraries:**
- `pandas` - Data manipulation
- `datetime` - Date handling
- `typing` - Type hints

---

## 📈 To Reach Target

**Current:** 74.4% (29/39 on-time)  
**Target:** 95.0% (37/39 on-time)  
**Need:** 8 more on-time completions

**Actions to improve:**
1. Focus on RCA completion timeliness
2. Improve RCA process efficiency
3. Track problems closer to deadlines
4. Allocate resources to overdue RCAs

---

## 🎨 Output Format

The result dictionary follows this structure:

```python
{
    'kpi_id': str,              # KPI identifier
    'kpi_name': str,            # Full KPI name
    'completion_rate': float,   # Percentage (1 decimal)
    'target': float,            # Target percentage
    'completed_ontime': int,    # Count of on-time
    'total_requiring_rca': int, # Total eligible
    'total_problems': int,      # All problems
    'status': str,              # GREEN/YELLOW/RED
    'gap': float,               # actual - target
    'calculation_date': str     # YYYY-MM-DD
}
```

---

## 🚀 Next Steps

After calculating KPIs, you can:
1. Export to Excel (Session 4)
2. Create visualizations
3. Send email reports
4. Store in database
5. Create dashboards

---

**Quick Help:**
- Full docs: See `SESSION_3_COMPLETE.md`
- Test: Run `python src/calculate_pm_kpis.py`
- Issues: Check docstrings in the module
