"""
Test script for transform_problems.py
Creates sample data and validates all transformation functions.

Run this to verify transformations work correctly:
    python tests/test_transform_problems.py
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.transform_problems import (
    extract_priority_number,
    add_problem_calculated_fields,
    add_task_calculated_fields,
    join_problems_with_tasks,
    transform_all_problem_data,
    validate_transformation
)


def create_sample_problems():
    """Create sample problem data for testing"""
    current_date = pd.Timestamp('2025-11-03')
    
    data = {
        'number': ['PRB0001', 'PRB0002', 'PRB0003', 'PRB0004', 'PRB0005'],
        'priority': ['2 - High', '1 - Critical', '2 - High', '3 - Moderate', '2 - High'],
        'u_rca_required': ['Yes', 'Yes', 'Yes', 'No', 'Yes'],
        'opened_at': [
            current_date - timedelta(days=30),
            current_date - timedelta(days=45),
            current_date - timedelta(days=20),
            current_date - timedelta(days=10),
            current_date - timedelta(days=15)
        ],
        'closed_at': [
            pd.NaT,
            current_date - timedelta(days=5),
            pd.NaT,
            current_date - timedelta(days=2),
            pd.NaT
        ],
        'state': ['Open', 'Closed', 'Open', 'Closed', 'Pending Change'],
        'short_description': [
            'Database connectivity issue',
            'Critical server outage',
            'Application performance degradation',
            'Minor configuration issue',
            'Network latency problem'
        ]
    }
    
    return pd.DataFrame(data)


def create_sample_tasks():
    """Create sample task data for testing"""
    data = {
        'task': ['PTASK001', 'PTASK002', 'PTASK003', 'PTASK004'],
        'task.parent.number': ['PRB0001', 'PRB0002', 'PRB0002', 'PRB0003'],
        'stage': ['Achieved', 'Breached', 'Achieved', 'In progress'],
        'has_breached': ['false', 'true', 'false', 'false'],
        'task.due_date': [
            pd.Timestamp('2025-10-20'),
            pd.Timestamp('2025-09-25'),
            pd.Timestamp('2025-09-20'),
            pd.Timestamp('2025-11-10')
        ],
        'end_time': [
            pd.Timestamp('2025-10-18'),
            pd.Timestamp('2025-09-30'),
            pd.Timestamp('2025-09-18'),
            pd.NaT
        ]
    }
    
    return pd.DataFrame(data)


def test_priority_extraction():
    """Test priority extraction function"""
    print("\n" + "=" * 60)
    print("TEST SUITE 1: Priority Extraction")
    print("=" * 60)
    
    test_cases = [
        ("2 - High", 2),
        ("1 - Critical", 1),
        ("3 - Moderate", 3),
        ("4 - Low", 4),
        ("Priority 2", 2),
        ("Unknown", 99),
        (None, 99),
        ("", 99)
    ]
    
    passed = 0
    failed = 0
    
    for input_val, expected in test_cases:
        result = extract_priority_number(input_val)
        if result == expected:
            print(f"[OK] '{input_val}' → {result}")
            passed += 1
        else:
            print(f"[FAIL] '{input_val}' → {result} (expected {expected})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_problem_calculated_fields():
    """Test problem calculated fields"""
    print("\n" + "=" * 60)
    print("TEST SUITE 2: Problem Calculated Fields")
    print("=" * 60)
    
    problems = create_sample_problems()
    transformed = add_problem_calculated_fields(problems)
    
    # Check required columns exist
    required_cols = ['Priority_Number', 'Is_Major_Problem', 'Requires_RCA', 'Days_Open', 'Is_Closed']
    missing = [col for col in required_cols if col not in transformed.columns]
    
    if missing:
        print(f"[FAIL] Missing columns: {missing}")
        return False
    
    print("[OK] All required columns present")
    
    # Validate specific values
    test_cases = [
        ('PRB0001', 'Priority_Number', 2),
        ('PRB0002', 'Priority_Number', 1),
        ('PRB0001', 'Is_Major_Problem', True),
        ('PRB0004', 'Is_Major_Problem', False),
        ('PRB0001', 'Requires_RCA', True),
        ('PRB0004', 'Requires_RCA', False),
        ('PRB0002', 'Is_Closed', True),
        ('PRB0001', 'Is_Closed', False),
    ]
    
    passed = 0
    failed = 0
    
    for problem_num, col, expected in test_cases:
        row = transformed[transformed['number'] == problem_num].iloc[0]
        actual = row[col]
        if isinstance(expected, bool):
            match = actual == expected
        else:
            match = actual == expected
        if match:
            print(f"[OK] {problem_num}.{col} = {actual}")
            passed += 1
        else:
            print(f"[FAIL] {problem_num}.{col} = {actual} (expected {expected})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_task_calculated_fields():
    """Test task calculated fields"""
    print("\n" + "=" * 60)
    print("TEST SUITE 3: Task Calculated Fields")
    print("=" * 60)
    
    tasks = create_sample_tasks()
    transformed = add_task_calculated_fields(tasks)
    
    # Check required columns
    required_cols = ['Is_RCA_Complete', 'Is_RCA_OnTime', 'Is_RCA_Late', 'Is_RCA_InProgress', 'task_priority']
    missing = [col for col in required_cols if col not in transformed.columns]
    
    if missing:
        print(f"[FAIL] Missing columns: {missing}")
        return False
    
    print("[OK] All required columns present")
    
    # Validate values
    test_cases = [
        ('PTASK001', 'Is_RCA_OnTime', True),
        ('PTASK001', 'Is_RCA_Late', False),
        ('PTASK002', 'Is_RCA_Late', True),
        ('PTASK002', 'Is_RCA_OnTime', False),
        ('PTASK004', 'Is_RCA_InProgress', True),
        ('PTASK001', 'task_priority', 1),  # Achieved
        ('PTASK002', 'task_priority', 2),  # Breached
        ('PTASK004', 'task_priority', 3),  # In progress
    ]
    
    passed = 0
    failed = 0
    
    for task_num, col, expected in test_cases:
        row = transformed[transformed['task'] == task_num].iloc[0]
        actual = row[col]
        if actual == expected:
            print(f"[OK] {task_num}.{col} = {actual}")
            passed += 1
        else:
            print(f"[FAIL] {task_num}.{col} = {actual} (expected {expected})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_join_problems_tasks():
    """Test joining problems with tasks"""
    print("\n" + "=" * 60)
    print("TEST SUITE 4: Join Problems with Tasks")
    print("=" * 60)
    
    problems = create_sample_problems()
    tasks = create_sample_tasks()
    
    problems_transformed = add_problem_calculated_fields(problems)
    tasks_transformed = add_task_calculated_fields(tasks)
    
    result = join_problems_with_tasks(problems_transformed, tasks_transformed)
    
    # Should have all 5 problems
    if len(result) != 5:
        print(f"[FAIL] Expected 5 problems, got {len(result)}")
        return False
    
    print(f"[OK] All 5 problems preserved (LEFT JOIN)")
    
    # PRB0002 has two tasks (PTASK002 Breached, PTASK003 Achieved)
    # Should pick PTASK003 (Achieved) because it has higher priority
    prb0002 = result[result['number'] == 'PRB0002'].iloc[0]
    if prb0002['rca_task_number'] == 'PTASK003':
        print("[OK] Multiple tasks per problem: Selected Achieved (best task)")
    else:
        print(f"[FAIL] Expected PTASK003, got {prb0002['rca_task_number']}")
        return False
    
    # PRB0004 has no task - should have null/False values
    prb0004 = result[result['number'] == 'PRB0004'].iloc[0]
    if pd.isna(prb0004.get('rca_task_number')):
        print("[OK] Problem without task: Has null task number")
    else:
        print("[FAIL] Expected null task number for problem without task")
        return False
    
    # PRB0005 has no task - RCA flags should be False
    prb0005 = result[result['number'] == 'PRB0005'].iloc[0]
    if not prb0005.get('RCA_OnTime', True):  # Should be False
        print("[OK] Problem without task: RCA_OnTime = False")
    else:
        print("[FAIL] Expected RCA_OnTime = False for problem without task")
        return False
    
    print("\n[OK] All join tests passed")
    return True


def test_full_transformation():
    """Test full transformation pipeline"""
    print("\n" + "=" * 60)
    print("TEST SUITE 5: Full Transformation Pipeline")
    print("=" * 60)
    
    problems = create_sample_problems()
    tasks = create_sample_tasks()
    
    result = transform_all_problem_data(problems, tasks)
    
    # Validate structure
    required_cols = ['number', 'Priority_Number', 'Is_Major_Problem', 'Requires_RCA', 
                     'RCA_OnTime', 'RCA_Late', 'RCA_InProgress']
    missing = [col for col in required_cols if col not in result.columns]
    
    if missing:
        print(f"[FAIL] Missing columns: {missing}")
        return False
    
    print("[OK] All required columns present in result")
    
    # Validate counts
    stats = validate_transformation(result)
    
    checks = [
        (stats['total_problems'], 5, 'total_problems'),
        (stats['major_problems'], 4, 'major_problems'),  # P1/P2 = 4
        (stats['requires_rca'], 4, 'requires_rca'),  # 4 out of 5 require RCA
        (stats['rca_ontime'], 2, 'rca_ontime'),  # PTASK001 and PTASK003
    ]
    
    passed = 0
    failed = 0
    
    for actual, expected, name in checks:
        if actual == expected:
            print(f"[OK] {name}: {actual}")
            passed += 1
        else:
            print(f"[FAIL] {name}: {actual} (expected {expected})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_with_real_data():
    """Test with actual data files if available"""
    print("\n" + "=" * 60)
    print("TEST SUITE 6: Real Data Integration")
    print("=" * 60)
    
    try:
        from src import load_problem_data
        
        problems, tasks = load_problem_data.load_all_problem_data('data')
        
        if problems is None or tasks is None:
            print("[SKIP] Real data not available (this is OK)")
            return True
        
        result = transform_all_problem_data(problems, tasks)
        stats = validate_transformation(result)
        
        print(f"[OK] Loaded and transformed {len(result)} problems")
        print(f"[OK] Requires RCA: {stats['requires_rca']}")
        print(f"[OK] RCA on-time: {stats['rca_ontime']}")
        print(f"[OK] Completion rate: {stats['rca_completion_rate_pct']:.1f}%")
        
        # Expected values from Session 2 summary
        if stats['total_problems'] == 49 and stats['rca_ontime'] == 29:
            print("[OK] Validation matches expected Session 2 results")
        else:
            print(f"[WARNING] Results differ from expected (49 problems, 29 on-time)")
            print(f"          Got: {stats['total_problems']} problems, {stats['rca_ontime']} on-time")
        
        return True
        
    except ImportError:
        print("[SKIP] load_problem_data not available")
        return True
    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test suites"""
    print("=" * 60)
    print("TRANSFORM_PROBLEMS.PY TEST SUITE")
    print("=" * 60)
    
    results = []
    
    results.append(("Priority Extraction", test_priority_extraction()))
    results.append(("Problem Calculated Fields", test_problem_calculated_fields()))
    results.append(("Task Calculated Fields", test_task_calculated_fields()))
    results.append(("Join Problems with Tasks", test_join_problems_tasks()))
    results.append(("Full Transformation", test_full_transformation()))
    results.append(("Real Data Integration", test_with_real_data()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    if passed == total:
        print("\n[OK] All tests PASSED!")
        return 0
    else:
        print("\n[FAIL] Some tests failed")
        return 1


if __name__ == '__main__':
    exit(main())

