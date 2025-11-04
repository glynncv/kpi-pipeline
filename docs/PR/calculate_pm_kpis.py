"""
Calculate Problem Management KPIs
Compute RCA completion rates and determine status.

This module calculates KPIs for Problem Management, specifically:
- RCA001: Root Cause Analysis Completion Rate for P1/P2 problems

Expected results with EMEA data:
- 49 total problems (P2)
- 39 requiring RCA
- 29 completed on-time
- 74.4% completion rate
- RED status (< 85% threshold)

Version: 1.0
Author: KPI Pipeline Project
Date: 2025-11-03
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional


def calculate_rca_completion(df: pd.DataFrame, config: Optional[Any] = None) -> Dict[str, Any]:
    """
    Calculate RCA completion rate for P1/P2 problems.
    
    This function filters for major problems (P1/P2) that require RCA,
    counts how many have RCA completed on-time, and calculates the
    completion rate percentage.
    
    Business Logic:
    - Only P1/P2 problems (Is_Major_Problem = True)
    - Only problems requiring RCA (Requires_RCA = True)
    - RCA is "completed on-time" if RCA_OnTime = True
    - Target: 95% completion rate
    - Thresholds: GREEN ≥95%, YELLOW ≥85%, RED <85%
    
    Args:
        df: Transformed problem DataFrame (from transform_problems.py)
            Must contain columns: Is_Major_Problem, Requires_RCA, RCA_OnTime
        config: Config object (optional, for thresholds)
                If None, uses default thresholds
    
    Returns:
        Dictionary with RCA completion metrics and status:
        {
            'kpi_id': 'RCA001',
            'kpi_name': 'Root Cause Analysis Completion Rate',
            'completion_rate': 74.4,  # percentage
            'target': 95.0,
            'completed_ontime': 29,   # count
            'total_requiring_rca': 39,  # count
            'total_problems': 49,     # count
            'status': 'RED',
            'gap': -20.6,  # actual - target
            'calculation_date': '2025-11-03'
        }
    
    Example:
        >>> result = calculate_rca_completion(transformed_df)
        >>> print(f"RCA Completion: {result['completion_rate']}%")
        RCA Completion: 74.4%
    """
    # Filter: Only P1/P2 problems requiring RCA
    # Both conditions must be True
    eligible = df[
        (df['Is_Major_Problem'] == True) &
        (df['Requires_RCA'] == True)
    ]
    
    # Count metrics
    total_problems = len(df)
    total_requiring_rca = len(eligible)
    
    # Count RCA completed on-time
    # RCA_OnTime is True when task stage = 'Achieved'
    completed_ontime = eligible['RCA_OnTime'].sum()
    
    # Calculate completion rate
    # Handle division by zero case
    if total_requiring_rca > 0:
        completion_rate = (completed_ontime / total_requiring_rca) * 100
    else:
        completion_rate = 0.0
    
    # Get target and thresholds from config or use defaults
    if config:
        rca_config = config.get_kpi_config('RCA001')
        target = rca_config['target']['expected']
        thresholds = rca_config['thresholds']
    else:
        # Default values if no config provided
        target = 95.0
        thresholds = {'green': 95.0, 'yellow': 85.0, 'red': 85.0}
    
    # Determine status based on completion rate
    if completion_rate >= thresholds['green']:
        status = 'GREEN'
    elif completion_rate >= thresholds['yellow']:
        status = 'YELLOW'
    else:
        status = 'RED'
    
    # Calculate gap (negative = underperformance, positive = overperformance)
    gap = completion_rate - target
    
    # Return structured result
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
    
    This is a convenience wrapper around calculate_rca_completion()
    that always uses config for thresholds. Use this when you have
    a config object available.
    
    Args:
        df: Transformed problem DataFrame
        config: Config object (required)
    
    Returns:
        Same as calculate_rca_completion()
    
    Example:
        >>> from src.config_loader import Config
        >>> config = Config()
        >>> result = calculate_rca_kpi_status(df, config)
    """
    return calculate_rca_completion(df, config)


def calculate_all_pm_kpis(df: pd.DataFrame, config: Any) -> Dict[str, Dict[str, Any]]:
    """
    Calculate all Problem Management KPIs.
    
    This is the main orchestration function that calculates all
    PM KPIs and returns them in a structured dictionary.
    
    Currently calculates:
    - RCA001: Root Cause Analysis Completion Rate
    
    Future KPIs can be added here as they are implemented.
    
    Args:
        df: Transformed problem DataFrame
        config: Config object
    
    Returns:
        Dictionary mapping KPI ID to KPI results:
        {
            'RCA001': {
                'kpi_id': 'RCA001',
                'kpi_name': '...',
                'completion_rate': 74.4,
                ...
            },
            # Future KPIs will be added here
        }
    
    Example:
        >>> from src.config_loader import Config
        >>> config = Config()
        >>> all_kpis = calculate_all_pm_kpis(transformed_df, config)
        >>> print(f"Calculated {len(all_kpis)} KPIs")
        Calculated 1 KPIs
        >>> print(f"RCA001 status: {all_kpis['RCA001']['status']}")
        RCA001 status: RED
    """
    results = {}
    
    # Calculate RCA001: Root Cause Analysis Completion Rate
    results['RCA001'] = calculate_rca_kpi_status(df, config)
    
    # Future PM KPIs will be added here, for example:
    # results['RCA002'] = calculate_rca_timeliness(df, config)
    # results['PM001'] = calculate_problem_volume(df, config)
    
    return results


def test_pm_kpis():
    """
    Test PM KPI calculations with actual EMEA data.
    
    This test function loads real data and validates that:
    1. RCA completion calculation works correctly
    2. Status determination is accurate
    3. All expected metrics are present
    4. Values match expected results
    
    Expected results with EMEA data:
    - Total problems: 49
    - Requiring RCA: 39
    - Completed on-time: 29
    - Completion rate: 74.4%
    - Status: RED
    - Gap: -20.6%
    """
    print("=" * 60)
    print("Testing Problem Management KPI Calculations")
    print("=" * 60)
    
    try:
        # Import required modules
        import sys
        import os
        
        # Add src directory to path if running from project root
        src_path = os.path.join(os.path.dirname(__file__), 'src')
        if os.path.exists(src_path):
            sys.path.insert(0, src_path)
        
        from config_loader import Config
        from load_problem_data import load_all_problem_data
        from transform_problems import transform_all_problem_data
        
        print("\n1. Loading data from data/ directory...")
        problems, tasks = load_all_problem_data('data')
        print(f"   ✓ Loaded {len(problems)} problems, {len(tasks)} tasks")
        
        print("\n2. Transforming problem data...")
        transformed = transform_all_problem_data(problems, tasks)
        print(f"   ✓ Transformed {len(transformed)} problems")
        
        print("\n3. Testing RCA completion calculation...")
        result = calculate_rca_completion(transformed)
        
        print(f"\n   Metrics:")
        print(f"   • Total problems: {result['total_problems']}")
        print(f"   • Requiring RCA: {result['total_requiring_rca']}")
        print(f"   • Completed on-time: {result['completed_ontime']}")
        print(f"   • Completion rate: {result['completion_rate']}%")
        
        print(f"\n   Status:")
        print(f"   • Target: {result['target']}%")
        print(f"   • Status: {result['status']}")
        print(f"   • Gap: {result['gap']}%")
        print(f"   • Calculation date: {result['calculation_date']}")
        
        print("\n4. Testing with config integration...")
        config = Config()
        result_with_config = calculate_rca_kpi_status(transformed, config)
        print(f"   ✓ Config-based calculation successful")
        print(f"   • Status: {result_with_config['status']}")
        
        print("\n5. Testing full KPI calculation...")
        all_kpis = calculate_all_pm_kpis(transformed, config)
        print(f"   ✓ Calculated {len(all_kpis)} KPI(s)")
        print(f"   • KPIs: {list(all_kpis.keys())}")
        
        print("\n6. Validating expected results...")
        
        # Validation assertions
        assertions = [
            (result['total_problems'] == 49, 
             f"Total problems should be 49, got {result['total_problems']}"),
            (result['total_requiring_rca'] == 39, 
             f"Requiring RCA should be 39, got {result['total_requiring_rca']}"),
            (result['completed_ontime'] == 29, 
             f"Completed on-time should be 29, got {result['completed_ontime']}"),
            (result['completion_rate'] == 74.4, 
             f"Completion rate should be 74.4%, got {result['completion_rate']}%"),
            (result['status'] == 'RED', 
             f"Status should be RED, got {result['status']}"),
            (result['gap'] == -20.6, 
             f"Gap should be -20.6%, got {result['gap']}%"),
            (result['target'] == 95.0, 
             f"Target should be 95.0%, got {result['target']}%"),
            ('RCA001' in all_kpis, 
             "RCA001 should be in all_kpis result"),
        ]
        
        all_passed = True
        for assertion, message in assertions:
            if assertion:
                print(f"   ✓ {message.split('should be')[0].strip()} validated")
            else:
                print(f"   ✗ FAILED: {message}")
                all_passed = False
        
        if all_passed:
            print("\n" + "=" * 60)
            print("✓ ALL TESTS PASSED!")
            print("=" * 60)
            print("\nKPI Calculation Summary:")
            print(f"  RCA001: {result['completion_rate']}% (Target: {result['target']}%) - {result['status']}")
            print(f"  {result['completed_ontime']}/{result['total_requiring_rca']} problems with RCA completed on-time")
            print(f"  Gap to target: {result['gap']}%")
        else:
            print("\n" + "=" * 60)
            print("✗ SOME TESTS FAILED")
            print("=" * 60)
            return False
        
        return True
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("\nMake sure you are running from the project root directory and that:")
        print("  1. src/config_loader.py exists")
        print("  2. src/load_problem_data.py exists")
        print("  3. src/transform_problems.py exists")
        print("  4. config/kpi_config.yaml exists")
        return False
        
    except FileNotFoundError as e:
        print(f"\n✗ File Not Found: {e}")
        print("\nMake sure the data files exist:")
        print("  1. data/PYTHON_EMEA_PM_P1P2__This_Year_.csv")
        print("  2. data/PYTHON_EMEA_TASK_RCA__This_Year_.csv")
        return False
        
    except Exception as e:
        print(f"\n✗ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Run tests when executed directly
    test_pm_kpis()
