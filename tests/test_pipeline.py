"""
Test suite for KPI Pipeline
Validates data loading, transformation, and KPI calculations.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import config_loader, load_data, transform, calculate_kpis
import pandas as pd


def test_config_loading():
    """Test configuration loading."""
    print("\n" + "="*70)
    print("TEST 1: Configuration Loading")
    print("="*70)
    
    try:
        config = config_loader.load_config('config/kpi_config.yaml')
        
        # Validate key sections exist
        assert 'metadata' in config, "Missing 'metadata' section"
        assert 'kpis' in config, "Missing 'kpis' section"
        assert 'column_mappings' in config, "Missing 'column_mappings' section"
        
        print("✓ Configuration loaded successfully")
        print(f"  Organization: {config['metadata']['organization']}")
        print(f"  Version: {config['metadata']['version']}")
        print(f"  KPIs configured: {len([k for k in config['kpis'] if config['kpis'][k]['enabled']])}")
        
        return True, config
        
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False, None


def test_data_loading(config):
    """Test data loading with sample data."""
    print("\n" + "="*70)
    print("TEST 2: Data Loading")
    print("="*70)
    
    try:
        # Check if sample data exists, otherwise use real data
        sample_incident_path = 'tests/sample_data/sample_incidents.csv'
        sample_request_path = 'tests/sample_data/sample_requests.csv'
        
        if os.path.exists(sample_incident_path):
            incidents_path = sample_incident_path
        else:
            incidents_path = 'data/input/PYTHON EMEA IM (last 90 days)_redacted_clean.csv'
            print("  ℹ Using real incident data (sample data not found)")
        
        # Load incidents
        incidents = load_data.load_incidents(incidents_path, config)
        print(f"✓ Loaded {len(incidents)} incidents")
        
        # Validate required columns
        required_cols = ['number', 'priority', 'opened_at']
        for col in required_cols:
            assert col in incidents.columns, f"Missing required column: {col}"
        print(f"  Columns: {len(incidents.columns)}")
        
        # Load requests if enabled
        requests = None
        if config['kpis']['SM003']['enabled']:
            if os.path.exists(sample_request_path):
                requests_path = sample_request_path
            else:
                requests_path = 'data/input/PYTHON EMEA SCT (last 90 days)_redacted_clean.csv'
                print("  ℹ Using real request data (sample data not found)")
            
            requests = load_data.load_requests(requests_path, config)
            print(f"✓ Loaded {len(requests)} requests")
        
        return True, incidents, requests
        
    except Exception as e:
        print(f"✗ Data loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_data_transformation(incidents, requests, config):
    """Test data transformation."""
    print("\n" + "="*70)
    print("TEST 3: Data Transformation")
    print("="*70)
    
    try:
        # Transform incidents
        incidents_transformed = transform.add_incident_flags(incidents.copy(), config)
        print(f"✓ Transformed incidents")
        
        # Check for added columns
        expected_flags = ['is_major_incident', 'is_backlog', 'age_days']
        for flag in expected_flags:
            if flag in incidents_transformed.columns:
                print(f"  ✓ Added column: {flag}")
        
        # Transform requests if available
        if requests is not None:
            requests_transformed = transform.add_request_flags(requests.copy(), config)
            print(f"✓ Transformed requests")
            
            if 'is_aged' in requests_transformed.columns:
                print(f"  ✓ Added column: is_aged")
        else:
            requests_transformed = None
        
        return True, incidents_transformed, requests_transformed
        
    except Exception as e:
        print(f"✗ Data transformation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None


def test_kpi_calculations(incidents, requests, config):
    """Test KPI calculations."""
    print("\n" + "="*70)
    print("TEST 4: KPI Calculations")
    print("="*70)
    
    try:
        kpi_results = calculate_kpis.calculate_all(incidents, requests, config)
        
        print(f"✓ Calculated KPIs")
        print(f"\nKPI Results:")
        print("-" * 70)
        
        for kpi_code, kpi_data in kpi_results.items():
            if kpi_code == 'OVERALL':
                print(f"\n{kpi_code}:")
                print(f"  Overall Score: {kpi_data['Overall_Score']}%")
                print(f"  Overall Status: {kpi_data['Overall_Status']}")
            else:
                print(f"\n{kpi_code}: {kpi_data['KPI_Name']}")
                print(f"  Status: {kpi_data['Status']}")
                print(f"  Adherence: {kpi_data['Adherence_Rate']}%")
                print(f"  Business Impact: {kpi_data['Business_Impact']}")
        
        # Validate expected KPIs
        expected_kpis = ['SM001', 'SM002', 'SM004', 'OVERALL']
        if config['kpis']['SM003']['enabled']:
            expected_kpis.insert(2, 'SM003')
        
        for kpi in expected_kpis:
            assert kpi in kpi_results, f"Missing expected KPI: {kpi}"
        
        print(f"\n✓ All expected KPIs present")
        
        return True, kpi_results
        
    except Exception as e:
        print(f"✗ KPI calculation failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_expected_results():
    """Display expected results from Power Query for validation."""
    print("\n" + "="*70)
    print("TEST 5: Expected Results (Power Query Baseline)")
    print("="*70)
    
    print("""
Expected KPI Values (from Power Query validation):

SM001 - Major Incident Management:
  - P1 Incidents: Should be ≤ target
  - P2 Incidents: Should be ≤ target
  - Target adherence: ≥ 95%

SM002 - Backlog Management:
  - Incidents aged > 10 days
  - Target adherence: ≥ 95%

SM003 - Request Aging (if enabled):
  - Requests aged > 30 days
  - Target adherence: ≥ 95%

SM004 - First Contact Resolution:
  - FCR rate calculation
  - Target: ≥ 70%

OVERALL:
  - Weighted score from all KPIs
  - Excellent: ≥ 90%
  - Good: 80-89%
  - Needs Improvement: < 80%

Note: Compare your results with these baselines to ensure accuracy.
    """)
    
    return True


def run_all_tests():
    """Run all tests in sequence."""
    print("="*70)
    print("KPI PIPELINE - TEST SUITE")
    print("="*70)
    
    results = {}
    
    # Test 1: Config loading
    success, config = test_config_loading()
    results['config_loading'] = success
    if not success:
        return results
    
    # Test 2: Data loading
    success, incidents, requests = test_data_loading(config)
    results['data_loading'] = success
    if not success:
        return results
    
    # Test 3: Data transformation
    success, incidents_transformed, requests_transformed = test_data_transformation(
        incidents, requests, config
    )
    results['data_transformation'] = success
    if not success:
        return results
    
    # Test 4: KPI calculations
    success, kpi_results = test_kpi_calculations(
        incidents_transformed, requests_transformed, config
    )
    results['kpi_calculations'] = success
    
    # Test 5: Expected results
    success = test_expected_results()
    results['expected_results'] = success
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASSED" if passed_test else "✗ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ {total - passed} TEST(S) FAILED")
    
    print("="*70)
    
    return results


if __name__ == "__main__":
    results = run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(results.values())
    sys.exit(0 if all_passed else 1)



