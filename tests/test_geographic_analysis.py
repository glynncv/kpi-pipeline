"""
Unit tests for geographic_analysis module.

Tests all key functions:
- classify_volume_tier()
- identify_intervention_priority()
- calculate_country_metrics()
- calculate_location_metrics()
- get_top_performers()
- get_bottom_performers()
- analyze_geography()

Run with: python test_geographic_analysis.py
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import geographic_analysis


def create_test_config():
    """Create a sample configuration for testing."""
    return {
        'okr': {
            'geographic_analysis': {
                'volume_tiers': {
                    'tier_1': {
                        'threshold': 500,
                        'name': 'High Volume',
                        'description': '≥500 incidents/requests per quarter'
                    },
                    'tier_2': {
                        'threshold': 200,
                        'name': 'Medium Volume',
                        'description': '200-499 incidents/requests per quarter'
                    },
                    'tier_3': {
                        'threshold': 100,
                        'name': 'Standard Volume',
                        'description': '100-199 incidents/requests per quarter'
                    },
                    'tier_4': {
                        'threshold': 0,
                        'name': 'Low Volume',
                        'description': '<100 incidents/requests per quarter'
                    }
                }
            }
        },
        'kpis': {
            'SM002': {'targets': {'backlog_max': 0.10}},  # 10% max backlog
            'SM004': {'targets': {'fcr_min': 0.80}},       # 80% min FCR
        }
    }


def create_test_data():
    """Create sample incident data for testing."""
    return pd.DataFrame({
        'location_country': ['USA', 'USA', 'UK', 'UK', 'Germany', 'Germany', 'France', 'France'] * 20,
        'location': ['100', '200', '300', '400', '500', '600', '700', '800'] * 20,
        'location_u_site_name': [
            'New York HQ', 'Chicago Office', 'London Office', 'Manchester Site',
            'Berlin Office', 'Munich Site', 'Paris Office', 'Lyon Site'
        ] * 20,
        'Is_Backlog': [True, False, True, False, False, True, False, True] * 20,
        'Is_Major_Incident': [False, False, True, False, False, False, True, False] * 20,
        'Is_First_Call_Resolution': [True, True, False, True, True, False, True, False] * 20,
        'Is_First_Time_Fix': [True, True, True, True, True, True, True, False] * 20,
    })


def test_classify_volume_tier():
    """Test volume tier classification."""
    print("\nTest 1: classify_volume_tier()")
    print("-" * 60)
    
    config = create_test_config()
    
    test_cases = [
        (600, 'tier_1', 'High Volume'),
        (500, 'tier_1', 'High Volume'),
        (450, 'tier_2', 'Medium Volume'),
        (200, 'tier_2', 'Medium Volume'),
        (150, 'tier_3', 'Standard Volume'),
        (100, 'tier_3', 'Standard Volume'),
        (50, 'tier_4', 'Low Volume'),
        (1, 'tier_4', 'Low Volume'),
    ]
    
    passed = 0
    failed = 0
    
    for volume, expected_tier, expected_name in test_cases:
        result = geographic_analysis.classify_volume_tier(volume, config)
        
        if result['tier'] == expected_tier and result['tier_name'] == expected_name:
            print(f"✓ Volume {volume} -> {result['tier_name']} ({result['tier']})")
            passed += 1
        else:
            print(f"✗ Volume {volume} -> Expected {expected_tier}, got {result['tier']}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_identify_intervention_priority():
    """Test intervention priority identification."""
    print("\nTest 2: identify_intervention_priority()")
    print("-" * 60)
    
    config = create_test_config()
    
    test_cases = [
        # (tier, backlog_pct, fcr_rate, expected_priority)
        ('tier_1', 15.0, 70.0, 'Critical'),  # High volume + poor performance
        ('tier_1', 5.0, 85.0, 'High'),       # High volume, good performance
        ('tier_2', 15.0, 70.0, 'Critical'),  # High volume + poor performance
        ('tier_2', 5.0, 85.0, 'High'),       # High volume, good performance
        ('tier_3', 15.0, 70.0, 'High'),      # Low volume + poor performance
        ('tier_3', 5.0, 85.0, 'Standard'),   # Low volume, good performance
        ('tier_4', 15.0, 70.0, 'Monitor'),   # Low volume + poor performance
        ('tier_4', 5.0, 85.0, 'Standard'),   # Low volume, good performance
    ]
    
    passed = 0
    failed = 0
    
    for tier, backlog, fcr, expected in test_cases:
        row = pd.Series({
            'Volume_Tier': tier,
            'Backlog_Pct': backlog,
            'FCR_Rate': fcr
        })
        
        result = geographic_analysis.identify_intervention_priority(row, config)
        
        if result == expected:
            print(f"✓ {tier}, Backlog={backlog}%, FCR={fcr}% -> {result}")
            passed += 1
        else:
            print(f"✗ {tier}, Backlog={backlog}%, FCR={fcr}% -> Expected {expected}, got {result}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


def test_calculate_country_metrics():
    """Test country-level metric calculation."""
    print("\nTest 3: calculate_country_metrics()")
    print("-" * 60)
    
    config = create_test_config()
    data = create_test_data()
    
    result = geographic_analysis.calculate_country_metrics(
        data, 'location_country', config
    )
    
    print(f"Countries analyzed: {len(result)}")
    print(f"Columns: {', '.join(result.columns)}")
    print(f"\nCountry breakdown:")
    print(result[['Country', 'Total_Volume', 'Backlog_Pct', 'FCR_Rate', 'Volume_Tier_Name']].to_string(index=False))
    
    # Validation checks
    checks_passed = True
    
    # Check that all countries are present
    expected_countries = {'USA', 'UK', 'Germany', 'France'}
    actual_countries = set(result['Country'])
    if expected_countries == actual_countries:
        print("\n✓ All expected countries present")
    else:
        print(f"\n✗ Country mismatch: Expected {expected_countries}, got {actual_countries}")
        checks_passed = False
    
    # Check that volumes are correct (each country appears 40 times)
    if all(result['Total_Volume'] == 40):
        print("✓ Volume counts correct")
    else:
        print(f"✗ Volume counts incorrect: {result['Total_Volume'].tolist()}")
        checks_passed = False
    
    # Check that percentages are in valid range
    if all((result['Backlog_Pct'] >= 0) & (result['Backlog_Pct'] <= 100)):
        print("✓ Backlog percentages in valid range")
    else:
        print("✗ Backlog percentages out of range")
        checks_passed = False
    
    return checks_passed


def test_calculate_location_metrics():
    """Test location-level metric calculation."""
    print("\nTest 4: calculate_location_metrics()")
    print("-" * 60)
    
    config = create_test_config()
    data = create_test_data()
    
    result = geographic_analysis.calculate_location_metrics(
        data, 'location_u_site_name', 'location_country', config
    )
    
    print(f"Locations analyzed: {len(result)}")
    print(f"\nTop 5 locations:")
    print(result.head()[['Location', 'Country', 'Total_Volume', 'Volume_Tier_Name']].to_string(index=False))
    
    # Validation checks
    checks_passed = True
    
    # Check that all locations are present
    expected_count = 8  # 8 unique locations
    if len(result) == expected_count:
        print(f"\n✓ All {expected_count} locations present")
    else:
        print(f"\n✗ Location count incorrect: Expected {expected_count}, got {len(result)}")
        checks_passed = False
    
    # Check that each location has 20 records
    if all(result['Total_Volume'] == 20):
        print("✓ Volume counts correct (20 per location)")
    else:
        print(f"✗ Volume counts incorrect: {result['Total_Volume'].tolist()}")
        checks_passed = False
    
    return checks_passed


def test_top_bottom_performers():
    """Test top and bottom performer identification."""
    print("\nTest 5: get_top_performers() and get_bottom_performers()")
    print("-" * 60)
    
    config = create_test_config()
    data = create_test_data()
    
    location_df = geographic_analysis.calculate_location_metrics(
        data, 'location_u_site_name', 'location_country', config
    )
    
    # Get top 3 performers
    top = geographic_analysis.get_top_performers(location_df, n=3)
    print(f"\nTop 3 performers:")
    print(top[['Location', 'FCR_Rate', 'Backlog_Pct']].to_string(index=False))
    
    # Get bottom 3 performers
    bottom = geographic_analysis.get_bottom_performers(location_df, n=3)
    print(f"\nBottom 3 performers:")
    print(bottom[['Location', 'FCR_Rate', 'Backlog_Pct']].to_string(index=False))
    
    # Validation
    checks_passed = True
    
    if len(top) == 3:
        print("\n✓ Top performers count correct")
    else:
        print(f"\n✗ Top performers count incorrect: {len(top)}")
        checks_passed = False
    
    if len(bottom) == 3:
        print("✓ Bottom performers count correct")
    else:
        print(f"✗ Bottom performers count incorrect: {len(bottom)}")
        checks_passed = False
    
    # Check that top performers have higher FCR than bottom
    if top['FCR_Rate'].min() >= bottom['FCR_Rate'].max():
        print("✓ Top performers have better FCR than bottom performers")
    else:
        print("✗ FCR ranking may be incorrect")
        checks_passed = False
    
    return checks_passed


def test_intervention_summary():
    """Test intervention priority summary."""
    print("\nTest 6: get_intervention_summary()")
    print("-" * 60)
    
    config = create_test_config()
    data = create_test_data()
    
    location_df = geographic_analysis.calculate_location_metrics(
        data, 'location_u_site_name', 'location_country', config
    )
    
    summary = geographic_analysis.get_intervention_summary(location_df)
    
    print(f"Total locations: {summary['total_locations']}")
    print(f"Critical: {summary['critical_count']}")
    print(f"High: {summary['high_count']}")
    print(f"Monitor: {summary['monitor_count']}")
    print(f"Standard: {summary['standard_count']}")
    
    # Validation
    total = (summary['critical_count'] + summary['high_count'] + 
             summary['monitor_count'] + summary['standard_count'])
    
    if total == summary['total_locations']:
        print("\n✓ Priority counts sum to total locations")
        return True
    else:
        print(f"\n✗ Priority counts don't sum correctly: {total} != {summary['total_locations']}")
        return False


def test_analyze_geography():
    """Test main analysis function."""
    print("\nTest 7: analyze_geography() - Integration Test")
    print("-" * 60)
    
    config = create_test_config()
    incidents = create_test_data()
    requests = None  # Test with incidents only
    
    result = geographic_analysis.analyze_geography(incidents, requests, config)
    
    print(f"Keys in result: {list(result.keys())}")
    
    # Validation checks
    checks_passed = True
    
    expected_keys = ['country_summary', 'location_summary', 'top_performers', 
                     'bottom_performers', 'intervention_summary']
    
    for key in expected_keys:
        if key in result:
            print(f"✓ {key} present")
        else:
            print(f"✗ {key} missing")
            checks_passed = False
    
    # Check data types
    if isinstance(result['country_summary'], pd.DataFrame):
        print("✓ country_summary is DataFrame")
    else:
        print("✗ country_summary is not DataFrame")
        checks_passed = False
    
    if isinstance(result['intervention_summary'], dict):
        print("✓ intervention_summary is dict")
    else:
        print("✗ intervention_summary is not dict")
        checks_passed = False
    
    return checks_passed


def run_all_tests():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("GEOGRAPHIC ANALYSIS MODULE - UNIT TESTS")
    print("=" * 60)
    
    tests = [
        ("Volume Tier Classification", test_classify_volume_tier),
        ("Intervention Priority", test_identify_intervention_priority),
        ("Country Metrics", test_calculate_country_metrics),
        ("Location Metrics", test_calculate_location_metrics),
        ("Top/Bottom Performers", test_top_bottom_performers),
        ("Intervention Summary", test_intervention_summary),
        ("Full Analysis Integration", test_analyze_geography),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    exit(exit_code)
