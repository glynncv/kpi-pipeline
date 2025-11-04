# Start Session 2: Problem Management Data Transformation

**Copy this entire document to start your new conversation**

---

## 📋 Quick Context: What's Already Done

### Session 1 Complete ✅
Built the foundation for Problem Management KPIs:

1. **`config/kpi_config.yaml`** - Configuration with RCA001 KPI definition
2. **`src/config_loader.py`** - Config loader with PM methods
3. **`src/load_problem_data.py`** - Loads Problem and Task CSVs

**All tested and working with your EMEA data:**
- 49 P2 problems loaded
- 52 RCA tasks loaded  
- 77.6% task coverage
- Current RCA completion rate: ~74% (below 95% target)

---

## 🎯 Session 2 Goal

**Create `transform_problems.py`** - Transform and join Problem Management data

### What We're Building Today:

1. **`extract_priority_number()`** 
   - Extract numeric priority from text
   - Input: "2 - High" → Output: 2
   
2. **`add_problem_calculated_fields()`**
   - Add calculated fields to Problem DataFrame:
     - `Priority_Number`: int (1, 2, 3, 4, 99)
     - `Is_Major_Problem`: bool (True for P1/P2)
     - `Requires_RCA`: bool (True if u_rca_required == 'Yes')
     - `Days_Open`: int (days since opened)
     - `Is_Closed`: bool (closed_at is not null)

3. **`add_task_calculated_fields()`**
   - Add calculated fields to Task DataFrame:
     - `Is_RCA_Complete`: bool (stage in ['Achieved', 'Breached'])
     - `Is_RCA_OnTime`: bool (stage == 'Achieved')
     - `Is_RCA_Late`: bool (stage == 'Breached')
     - `Is_RCA_InProgress`: bool (stage == 'In progress')

4. **`join_problems_with_tasks()`**
   - LEFT JOIN Problems with Tasks
   - Handle multiple tasks per problem (prioritize completed)
   - Keep all problems (even those without tasks)
   - Merge RCA status into problem records

5. **`transform_all_problem_data()`**
   - Orchestrate all transformations
   - Return fully transformed DataFrame

---

## 📊 Your Data Characteristics (Important!)

Based on your actual EMEA exports:

### Problems:
- **Count:** 49 P2 problems
- **Priority format:** Text "2 - High" (need to extract '2')
- **RCA Required:** 39 Yes, 10 No
- **States:** 35 Pending Change, 14 Open
- **Some problems have no RCA tasks** (11 problems = 22%)

### Tasks:
- **Count:** 52 RCA tasks
- **Stages:** 29 Achieved, 15 Breached, 4 In Progress, 4 Paused
- **Multiple tasks per problem:** Some problems have 2+ tasks
- **has_breached field:** Text format ("true"/"false"), needs boolean conversion

### Join Strategy Needed:
- **38 problems** have matching tasks (77.6%)
- **11 problems** have NO tasks (recent problems, not started)
- **Some problems have 2+ tasks** (need to pick "best" one)

---

## 🔑 Key Design Decisions

### 1. Priority Extraction
```python
# Input: "2 - High", "1 - Critical", "3 - Moderate"
# Output: 2, 1, 3
# Fallback: 99 for unparseable values
```

### 2. Multiple Tasks Per Problem
**Strategy:** Prioritize by completion status
```
Priority order:
1. Achieved (completed on-time) - TAKE THIS ONE
2. Breached (completed late)
3. In progress (still working)
4. Paused (lowest priority)
```

### 3. LEFT JOIN Approach
```python
# Keep ALL problems in result
problems (49) LEFT JOIN tasks (52)
↓
Result: 49 problems
- 38 with task info merged
- 11 with RCA fields = null/False
```

### 4. Null Handling
```python
# For problems without tasks:
RCA_Complete = False
RCA_OnTime = False  
RCA_Late = False
RCA_InProgress = False
```

---

## 📁 Files You Already Have

From Session 1, you should have:

```
project/
├── config/
│   └── kpi_config.yaml          # Configuration (452 lines)
├── src/
│   ├── config_loader.py         # Config loader (346 lines)
│   └── load_problem_data.py     # Data loader (343 lines)
└── data/
    ├── PYTHON_EMEA_PM_P1P2__This_Year_.csv
    └── PYTHON_EMEA_TASK_RCA__This_Year_.csv
```

If you don't have these files, ask Claude to retrieve them from the project knowledge or previous session outputs.

---

## ✅ Success Criteria for Session 2

At the end of this session, you should have:

1. **`src/transform_problems.py`** created and tested
2. **Priority extraction working:**
   - "2 - High" → 2 ✅
   - All 49 problems have Priority_Number ✅
   
3. **Calculated fields added:**
   - 49 problems have Is_Major_Problem (all True for P2) ✅
   - 39 problems have Requires_RCA = True ✅
   - Days_Open calculated for all ✅
   
4. **Task fields added:**
   - 29 tasks marked Is_RCA_OnTime ✅
   - 15 tasks marked Is_RCA_Late ✅
   
5. **Join successful:**
   - Result has 49 rows (all problems kept) ✅
   - 38 problems have RCA status from tasks ✅
   - 11 problems have RCA_OnTime = False (no task) ✅

6. **Validation:**
   - Total Requires_RCA: 39 ✅
   - Total RCA_OnTime: 29 ✅
   - Completion rate: 29/39 = 74.4% ✅

---

## 🧪 Test Plan

After building each function, test with:

```python
from src.config_loader import Config
from src.load_problem_data import load_all_problem_data
from src.transform_problems import *

# Load data
problems, tasks = load_all_problem_data('data')

# Test 1: Priority extraction
print("Test 1: Priority Extraction")
print(problems['priority'].iloc[0])  # "2 - High"
problems_transformed = add_problem_calculated_fields(problems)
print(problems_transformed['Priority_Number'].iloc[0])  # Should be: 2

# Test 2: RCA flags
print("\nTest 2: Task RCA Flags")
tasks_transformed = add_task_calculated_fields(tasks)
print(tasks_transformed['Is_RCA_OnTime'].sum())  # Should be: 29
print(tasks_transformed['Is_RCA_Late'].sum())    # Should be: 15

# Test 3: Join
print("\nTest 3: Join Problems with Tasks")
result = join_problems_with_tasks(problems_transformed, tasks_transformed)
print(f"Total problems: {len(result)}")           # Should be: 49
print(f"With RCA on-time: {result['RCA_OnTime'].sum()}")  # Should be: 29
print(f"Without tasks: {result['rca_task_number'].isna().sum()}")  # Should be: 11

# Test 4: Full transformation
print("\nTest 4: Full Transformation")
final = transform_all_problem_data(problems, tasks)
print(f"Problems requiring RCA: {final['Requires_RCA'].sum()}")  # 39
print(f"RCA on-time: {final['RCA_OnTime'].sum()}")  # 29
print(f"Completion rate: {final['RCA_OnTime'].sum() / final['Requires_RCA'].sum() * 100:.1f}%")  # 74.4%
```

---

## 💡 Implementation Hints

### Priority Extraction Pattern:
```python
import re

def extract_priority_number(priority_text):
    """Extract first digit from priority text"""
    if pd.isna(priority_text):
        return 99
    
    # Extract first digit
    match = re.search(r'(\d+)', str(priority_text))
    if match:
        return int(match.group(1))
    return 99
```

### Boolean Conversion for has_breached:
```python
# Task file has text "true"/"false", need to convert
df['has_breached'] = df['has_breached'].map({
    'true': True, 'True': True, True: True,
    'false': False, 'False': False, False: False
})
```

### Multiple Tasks Per Problem:
```python
# Create priority column
tasks_df['task_priority'] = tasks_df['stage'].map({
    'Achieved': 1,      # Take this one first!
    'Breached': 2,
    'In progress': 3,
    'Paused': 4
})

# Sort and take first per problem
tasks_df = tasks_df.sort_values('task_priority')
tasks_first = tasks_df.groupby('task.parent.number').first().reset_index()
```

---

## 📝 Starter Code Template

Here's the basic structure to start with:

```python
"""
Transform Problem Management Data
Add calculated fields and join Problems with Tasks

Version: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

def extract_priority_number(priority_text):
    """Extract numeric priority from text like '2 - High'"""
    # YOUR CODE HERE
    pass

def add_problem_calculated_fields(df, current_date=None):
    """Add calculated fields to Problem DataFrame"""
    if current_date is None:
        current_date = pd.Timestamp.now()
    
    df = df.copy()
    
    # Extract priority number
    # YOUR CODE HERE
    
    # Add flags
    # YOUR CODE HERE
    
    return df

def add_task_calculated_fields(df):
    """Add calculated fields to Task DataFrame"""
    # YOUR CODE HERE
    pass

def join_problems_with_tasks(problems_df, tasks_df):
    """LEFT JOIN Problems with Tasks"""
    # YOUR CODE HERE
    pass

def transform_all_problem_data(problems_df, tasks_df, current_date=None):
    """Orchestrate all transformations"""
    problems_transformed = add_problem_calculated_fields(problems_df, current_date)
    tasks_transformed = add_task_calculated_fields(tasks_df)
    final = join_problems_with_tasks(problems_transformed, tasks_transformed)
    return final

# Test function
def test_transform():
    """Test transformations with actual data"""
    from config_loader import Config
    from load_problem_data import load_all_problem_data
    
    problems, tasks = load_all_problem_data('data')
    
    if problems is not None:
        final = transform_all_problem_data(problems, tasks)
        print(f"✓ Transformed {len(final)} problems")
        # Add more tests...

if __name__ == '__main__':
    test_transform()
```

---

## 🚀 How to Start Session 2

**Simply paste this into your new conversation:**

```
Hi Claude! I'm continuing the KPI pipeline project.

Session 1 is complete - we built the configuration and data loading for Problem Management.

Now I need you to create `src/transform_problems.py` following the Session 2 specification.

[Paste the relevant sections from above]

Let's build the transform_problems.py module!
```

---

## 📚 Reference: Config Methods Available

You already have these config methods from Session 1:

```python
config = Config()

# Get RCA settings
config.get_rca_timeframe(2)                    # Returns: 14 days
config.get_rca_targets()                       # Returns: {completion_rate_expected: 95.0, ...}

# Get column mappings  
config.get_problem_column_mapping('priority')  # Returns: "priority"
config.get_task_column_mapping('stage')        # Returns: "stage"

# Get processing configs
config.get_boolean_processing_config()         # Returns: {true_values: [...], ...}
config.get_rca_stage_config()                  # Returns: {ontime_states: ['Achieved'], ...}
```

---

## ⚠️ Common Gotchas to Watch For

1. **Priority text format varies** - Use regex to extract first digit
2. **has_breached is string** - Need to convert "true"/"false" to boolean
3. **Multiple tasks per problem** - Must choose which one to use
4. **Some problems have no tasks** - LEFT JOIN handles this
5. **Date parsing** - Use `pd.Timestamp.now()` for current date
6. **Column renaming after join** - Avoid naming conflicts

---

## 📊 Expected Final DataFrame Schema

After transformation, the DataFrame should have:

```
Original Problem columns (21):
- number, opened_at, closed_at, priority, state, etc.

New Calculated columns (9):
- Priority_Number: int
- Is_Major_Problem: bool
- Requires_RCA: bool
- Days_Open: int
- Is_Closed: bool
- RCA_Complete: bool
- RCA_OnTime: bool
- RCA_Late: bool
- RCA_InProgress: bool

Merged Task columns (6):
- rca_task_number: str or null
- rca_stage: str or null
- rca_has_breached: bool or null
- rca_due_date: datetime or null
- rca_end_time: datetime or null
- task.parent.number: str (join key)
```

---

## ✅ Ready to Build!

You now have everything needed to create `transform_problems.py` in your new conversation.

**Good luck with Session 2!** 🚀

---

**Quick Start for New Chat:**

"Hi Claude! Continuing KPI pipeline project - Session 2.

Session 1 complete: config_loader.py and load_problem_data.py working.

Now create transform_problems.py following this spec:
[paste relevant sections above]

Let's build it!"
