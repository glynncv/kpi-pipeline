# Problem Management KPI Implementation Plan

## 📊 **Data Analysis Summary**

### **Available Data Files:**
1. **PYTHON_EMEA_PM_P1P2__This_Year_.csv** (48 P2 problems)
   - All P2 priority (no P1s in dataset)
   - 39 require RCA, 9 don't require RCA
   - States: 33 "Pending Change", 15 "Open"
   - **DATA QUALITY ISSUE:** All show `u_rca_delivered = False` (likely not updated)
   - Has RCA fields but appear unreliable

2. **PYTHON_EMEA_TASK_RCA__This_Year_.csv** (51 RCA tasks)
   - SLA tracking for RCA tasks
   - **MORE RELIABLE:** Shows actual completion status
   - Stages: 28 Achieved, 14 Breached, 5 In Progress, 4 Paused
   - Links to parent problems via `task.parent.number`
   - 44 tasks match our Problem file (7 are from problems outside P1/P2 filter)

### **Key Findings:**
- ✅ Both files available and joinable
- ⚠️ Problem file RCA fields unreliable - use Task file as primary source
- ✅ Task file has detailed SLA breach tracking
- ⚠️ No P1 problems in dataset (only P2)
- ✅ Can calculate RCA001 completion rate from Task file

---

## 🎯 **Implementation Strategy**

### **Phase 2A: RCA001 Implementation** (Priority 1)
**Goal:** Add RCA001 KPI calculation using REAL data structure

**Key Decision:** Use Task file as primary source, Problem file for context

---

## 📋 **Detailed Implementation Plan**

### **File 1: `config_loader.py` Extensions**
**Action:** Add Problem Management configuration support

```python
# New methods to add:

def get_problem_column_mapping(self, field_name):
    """Get column mapping for Problem table fields"""
    return self.config['column_mappings']['problem_data'].get(field_name)

def get_task_column_mapping(self, field_name):
    """Get column mapping for Task table fields"""
    return self.config['column_mappings']['task_data'].get(field_name)

def get_rca_timeframe(self, priority):
    """Get RCA completion timeframe in days based on priority
    P1: 7 days, P2: 14 days
    """
    return self.config['kpis']['RCA001']['targets'].get(
        f'p{priority}_rca_timeframe_days'
    )

def get_rca_targets(self):
    """Get RCA001 target thresholds"""
    return self.config['kpis']['RCA001']['targets']
```

**YAML Config Updates Needed:**
```yaml
column_mappings:
  problem_data:
    number: "number"
    opened_at: "opened_at"
    closed_at: "closed_at"
    priority: "priority"
    state: "state"
    assignment_group: "assignment_group"
    u_rca_required: "u_rca_required"
    u_root_cause: "u_root_cause"
    location_country: "location.country"
    
  task_data:
    task_number: "task"
    parent_number: "task.parent.number"
    stage: "stage"
    has_breached: "has_breached"
    due_date: "task.due_date"
    start_time: "start_time"
    end_time: "end_time"
```

---

### **File 2: `load_problem_data.py`** (NEW)
**Purpose:** Load Problem and Task CSV files

```python
"""
Load Problem Management data from ServiceNow exports
"""
import pandas as pd
from pathlib import Path
from config_loader import Config

def load_problem_data(data_dir='data', config=None):
    """
    Load Problem table CSV
    
    Returns:
        pd.DataFrame: Problems with parsed dates
    """
    if config is None:
        config = Config()
    
    problem_file = Path(data_dir) / 'PYTHON_EMEA_PM_P1P2__This_Year_.csv'
    
    if not problem_file.exists():
        print(f"Warning: Problem file not found: {problem_file}")
        return None
    
    # Load with latin-1 encoding (handles special characters)
    df = pd.read_csv(
        problem_file,
        encoding='latin-1',
        parse_dates=['opened_at', 'closed_at'],
        low_memory=False
    )
    
    print(f"Loaded {len(df)} problems")
    return df


def load_task_data(data_dir='data', config=None):
    """
    Load PM Task (RCA) table CSV
    
    Returns:
        pd.DataFrame: RCA tasks with parsed dates
    """
    if config is None:
        config = Config()
    
    task_file = Path(data_dir) / 'PYTHON_EMEA_TASK_RCA__This_Year_.csv'
    
    if not task_file.exists():
        print(f"Warning: Task file not found: {task_file}")
        return None
    
    df = pd.read_csv(
        task_file,
        encoding='latin-1',
        parse_dates=['start_time', 'planned_end_time', 'task.due_date', 'end_time'],
        low_memory=False
    )
    
    print(f"Loaded {len(df)} RCA tasks")
    return df


def load_all_problem_data(data_dir='data'):
    """
    Load both Problem and Task data
    
    Returns:
        tuple: (problems_df, tasks_df) or (None, None) if files not found
    """
    config = Config()
    
    problems = load_problem_data(data_dir, config)
    tasks = load_task_data(data_dir, config)
    
    if problems is None or tasks is None:
        print("Warning: Problem Management data not available")
        print("Skipping Problem Management KPIs")
        return None, None
    
    return problems, tasks
```

---

### **File 3: `transform_problems.py`** (NEW)
**Purpose:** Add calculated fields to Problem and Task data

```python
"""
Transform Problem Management data - add calculated fields
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def extract_priority_number(priority_text):
    """
    Extract numeric priority from text
    '2 - High' -> 2
    '1 - Critical' -> 1
    """
    if pd.isna(priority_text):
        return 99
    
    # Extract first digit
    priority_str = str(priority_text).strip()
    if priority_str[0].isdigit():
        return int(priority_str[0])
    return 99


def add_problem_calculated_fields(df, current_date=None):
    """
    Add calculated fields to Problem DataFrame
    
    Calculated fields:
    - Priority_Number: Numeric priority (1, 2, 3, 4, 99)
    - Is_Major_Problem: True if P1 or P2
    - Requires_RCA: True if u_rca_required == 'Yes'
    - Days_Open: Days since opened
    """
    if current_date is None:
        current_date = pd.Timestamp.now()
    
    df = df.copy()
    
    # Extract numeric priority
    df['Priority_Number'] = df['priority'].apply(extract_priority_number)
    
    # Is this a major problem? (P1 or P2)
    df['Is_Major_Problem'] = df['Priority_Number'] <= 2
    
    # Requires RCA?
    df['Requires_RCA'] = df['u_rca_required'] == 'Yes'
    
    # Days open
    df['Days_Open'] = (current_date - df['opened_at']).dt.days
    
    # Is closed?
    df['Is_Closed'] = df['closed_at'].notna()
    
    return df


def add_task_calculated_fields(df, current_date=None):
    """
    Add calculated fields to Task DataFrame
    
    Calculated fields:
    - Is_RCA_Complete: Stage is 'Achieved' or 'Breached'
    - Is_RCA_OnTime: Stage is 'Achieved' (not breached)
    - Is_RCA_Late: Stage is 'Breached'
    - Is_RCA_InProgress: Stage is 'In progress'
    """
    if current_date is None:
        current_date = pd.Timestamp.now()
    
    df = df.copy()
    
    # RCA completion status
    df['Is_RCA_Complete'] = df['stage'].isin(['Achieved', 'Breached'])
    df['Is_RCA_OnTime'] = df['stage'] == 'Achieved'
    df['Is_RCA_Late'] = df['stage'] == 'Breached'
    df['Is_RCA_InProgress'] = df['stage'] == 'In progress'
    
    # Convert has_breached to boolean if needed
    if df['has_breached'].dtype == 'object':
        df['has_breached'] = df['has_breached'].map({
            'true': True, 'True': True, 'TRUE': True, True: True,
            'false': False, 'False': False, 'FALSE': False, False: False
        })
    
    return df


def join_problems_with_tasks(problems_df, tasks_df):
    """
    Join Problems with their RCA Tasks
    
    Strategy: LEFT JOIN to keep all problems (even those without tasks)
    Multiple tasks per problem are OK (take first completed task)
    
    Returns:
        pd.DataFrame: Problems with task information
    """
    # For problems with multiple tasks, prioritize completed tasks
    tasks_df = tasks_df.copy()
    tasks_df['task_priority'] = tasks_df['stage'].map({
        'Achieved': 1,      # Completed on-time (highest priority)
        'Breached': 2,      # Completed late
        'In progress': 3,   # Still working
        'Paused': 4         # Paused (lowest priority)
    })
    
    # Sort and take first task per problem
    tasks_df = tasks_df.sort_values('task_priority')
    tasks_first = tasks_df.groupby('task.parent.number').first().reset_index()
    
    # Rename task columns to avoid collision
    task_cols_rename = {
        'task': 'rca_task_number',
        'stage': 'rca_stage',
        'has_breached': 'rca_has_breached',
        'task.due_date': 'rca_due_date',
        'start_time': 'rca_start_time',
        'end_time': 'rca_end_time',
        'Is_RCA_Complete': 'RCA_Complete',
        'Is_RCA_OnTime': 'RCA_OnTime',
        'Is_RCA_Late': 'RCA_Late',
        'Is_RCA_InProgress': 'RCA_InProgress'
    }
    
    tasks_first = tasks_first.rename(columns=task_cols_rename)
    
    # Join problems with tasks
    merged = problems_df.merge(
        tasks_first[['task.parent.number', 'rca_task_number', 'rca_stage', 
                     'rca_has_breached', 'rca_due_date', 'rca_end_time',
                     'RCA_Complete', 'RCA_OnTime', 'RCA_Late', 'RCA_InProgress']],
        left_on='number',
        right_on='task.parent.number',
        how='left'
    )
    
    # Fill NaN for problems without tasks
    merged['RCA_Complete'] = merged['RCA_Complete'].fillna(False)
    merged['RCA_OnTime'] = merged['RCA_OnTime'].fillna(False)
    merged['RCA_Late'] = merged['RCA_Late'].fillna(False)
    merged['RCA_InProgress'] = merged['RCA_InProgress'].fillna(False)
    
    return merged


def transform_all_problem_data(problems_df, tasks_df, current_date=None):
    """
    Apply all transformations to Problem Management data
    
    Returns:
        pd.DataFrame: Fully transformed and joined Problem data
    """
    # Add calculated fields
    problems_transformed = add_problem_calculated_fields(problems_df, current_date)
    tasks_transformed = add_task_calculated_fields(tasks_df, current_date)
    
    # Join problems with tasks
    final_df = join_problems_with_tasks(problems_transformed, tasks_transformed)
    
    return final_df
```

---

### **File 4: `calculate_problem_kpis.py`** (NEW)
**Purpose:** Calculate Problem Management KPIs

```python
"""
Calculate Problem Management KPIs
"""
import pandas as pd
from config_loader import Config


def calculate_rca001(problems_df, config=None):
    """
    Calculate RCA001: RCA Completion Rate
    
    Formula:
    - Denominator: P1/P2 problems requiring RCA
    - Numerator: P1/P2 problems with RCA completed on-time
    - Rate: (On-time count / Total requiring RCA) × 100
    
    Returns:
        dict: RCA001 calculation results
    """
    if config is None:
        config = Config()
    
    targets = config.get_rca_targets()
    
    # Filter to P1/P2 problems requiring RCA
    eligible_problems = problems_df[
        (problems_df['Is_Major_Problem'] == True) &
        (problems_df['Requires_RCA'] == True)
    ].copy()
    
    total_requiring_rca = len(eligible_problems)
    
    # Count completed on-time
    ontime_count = eligible_problems['RCA_OnTime'].sum()
    
    # Count completed late
    late_count = eligible_problems['RCA_Late'].sum()
    
    # Count in progress
    inprogress_count = eligible_problems['RCA_InProgress'].sum()
    
    # Count not started (no task)
    not_started_count = total_requiring_rca - (ontime_count + late_count + inprogress_count)
    
    # Calculate completion rate
    if total_requiring_rca > 0:
        completion_rate = (ontime_count / total_requiring_rca) * 100
    else:
        completion_rate = 0.0
    
    # Determine status
    if completion_rate >= targets['completion_rate_expected']:
        status = 'Target Met'
        status_color = 'green'
    elif completion_rate >= targets['completion_rate_minimum']:
        status = 'Minimum Met'
        status_color = 'yellow'
    else:
        status = 'Below Target'
        status_color = 'red'
    
    return {
        'kpi_id': 'RCA001',
        'kpi_name': 'RCA Completion Rate',
        'total_requiring_rca': total_requiring_rca,
        'completed_ontime': ontime_count,
        'completed_late': late_count,
        'in_progress': inprogress_count,
        'not_started': not_started_count,
        'completion_rate': round(completion_rate, 1),
        'target_expected': targets['completion_rate_expected'],
        'target_minimum': targets['completion_rate_minimum'],
        'status': status,
        'status_color': status_color
    }


def calculate_all_problem_kpis(problems_df):
    """
    Calculate all enabled Problem Management KPIs
    
    Currently: RCA001 only
    Future: PM001-PM005
    
    Returns:
        dict: All PM KPI results
    """
    config = Config()
    
    results = {}
    
    # RCA001: RCA Completion Rate (enabled)
    results['RCA001'] = calculate_rca001(problems_df, config)
    
    # Future: PM001-PM005 (currently disabled)
    # results['PM001'] = calculate_pm001(problems_df, config)
    # results['PM002'] = calculate_pm002(problems_df, incidents_df, config)
    # etc.
    
    return results
```

---

### **File 5: Update `calculate_kpis.py`**
**Action:** Integrate Problem Management KPIs into overall calculation

```python
# Add to existing calculate_kpis.py

from calculate_problem_kpis import calculate_all_problem_kpis

def calculate_all_kpis(incidents_df, requests_df, problems_df=None):
    """
    Calculate all KPIs (Incident, Request, and Problem Management)
    
    Args:
        incidents_df: Incident DataFrame
        requests_df: Request DataFrame
        problems_df: Problem DataFrame (optional, joined with tasks)
    
    Returns:
        dict: All KPI results
    """
    results = {}
    
    # Existing Incident/Request KPIs
    results['SM001'] = calculate_sm001(incidents_df)
    results['SM002'] = calculate_sm002(incidents_df)
    results['SM003'] = calculate_sm003(requests_df)
    results['SM004'] = calculate_sm004(incidents_df)
    results['GEOGRAPHIC'] = calculate_geographic(incidents_df, requests_df)
    
    # Problem Management KPIs (if data available)
    if problems_df is not None and len(problems_df) > 0:
        pm_kpis = calculate_all_problem_kpis(problems_df)
        results.update(pm_kpis)
    else:
        print("Problem Management data not available - skipping PM KPIs")
    
    return results
```

---

### **File 6: Update `generate_reports.py`**
**Action:** Add Problem Management sheet to Excel output

```python
# Add to existing generate_reports.py

def create_problem_management_sheet(writer, problems_df, kpi_results):
    """
    Create Problem Management dashboard sheet
    
    Sections:
    1. RCA001 Summary
    2. Problem breakdown by priority
    3. RCA task status breakdown
    4. Problems by country
    """
    # Create DataFrame for RCA001 summary
    rca_data = kpi_results.get('RCA001', {})
    
    summary_data = {
        'Metric': [
            'Total P1/P2 Requiring RCA',
            'RCA Completed On-Time',
            'RCA Completed Late',
            'RCA In Progress',
            'RCA Not Started',
            '',
            'Completion Rate',
            'Target (Expected)',
            'Target (Minimum)',
            'Status'
        ],
        'Value': [
            rca_data.get('total_requiring_rca', 0),
            rca_data.get('completed_ontime', 0),
            rca_data.get('completed_late', 0),
            rca_data.get('in_progress', 0),
            rca_data.get('not_started', 0),
            '',
            f"{rca_data.get('completion_rate', 0)}%",
            f"{rca_data.get('target_expected', 95)}%",
            f"{rca_data.get('target_minimum', 90)}%",
            rca_data.get('status', 'Unknown')
        ]
    }
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_excel(writer, sheet_name='Problem Management', index=False)
    
    # Add problem details below
    # (implementation continues...)
```

---

### **File 7: Update `main.py`**
**Action:** Integrate Problem Management pipeline

```python
# Updated main.py

def main():
    """
    Main pipeline execution
    """
    print("=" * 80)
    print("KPI CALCULATION PIPELINE - With Problem Management")
    print("=" * 80)
    
    # Load configuration
    config = Config()
    
    # Load Incident and Request data
    print("\n1. Loading Incident and Request data...")
    incidents, requests = load_all_data()
    
    # Transform Incident and Request data
    print("\n2. Transforming Incident and Request data...")
    incidents = transform_incidents(incidents)
    requests = transform_requests(requests)
    
    # Load Problem Management data (optional)
    print("\n3. Loading Problem Management data...")
    problems, tasks = load_all_problem_data()
    
    if problems is not None and tasks is not None:
        print("   ✓ Problem Management data available")
        problems = transform_all_problem_data(problems, tasks)
    else:
        print("   ⚠ Problem Management data not available")
        problems = None
    
    # Calculate all KPIs
    print("\n4. Calculating KPIs...")
    kpi_results = calculate_all_kpis(incidents, requests, problems)
    
    # Generate reports
    print("\n5. Generating Excel report...")
    generate_excel_report(kpi_results, incidents, requests, problems)
    
    print("\n" + "=" * 80)
    print("✓ Pipeline Complete!")
    print("=" * 80)
```

---

## 📝 **Configuration Updates Needed**

### **Update `kpi_config.yaml`:**

Add these sections:

```yaml
# Problem Management Column Mappings
column_mappings:
  problem_data:
    number: "number"
    opened_at: "opened_at"
    closed_at: "closed_at"
    priority: "priority"
    state: "state"
    assignment_group: "assignment_group"
    u_rca_required: "u_rca_required"
    u_root_cause: "u_root_cause"
    location_country: "location.country"
    
  task_data:
    task_number: "task"
    parent_number: "task.parent.number"
    stage: "stage"
    has_breached: "has_breached"
    due_date: "task.due_date"
    start_time: "start_time"
    end_time: "end_time"

# RCA001 KPI Configuration
kpis:
  RCA001:
    name: "RCA Completion Rate"
    enabled: true
    category: "Problem Management"
    priority: "Critical"
    targets:
      completion_rate_minimum: 90.0
      completion_rate_expected: 95.0
      p1_rca_timeframe_days: 7
      p2_rca_timeframe_days: 14
    weight: 15  # 15% of overall scorecard
```

---

## ✅ **Testing Plan**

### **Test 1: Data Loading**
```python
problems, tasks = load_all_problem_data('data')
print(f"Problems: {len(problems)}")  # Expect: 48
print(f"Tasks: {len(tasks)}")        # Expect: 51
```

### **Test 2: Transformation**
```python
problems = transform_all_problem_data(problems, tasks)
print(f"Problems requiring RCA: {problems['Requires_RCA'].sum()}")  # Expect: 39
print(f"RCA completed on-time: {problems['RCA_OnTime'].sum()}")     # Expect: 28
```

### **Test 3: RCA001 Calculation**
```python
rca_result = calculate_rca001(problems)
print(f"Completion rate: {rca_result['completion_rate']}%")
# Expect: 28/39 * 100 = 71.8%
```

---

## 🎯 **Success Criteria**

- ✅ Load both Problem and Task CSV files
- ✅ Extract numeric priority from text ("2 - High" → 2)
- ✅ Join Problems with Tasks (44 should match)
- ✅ Calculate RCA completion rate correctly (~71.8% based on current data)
- ✅ Handle problems without tasks gracefully
- ✅ Add Problem Management sheet to Excel output
- ✅ Pipeline runs with or without Problem data
- ✅ Code follows same patterns as existing IM/SCT modules

---

## 📅 **Implementation Order**

1. **Session 1:** Update `config_loader.py` + YAML config + test
2. **Session 2:** Create `load_problem_data.py` + test loading
3. **Session 3:** Create `transform_problems.py` + test transformations
4. **Session 4:** Create `calculate_problem_kpis.py` + test RCA001
5. **Session 5:** Update `calculate_kpis.py`, `generate_reports.py`, `main.py`
6. **Session 6:** End-to-end testing + validation

---

## 🚀 **Ready to Start?**

**Recommended starting point:**
- Start with Session 1 (config updates)
- Build and test incrementally
- Validate against actual data at each step

**Data Quality Notes:**
- Problem file RCA fields are unreliable - we'll use Task file
- No P1 problems in dataset (only P2)
- 28 of 39 RCAs completed on-time (71.8% - below 90% target)
- This is realistic data showing areas for improvement!
