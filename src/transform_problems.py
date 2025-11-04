"""
Transform Problem Management Data
Add calculated fields and join Problems with Tasks for RCA analysis.

This module transforms raw Problem and Task data by:
1. Extracting priority numbers from text format
2. Adding calculated fields (Is_Major_Problem, Requires_RCA, Days_Open)
3. Adding RCA status flags (OnTime, Late, InProgress)
4. Joining problems with tasks (LEFT JOIN, handles multiple tasks)

Version: 1.0
Date: 2025-11-03
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import Optional


def extract_priority_number(priority_text: str) -> int:
    """
    Extract numeric priority from text format.
    
    Handles priority formats like:
    - "2 - High" → 2
    - "1 - Critical" → 1
    - "3 - Moderate" → 3
    
    Args:
        priority_text: Priority as text string
        
    Returns:
        Numeric priority (1-4) or 99 if unparseable
        
    Examples:
        >>> extract_priority_number("2 - High")
        2
        >>> extract_priority_number("Priority 1")
        1
        >>> extract_priority_number("Unknown")
        99
    """
    if pd.isna(priority_text):
        return 99
    
    # Convert to string and extract first digit
    priority_str = str(priority_text)
    match = re.search(r'(\d+)', priority_str)
    
    if match:
        return int(match.group(1))
    
    return 99


def add_problem_calculated_fields(df: pd.DataFrame, current_date: Optional[pd.Timestamp] = None) -> pd.DataFrame:
    """
    Add calculated fields to Problem DataFrame.
    
    Adds the following fields:
    - Priority_Number: Numeric priority (1-4, 99 for unknown)
    - Is_Major_Problem: True for P1 and P2 problems
    - Requires_RCA: True if RCA is required
    - Days_Open: Days since problem was opened
    - Is_Closed: True if problem is closed
    
    Args:
        df: Problem DataFrame
        current_date: Reference date for calculations (defaults to now)
        
    Returns:
        DataFrame with added calculated fields
    """
    if current_date is None:
        current_date = pd.Timestamp.now()
    
    df = df.copy()
    
    # Extract numeric priority
    df['Priority_Number'] = df['priority'].apply(extract_priority_number)
    
    # Identify major problems (P1 and P2)
    df['Is_Major_Problem'] = df['Priority_Number'].isin([1, 2])
    
    # Check if RCA is required
    # u_rca_required can be 'Yes', 'yes', True, or similar variations
    df['Requires_RCA'] = df['u_rca_required'].astype(str).str.lower().isin(['yes', 'true', '1'])
    
    # Calculate days open
    # Convert opened_at to datetime if not already
    df['opened_at'] = pd.to_datetime(df['opened_at'], errors='coerce')
    df['Days_Open'] = (current_date - df['opened_at']).dt.days
    
    # Check if closed
    df['Is_Closed'] = df['closed_at'].notna()
    
    return df


def add_task_calculated_fields(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add calculated fields to Task DataFrame.
    
    Adds the following RCA status fields:
    - Is_RCA_Complete: Task is finished (Achieved or Breached)
    - Is_RCA_OnTime: Task completed on time (Achieved)
    - Is_RCA_Late: Task completed late (Breached)
    - Is_RCA_InProgress: Task is in progress
    - task_priority: Priority for choosing best task (internal)
    
    Args:
        df: Task DataFrame with 'stage' column
        
    Returns:
        DataFrame with added calculated fields
    """
    df = df.copy()
    
    # Normalize stage values (handle case variations)
    df['stage_normalized'] = df['stage'].astype(str).str.strip().str.lower()
    
    # RCA completion flags based on stage
    df['Is_RCA_Complete'] = df['stage_normalized'].isin(['achieved', 'breached'])
    df['Is_RCA_OnTime'] = df['stage_normalized'] == 'achieved'
    df['Is_RCA_Late'] = df['stage_normalized'] == 'breached'
    df['Is_RCA_InProgress'] = df['stage_normalized'] == 'in progress'
    
    # Convert has_breached from text to boolean
    # Handle variations: "true", "True", "false", "False", True, False
    if 'has_breached' in df.columns:
        df['has_breached_bool'] = df['has_breached'].astype(str).str.lower().map({
            'true': True,
            'false': False
        })
    
    # Add task priority for selecting best task when multiple exist
    # Priority: Achieved (1) > Breached (2) > In Progress (3) > Paused (4) > Other (5)
    stage_priority_map = {
        'achieved': 1,
        'breached': 2,
        'in progress': 3,
        'paused': 4
    }
    df['task_priority'] = df['stage_normalized'].map(stage_priority_map).fillna(5)
    
    return df


def join_problems_with_tasks(problems_df: pd.DataFrame, tasks_df: pd.DataFrame) -> pd.DataFrame:
    """
    LEFT JOIN Problems with Tasks, handling multiple tasks per problem.
    
    Strategy:
    - LEFT JOIN to keep all problems (even without tasks)
    - When multiple tasks exist for a problem, pick the "best" one:
      1. Achieved (completed on-time) - highest priority
      2. Breached (completed late)
      3. In progress (still working)
      4. Paused (lowest priority)
    - Problems without tasks will have RCA flags set to False
    
    Args:
        problems_df: Problem DataFrame with calculated fields
        tasks_df: Task DataFrame with calculated fields
        
    Returns:
        DataFrame with problems and their associated RCA task info
    """
    # Sort tasks by priority and take first per problem
    # This ensures we get the "best" task when multiple exist
    tasks_sorted = tasks_df.sort_values('task_priority')
    tasks_deduped = tasks_sorted.groupby('task.parent.number').first().reset_index()
    
    # Prepare task columns for merge (prefix with 'rca_' to avoid conflicts)
    # Note: Task DataFrame has 'task' column (not 'number'), 'task.parent.number', etc.
    task_columns_to_merge = {
        'task': 'rca_task_number',
        'stage': 'rca_stage',
        'has_breached': 'rca_has_breached',
        'task.due_date': 'rca_due_date',
        'end_time': 'rca_end_time',
        'Is_RCA_OnTime': 'RCA_OnTime',
        'Is_RCA_Late': 'RCA_Late',
        'Is_RCA_InProgress': 'RCA_InProgress',
        'Is_RCA_Complete': 'RCA_Complete'
    }
    
    # Select and rename task columns
    task_merge_cols = ['task.parent.number'] + list(task_columns_to_merge.keys())
    # Only include columns that exist
    task_merge_cols = [col for col in task_merge_cols if col in tasks_deduped.columns]
    tasks_for_merge = tasks_deduped[task_merge_cols].copy()
    
    # Rename columns
    rename_dict = {k: v for k, v in task_columns_to_merge.items() if k in tasks_for_merge.columns}
    tasks_for_merge.rename(columns=rename_dict, inplace=True)
    
    # LEFT JOIN: Keep all problems
    result = problems_df.merge(
        tasks_for_merge,
        left_on='number',
        right_on='task.parent.number',
        how='left'
    )
    
    # Fill NaN values for problems without tasks
    # Convert to boolean explicitly to avoid pandas FutureWarning
    rca_flag_columns = ['RCA_OnTime', 'RCA_Late', 'RCA_InProgress', 'RCA_Complete']
    for col in rca_flag_columns:
        if col in result.columns:
            # Create boolean column properly
            result[col] = result[col].notna() & (result[col] == True)
    
    return result


def transform_all_problem_data(
    problems_df: pd.DataFrame,
    tasks_df: pd.DataFrame,
    current_date: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Orchestrate all transformations for Problem Management data.
    
    This is the main entry point that:
    1. Adds calculated fields to problems
    2. Adds calculated fields to tasks
    3. Joins problems with tasks
    4. Returns fully transformed data ready for KPI calculations
    
    Args:
        problems_df: Raw Problem DataFrame
        tasks_df: Raw Task DataFrame
        current_date: Reference date for calculations (defaults to now)
        
    Returns:
        Fully transformed DataFrame with all problems and RCA status
    """
    # Transform problems
    problems_transformed = add_problem_calculated_fields(problems_df, current_date)
    
    # Transform tasks
    tasks_transformed = add_task_calculated_fields(tasks_df)
    
    # Join problems with tasks
    final = join_problems_with_tasks(problems_transformed, tasks_transformed)
    
    return final


def validate_transformation(df: pd.DataFrame) -> dict:
    """
    Validate the transformed data and return summary statistics.
    
    Args:
        df: Transformed Problem DataFrame
        
    Returns:
        Dictionary with validation statistics
    """
    stats = {
        'total_problems': len(df),
        'major_problems': df['Is_Major_Problem'].sum(),
        'requires_rca': df['Requires_RCA'].sum(),
        'has_rca_task': df['rca_task_number'].notna().sum() if 'rca_task_number' in df.columns else 0,
        'rca_ontime': df['RCA_OnTime'].sum() if 'RCA_OnTime' in df.columns else 0,
        'rca_late': df['RCA_Late'].sum() if 'RCA_Late' in df.columns else 0,
        'rca_in_progress': df['RCA_InProgress'].sum() if 'RCA_InProgress' in df.columns else 0,
        'closed_problems': df['Is_Closed'].sum(),
        'avg_days_open': df['Days_Open'].mean()
    }
    
    # Calculate coverage and completion rates
    if stats['requires_rca'] > 0:
        stats['task_coverage_pct'] = (stats['has_rca_task'] / stats['requires_rca']) * 100
        stats['rca_completion_rate_pct'] = (stats['rca_ontime'] / stats['requires_rca']) * 100
    else:
        stats['task_coverage_pct'] = 0
        stats['rca_completion_rate_pct'] = 0
    
    return stats


# Test function
def test_transform():
    """
    Test transformations with sample data or actual data if available.
    
    This function is designed to be run standalone for testing.
    """
    print("=" * 60)
    print("Testing Problem Management Transformations")
    print("=" * 60)
    
    # Test priority extraction
    print("\n1. Testing Priority Extraction")
    print("-" * 40)
    test_priorities = ["2 - High", "1 - Critical", "3 - Moderate", "Invalid", None]
    for p in test_priorities:
        result = extract_priority_number(p)
        print(f"  '{p}' → {result}")
    
    # Try to load actual data if available
    try:
        # Import here to avoid circular dependencies
        try:
            from . import load_problem_data
        except ImportError:
            try:
                from src import load_problem_data
            except ImportError:
                import load_problem_data
        
        print("\n2. Testing with Actual Data")
        print("-" * 40)
        
        problems, tasks = load_problem_data.load_all_problem_data('data/input')
        
        if problems is not None and tasks is not None:
            print(f"[OK] Loaded {len(problems)} problems, {len(tasks)} tasks")
            
            # Transform data
            final = transform_all_problem_data(problems, tasks)
            print(f"[OK] Transformed {len(final)} problems")
            
            # Validate
            stats = validate_transformation(final)
            
            print("\n3. Validation Statistics")
            print("-" * 40)
            print(f"  Total problems: {stats['total_problems']}")
            print(f"  Major problems (P1/P2): {stats['major_problems']}")
            print(f"  Requires RCA: {stats['requires_rca']}")
            print(f"  Has RCA task: {stats['has_rca_task']}")
            print(f"  Task coverage: {stats['task_coverage_pct']:.1f}%")
            print(f"\n  RCA on-time: {stats['rca_ontime']}")
            print(f"  RCA late: {stats['rca_late']}")
            print(f"  RCA in progress: {stats['rca_in_progress']}")
            print(f"  RCA completion rate: {stats['rca_completion_rate_pct']:.1f}%")
            print(f"\n  Closed problems: {stats['closed_problems']}")
            print(f"  Average days open: {stats['avg_days_open']:.1f}")
            
            print("\n4. Sample Transformed Data")
            print("-" * 40)
            sample_cols = ['number', 'Priority_Number', 'Is_Major_Problem', 
                          'Requires_RCA', 'RCA_OnTime', 'Days_Open']
            available_cols = [col for col in sample_cols if col in final.columns]
            print(final[available_cols].head(3))
            
            # Success validation
            print("\n" + "=" * 60)
            expected_problems = 49
            expected_rca_ontime = 29
            expected_requires_rca = 39
            
            success = True
            if stats['total_problems'] == expected_problems:
                print("[OK] PASS: Total problems = 49")
            else:
                print(f"[FAIL] Expected 49 problems, got {stats['total_problems']}")
                success = False
                
            if stats['rca_ontime'] == expected_rca_ontime:
                print("[OK] PASS: RCA on-time = 29")
            else:
                print(f"[FAIL] Expected 29 RCA on-time, got {stats['rca_ontime']}")
                success = False
                
            if stats['requires_rca'] == expected_requires_rca:
                print("[OK] PASS: Requires RCA = 39")
            else:
                print(f"[FAIL] Expected 39 requires RCA, got {stats['requires_rca']}")
                success = False
            
            if success:
                print("\n[OK] All tests PASSED!")
            else:
                print("\n[WARNING] Some tests failed - review results above")
                
        else:
            print("[ERROR] Could not load data files")
            print("  Make sure data files are in 'data/' directory")
            
    except ImportError as e:
        print(f"\n[WARNING] Cannot load actual data: {e}")
        print("  This is normal if running standalone")
        print("  Install load_problem_data.py to test with real data")
    except Exception as e:
        print(f"\n[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    # For standalone execution, try relative import fallback
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from . import load_problem_data
    except ImportError:
        import load_problem_data
    
    test_transform()

