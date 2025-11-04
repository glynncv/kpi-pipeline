# Start Session 3: Problem Management KPI Calculations

**Copy this entire document to start your new conversation**

---

## 📋 Quick Context: Sessions 1 & 2 Complete

### ✅ Session 1 Complete
Built the foundation for Problem Management KPIs:
1. **`config/kpi_config.yaml`** - Configuration with RCA001 KPI definition
2. **`src/config_loader.py`** - Config loader with PM methods
3. **`src/load_problem_data.py`** - Loads Problem and Task CSVs

### ✅ Session 2 Complete
Built the transformation layer:
1. **`src/transform_problems.py`** - Transforms and joins Problem/Task data
2. **`test_transform_problems.py`** - Comprehensive test suite (ALL TESTS PASS ✓)

**Transformation Capabilities:**
- ✓ Extracts priority number from text ("2 - High" → 2)
- ✓ Adds calculated fields (Is_Major_Problem, Requires_RCA, Days_Open)
- ✓ Adds RCA status flags (OnTime, Late, InProgress)
- ✓ LEFT JOIN with intelligent task selection when multiple exist
- ✓ Handles 49 problems, 52 tasks, 77.6% task coverage
- ✓ Current RCA completion rate: 74.4% (29/39)

---

## 🎯 Session 3 Goal

**Create `calculate_pm_kpis.py`** - Calculate Problem Management KPIs

### What We're Building Today:

Build KPI calculator for **RCA001 (Root Cause Analysis Completion)**:

1. **`calculate_rca_completion()`**
   - Calculate RCA completion rate for P1/P2 problems
   - Filter: Only problems requiring RCA (u_rca_required = 'Yes')
   - Numerator: RCA completed on-time (stage = 'Achieved')
   - Denominator: Total problems requiring RCA
   - Output: Percentage (e.g., 74.4%)

2. **`calculate_rca_kpi_status()`**
   - Compare actual rate vs. target (95%)
   - Determine status: GREEN (≥95%), YELLOW (85-95%), RED (<85%)
   - Return structured result with metrics and status

3. **`calculate_all_pm_kpis()`**
   - Orchestrate all PM KPI calculations
   - Return dictionary with all KPI results
   - Ready for Excel export

---

## 📊 Your Data Characteristics (Validated!)

Based on Session 2 transformations with your EMEA data:

### Problems (49 P2 problems):
- **Total:** 49
- **Requires RCA:** 39 (79.6%)
- **Does not require RCA:** 10 (20.4%)
- **Open:** 14
- **Closed/Pending Change:** 35

### RCA Tasks (52 tasks):
- **Achieved (on-time):** 29
- **Breached (late):** 15
- **In Progress:** 4
- **Paused:** 4

### Key Metrics:
- **Task coverage:** 77.6% (38 of 49 problems have tasks)
- **RCA completion rate:** 74.4% (29/39)
- **Problems without tasks:** 11 (22.4%)
- **Target:** 95%
- **Status:** RED (74.4% < 85%)

---

## 🔑 KPI Calculation Logic

### RCA001: Root Cause Analysis Completion

**Configuration (from kpi_config.yaml):**
```yaml
RCA001:
  name: "Root Cause Analysis Completion Rate"
  description: "Percentage of P1/P2 problems with RCA completed on-time"
  target:
    expected: 95.0
    unit: "percent"
  thresholds:
    green: 95.0    # ≥95%
    yellow: 85.0   # 85-95%
    red: 85.0      # <85%
```

**Calculation Steps:**

1. **Filter Problems:**
   ```python
   # Only P1/P2 problems requiring RCA
   eligible = df[
       df['Is_Major_Problem'] == True &
       df['Requires_RCA'] == True
   ]
   ```

2. **Count Completions:**
   ```python
   # RCA tasks completed on-time
   completed_ontime = eligible['RCA_OnTime'].sum()
   total_requiring_rca = len(eligible)
   ```

3. **Calculate Rate:**
   ```python
   if total_requiring_rca > 0:
       completion_rate = (completed_ontime / total_requiring_rca) * 100
   else:
       completion_rate = 0.0
   ```

4. **Determine Status:**
   ```python
   if completion_rate >= 95.0:
       status = "GREEN"
   elif completion_rate >= 85.0:
       status = "YELLOW"
   else:
       status = "RED"
   ```

**Expected Result (Your Data):**
```python
{
    'kpi_id': 'RCA001',
    'kpi_name': 'Root Cause Analysis Completion Rate',
    'completion_rate': 74.4,
    'target': 95.0,
    'completed_ontime': 29,
    'total_requiring_rca': 39,
    'total_problems': 49,
    'status': 'RED',
    'gap': -20.6,  # 74.4 - 95.0
    'calculation_date': '2025-11-03'
}
```

---

## 📁 Files You Already Have

From Sessions 1 & 2:

```
project/
├── config/
│   └── kpi_config.yaml          # Configuration
├── src/
│   ├── config_loader.py         # Config loader (Session 1)
│   ├── load_problem_data.py     # Data loader (Session 1)
│   └── transform_problems.py    # Transformations (Session 2)
└── data/
    ├── PYTHON_EMEA_PM_P1P2__This_Year_.csv
    └── PYTHON_EMEA_TASK_RCA__This_Year_.csv
```

---

## ✅ Success Criteria for Session 3

At the end of this session, you should have:

1. **`src/calculate_pm_kpis.py`** created and tested ✓
2. **RCA completion calculation working:**
   - Filters 39 problems requiring RCA ✓
   - Counts 29 RCA completed on-time ✓
   - Calculates 74.4% completion rate ✓
   
3. **Status determination working:**
   - Compares 74.4% vs 95% target ✓
   - Returns RED status (< 85%) ✓
   - Calculates -20.6% gap ✓
   
4. **Full KPI calculation:**
   - Returns structured result dictionary ✓
   - Includes all required metrics ✓
   - Ready for Excel export ✓

5. **Validation:**
   - Test with actual EMEA data ✓
   - All assertions pass ✓
   - Output matches expected values ✓

---

## 🧪 Test Plan

After building each function, test with:

```python
from src.config_loader import Config
from src.load_problem_data import load_all_problem_data
from src.transform_problems import transform_all_problem_data
from src.calculate_pm_kpis import *

# Load and transform data
problems, tasks = load_all_problem_data('data')
transformed = transform_all_problem_data(problems, tasks)

# Test 1: RCA completion calculation
print("Test 1: RCA Completion Calculation")
result = calculate_rca_completion(transformed)
print(f"  Total problems: {result['total_problems']}")           # Should be: 49
print(f"  Requiring RCA: {result['total_requiring_rca']}")       # Should be: 39
print(f"  Completed on-time: {result['completed_ontime']}")      # Should be: 29
print(f"  Completion rate: {result['completion_rate']:.1f}%")    # Should be: 74.4%

# Test 2: Status determination
print("\nTest 2: Status Determination")
print(f"  Status: {result['status']}")                           # Should be: RED
print(f"  Target: {result['target']}")                           # Should be: 95.0
print(f"  Gap: {result['gap']:.1f}%")                            # Should be: -20.6

# Test 3: Full KPI calculation
print("\nTest 3: Full KPI Calculation")
config = Config()
all_kpis = calculate_all_pm_kpis(transformed, config)
print(f"  KPIs calculated: {list(all_kpis.keys())}")
print(f"  RCA001 result: {all_kpis['RCA001']}")

# Validation
assert result['completion_rate'] == 74.4, "Completion rate should be 74.4%"
assert result['status'] == 'RED', "Status should be RED"
assert result['completed_ontime'] == 29, "Should have 29 on-time completions"
assert result['total_requiring_rca'] == 39, "Should have 39 requiring RCA"
print("\n✓ All validations passed!")
```

---

## 💡 Implementation Hints

### Status Determination Logic:
```python
def determine_status(actual, target, thresholds):
    """
    Determine KPI status based on actual vs target.
    
    Args:
        actual: Actual percentage (e.g., 74.4)
        target: Target percentage (e.g., 95.0)
        thresholds: Dict with 'green', 'yellow', 'red' values
        
    Returns:
        'GREEN', 'YELLOW', or 'RED'
    """
    if actual >= thresholds['green']:
        return 'GREEN'
    elif actual >= thresholds['yellow']:
        return 'YELLOW'
    else:
        return 'RED'
```

### Gap Calculation:
```python
gap = actual - target
# Negative gap = underperformance
# Positive gap = overperformance
```

### Config Access:
```python
# Get RCA target and thresholds from config
config = Config()
rca_config = config.get_kpi_config('RCA001')

target = rca_config['target']['expected']        # 95.0
thresholds = rca_config['thresholds']            # {green: 95, yellow: 85, ...}
```

---

## 📝 Starter Code Template

```python
"""
Calculate Problem Management KPIs
Compute RCA completion rates and determine status.

Version: 1.0
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any

def calculate_rca_completion(df: pd.DataFrame, config: Any = None) -> Dict[str, Any]:
    """
    Calculate RCA completion rate for P1/P2 problems.
    
    Args:
        df: Transformed problem DataFrame (from transform_problems.py)
        config: Config object (optional, for thresholds)
        
    Returns:
        Dictionary with RCA completion metrics and status
    """
    # Filter: Only P1/P2 problems requiring RCA
    eligible = df[
        (df['Is_Major_Problem'] == True) &
        (df['Requires_RCA'] == True)
    ]
    
    # Count completions
    total_problems = len(df)
    total_requiring_rca = len(eligible)
    completed_ontime = eligible['RCA_OnTime'].sum()
    
    # Calculate rate
    if total_requiring_rca > 0:
        completion_rate = (completed_ontime / total_requiring_rca) * 100
    else:
        completion_rate = 0.0
    
    # Determine status (TODO: get from config)
    target = 95.0
    if completion_rate >= 95.0:
        status = 'GREEN'
    elif completion_rate >= 85.0:
        status = 'YELLOW'
    else:
        status = 'RED'
    
    # Calculate gap
    gap = completion_rate - target
    
    return {
        'kpi_id': 'RCA001',
        'kpi_name': 'Root Cause Analysis Completion Rate',
        'completion_rate': round(completion_rate, 1),
        'target': target,
        'completed_ontime': int(completed_ontime),
        'total_requiring_rca': int(total_requiring_rca),
        'total_problems': total_problems,
        'status': status,
        'gap': round(gap, 1),
        'calculation_date': datetime.now().strftime('%Y-%m-%d')
    }

def calculate_rca_kpi_status(df: pd.DataFrame, config: Any) -> Dict[str, Any]:
    """
    Calculate RCA KPI with status from config.
    
    Same as calculate_rca_completion but uses config for thresholds.
    """
    # YOUR CODE HERE
    pass

def calculate_all_pm_kpis(df: pd.DataFrame, config: Any) -> Dict[str, Dict[str, Any]]:
    """
    Calculate all Problem Management KPIs.
    
    Args:
        df: Transformed problem DataFrame
        config: Config object
        
    Returns:
        Dictionary mapping KPI ID to KPI results
    """
    results = {}
    
    # Calculate RCA001
    results['RCA001'] = calculate_rca_kpi_status(df, config)
    
    # Add more KPIs here in the future
    
    return results

# Test function
def test_pm_kpis():
    """Test PM KPI calculations with actual data"""
    # YOUR CODE HERE
    pass

if __name__ == '__main__':
    test_pm_kpis()
```

---

## 🚀 How to Start Session 3

**Simply paste this into your new conversation:**

```
Hi Claude! Continuing the KPI pipeline project - Session 3.

Sessions 1 & 2 complete:
- config_loader.py: Configuration loading ✓
- load_problem_data.py: Data loading ✓
- transform_problems.py: Data transformation ✓

All tested with EMEA data (49 problems, 52 tasks, 74.4% RCA completion).

Now I need you to create `src/calculate_pm_kpis.py` to calculate RCA001 KPI.

Expected result: 74.4% completion rate, RED status (target 95%).

[Paste relevant sections from above]

Let's build the KPI calculator!
```

---

## 📚 Reference: Available Config Methods

From Session 1, you have these config methods:

```python
config = Config()

# Get KPI configuration
rca_config = config.get_kpi_config('RCA001')
# Returns: {
#   'name': 'Root Cause Analysis Completion Rate',
#   'target': {'expected': 95.0, 'unit': 'percent'},
#   'thresholds': {'green': 95.0, 'yellow': 85.0, 'red': 85.0},
#   ...
# }

# Get specific values
target = config.get_kpi_target('RCA001')               # 95.0
thresholds = config.get_kpi_thresholds('RCA001')       # {green: 95, yellow: 85, ...}

# Get RCA timeframes
p1_timeframe = config.get_rca_timeframe(1)             # 7 days
p2_timeframe = config.get_rca_timeframe(2)             # 14 days
```

---

## ⚠️ Common Gotchas to Watch For

1. **Filtering logic** - Must check BOTH Is_Major_Problem AND Requires_RCA
2. **Division by zero** - Handle case where total_requiring_rca = 0
3. **Rounding** - Round percentages to 1 decimal place (74.4, not 74.35897)
4. **Integer counts** - completed_ontime should be int, not float
5. **Status logic** - GREEN if >= 95%, YELLOW if >= 85%, RED if < 85%
6. **Date format** - Use ISO format 'YYYY-MM-DD' for calculation_date

---

## 📊 Expected Output Structure

After calculation, the result dictionary should look like:

```python
{
    'RCA001': {
        'kpi_id': 'RCA001',
        'kpi_name': 'Root Cause Analysis Completion Rate',
        'completion_rate': 74.4,
        'target': 95.0,
        'completed_ontime': 29,
        'total_requiring_rca': 39,
        'total_problems': 49,
        'status': 'RED',
        'gap': -20.6,
        'calculation_date': '2025-11-03',
        
        # Optional detailed breakdown
        'breakdown': {
            'achieved': 29,
            'breached': 10,
            'in_progress': 0,
            'no_task': 0
        }
    }
}
```

---

## ✅ Ready to Build!

You now have everything needed to create `calculate_pm_kpis.py` in your new conversation.

**Key points:**
- ✓ Transform layer complete (Session 2)
- ✓ Test data validated (74.4% completion)
- ✓ Config methods available (Session 1)
- ✓ Expected result structure defined

**Good luck with Session 3!** 🚀

---

**Quick Start for New Chat:**

"Hi Claude! Continuing KPI pipeline - Session 3.

Sessions 1-2 complete: config_loader, load_problem_data, transform_problems all working.

Validated with EMEA data: 49 problems, 39 requiring RCA, 29 completed on-time = 74.4% (RED status).

Now create calculate_pm_kpis.py to calculate RCA001 KPI following this spec:
[paste relevant sections above]

Let's build it!"
