"""
Load Problem Management Data from ServiceNow Exports

Loads Problem and PM Task (RCA) CSV files with proper encoding and date parsing.
Handles the specific structure of EMEA Problem Management exports.

Version: 1.0
"""

import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
import sys

# Add src to path if running as standalone
if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).parent))

from config_loader import Config


def load_problem_data(data_dir: str = 'data', config: Optional[Config] = None) -> Optional[pd.DataFrame]:
    """
    Load Problem table CSV export from ServiceNow
    
    Handles:
    - Latin-1 encoding (special characters in descriptions)
    - Date parsing for opened_at, closed_at
    - P1/P2 problem filtering (file should already be filtered)
    
    Args:
        data_dir: Directory containing CSV files
        config: Config object (creates new if None)
        
    Returns:
        pd.DataFrame: Problem data or None if file not found
        
    Columns expected:
        - number: Problem ID (e.g., PRB0050848)
        - opened_at: Problem opened datetime
        - closed_at: Problem closed datetime (may be null)
        - priority: Priority text (e.g., "2 - High")
        - state: Problem state
        - u_rca_required: Yes/No flag
        - location.country: Country
        - Other fields...
    """
    if config is None:
        config = Config()
    
    problem_filename = config.get_problem_filename()
    problem_file = Path(data_dir) / problem_filename
    
    if not problem_file.exists():
        print(f"⚠ Warning: Problem file not found: {problem_file}")
        print(f"   Problem Management KPIs will be skipped")
        return None
    
    try:
        # Load with latin-1 encoding to handle special characters
        # Parse dates automatically
        df = pd.read_csv(
            problem_file,
            encoding='latin-1',
            parse_dates=['opened_at', 'closed_at'],
            low_memory=False
        )
        
        print(f"✓ Loaded {len(df)} problems from {problem_filename}")
        
        # Basic validation
        required_cols = ['number', 'opened_at', 'priority']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"⚠ Warning: Missing required columns: {missing_cols}")
        
        return df
        
    except Exception as e:
        print(f"✗ Error loading problem data: {e}")
        return None


def load_task_data(data_dir: str = 'data', config: Optional[Config] = None) -> Optional[pd.DataFrame]:
    """
    Load PM Task (RCA) table CSV export from ServiceNow
    
    This table contains SLA tracking for RCA tasks associated with problems.
    More reliable than Problem table RCA fields for determining completion status.
    
    Handles:
    - Latin-1 encoding
    - Date parsing for multiple datetime fields
    - Boolean conversion for has_breached
    
    Args:
        data_dir: Directory containing CSV files
        config: Config object (creates new if None)
        
    Returns:
        pd.DataFrame: Task data or None if file not found
        
    Key columns:
        - task: Task ID (e.g., PTASK0051767)
        - task.parent.number: Parent problem ID (e.g., PRB0050887)
        - stage: RCA status (Achieved, Breached, In progress, Paused)
        - has_breached: Boolean - did RCA breach SLA?
        - task.due_date: When RCA was due
        - end_time: When RCA was completed
    """
    if config is None:
        config = Config()
    
    task_filename = config.get_task_filename()
    task_file = Path(data_dir) / task_filename
    
    if not task_file.exists():
        print(f"⚠ Warning: Task file not found: {task_file}")
        print(f"   RCA tracking will not be available")
        return None
    
    try:
        # Load with latin-1 encoding
        # Parse all datetime columns
        df = pd.read_csv(
            task_file,
            encoding='latin-1',
            parse_dates=['start_time', 'planned_end_time', 'task.due_date', 'end_time'],
            low_memory=False
        )
        
        print(f"✓ Loaded {len(df)} RCA tasks from {task_filename}")
        
        # Basic validation
        required_cols = ['task', 'task.parent.number', 'stage']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"⚠ Warning: Missing required columns: {missing_cols}")
        
        return df
        
    except Exception as e:
        print(f"✗ Error loading task data: {e}")
        return None


def load_all_problem_data(data_dir: str = 'data', config: Optional[Config] = None) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    Load both Problem and Task data files
    
    Convenience function that loads both files and returns them as a tuple.
    If either file is missing, returns (None, None) to indicate Problem
    Management data is not available.
    
    Args:
        data_dir: Directory containing CSV files
        config: Config object (creates new if None)
        
    Returns:
        tuple: (problems_df, tasks_df) or (None, None) if files not found
        
    Example:
        >>> problems, tasks = load_all_problem_data('data')
        >>> if problems is not None:
        ...     print(f"Loaded {len(problems)} problems and {len(tasks)} tasks")
        ... else:
        ...     print("Problem Management data not available")
    """
    if config is None:
        config = Config()
    
    print("\n" + "=" * 80)
    print("Loading Problem Management Data")
    print("=" * 80)
    
    problems = load_problem_data(data_dir, config)
    tasks = load_task_data(data_dir, config)
    
    # Both files must be present for Problem Management KPIs
    if problems is None or tasks is None:
        print("\n⚠ Problem Management data incomplete - PM KPIs will be skipped")
        print("=" * 80)
        return None, None
    
    # Verify we can join them
    problem_numbers = set(problems['number'].values)
    task_parent_numbers = set(tasks['task.parent.number'].values)
    matching = problem_numbers & task_parent_numbers
    
    print(f"\n✓ Data Quality Check:")
    print(f"  Problems in file: {len(problems)}")
    print(f"  Tasks in file: {len(tasks)}")
    print(f"  Tasks matching problems: {len(matching)}")
    print(f"  Coverage: {len(matching)/len(problems)*100:.1f}%")
    
    if len(matching) < len(problems) * 0.5:
        print(f"\n⚠ Warning: Low task coverage (<50%)")
        print(f"  Some problems may not have RCA tasks")
    
    print("=" * 80)
    
    return problems, tasks


def print_problem_data_summary(problems_df: pd.DataFrame, tasks_df: pd.DataFrame):
    """
    Print summary statistics for Problem Management data
    
    Useful for validation and debugging
    
    Args:
        problems_df: Problem DataFrame
        tasks_df: Task DataFrame
    """
    print("\n" + "=" * 80)
    print("Problem Management Data Summary")
    print("=" * 80)
    
    # Problem summary
    print("\nPROBLEM DATA:")
    print(f"  Total problems: {len(problems_df)}")
    
    if 'priority' in problems_df.columns:
        print(f"\n  Priority distribution:")
        for priority, count in problems_df['priority'].value_counts().items():
            print(f"    {priority}: {count}")
    
    if 'state' in problems_df.columns:
        print(f"\n  State distribution:")
        for state, count in problems_df['state'].value_counts().head(5).items():
            print(f"    {state}: {count}")
    
    if 'u_rca_required' in problems_df.columns:
        print(f"\n  RCA Required:")
        for req, count in problems_df['u_rca_required'].value_counts().items():
            print(f"    {req}: {count}")
    
    # Task summary
    print("\n\nTASK DATA:")
    print(f"  Total RCA tasks: {len(tasks_df)}")
    
    if 'stage' in tasks_df.columns:
        print(f"\n  RCA Stage distribution:")
        for stage, count in tasks_df['stage'].value_counts().items():
            print(f"    {stage}: {count}")
    
    if 'has_breached' in tasks_df.columns:
        print(f"\n  SLA Breach status:")
        breach_counts = tasks_df['has_breached'].value_counts()
        for status, count in breach_counts.items():
            print(f"    Breached={status}: {count}")
    
    print("=" * 80)


def test_load_problem_data():
    """Test function to validate data loading"""
    print("\n" + "=" * 80)
    print("Testing Problem Management Data Loading")
    print("=" * 80)
    
    # Test with actual data
    config = Config()
    
    # Test individual loads
    print("\n1. Testing individual file loads...")
    problems = load_problem_data('data', config)
    tasks = load_task_data('data', config)
    
    if problems is not None:
        print(f"\n✓ Problems loaded: {len(problems)} rows")
        print(f"  Columns: {list(problems.columns[:5])}...")
        print(f"  Date range: {problems['opened_at'].min()} to {problems['opened_at'].max()}")
    else:
        print("\n✗ Failed to load problems")
    
    if tasks is not None:
        print(f"\n✓ Tasks loaded: {len(tasks)} rows")
        print(f"  Columns: {list(tasks.columns[:5])}...")
    else:
        print("\n✗ Failed to load tasks")
    
    # Test combined load
    print("\n\n2. Testing combined load...")
    problems, tasks = load_all_problem_data('data', config)
    
    if problems is not None and tasks is not None:
        print("\n✓ Both files loaded successfully!")
        print_problem_data_summary(problems, tasks)
        
        # Check data quality
        print("\n\n3. Data Quality Checks:")
        
        # Check for required fields
        required_problem_fields = ['number', 'opened_at', 'priority', 'u_rca_required']
        missing_problem = [f for f in required_problem_fields if f not in problems.columns]
        if missing_problem:
            print(f"  ⚠ Missing problem fields: {missing_problem}")
        else:
            print(f"  ✓ All required problem fields present")
        
        required_task_fields = ['task', 'task.parent.number', 'stage', 'has_breached']
        missing_task = [f for f in required_task_fields if f not in tasks.columns]
        if missing_task:
            print(f"  ⚠ Missing task fields: {missing_task}")
        else:
            print(f"  ✓ All required task fields present")
        
        # Check for nulls in critical fields
        print(f"\n  Null counts in critical fields:")
        print(f"    Problem number nulls: {problems['number'].isna().sum()}")
        print(f"    Problem opened_at nulls: {problems['opened_at'].isna().sum()}")
        print(f"    Task parent.number nulls: {tasks['task.parent.number'].isna().sum()}")
        
        print("\n✓ Data loading tests complete!")
        
    else:
        print("\n⚠ Problem Management data not available")
    
    print("=" * 80)


if __name__ == '__main__':
    # Run tests when module is executed directly
    test_load_problem_data()
