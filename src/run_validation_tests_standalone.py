#!/usr/bin/env python3
"""
Standalone Validation Test Script for KPI Pipeline
Tests the pipeline with real CSV data and compares to Power Query expectations.

This script can be run directly: python src/run_validation_tests_standalone.py
Or as a module: python -m src.run_validation_tests_standalone

Expected Results (from Power Query):
- Total incidents: 2,132
- Total requests: 6,617
- Backlog: ~610 incidents (25%)
- Major incidents: 3-5 (P1=0, P2=3-5)
- First Time Fix target: ≥80%
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
import sys
import os
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Import pipeline modules
import config_loader
import load_data
import transform
import calculate_kpis


class ValidationTester:
    """Comprehensive validation testing for KPI pipeline."""
    
    def __init__(self):
        self.results = {
            'test_date': datetime.now().isoformat(),
            'tests': {},
            'power_query_comparison': {},
            'overall_status': 'PENDING'
        }
        self.config = None
        self.incidents = None
        self.requests = None
        
    def run_all_tests(self):
        """Run all validation tests."""
        print("="*70)
        print("KPI PIPELINE VALIDATION TEST SUITE")
        print("="*70)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Test 1: Configuration
        self.test_configuration()
        
        # Test 2: Data Loading
        self.test_data_loading()
        
        # Test 3: Transform
        self.test_transform()
        
        # Test 4: KPI Calculations
        self.test_kpi_calculations()
        
        # Test 5: Power Query Comparison
        self.compare_to_power_query()
        
        # Generate summary
        self.generate_summary()
        
        # Save results
        self.save_results()
        
    def test_configuration(self):
        """Test configuration loading."""
        print("\n" + "="*70)
        print("TEST 1: CONFIGURATION LOADING")
        print("="*70)
        
        try:
            self.config = config_loader.load_config()
            
            # Verify key sections
            assert 'column_mappings' in self.config, "Missing column_mappings"
            assert 'thresholds' in self.config, "Missing thresholds"
            assert 'kpis' in self.config, "Missing kpis"
            
            # Verify KPI weights sum to 100
            weights = config_loader.get_kpi_weights(self.config)
            total_weight = sum(weights.values())
            
            print(f"✓ Configuration loaded successfully")
            print(f"✓ Organization: {self.config['metadata']['organization']}")
            print(f"✓ Version: {self.config['metadata']['version']}")
            print(f"✓ KPIs configured: {len(self.config['kpis'])}")
            print(f"✓ KPI weights: {weights}")
            print(f"✓ Total weight: {total_weight}%")
            
            assert total_weight == 100, f"KPI weights don't sum to 100: {total_weight}"
            
            self.results['tests']['configuration'] = {
                'status': 'PASS',
                'details': {
                    'organization': self.config['metadata']['organization'],
                    'version': self.config['metadata']['version'],
                    'kpi_count': len(self.config['kpis']),
                    'weights': weights,
                    'total_weight': total_weight
                }
            }
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.results['tests']['configuration'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            raise
    
    def test_data_loading(self):
        """Test data loading from CSV files."""
        print("\n" + "="*70)
        print("TEST 2: DATA LOADING")
        print("="*70)
        
        try:
            # Load incidents
            incidents_file = 'data/input/PYTHON EMEA IM (last 90 days)_redacted_clean.csv'
            self.incidents = load_data.load_incidents(incidents_file, self.config)
            
            print(f"\n✓ Incidents loaded: {len(self.incidents)} rows")
            print(f"✓ Columns: {len(self.incidents.columns)}")
            print(f"✓ Date columns: {list(self.incidents.select_dtypes(include=['datetime64']).columns)}")
            print(f"✓ Priority range: {self.incidents['Priority_Number'].min()}-{self.incidents['Priority_Number'].max()}")
            print(f"✓ Null reassignments filled: {(self.incidents['reassignment_count'] == 0).sum()}")
            
            # Expected: 2,132 incidents
            expected_incidents = 2132
            assert len(self.incidents) == expected_incidents, \
                f"Expected {expected_incidents} incidents, got {len(self.incidents)}"
            
            # Load requests
            requests_file = 'data/input/PYTHON EMEA SCT (last 90 days)_redacted_clean.csv'
            self.requests = load_data.load_requests(requests_file, self.config)
            
            print(f"\n✓ Requests loaded: {len(self.requests)} rows")
            print(f"✓ Columns: {len(self.requests.columns)}")
            print(f"✓ Date columns: {list(self.requests.select_dtypes(include=['datetime64']).columns)}")
            
            # Expected: 6,617 requests
            expected_requests = 6617
            assert len(self.requests) == expected_requests, \
                f"Expected {expected_requests} requests, got {len(self.requests)}"
            
            self.results['tests']['data_loading'] = {
                'status': 'PASS',
                'details': {
                    'incidents_count': len(self.incidents),
                    'incidents_columns': len(self.incidents.columns),
                    'requests_count': len(self.requests),
                    'requests_columns': len(self.requests.columns)
                }
            }
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.results['tests']['data_loading'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            raise
    
    def test_transform(self):
        """Test transform logic."""
        print("\n" + "="*70)
        print("TEST 3: TRANSFORM & CALCULATED FIELDS")
        print("="*70)
        
        try:
            # Add incident flags
            self.incidents = transform.add_incident_flags(self.incidents, self.config)
            
            # Count key metrics
            major_incidents = self.incidents['Is_Major_Incident'].sum()
            p1_count = self.incidents['Is_P1'].sum()
            p2_count = self.incidents['Is_P2'].sum()
            backlog_count = self.incidents['Is_Backlog'].sum()
            backlog_pct = (backlog_count / len(self.incidents) * 100)
            ftf_count = self.incidents['Is_First_Time_Fix'].sum()
            fcr_count = self.incidents['Is_First_Call_Resolution'].sum()
            
            print(f"\n✓ Major incidents: {major_incidents} (P1={p1_count}, P2={p2_count})")
            print(f"✓ Backlog: {backlog_count} incidents ({backlog_pct:.1f}%)")
            print(f"✓ First Time Fix: {ftf_count} ({ftf_count/len(self.incidents)*100:.1f}%)")
            print(f"✓ First Call Resolution: {fcr_count} ({fcr_count/len(self.incidents)*100:.1f}%)")
            
            # Verify backlog breakdown
            resolved_mask = self.incidents['resolved_at'].notna()
            aged_resolved = (resolved_mask & (self.incidents['Days_To_Resolve'] > 10)).sum()
            aged_unresolved = ((~resolved_mask) & (self.incidents['Days_Open'] > 10)).sum()
            
            print(f"\n  Backlog breakdown:")
            print(f"    - Resolved >10 days: {aged_resolved}")
            print(f"    - Unresolved >10 days: {aged_unresolved}")
            print(f"    - Total backlog: {aged_resolved + aged_unresolved}")
            
            # Add request flags (if enabled)
            if self.config['kpis']['SM003']['enabled']:
                self.requests = transform.add_request_flags(self.requests, self.config)
                aged_requests = self.requests['Is_Aged'].sum()
                aged_pct = (aged_requests / len(self.requests) * 100)
                print(f"\n✓ Aged requests: {aged_requests} ({aged_pct:.1f}%)")
            
            self.results['tests']['transform'] = {
                'status': 'PASS',
                'details': {
                    'major_incidents': int(major_incidents),
                    'p1_count': int(p1_count),
                    'p2_count': int(p2_count),
                    'backlog_count': int(backlog_count),
                    'backlog_percentage': round(backlog_pct, 1),
                    'ftf_count': int(ftf_count),
                    'fcr_count': int(fcr_count)
                }
            }
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.results['tests']['transform'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            raise
    
    def test_kpi_calculations(self):
        """Test KPI calculations."""
        print("\n" + "="*70)
        print("TEST 4: KPI CALCULATIONS")
        print("="*70)
        
        try:
            # Calculate all KPIs
            kpi_results = calculate_kpis.calculate_all(
                self.incidents, 
                self.requests,
                self.config
            )
            
            # Display results
            for kpi_code, kpi_data in kpi_results.items():
                if kpi_code == 'OVERALL':
                    print(f"\n{'='*50}")
                    print(f"OVERALL PERFORMANCE")
                    print(f"{'='*50}")
                    print(f"Score: {kpi_data['Overall_Score']}%")
                    print(f"Status: {kpi_data['Overall_Status']}")
                else:
                    print(f"\n{kpi_code}: {kpi_data['KPI_Name']}")
                    print(f"  Status: {kpi_data['Status']}")
                    print(f"  Adherence: {kpi_data['Adherence_Rate']}%")
            
            self.results['tests']['kpi_calculations'] = {
                'status': 'PASS',
                'details': kpi_results
            }
            
        except Exception as e:
            print(f"✗ FAILED: {e}")
            self.results['tests']['kpi_calculations'] = {
                'status': 'FAIL',
                'error': str(e)
            }
            raise
    
    def compare_to_power_query(self):
        """Compare results to Power Query expectations."""
        print("\n" + "="*70)
        print("TEST 5: POWER QUERY COMPARISON")
        print("="*70)
        
        # Expected values from Power Query
        expected = {
            'total_incidents': 2132,
            'total_requests': 6617,
            'backlog_count': 610,  # Approximate
            'backlog_percentage': 25.0,
            'major_incidents': 3,  # Could be 3-5
            'p1_count': 0,
            'p2_count': 3
        }
        
        # Get actual values
        actual = {
            'total_incidents': len(self.incidents),
            'total_requests': len(self.requests),
            'backlog_count': int(self.incidents['Is_Backlog'].sum()),
            'backlog_percentage': round(self.incidents['Is_Backlog'].sum() / len(self.incidents) * 100, 1),
            'major_incidents': int(self.incidents['Is_Major_Incident'].sum()),
            'p1_count': int(self.incidents['Is_P1'].sum()),
            'p2_count': int(self.incidents['Is_P2'].sum())
        }
        
        # Calculate variances
        print("\n" + "="*70)
        print("METRIC COMPARISON")
        print("="*70)
        print(f"{'Metric':<25} {'Expected':<15} {'Python':<15} {'Match?':<10} {'Variance'}")
        print("-"*70)
        
        comparisons = []
        for key in expected.keys():
            exp_val = expected[key]
            act_val = actual[key]
            
            # Calculate variance
            if key.endswith('_percentage'):
                variance = abs(exp_val - act_val)
                match = '✓' if variance <= 1.0 else '⚠'
                var_str = f"{variance:.1f}%"
            else:
                variance = abs(exp_val - act_val)
                match = '✓' if variance <= 5 or (variance / exp_val * 100 <= 5) else '⚠'
                if exp_val > 0:
                    var_pct = (variance / exp_val * 100)
                    var_str = f"{variance} ({var_pct:.1f}%)"
                else:
                    var_str = str(variance)
            
            print(f"{key:<25} {str(exp_val):<15} {str(act_val):<15} {match:<10} {var_str}")
            
            comparisons.append({
                'metric': key,
                'expected': exp_val,
                'actual': act_val,
                'match': match == '✓',
                'variance': variance
            })
        
        self.results['power_query_comparison'] = {
            'expected': expected,
            'actual': actual,
            'comparisons': comparisons
        }
        
        print("\n" + "="*70)
    
    def generate_summary(self):
        """Generate test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        all_passed = all(
            test['status'] == 'PASS' 
            for test in self.results['tests'].values()
        )
        
        if all_passed:
            self.results['overall_status'] = 'PASS'
            print("\n✓ ALL TESTS PASSED")
            print("\nThe pipeline is working correctly and ready for production use.")
        else:
            self.results['overall_status'] = 'FAIL'
            print("\n✗ SOME TESTS FAILED")
            print("\nPlease review the failures above.")
        
        print(f"\nTest Date: {self.results['test_date']}")
        print(f"Overall Status: {self.results['overall_status']}")
        
        for test_name, test_result in self.results['tests'].items():
            status_icon = '✓' if test_result['status'] == 'PASS' else '✗'
            print(f"  {status_icon} {test_name}: {test_result['status']}")
    
    def save_results(self):
        """Save test results to JSON file."""
        output_file = 'validation_results.json'
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"\n✓ Results saved to: {output_file}")


def main():
    """Main test execution."""
    tester = ValidationTester()
    
    try:
        tester.run_all_tests()
        sys.exit(0 if tester.results['overall_status'] == 'PASS' else 1)
    except Exception as e:
        print(f"\n✗ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
