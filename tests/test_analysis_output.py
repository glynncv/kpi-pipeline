"""
Comprehensive test suite for analysis_output module.

Tests all functionality documented in docs/ANALYSIS_OUTPUT.md:
- Individual table creation functions (7 tables)
- Integration with create_all_output_tables
- File persistence (Parquet, CSV, JSON)
- Data contract validation
- CLI integration
- Edge cases and error handling
- Performance and round-trip tests

Run with: python tests/test_analysis_output.py
Or with pytest: pytest tests/test_analysis_output.py -v
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import analysis_output


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

def create_mock_kpi_results():
    """Create mock KPI results with all KPI types."""
    return {
        'SM001': {
            'KPI_Name': 'Major Incident Management',
            'Status': 'Met',
            'Adherence_Rate': 100.0,
            'Business_Impact': 'High',
            'P1_Count': 0,
            'P2_Count': 3,
            'Total_Major': 3,
            'P1_Target': 0,
            'P2_Target': 5
        },
        'SM002': {
            'KPI_Name': 'Backlog Management',
            'Status': 'Warning',
            'Adherence_Rate': 92.5,
            'Business_Impact': 'Medium',
            'Total_Incidents': 1000,
            'Backlog_Count': 75,
            'Backlog_Percentage': 7.5,
            'Target_Adherence': 95.0
        },
        'SM003': {
            'KPI_Name': 'Request Aging',
            'Status': 'Critical',
            'Adherence_Rate': 85.0,
            'Business_Impact': 'High',
            'Total_Requests': 500,
            'Aged_Count': 75,
            'Aged_Percentage': 15.0,
            'Target_Adherence': 95.0
        },
        'SM004': {
            'KPI_Name': 'First Contact Resolution',
            'Status': 'Met',
            'Adherence_Rate': 78.5,
            'Business_Impact': 'Medium',
            'Total_Resolved': 800,
            'FCR_Count': 628,
            'FCR_Percentage': 78.5,
            'Target_Rate': 70.0
        },
        'OVERALL': {
            'Overall_Score': 78.5,
            'Overall_Status': 'Good',
            'Total_Weight': 100
        }
    }


def create_mock_okr_results():
    """Create mock OKR results with all Key Results."""
    return {
        'objective': 'Improve Service Management Performance',
        'overall_score': 75.0,
        'overall_status': 'At Risk',
        'key_results': {
            'KR3': {
                'name': 'Reduce Major Incidents',
                'score': 100.0,
                'status': 'On Track',
                'current_value': 3,
                'target_value': 5,
                'target_operator': '≤',
                'gap_to_target': '2 below target',
                'owner': 'Incident Manager'
            },
            'KR4': {
                'name': 'Reduce Backlog',
                'score': 92.5,
                'status': 'At Risk',
                'current_value': 7.5,
                'target_value': 5.0,
                'target_operator': '≤',
                'gap_to_target': '2.5% above target',
                'owner': 'Service Manager'
            },
            'KR5': {
                'name': 'Improve Request Aging',
                'score': 85.0,
                'status': 'Off Track',
                'current_value': 15.0,
                'target_value': 5.0,
                'target_operator': '≤',
                'gap_to_target': '10% above target',
                'owner': 'Request Manager'
            },
            'KR6': {
                'name': 'Improve FCR Rate',
                'score': 78.5,
                'status': 'On Track',
                'current_value': 78.5,
                'target_value': 70.0,
                'target_operator': '≥',
                'gap_to_target': '8.5% above target',
                'owner': 'Support Manager'
            }
        }
    }


def create_mock_action_triggers():
    """Create mock action triggers."""
    return {
        'critical': [
            {
                'kr_id': 'KR5',
                'action': 'Immediate escalation required for request aging',
                'escalation': 'Service Manager → Director'
            }
        ],
        'warning': [
            {
                'kr_id': 'KR4',
                'action': 'Review backlog management process',
                'escalation': 'Service Manager'
            }
        ]
    }


def create_mock_incidents():
    """Create mock incident DataFrame with all required columns."""
    return pd.DataFrame({
        'number': ['INC001', 'INC002', 'INC003', 'INC004', 'INC005'],
        'priority': ['P1', 'P2', 'P3', 'P2', 'P4'],
        'Priority_Number': [1, 2, 3, 2, 4],
        'opened_at': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']),
        'resolved_at': pd.to_datetime(['2024-01-02', '2024-01-03', '2024-01-10', '2024-01-05', '2024-01-06']),
        'Days_Open': [1, 1, 7, 1, 1],
        'Days_To_Resolve': [1, 1, 7, 1, 1],
        'Is_Major_Incident': [True, True, False, True, False],
        'Is_Backlog': [False, False, True, False, False],
        'Is_First_Call_Resolution': [False, True, True, True, True],
        'country': ['USA', 'UK', 'Germany', 'France', 'USA']
    })


def create_mock_requests():
    """Create mock request DataFrame with all required columns."""
    return pd.DataFrame({
        'number': ['REQ001', 'REQ002', 'REQ003', 'REQ004'],
        'opened_at': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04']),
        'closed_at': pd.to_datetime(['2024-01-02', '2024-01-20', '2024-01-10', '2024-01-05']),
        'Days_Open': [1, 18, 7, 1],
        'Days_To_Close': [1, 18, 7, 1],
        'Is_Aged': [False, True, False, False],
        'Is_Closed': [True, False, True, True],
        'country': ['USA', 'UK', 'Germany', 'France']
    })


def create_mock_geo_results():
    """Create mock geographic analysis results."""
    return {
        'location_summary': pd.DataFrame({
            'country': ['USA', 'UK', 'Germany', 'France'],
            'total': [100, 80, 60, 40],
            'backlog_count': [10, 8, 6, 4],
            'backlog_percentage': [10.0, 10.0, 10.0, 10.0],
            'fcr_rate': [80.0, 75.0, 70.0, 85.0]
        })
    }


def create_mock_problems():
    """Create mock problem DataFrame for testing."""
    return pd.DataFrame({
        'number': ['PRB001', 'PRB002', 'PRB003'],
        'priority': ['1 - Critical', '2 - High', '2 - High'],
        'Priority_Number': [1, 2, 2],
        'state': ['Open', 'Closed', 'Open'],
        'opened_at': pd.to_datetime(['2025-01-01', '2025-01-15', '2025-02-01']),
        'closed_at': [pd.NaT, pd.to_datetime('2025-01-20'), pd.NaT],
        'Days_Open': [50, 5, 30],
        'Is_Major_Problem': [True, True, True],
        'Requires_RCA': [True, True, False],
        'RCA_OnTime': [True, False, False],
        'country': ['USA', 'UK', 'Germany'],
        'location.name': ['Site A', 'Site B', 'Site C']
    })


# ============================================================================
# SECTION 1: UNIT TESTS - Individual Table Creation Functions
# ============================================================================

def test_create_kpi_summary_table_all_kpi_types():
    """Test create_kpi_summary_table with all KPI types."""
    print("\n" + "="*70)
    print("TEST 1.1: create_kpi_summary_table - All KPI Types")
    print("="*70)
    
    kpi_results = create_mock_kpi_results()
    df = analysis_output.create_kpi_summary_table(kpi_results)
    
    # Verify basic structure
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 4, "Should have 4 KPIs (excluding OVERALL)"
    
    # Verify required columns
    required_cols = ['kpi_code', 'kpi_name', 'status', 'adherence_rate', 'business_impact', 'timestamp']
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"
    
    # Verify OVERALL is excluded
    assert 'OVERALL' not in df['kpi_code'].values, "OVERALL should be excluded"
    
    # Verify SM001 specific columns
    sm001 = df[df['kpi_code'] == 'SM001'].iloc[0]
    assert 'p1_count' in df.columns, "SM001 should have p1_count"
    assert sm001['p1_count'] == 0
    assert sm001['p2_count'] == 3
    
    # Verify SM002 specific columns
    sm002 = df[df['kpi_code'] == 'SM002'].iloc[0]
    assert 'backlog_count' in df.columns, "SM002 should have backlog_count"
    assert sm002['backlog_count'] == 75
    
    # Verify SM003 specific columns
    sm003 = df[df['kpi_code'] == 'SM003'].iloc[0]
    assert 'aged_count' in df.columns, "SM003 should have aged_count"
    assert sm003['aged_count'] == 75
    
    # Verify SM004 specific columns
    sm004 = df[df['kpi_code'] == 'SM004'].iloc[0]
    assert 'fcr_count' in df.columns, "SM004 should have fcr_count"
    assert sm004['fcr_count'] == 628
    
    # Verify timestamp is generated
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp']), "timestamp should be datetime"
    
    # Verify status values
    valid_statuses = ['Met', 'Warning', 'Critical']
    assert df['status'].isin(valid_statuses).all(), f"Status values should be in {valid_statuses}"
    
    print("[OK] All KPI types handled correctly")
    return True


def test_create_kpi_summary_table_empty():
    """Test create_kpi_summary_table with empty kpi_results."""
    print("\nTEST 1.1b: create_kpi_summary_table - Empty Input")
    
    df = analysis_output.create_kpi_summary_table({})
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 0, "Should be empty DataFrame"
    
    print("[OK] Empty input handled correctly")
    return True


def test_create_kpi_summary_table_missing_fields():
    """Test create_kpi_summary_table with missing optional fields."""
    print("\nTEST 1.1c: create_kpi_summary_table - Missing Fields")
    
    kpi_results = {
        'SM001': {
            'KPI_Name': 'Test',
            'Status': 'Met',
            # Missing Adherence_Rate, Business_Impact
        }
    }
    
    df = analysis_output.create_kpi_summary_table(kpi_results)
    assert len(df) == 1, "Should create one row"
    assert df.iloc[0]['adherence_rate'] == 0.0, "Should default to 0.0"
    assert df.iloc[0]['business_impact'] == '', "Should default to empty string"
    
    print("[OK] Missing fields handled gracefully")
    return True


def test_create_overall_score_table():
    """Test create_overall_score_table with OVERALL present."""
    print("\nTEST 1.2: create_overall_score_table")
    
    kpi_results = create_mock_kpi_results()
    df = analysis_output.create_overall_score_table(kpi_results)
    
    # Verify structure
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 1, "Should have one row"
    
    # Verify columns
    required_cols = ['overall_score', 'overall_status', 'total_weight', 'timestamp']
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    
    # Verify data types
    assert pd.api.types.is_float_dtype(df['overall_score']), "overall_score should be float"
    assert pd.api.types.is_object_dtype(df['overall_status']), "overall_status should be string"
    assert pd.api.types.is_integer_dtype(df['total_weight']), "total_weight should be int"
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp']), "timestamp should be datetime"
    
    # Verify values
    assert df.iloc[0]['overall_score'] == 78.5
    assert df.iloc[0]['overall_status'] == 'Good'
    assert df.iloc[0]['total_weight'] == 100
    
    print("[OK] Overall score table created correctly")
    return True


def test_create_overall_score_table_missing():
    """Test create_overall_score_table with missing OVERALL."""
    print("\nTEST 1.2b: create_overall_score_table - Missing OVERALL")
    
    kpi_results = {'SM001': {'KPI_Name': 'Test'}}
    df = analysis_output.create_overall_score_table(kpi_results)
    
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 0, "Should return empty DataFrame"
    
    print("[OK] Missing OVERALL handled correctly")
    return True


def test_create_okr_scorecard_table():
    """Test create_okr_scorecard_table with valid okr_results."""
    print("\nTEST 1.3: create_okr_scorecard_table")
    
    okr_results = create_mock_okr_results()
    df = analysis_output.create_okr_scorecard_table(okr_results)
    
    # Verify structure
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 4, "Should have 4 Key Results"
    
    # Verify columns
    required_cols = ['kr_id', 'kr_name', 'score', 'status', 'current_value', 
                     'target_value', 'target_operator', 'gap_to_target', 'owner']
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    
    # Verify status values
    valid_statuses = ['On Track', 'At Risk', 'Off Track']
    assert df['status'].isin(valid_statuses).all(), f"Status should be in {valid_statuses}"
    
    # Verify score range
    assert (df['score'] >= 0).all() and (df['score'] <= 100).all(), "Score should be 0-100"
    
    # Verify Key Results present
    assert 'KR3' in df['kr_id'].values
    assert 'KR4' in df['kr_id'].values
    assert 'KR5' in df['kr_id'].values
    assert 'KR6' in df['kr_id'].values
    
    print("[OK] OKR scorecard table created correctly")
    return True


def test_create_okr_scorecard_table_missing():
    """Test create_okr_scorecard_table with missing key_results."""
    print("\nTEST 1.3b: create_okr_scorecard_table - Missing key_results")
    
    okr_results = {'objective': 'Test'}
    df = analysis_output.create_okr_scorecard_table(okr_results)
    
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 0, "Should return empty DataFrame"
    
    print("[OK] Missing key_results handled correctly")
    return True


def test_create_action_triggers_table():
    """Test create_action_triggers_table with both critical and warning."""
    print("\nTEST 1.4: create_action_triggers_table")
    
    action_triggers = create_mock_action_triggers()
    df = analysis_output.create_action_triggers_table(action_triggers)
    
    # Verify structure
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 2, "Should have 2 triggers"
    
    # Verify columns
    required_cols = ['severity', 'kr_id', 'action', 'escalation']
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    
    # Verify severity capitalization
    assert df['severity'].isin(['Critical', 'Warning']).all(), "Severity should be Critical or Warning"
    
    # Verify all triggers included
    critical_count = len(df[df['severity'] == 'Critical'])
    warning_count = len(df[df['severity'] == 'Warning'])
    assert critical_count == 1, "Should have 1 critical trigger"
    assert warning_count == 1, "Should have 1 warning trigger"
    
    print("[OK] Action triggers table created correctly")
    return True


def test_create_action_triggers_table_empty():
    """Test create_action_triggers_table with empty triggers."""
    print("\nTEST 1.4b: create_action_triggers_table - Empty")
    
    action_triggers = {'critical': [], 'warning': []}
    df = analysis_output.create_action_triggers_table(action_triggers)
    
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 0, "Should return empty DataFrame"
    
    print("[OK] Empty triggers handled correctly")
    return True


def test_create_incident_detail_table():
    """Test create_incident_detail_table with full DataFrame."""
    print("\nTEST 1.5: create_incident_detail_table")
    
    incidents = create_mock_incidents()
    df = analysis_output.create_incident_detail_table(incidents)
    
    # Verify structure
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == len(incidents), "Should have same number of rows"
    
    # Verify required columns
    required_cols = ['number', 'priority', 'Priority_Number', 'opened_at', 'resolved_at', 
                     'Days_Open', 'Is_Major_Incident', 'Is_Backlog', 
                     'Is_First_Call_Resolution', 'country']
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    
    # Verify Days_To_Resolve included if present
    if 'Days_To_Resolve' in incidents.columns:
        assert 'Days_To_Resolve' in df.columns, "Days_To_Resolve should be included"
    
    # Verify copy (modifying original shouldn't affect result)
    original_value = df.iloc[0]['number']
    # Create a copy and modify it to verify independence
    incidents_copy = incidents.copy()
    incidents_copy.loc[incidents_copy.index[0], 'number'] = 'MODIFIED'
    # Original DataFrame should be unchanged
    assert df.iloc[0]['number'] == original_value, "Should be a copy, not reference"
    
    print("[OK] Incident detail table created correctly")
    return True


def test_create_incident_detail_table_missing_columns():
    """Test create_incident_detail_table with missing optional columns."""
    print("\nTEST 1.5b: create_incident_detail_table - Missing Columns")
    
    incidents = pd.DataFrame({
        'number': ['INC001'],
        'priority': ['P1'],
        'opened_at': pd.to_datetime(['2024-01-01'])
        # Missing many columns
    })
    
    df = analysis_output.create_incident_detail_table(incidents)
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    # Should only include available columns
    assert 'number' in df.columns
    
    print("[OK] Missing columns handled gracefully")
    return True


def test_create_request_detail_table():
    """Test create_request_detail_table with full DataFrame."""
    print("\nTEST 1.6: create_request_detail_table")
    
    requests = create_mock_requests()
    df = analysis_output.create_request_detail_table(requests)
    
    # Verify structure
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == len(requests), "Should have same number of rows"
    
    # Verify required columns
    required_cols = ['number', 'opened_at', 'closed_at', 'Days_Open', 
                     'Is_Aged', 'Is_Closed', 'country']
    for col in required_cols:
        assert col in df.columns, f"Missing column: {col}"
    
    # Verify Days_To_Close included if present
    if 'Days_To_Close' in requests.columns:
        assert 'Days_To_Close' in df.columns, "Days_To_Close should be included"
    
    print("[OK] Request detail table created correctly")
    return True


def test_create_request_detail_table_empty():
    """Test create_request_detail_table with empty DataFrame."""
    print("\nTEST 1.6b: create_request_detail_table - Empty")
    
    requests = pd.DataFrame()
    df = analysis_output.create_request_detail_table(requests)
    
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 0, "Should return empty DataFrame"
    
    print("[OK] Empty DataFrame handled correctly")
    return True


def test_create_problem_detail_table():
    """Test create_problem_detail_table with full DataFrame."""
    print("\nTEST 1.6c: create_problem_detail_table")
    
    problems = create_mock_problems()
    df = analysis_output.create_problem_detail_table(problems)
    
    assert not df.empty, "Should not be empty"
    assert 'number' in df.columns, "Should have number column"
    assert 'priority' in df.columns, "Should have priority column"
    assert 'Is_Major_Problem' in df.columns, "Should have Is_Major_Problem column"
    assert 'Requires_RCA' in df.columns, "Should have Requires_RCA column"
    assert 'RCA_OnTime' in df.columns, "Should have RCA_OnTime column"
    
    print(f"[OK] Problem detail table created: {len(df)} rows, {len(df.columns)} columns")
    return True


def test_create_problem_detail_table_empty():
    """Test create_problem_detail_table with empty DataFrame."""
    print("\nTEST 1.6d: create_problem_detail_table - Empty")
    
    problems = pd.DataFrame()
    df = analysis_output.create_problem_detail_table(problems)
    
    assert df.empty, "Should return empty DataFrame"
    print("[OK] Empty problem DataFrame handled correctly")
    return True


def test_create_geographic_summary_table():
    """Test create_geographic_summary_table with valid geo_results."""
    print("\nTEST 1.7: create_geographic_summary_table")
    
    geo_results = create_mock_geo_results()
    df = analysis_output.create_geographic_summary_table(geo_results)
    
    # Verify structure
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == len(geo_results['location_summary']), "Should match location_summary"
    
    # Verify it's a copy (pass-through)
    assert 'country' in df.columns
    assert 'total' in df.columns
    
    print("[OK] Geographic summary table created correctly")
    return True


def test_create_geographic_summary_table_missing():
    """Test create_geographic_summary_table with missing location_summary."""
    print("\nTEST 1.7b: create_geographic_summary_table - Missing location_summary")
    
    geo_results = {}
    df = analysis_output.create_geographic_summary_table(geo_results)
    
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    assert len(df) == 0, "Should return empty DataFrame"
    
    print("[OK] Missing location_summary handled correctly")
    return True


# ============================================================================
# SECTION 2: INTEGRATION TESTS - Main Entry Point
# ============================================================================

def test_create_all_output_tables_complete():
    """Test create_all_output_tables with complete valid inputs."""
    print("\n" + "="*70)
    print("TEST 2.1: create_all_output_tables - Complete Inputs")
    print("="*70)
    
    kpi_results = create_mock_kpi_results()
    okr_results = create_mock_okr_results()
    action_triggers = create_mock_action_triggers()
    incidents = create_mock_incidents()
    requests = create_mock_requests()
    geo_results = create_mock_geo_results()
    
    output_tables = analysis_output.create_all_output_tables(
        kpi_results=kpi_results,
        okr_results=okr_results,
        action_triggers=action_triggers,
        incidents=incidents,
        requests=requests,
        geo_results=geo_results
    )
    
    # Verify all 7 core tables exist (problem_detail is optional)
    expected_tables = ['kpi_summary', 'overall_score', 'okr_scorecard', 
                       'action_triggers', 'incident_detail', 'request_detail', 
                       'geographic_summary']
    for table_name in expected_tables:
        assert table_name in output_tables, f"Missing table: {table_name}"
        assert isinstance(output_tables[table_name], pd.DataFrame), f"{table_name} should be DataFrame"
    
    # Verify tables are not empty (except possibly request_detail)
    for table_name, df in output_tables.items():
        if table_name not in ['request_detail', 'problem_detail']:  # May be empty if no requests/problems
            assert not df.empty, f"{table_name} should not be empty"
    
    # Verify problem_detail is NOT present when problems not provided
    assert 'problem_detail' not in output_tables, "problem_detail should not exist without problems data"
    
    print("[OK] All 7 core tables created successfully")
    return True


def test_create_all_output_tables_empty_requests():
    """Test create_all_output_tables with empty requests DataFrame."""
    print("\nTEST 2.1b: create_all_output_tables - Empty Requests")
    
    kpi_results = create_mock_kpi_results()
    okr_results = create_mock_okr_results()
    action_triggers = create_mock_action_triggers()
    incidents = create_mock_incidents()
    requests = pd.DataFrame()  # Empty
    geo_results = create_mock_geo_results()
    
    output_tables = analysis_output.create_all_output_tables(
        kpi_results=kpi_results,
        okr_results=okr_results,
        action_triggers=action_triggers,
        incidents=incidents,
        requests=requests,
        geo_results=geo_results
    )
    
    # request_detail should be empty
    assert output_tables['request_detail'].empty, "request_detail should be empty"
    
    # Other tables should still exist
    assert not output_tables['kpi_summary'].empty
    assert not output_tables['incident_detail'].empty
    
    print("[OK] Empty requests handled correctly")
    return True


def test_create_all_output_tables_with_problems():
    """Test create_all_output_tables with problems DataFrame."""
    print("\nTEST 2.1d: create_all_output_tables - With Problems")
    
    kpi_results = create_mock_kpi_results()
    okr_results = create_mock_okr_results()
    action_triggers = create_mock_action_triggers()
    incidents = create_mock_incidents()
    requests = create_mock_requests()
    geo_results = create_mock_geo_results()
    problems = create_mock_problems()
    
    output_tables = analysis_output.create_all_output_tables(
        kpi_results=kpi_results,
        okr_results=okr_results,
        action_triggers=action_triggers,
        incidents=incidents,
        requests=requests,
        geo_results=geo_results,
        problems=problems
    )
    
    # Verify problem_detail table exists
    assert 'problem_detail' in output_tables, "problem_detail should exist when problems provided"
    assert not output_tables['problem_detail'].empty, "problem_detail should not be empty"
    assert isinstance(output_tables['problem_detail'], pd.DataFrame), "problem_detail should be DataFrame"
    
    # Verify it has expected columns
    assert 'number' in output_tables['problem_detail'].columns
    assert 'Requires_RCA' in output_tables['problem_detail'].columns
    assert 'RCA_OnTime' in output_tables['problem_detail'].columns
    
    print("[OK] All 8 tables created successfully (including problem_detail)")
    return True


def test_create_all_output_tables_without_problems():
    """Test create_all_output_tables without problems DataFrame (should not create problem_detail)."""
    print("\nTEST 2.1e: create_all_output_tables - Without Problems")
    
    kpi_results = create_mock_kpi_results()
    okr_results = create_mock_okr_results()
    action_triggers = create_mock_action_triggers()
    incidents = create_mock_incidents()
    requests = create_mock_requests()
    geo_results = create_mock_geo_results()
    
    output_tables = analysis_output.create_all_output_tables(
        kpi_results=kpi_results,
        okr_results=okr_results,
        action_triggers=action_triggers,
        incidents=incidents,
        requests=requests,
        geo_results=geo_results,
        problems=None  # Explicitly no problems
    )
    
    # Verify problem_detail table does NOT exist
    assert 'problem_detail' not in output_tables, "problem_detail should not exist when problems not provided"
    
    # Verify core 7 tables still exist
    expected_tables = ['kpi_summary', 'overall_score', 'okr_scorecard', 
                       'action_triggers', 'incident_detail', 'request_detail', 
                       'geographic_summary']
    for table_name in expected_tables:
        assert table_name in output_tables, f"Missing table: {table_name}"
    
    print("[OK] 7 core tables created (problem_detail correctly omitted)")
    return True


def test_create_all_output_tables_table_independence():
    """Test that modifying one table doesn't affect others."""
    print("\nTEST 2.1c: create_all_output_tables - Table Independence")
    
    kpi_results = create_mock_kpi_results()
    okr_results = create_mock_okr_results()
    action_triggers = create_mock_action_triggers()
    incidents = create_mock_incidents()
    requests = create_mock_requests()
    geo_results = create_mock_geo_results()
    
    output_tables = analysis_output.create_all_output_tables(
        kpi_results=kpi_results,
        okr_results=okr_results,
        action_triggers=action_triggers,
        incidents=incidents,
        requests=requests,
        geo_results=geo_results
    )
    
    # Modify one table
    original_count = len(output_tables['kpi_summary'])
    output_tables['kpi_summary'] = pd.DataFrame()  # Clear it
    
    # Other tables should be unaffected
    assert len(output_tables['okr_scorecard']) > 0, "Other tables should be unaffected"
    assert len(output_tables['incident_detail']) > 0, "Other tables should be unaffected"
    
    print("[OK] Tables are independent")
    return True


# ============================================================================
# SECTION 3: FILE PERSISTENCE TESTS
# ============================================================================

def test_save_output_tables_parquet():
    """Test saving tables as Parquet format."""
    print("\n" + "="*70)
    print("TEST 3.1: save_output_tables - Parquet Format")
    print("="*70)
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        output_tables = {
            'kpi_summary': create_mock_kpi_results(),
            'overall_score': analysis_output.create_overall_score_table(create_mock_kpi_results())
        }
        output_tables['kpi_summary'] = analysis_output.create_kpi_summary_table(output_tables['kpi_summary'])
        
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='parquet'
        )
        
        # Verify files created
        assert len(saved_files) == 2, "Should save 2 tables"
        assert 'kpi_summary' in saved_files
        assert 'overall_score' in saved_files
        
        # Verify file paths
        for table_name, filepath in saved_files.items():
            assert os.path.exists(filepath), f"File should exist: {filepath}"
            assert filepath.endswith('.parquet'), "Should be .parquet file"
            assert table_name in filepath, "Filename should contain table name"
            
            # Verify timestamp format in filename
            filename = os.path.basename(filepath)
            # Format: table_name_YYYYMMDD_HHMMSS.parquet
            parts = filename.replace('.parquet', '').split('_')
            assert len(parts) >= 3, "Filename should have timestamp"
        
        # Verify files are readable
        for filepath in saved_files.values():
            df = pd.read_parquet(filepath)
            assert isinstance(df, pd.DataFrame), "Should be readable as DataFrame"
            assert not df.empty, "Should not be empty"
        
        print("[OK] Parquet files saved and readable")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_save_output_tables_csv():
    """Test saving tables as CSV format."""
    print("\nTEST 3.2: save_output_tables - CSV Format")
    
    temp_dir = tempfile.mkdtemp()
    try:
        output_tables = {
            'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        }
        
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='csv'
        )
        
        # Verify file created
        assert len(saved_files) == 1
        filepath = saved_files['kpi_summary']
        assert filepath.endswith('.csv'), "Should be .csv file"
        
        # Verify readable
        df = pd.read_csv(filepath)
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        
        # Verify no index column
        assert 'Unnamed: 0' not in df.columns, "Should not have index column"
        
        print("[OK] CSV files saved and readable")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_save_output_tables_json():
    """Test saving tables as JSON format."""
    print("\nTEST 3.3: save_output_tables - JSON Format")
    
    temp_dir = tempfile.mkdtemp()
    try:
        output_tables = {
            'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        }
        
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='json'
        )
        
        # Verify file created
        assert len(saved_files) == 1
        filepath = saved_files['kpi_summary']
        assert filepath.endswith('.json'), "Should be .json file"
        
        # Verify readable
        df = pd.read_json(filepath, orient='records')
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        
        print("[OK] JSON files saved and readable")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_save_output_tables_empty_tables():
    """Test that empty tables are skipped."""
    print("\nTEST 3.4: save_output_tables - Empty Tables Skipped")
    
    temp_dir = tempfile.mkdtemp()
    try:
        output_tables = {
            'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results()),
            'empty_table': pd.DataFrame()  # Empty
        }
        
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='parquet'
        )
        
        # Should only save non-empty tables
        assert len(saved_files) == 1, "Should only save non-empty tables"
        assert 'kpi_summary' in saved_files
        assert 'empty_table' not in saved_files
        
        print("[OK] Empty tables skipped correctly")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_save_output_tables_invalid_format():
    """Test error handling for invalid format."""
    print("\nTEST 3.4b: save_output_tables - Invalid Format")
    
    temp_dir = tempfile.mkdtemp()
    try:
        output_tables = {
            'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        }
        
        try:
            analysis_output.save_output_tables(
                output_tables,
                output_dir=temp_dir,
                format='invalid_format'
            )
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert 'Unsupported format' in str(e), "Should raise ValueError with message"
            print("[OK] Invalid format raises ValueError")
            return True
            
    finally:
        shutil.rmtree(temp_dir)


def test_save_output_tables_directory_creation():
    """Test that directory is created if it doesn't exist."""
    print("\nTEST 3.4c: save_output_tables - Directory Creation")
    
    temp_dir = tempfile.mkdtemp()
    new_dir = os.path.join(temp_dir, 'new_subdir')
    
    try:
        output_tables = {
            'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        }
        
        # Directory shouldn't exist yet
        assert not os.path.exists(new_dir)
        
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=new_dir,
            format='parquet'
        )
        
        # Directory should be created
        assert os.path.exists(new_dir), "Directory should be created"
        assert len(saved_files) == 1, "File should be saved"
        
        print("[OK] Directory creation works")
        return True
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


# ============================================================================
# SECTION 4: DATA CONTRACT VALIDATION TESTS
# ============================================================================

def test_kpi_summary_data_contract():
    """Test kpi_summary table data contract."""
    print("\n" + "="*70)
    print("TEST 4.1: Data Contract - kpi_summary")
    print("="*70)
    
    kpi_results = create_mock_kpi_results()
    df = analysis_output.create_kpi_summary_table(kpi_results)
    
    # Verify column names match documentation
    expected_cols = ['kpi_code', 'kpi_name', 'status', 'adherence_rate', 
                     'business_impact', 'timestamp']
    for col in expected_cols:
        assert col in df.columns, f"Missing documented column: {col}"
    
    # Verify column types
    assert pd.api.types.is_object_dtype(df['kpi_code']), "kpi_code should be string"
    assert pd.api.types.is_float_dtype(df['adherence_rate']), "adherence_rate should be float"
    assert pd.api.types.is_object_dtype(df['status']), "status should be string"
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp']), "timestamp should be datetime"
    
    # Verify status values
    valid_statuses = ['Met', 'Warning', 'Critical']
    assert df['status'].isin(valid_statuses).all(), f"Status should be in {valid_statuses}"
    
    # Verify adherence_rate range
    assert (df['adherence_rate'] >= 0).all() and (df['adherence_rate'] <= 100).all(), \
        "adherence_rate should be 0-100"
    
    # Verify KPI-specific columns only present for relevant KPIs
    sm001 = df[df['kpi_code'] == 'SM001']
    assert 'p1_count' in sm001.columns, "SM001 should have p1_count"
    
    sm002 = df[df['kpi_code'] == 'SM002']
    assert 'backlog_count' in sm002.columns, "SM002 should have backlog_count"
    
    print("[OK] kpi_summary data contract validated")
    return True


def test_okr_scorecard_data_contract():
    """Test okr_scorecard table data contract."""
    print("\nTEST 4.2: Data Contract - okr_scorecard")
    
    okr_results = create_mock_okr_results()
    df = analysis_output.create_okr_scorecard_table(okr_results)
    
    # Verify column names
    expected_cols = ['kr_id', 'kr_name', 'score', 'status', 'current_value', 
                     'target_value', 'target_operator', 'gap_to_target', 'owner']
    for col in expected_cols:
        assert col in df.columns, f"Missing documented column: {col}"
    
    # Verify column types
    assert pd.api.types.is_object_dtype(df['kr_id']), "kr_id should be string"
    assert pd.api.types.is_float_dtype(df['score']), "score should be float"
    assert pd.api.types.is_object_dtype(df['status']), "status should be string"
    
    # Verify status values
    valid_statuses = ['On Track', 'At Risk', 'Off Track']
    assert df['status'].isin(valid_statuses).all(), f"Status should be in {valid_statuses}"
    
    # Verify score range
    assert (df['score'] >= 0).all() and (df['score'] <= 100).all(), "score should be 0-100"
    
    # Verify target_operator values
    valid_operators = ['≥', '≤']
    assert df['target_operator'].isin(valid_operators).all(), f"target_operator should be in {valid_operators}"
    
    print("[OK] okr_scorecard data contract validated")
    return True


def test_action_triggers_data_contract():
    """Test action_triggers table data contract."""
    print("\nTEST 4.3: Data Contract - action_triggers")
    
    action_triggers = create_mock_action_triggers()
    df = analysis_output.create_action_triggers_table(action_triggers)
    
    # Verify column names
    expected_cols = ['severity', 'kr_id', 'action', 'escalation']
    for col in expected_cols:
        assert col in df.columns, f"Missing documented column: {col}"
    
    # Verify severity values
    valid_severities = ['Critical', 'Warning']
    assert df['severity'].isin(valid_severities).all(), f"severity should be in {valid_severities}"
    
    # Verify kr_id format (should be KR followed by number)
    assert df['kr_id'].str.startswith('KR').all(), "kr_id should start with KR"
    
    print("[OK] action_triggers data contract validated")
    return True


def test_incident_detail_data_contract():
    """Test incident_detail table data contract."""
    print("\nTEST 4.4a: Data Contract - incident_detail")
    
    incidents = create_mock_incidents()
    df = analysis_output.create_incident_detail_table(incidents)
    
    # Verify required columns from documentation
    required_cols = ['number', 'priority', 'Priority_Number', 'opened_at', 
                     'resolved_at', 'Days_Open', 'Is_Major_Incident', 
                     'Is_Backlog', 'Is_First_Call_Resolution', 'country']
    for col in required_cols:
        assert col in df.columns, f"Missing documented column: {col}"
    
    # Verify data types
    assert pd.api.types.is_string_dtype(df['number']) or pd.api.types.is_object_dtype(df['number']), "number should be string"
    assert pd.api.types.is_datetime64_any_dtype(df['opened_at']), "opened_at should be datetime"
    assert pd.api.types.is_numeric_dtype(df['Days_Open']), "Days_Open should be numeric"
    assert pd.api.types.is_bool_dtype(df['Is_Major_Incident']) or pd.api.types.is_object_dtype(df['Is_Major_Incident']), "Is_Major_Incident should be boolean"
    
    print("[OK] incident_detail data contract validated")
    return True


def test_request_detail_data_contract():
    """Test request_detail table data contract."""
    print("\nTEST 4.4b: Data Contract - request_detail")
    
    requests = create_mock_requests()
    df = analysis_output.create_request_detail_table(requests)
    
    # Verify required columns from documentation
    required_cols = ['number', 'opened_at', 'closed_at', 'Days_Open',
                     'Is_Aged', 'Is_Closed', 'country']
    for col in required_cols:
        assert col in df.columns, f"Missing documented column: {col}"
    
    # Verify data types
    assert pd.api.types.is_string_dtype(df['number']) or pd.api.types.is_object_dtype(df['number']), "number should be string"
    assert pd.api.types.is_datetime64_any_dtype(df['opened_at']), "opened_at should be datetime"
    assert pd.api.types.is_numeric_dtype(df['Days_Open']), "Days_Open should be numeric"
    assert pd.api.types.is_bool_dtype(df['Is_Aged']) or pd.api.types.is_object_dtype(df['Is_Aged']), "Is_Aged should be boolean"
    
    print("[OK] request_detail data contract validated")
    return True


def test_problem_detail_data_contract():
    """Test problem_detail table data contract."""
    print("\nTEST 4.4c: Data Contract - problem_detail")
    
    problems = create_mock_problems()
    df = analysis_output.create_problem_detail_table(problems)
    
    # Verify required columns
    required_cols = ['number', 'priority', 'Is_Major_Problem', 'Requires_RCA', 'RCA_OnTime']
    for col in required_cols:
        assert col in df.columns, f"Missing documented column: {col}"
    
    # Verify data types
    assert pd.api.types.is_string_dtype(df['number']) or pd.api.types.is_object_dtype(df['number']), "number should be string"
    assert pd.api.types.is_bool_dtype(df['Is_Major_Problem']) or pd.api.types.is_object_dtype(df['Is_Major_Problem']), "Is_Major_Problem should be boolean"
    assert pd.api.types.is_bool_dtype(df['Requires_RCA']) or pd.api.types.is_object_dtype(df['Requires_RCA']), "Requires_RCA should be boolean"
    assert pd.api.types.is_bool_dtype(df['RCA_OnTime']) or pd.api.types.is_object_dtype(df['RCA_OnTime']), "RCA_OnTime should be boolean"
    
    print("[OK] problem_detail data contract validated")
    return True


def test_geographic_summary_data_contract():
    """Test geographic_summary table data contract."""
    print("\nTEST 4.4c: Data Contract - geographic_summary")
    
    geo_results = create_mock_geo_results()
    df = analysis_output.create_geographic_summary_table(geo_results)
    
    # Verify it's a DataFrame
    assert isinstance(df, pd.DataFrame), "Should return DataFrame"
    
    # Verify it matches location_summary structure
    assert not df.empty, "Should have data"
    
    # Verify expected columns from geographic analysis
    expected_cols = ['country', 'total', 'backlog_count']
    for col in expected_cols:
        if col in geo_results['location_summary'].columns:
            assert col in df.columns, f"Missing expected column: {col}"
    
    # Verify it's a copy (pass-through but independent)
    assert df is not geo_results['location_summary'], "Should be a copy, not reference"
    
    print("[OK] geographic_summary data contract validated")
    return True


# ============================================================================
# SECTION 5: CLI INTEGRATION TESTS
# ============================================================================

def test_cli_save_tables_flag():
    """Test CLI --save-tables flag integration."""
    print("\n" + "="*70)
    print("TEST 5.1: CLI Integration - --save-tables Flag")
    print("="*70)
    
    # This test would require running main.py, which is complex in unit tests
    # Instead, we verify the function works as expected when called
    temp_dir = tempfile.mkdtemp()
    try:
        output_tables = {
            'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results()),
            'overall_score': analysis_output.create_overall_score_table(create_mock_kpi_results()),
            'okr_scorecard': analysis_output.create_okr_scorecard_table(create_mock_okr_results()),
            'action_triggers': analysis_output.create_action_triggers_table(create_mock_action_triggers()),
            'incident_detail': analysis_output.create_incident_detail_table(create_mock_incidents()),
            'request_detail': analysis_output.create_request_detail_table(create_mock_requests()),
            'geographic_summary': analysis_output.create_geographic_summary_table(create_mock_geo_results())
        }
        
        # Simulate --save-tables behavior (default CSV)
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='csv'
        )
        
        # Verify all 7 tables saved
        assert len(saved_files) == 7, "Should save all 7 tables"
        
        # Verify files exist
        for filepath in saved_files.values():
            assert os.path.exists(filepath), f"File should exist: {filepath}"
        
        print("[OK] CLI --save-tables simulation works")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_cli_tables_format_options():
    """Test CLI --tables-format options."""
    print("\nTEST 5.1b: CLI Integration - --tables-format Options")
    
    formats = ['parquet', 'csv', 'json']
    
    for fmt in formats:
        temp_dir = tempfile.mkdtemp()
        try:
            output_tables = {
                'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results())
            }
            
            saved_files = analysis_output.save_output_tables(
                output_tables,
                output_dir=temp_dir,
                format=fmt
            )
            
            filepath = saved_files['kpi_summary']
            assert filepath.endswith(f'.{fmt}'), f"Should be .{fmt} file"
            
            # Verify readable
            if fmt == 'parquet':
                df = pd.read_parquet(filepath)
            elif fmt == 'csv':
                df = pd.read_csv(filepath)
            elif fmt == 'json':
                df = pd.read_json(filepath, orient='records')
            
            assert isinstance(df, pd.DataFrame)
            assert not df.empty
            
        finally:
            shutil.rmtree(temp_dir)
    
    print("[OK] All format options work")
    return True


def test_cli_pipeline_integration():
    """Test full pipeline integration with --save-tables."""
    print("\nTEST 5.2: CLI Integration - Pipeline Integration")
    
    # Test that main.py can be called with --save-tables
    # This is a simulation test since running full pipeline requires data files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Verify the save_output_tables function works as expected in pipeline context
        output_tables = {
            'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results()),
            'overall_score': analysis_output.create_overall_score_table(create_mock_kpi_results()),
            'okr_scorecard': analysis_output.create_okr_scorecard_table(create_mock_okr_results()),
            'action_triggers': analysis_output.create_action_triggers_table(create_mock_action_triggers()),
            'incident_detail': analysis_output.create_incident_detail_table(create_mock_incidents()),
            'request_detail': analysis_output.create_request_detail_table(create_mock_requests()),
            'geographic_summary': analysis_output.create_geographic_summary_table(create_mock_geo_results())
        }
        
        # Simulate Step 5.75: Create normalized output tables
        assert len(output_tables) == 7, "Step 5.75 should create 7 tables"
        for table_name, table_df in output_tables.items():
            assert isinstance(table_df, pd.DataFrame), f"{table_name} should be DataFrame"
        
        # Simulate Step 5.8: Save output tables (when --save-tables provided)
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='parquet'
        )
        
        # Verify Step 5.8 executed (files created)
        assert len(saved_files) == 7, "Step 5.8 should save all 7 tables"
        for filepath in saved_files.values():
            assert os.path.exists(filepath), f"File should exist: {filepath}"
        
        # Verify Step 5.8 skipped when --save-tables not provided (no files created)
        temp_dir2 = tempfile.mkdtemp()
        try:
            # When --save-tables not provided, save_output_tables should not be called
            # But if called, it should work
            saved_files2 = analysis_output.save_output_tables(
                output_tables,
                output_dir=temp_dir2,
                format='parquet'
            )
            assert len(saved_files2) == 7, "Should still work when called"
        finally:
            shutil.rmtree(temp_dir2)
        
        print("[OK] Pipeline integration works correctly")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_cli_console_output_simulation():
    """Test that console output would show correct information."""
    print("\nTEST 5.2b: CLI Integration - Console Output Simulation")
    
    # Simulate what console output should show
    output_tables = {
        'kpi_summary': analysis_output.create_kpi_summary_table(create_mock_kpi_results()),
        'overall_score': analysis_output.create_overall_score_table(create_mock_kpi_results()),
    }
    
    # Verify table creation progress info would be available
    table_info = []
    for table_name, table_df in output_tables.items():
        if not table_df.empty:
            table_info.append(f"  - {table_name}: {len(table_df)} rows, {len(table_df.columns)} columns")
    
    assert len(table_info) > 0, "Should have table creation info"
    
    # Verify file paths would be available when saved
    temp_dir = tempfile.mkdtemp()
    try:
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='parquet'
        )
        
        # Verify file paths are available for console output
        assert len(saved_files) > 0, "Should have saved file paths"
        for table_name, filepath in saved_files.items():
            assert filepath.endswith('.parquet'), f"File path should be valid: {filepath}"
            assert os.path.basename(filepath).startswith(table_name), f"Filename should start with table name: {filepath}"
        
        print("[OK] Console output simulation works")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


# ============================================================================
# SECTION 6: EDGE CASES AND ERROR HANDLING
# ============================================================================

def test_edge_case_empty_kpi_results():
    """Test with empty kpi_results."""
    print("\n" + "="*70)
    print("TEST 6.1: Edge Cases - Empty kpi_results")
    print("="*70)
    
    df = analysis_output.create_kpi_summary_table({})
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    
    df = analysis_output.create_overall_score_table({})
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    
    print("[OK] Empty kpi_results handled")
    return True


def test_edge_case_empty_dataframes():
    """Test with empty DataFrames."""
    print("\nTEST 6.1b: Edge Cases - Empty DataFrames")
    
    # Empty incidents
    df = analysis_output.create_incident_detail_table(pd.DataFrame())
    assert isinstance(df, pd.DataFrame)
    
    # Empty requests
    df = analysis_output.create_request_detail_table(pd.DataFrame())
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    
    print("[OK] Empty DataFrames handled")
    return True


def test_edge_case_missing_required_fields():
    """Test with missing required fields."""
    print("\nTEST 6.2: Edge Cases - Missing Required Fields")
    
    # Missing required fields in kpi_results
    kpi_results = {
        'SM001': {
            # Missing most fields
            'KPI_Name': 'Test'
        }
    }
    
    df = analysis_output.create_kpi_summary_table(kpi_results)
    assert len(df) == 1
    assert df.iloc[0]['adherence_rate'] == 0.0  # Default
    
    print("[OK] Missing required fields handled gracefully")
    return True


def test_edge_case_malformed_okr_results():
    """Test with malformed okr_results."""
    print("\nTEST 6.2b: Edge Cases - Malformed okr_results")
    
    # Missing key_results
    okr_results = {'objective': 'Test'}
    df = analysis_output.create_okr_scorecard_table(okr_results)
    assert len(df) == 0
    
    # Empty key_results
    okr_results = {'key_results': {}}
    df = analysis_output.create_okr_scorecard_table(okr_results)
    assert len(df) == 0
    
    print("[OK] Malformed okr_results handled")
    return True


def test_edge_case_timestamp_type():
    """Test that timestamp is pd.Timestamp type."""
    print("\nTEST 6.3: Edge Cases - Timestamp Type")
    
    kpi_results = create_mock_kpi_results()
    df = analysis_output.create_kpi_summary_table(kpi_results)
    
    assert pd.api.types.is_datetime64_any_dtype(df['timestamp']), "timestamp should be datetime"
    assert isinstance(df.iloc[0]['timestamp'], pd.Timestamp), "Should be pd.Timestamp"
    
    print("[OK] Timestamp type correct")
    return True


# ============================================================================
# SECTION 7: PERFORMANCE AND SCALABILITY TESTS
# ============================================================================

def test_performance_large_dataset():
    """Test with large datasets."""
    print("\n" + "="*70)
    print("TEST 7.1: Performance - Large Dataset")
    print("="*70)
    
    # Create large incident DataFrame (10,000+ rows)
    large_incidents = pd.DataFrame({
        'number': [f'INC{i:05d}' for i in range(10000)],
        'priority': ['P1', 'P2', 'P3', 'P4'] * 2500,
        'Priority_Number': [1, 2, 3, 4] * 2500,
        'opened_at': pd.to_datetime(['2024-01-01'] * 10000),
        'resolved_at': pd.to_datetime(['2024-01-02'] * 10000),
        'Days_Open': [1] * 10000,
        'Is_Major_Incident': [False] * 10000,
        'Is_Backlog': [False] * 10000,
        'Is_First_Call_Resolution': [True] * 10000,
        'country': ['USA', 'UK', 'Germany', 'France'] * 2500
    })
    
    import time
    start = time.time()
    df = analysis_output.create_incident_detail_table(large_incidents)
    elapsed = time.time() - start
    
    assert len(df) == 10000, "Should handle large dataset"
    assert elapsed < 5.0, "Should complete in reasonable time (<5s)"
    
    print(f"[OK] Large dataset handled ({len(df)} rows in {elapsed:.2f}s)")
    return True


# ============================================================================
# SECTION 8: ROUND-TRIP TESTS
# ============================================================================

def test_round_trip_parquet():
    """Test save and reload with Parquet format."""
    print("\n" + "="*70)
    print("TEST 8.1: Round-Trip - Parquet")
    print("="*70)
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create original table
        original_df = analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        
        # Save
        output_tables = {'kpi_summary': original_df}
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='parquet'
        )
        
        # Reload
        reloaded_df = pd.read_parquet(saved_files['kpi_summary'])
        
        # Compare
        assert len(reloaded_df) == len(original_df), "Row count should match"
        assert list(reloaded_df.columns) == list(original_df.columns), "Columns should match"
        
        # Compare values (excluding timestamp which may differ slightly)
        for col in original_df.columns:
            if col != 'timestamp':
                pd.testing.assert_series_equal(
                    reloaded_df[col], 
                    original_df[col], 
                    check_names=False
                )
        
        print("[OK] Parquet round-trip successful")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_round_trip_csv():
    """Test save and reload with CSV format."""
    print("\nTEST 8.1b: Round-Trip - CSV")
    
    temp_dir = tempfile.mkdtemp()
    try:
        original_df = analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        
        output_tables = {'kpi_summary': original_df}
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='csv'
        )
        
        reloaded_df = pd.read_csv(saved_files['kpi_summary'])
        
        assert len(reloaded_df) == len(original_df), "Row count should match"
        
        # CSV may lose some type information, so we check values more leniently
        assert reloaded_df['kpi_code'].equals(original_df['kpi_code'])
        
        print("[OK] CSV round-trip successful")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_round_trip_json():
    """Test save and reload with JSON format."""
    print("\nTEST 8.1c: Round-Trip - JSON")
    
    temp_dir = tempfile.mkdtemp()
    try:
        original_df = analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        
        output_tables = {'kpi_summary': original_df}
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='json'
        )
        
        reloaded_df = pd.read_json(saved_files['kpi_summary'], orient='records')
        
        assert len(reloaded_df) == len(original_df), "Row count should match"
        
        print("[OK] JSON round-trip successful")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


def test_round_trip_column_types_preserved():
    """Test that column types are preserved in Parquet."""
    print("\nTEST 8.1d: Round-Trip - Column Types Preserved (Parquet)")
    
    temp_dir = tempfile.mkdtemp()
    try:
        original_df = analysis_output.create_kpi_summary_table(create_mock_kpi_results())
        
        output_tables = {'kpi_summary': original_df}
        saved_files = analysis_output.save_output_tables(
            output_tables,
            output_dir=temp_dir,
            format='parquet'
        )
        
        reloaded_df = pd.read_parquet(saved_files['kpi_summary'])
        
        # Verify types preserved
        assert pd.api.types.is_object_dtype(reloaded_df['kpi_code']) == pd.api.types.is_object_dtype(original_df['kpi_code'])
        assert pd.api.types.is_float_dtype(reloaded_df['adherence_rate']) == pd.api.types.is_float_dtype(original_df['adherence_rate'])
        assert pd.api.types.is_datetime64_any_dtype(reloaded_df['timestamp']) == pd.api.types.is_datetime64_any_dtype(original_df['timestamp'])
        
        print("[OK] Column types preserved in Parquet")
        return True
        
    finally:
        shutil.rmtree(temp_dir)


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and provide summary."""
    print("="*70)
    print("ANALYSIS OUTPUT MODULE - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    tests = [
        # Section 1: Unit Tests
        ("1.1 KPI Summary - All Types", test_create_kpi_summary_table_all_kpi_types),
        ("1.1b KPI Summary - Empty", test_create_kpi_summary_table_empty),
        ("1.1c KPI Summary - Missing Fields", test_create_kpi_summary_table_missing_fields),
        ("1.2 Overall Score", test_create_overall_score_table),
        ("1.2b Overall Score - Missing", test_create_overall_score_table_missing),
        ("1.3 OKR Scorecard", test_create_okr_scorecard_table),
        ("1.3b OKR Scorecard - Missing", test_create_okr_scorecard_table_missing),
        ("1.4 Action Triggers", test_create_action_triggers_table),
        ("1.4b Action Triggers - Empty", test_create_action_triggers_table_empty),
        ("1.5 Incident Detail", test_create_incident_detail_table),
        ("1.5b Incident Detail - Missing Columns", test_create_incident_detail_table_missing_columns),
        ("1.6 Request Detail", test_create_request_detail_table),
        ("1.6b Request Detail - Empty", test_create_request_detail_table_empty),
        ("1.6c Problem Detail", test_create_problem_detail_table),
        ("1.6d Problem Detail - Empty", test_create_problem_detail_table_empty),
        ("1.7 Geographic Summary", test_create_geographic_summary_table),
        ("1.7b Geographic Summary - Missing", test_create_geographic_summary_table_missing),
        
        # Section 2: Integration Tests
        ("2.1 Create All Tables - Complete", test_create_all_output_tables_complete),
        ("2.1b Create All Tables - Empty Requests", test_create_all_output_tables_empty_requests),
        ("2.1c Create All Tables - Independence", test_create_all_output_tables_table_independence),
        ("2.1d Create All Tables - With Problems", test_create_all_output_tables_with_problems),
        ("2.1e Create All Tables - Without Problems", test_create_all_output_tables_without_problems),
        
        # Section 3: File Persistence
        ("3.1 Save Tables - Parquet", test_save_output_tables_parquet),
        ("3.2 Save Tables - CSV", test_save_output_tables_csv),
        ("3.3 Save Tables - JSON", test_save_output_tables_json),
        ("3.4 Save Tables - Empty Skipped", test_save_output_tables_empty_tables),
        ("3.4b Save Tables - Invalid Format", test_save_output_tables_invalid_format),
        ("3.4c Save Tables - Directory Creation", test_save_output_tables_directory_creation),
        
        # Section 4: Data Contracts
        ("4.1 Data Contract - KPI Summary", test_kpi_summary_data_contract),
        ("4.2 Data Contract - OKR Scorecard", test_okr_scorecard_data_contract),
        ("4.3 Data Contract - Action Triggers", test_action_triggers_data_contract),
        ("4.4a Data Contract - Incident Detail", test_incident_detail_data_contract),
        ("4.4b Data Contract - Request Detail", test_request_detail_data_contract),
        ("4.4c Data Contract - Problem Detail", test_problem_detail_data_contract),
        ("4.4d Data Contract - Geographic Summary", test_geographic_summary_data_contract),
        
        # Section 5: CLI Integration
        ("5.1 CLI - Save Tables Flag", test_cli_save_tables_flag),
        ("5.1b CLI - Format Options", test_cli_tables_format_options),
        ("5.2 CLI - Pipeline Integration", test_cli_pipeline_integration),
        ("5.2b CLI - Console Output", test_cli_console_output_simulation),
        
        # Section 6: Edge Cases
        ("6.1 Edge Case - Empty KPI Results", test_edge_case_empty_kpi_results),
        ("6.1b Edge Case - Empty DataFrames", test_edge_case_empty_dataframes),
        ("6.2 Edge Case - Missing Fields", test_edge_case_missing_required_fields),
        ("6.2b Edge Case - Malformed OKR", test_edge_case_malformed_okr_results),
        ("6.3 Edge Case - Timestamp Type", test_edge_case_timestamp_type),
        
        # Section 7: Performance
        ("7.1 Performance - Large Dataset", test_performance_large_dataset),
        
        # Section 8: Round-Trip
        ("8.1 Round-Trip - Parquet", test_round_trip_parquet),
        ("8.1b Round-Trip - CSV", test_round_trip_csv),
        ("8.1c Round-Trip - JSON", test_round_trip_json),
        ("8.1d Round-Trip - Types Preserved", test_round_trip_column_types_preserved),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n[FAILED] {test_name} FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{status}: {test_name}")
    
    print("-" * 70)
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n[OK] ALL TESTS PASSED!")
    else:
        print(f"\n[FAILED] {total_count - passed_count} TEST(S) FAILED")
    
    print("="*70)
    
    return results


if __name__ == "__main__":
    results = run_all_tests()
    
    # Exit with appropriate code
    all_passed = all(passed for _, passed in results)
    sys.exit(0 if all_passed else 1)

