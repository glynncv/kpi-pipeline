"""
Analysis output module for KPI pipeline.
Converts calculation results to normalized DataFrame tables for presentation layer.

This module serves as an intermediate layer between analysis and presentation,
providing structured tables that can be used for multiple output formats:
- Excel reports
- JSON API responses
- CSV exports
- Database loading
"""

import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime


def create_kpi_summary_table(kpi_results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Convert KPI calculation results to normalized summary table.

    Args:
        kpi_results: Dictionary of KPI results from calculate_kpis

    Returns:
        DataFrame with normalized KPI summary data

    Columns:
        - kpi_code: KPI identifier (SM001, SM002, etc.)
        - kpi_name: Full KPI name
        - status: Met/Warning/Critical
        - adherence_rate: Percentage adherence to target
        - business_impact: Impact description
        - timestamp: When the calculation was performed
    """
    rows = []
    timestamp = pd.Timestamp.now()

    for kpi_code, kpi_data in kpi_results.items():
        if kpi_code == 'OVERALL':
            continue

        row = {
            'kpi_code': kpi_code,
            'kpi_name': kpi_data.get('KPI_Name', ''),
            'status': kpi_data.get('Status', ''),
            'adherence_rate': kpi_data.get('Adherence_Rate', 0.0),
            'business_impact': kpi_data.get('Business_Impact', ''),
            'timestamp': timestamp
        }

        # Add KPI-specific metrics
        if 'P1_Count' in kpi_data:
            row['p1_count'] = kpi_data['P1_Count']
            row['p2_count'] = kpi_data['P2_Count']
            row['total_major'] = kpi_data['Total_Major']
            row['p1_target'] = kpi_data['P1_Target']
            row['p2_target'] = kpi_data['P2_Target']

        elif 'Backlog_Count' in kpi_data:
            row['total_incidents'] = kpi_data['Total_Incidents']
            row['backlog_count'] = kpi_data['Backlog_Count']
            row['backlog_percentage'] = kpi_data['Backlog_Percentage']
            row['target_adherence'] = kpi_data['Target_Adherence']

        elif 'Aged_Count' in kpi_data:
            row['total_requests'] = kpi_data['Total_Requests']
            row['aged_count'] = kpi_data['Aged_Count']
            row['aged_percentage'] = kpi_data['Aged_Percentage']
            row['target_adherence'] = kpi_data['Target_Adherence']

        elif 'FCR_Count' in kpi_data:
            row['total_resolved'] = kpi_data['Total_Resolved']
            row['fcr_count'] = kpi_data['FCR_Count']
            row['fcr_percentage'] = kpi_data['FCR_Percentage']
            row['target_rate'] = kpi_data['Target_Rate']

        rows.append(row)

    return pd.DataFrame(rows)


def create_overall_score_table(kpi_results: Dict[str, Dict]) -> pd.DataFrame:
    """
    Extract overall score information as a single-row table.

    Args:
        kpi_results: Dictionary of KPI results

    Returns:
        Single-row DataFrame with overall score metrics
    """
    if 'OVERALL' not in kpi_results:
        return pd.DataFrame()

    overall = kpi_results['OVERALL']
    timestamp = pd.Timestamp.now()

    return pd.DataFrame([{
        'overall_score': overall['Overall_Score'],
        'overall_status': overall['Overall_Status'],
        'total_weight': overall['Total_Weight'],
        'timestamp': timestamp
    }])


def create_okr_scorecard_table(okr_results: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert OKR results to normalized scorecard table.

    Args:
        okr_results: Dictionary of OKR results from okr_calculator

    Returns:
        DataFrame with OKR scorecard data

    Columns:
        - kr_id: Key Result identifier (KR3, KR4, etc.)
        - kr_name: Key Result name
        - score: Achievement score (0-100)
        - status: On Track/At Risk/Off Track
        - current_value: Current metric value
        - target_value: Target metric value
        - target_operator: Comparison operator (≥, ≤)
        - gap_to_target: Gap description
        - owner: Responsible owner
    """
    rows = []

    if 'key_results' not in okr_results:
        return pd.DataFrame()

    for kr_id, kr_data in okr_results['key_results'].items():
        row = {
            'kr_id': kr_id,
            'kr_name': kr_data.get('name', ''),
            'score': kr_data.get('score', 0),
            'status': kr_data.get('status', ''),
            'current_value': kr_data.get('current_value', 0),
            'target_value': kr_data.get('target_value', 0),
            'target_operator': kr_data.get('target_operator', ''),
            'gap_to_target': kr_data.get('gap_to_target', ''),
            'owner': kr_data.get('owner', '')
        }
        rows.append(row)

    return pd.DataFrame(rows)


def create_action_triggers_table(action_triggers: Dict[str, list]) -> pd.DataFrame:
    """
    Convert action triggers to normalized table.

    Args:
        action_triggers: Dictionary with 'critical' and 'warning' trigger lists

    Returns:
        DataFrame with action trigger data

    Columns:
        - severity: Critical/Warning
        - kr_id: Associated Key Result
        - action: Required action description
        - escalation: Escalation path
    """
    rows = []

    for severity in ['critical', 'warning']:
        for trigger in action_triggers.get(severity, []):
            row = {
                'severity': severity.capitalize(),
                'kr_id': trigger.get('kr_id', ''),
                'action': trigger.get('action', ''),
                'escalation': trigger.get('escalation', '')
            }
            rows.append(row)

    return pd.DataFrame(rows)


def create_incident_detail_table(incidents: pd.DataFrame) -> pd.DataFrame:
    """
    Create normalized incident detail table for reporting.

    Args:
        incidents: Enriched incident DataFrame

    Returns:
        DataFrame with key incident attributes for drill-down

    Columns selected for reporting:
        - number, priority, Priority_Number
        - opened_at, resolved_at, Days_Open, Days_To_Resolve
        - Is_Major_Incident, Is_Backlog, Is_First_Call_Resolution
        - country
    """
    columns = [
        'number', 'priority', 'Priority_Number',
        'opened_at', 'resolved_at', 'Days_Open',
        'Is_Major_Incident', 'Is_Backlog', 'Is_First_Call_Resolution',
        'country'
    ]

    # Add Days_To_Resolve if it exists
    if 'Days_To_Resolve' in incidents.columns:
        columns.insert(6, 'Days_To_Resolve')

    # Filter to only columns that exist
    available_columns = [col for col in columns if col in incidents.columns]

    return incidents[available_columns].copy()


def create_request_detail_table(requests: pd.DataFrame) -> pd.DataFrame:
    """
    Create normalized request detail table for reporting.

    Args:
        requests: Enriched request DataFrame

    Returns:
        DataFrame with key request attributes for drill-down

    Columns selected for reporting:
        - number, opened_at, closed_at, Days_Open
        - Is_Aged, Is_Closed
        - country
    """
    if requests.empty:
        return pd.DataFrame()

    columns = [
        'number', 'opened_at', 'closed_at', 'Days_Open',
        'Is_Aged', 'Is_Closed', 'country'
    ]

    # Add Days_To_Close if it exists
    if 'Days_To_Close' in requests.columns:
        columns.insert(4, 'Days_To_Close')

    # Filter to only columns that exist
    available_columns = [col for col in columns if col in requests.columns]

    return requests[available_columns].copy()


def create_problem_detail_table(problems: pd.DataFrame) -> pd.DataFrame:
    """
    Create normalized problem detail table for reporting.

    Args:
        problems: Enriched problem DataFrame with calculated flags

    Returns:
        DataFrame with key problem attributes for drill-down

    Columns selected for reporting:
        - number, priority, Priority_Number, state
        - opened_at, closed_at, Days_Open
        - Is_Major_Problem, Requires_RCA, RCA_OnTime
        - country, location (if available)
    """
    if problems is None or problems.empty:
        return pd.DataFrame()

    columns = [
        'number', 'priority', 'Priority_Number', 'state',
        'opened_at', 'closed_at', 'Days_Open',
        'Is_Major_Problem', 'Requires_RCA', 'RCA_OnTime'
    ]

    # Add location columns if available
    if 'country' in problems.columns:
        columns.append('country')
    elif 'location.country' in problems.columns:
        columns.append('location.country')
    
    if 'location' in problems.columns:
        columns.append('location')
    elif 'location.name' in problems.columns:
        columns.append('location.name')
    elif 'location.u_site_name' in problems.columns:
        columns.append('location.u_site_name')

    # Add RCA stage if available
    if 'rca_stage' in problems.columns:
        columns.append('rca_stage')

    # Filter to only columns that exist
    available_columns = [col for col in columns if col in problems.columns]

    return problems[available_columns].copy()


def create_geographic_summary_table(geo_results: Dict[str, Any]) -> pd.DataFrame:
    """
    Convert geographic analysis to normalized table.

    Args:
        geo_results: Dictionary with geographic analysis results

    Returns:
        DataFrame with location-level metrics
    """
    if 'location_summary' not in geo_results:
        return pd.DataFrame()

    return geo_results['location_summary'].copy()


def create_all_output_tables(
    kpi_results: Dict[str, Dict],
    okr_results: Dict[str, Any],
    action_triggers: Dict[str, list],
    incidents: pd.DataFrame,
    requests: pd.DataFrame,
    geo_results: Dict[str, Any],
    problems: Optional[pd.DataFrame] = None
) -> Dict[str, pd.DataFrame]:
    """
    Generate all normalized output tables from analysis results.

    This is the main entry point for creating the intermediate analysis layer.
    All tables are normalized DataFrames suitable for:
    - Excel report generation
    - JSON API responses
    - CSV export
    - Database loading
    - Historical archiving

    Args:
        kpi_results: KPI calculation results
        okr_results: OKR calculation results
        action_triggers: Triggered actions from OKR analysis
        incidents: Enriched incident DataFrame
        requests: Enriched request DataFrame
        geo_results: Geographic analysis results
        problems: Enriched problem DataFrame (optional)

    Returns:
        Dictionary of normalized DataFrames keyed by table name

    Table Keys:
        - kpi_summary: KPI-level metrics
        - overall_score: Overall performance score
        - okr_scorecard: Key Results tracking
        - action_triggers: Required actions
        - incident_detail: Incident-level data
        - request_detail: Request-level data
        - problem_detail: Problem-level data (if problems provided)
        - geographic_summary: Location-level analysis
    """
    output_tables = {
        'kpi_summary': create_kpi_summary_table(kpi_results),
        'overall_score': create_overall_score_table(kpi_results),
        'okr_scorecard': create_okr_scorecard_table(okr_results),
        'action_triggers': create_action_triggers_table(action_triggers),
        'incident_detail': create_incident_detail_table(incidents),
        'request_detail': create_request_detail_table(requests),
        'geographic_summary': create_geographic_summary_table(geo_results)
    }

    # Add problem detail table if problems data is available
    if problems is not None:
        output_tables['problem_detail'] = create_problem_detail_table(problems)

    return output_tables


def save_output_tables(
    output_tables: Dict[str, pd.DataFrame],
    output_dir: str = 'data/archive',
    format: str = 'parquet'
) -> Dict[str, str]:
    """
    Save normalized output tables to disk for archiving/auditing.

    Args:
        output_tables: Dictionary of output DataFrames
        output_dir: Directory to save files
        format: File format ('parquet', 'csv', or 'json')

    Returns:
        Dictionary mapping table names to saved file paths

    Example:
        >>> saved_files = save_output_tables(output_tables)
        >>> print(saved_files['kpi_summary'])
        'data/archive/kpi_summary_20251109_143022.parquet'
    """
    import os
    from pathlib import Path

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    saved_files = {}

    for table_name, df in output_tables.items():
        if df.empty:
            continue

        filename = f"{table_name}_{timestamp}"

        if format == 'parquet':
            filepath = os.path.join(output_dir, f"{filename}.parquet")
            df.to_parquet(filepath, index=False)
        elif format == 'csv':
            filepath = os.path.join(output_dir, f"{filename}.csv")
            df.to_csv(filepath, index=False)
        elif format == 'json':
            filepath = os.path.join(output_dir, f"{filename}.json")
            df.to_json(filepath, orient='records', date_format='iso')
        else:
            raise ValueError(f"Unsupported format: {format}")

        saved_files[table_name] = filepath

    return saved_files


if __name__ == "__main__":
    # Test with sample data
    print("Analysis Output Module - Test Mode")
    print("="*70)

    # Sample KPI results
    sample_kpi_results = {
        'SM001': {
            'KPI_Name': 'Major Incidents',
            'Status': 'Met',
            'Adherence_Rate': 100.0,
            'Business_Impact': 'High',
            'P1_Count': 0,
            'P2_Count': 3,
            'Total_Major': 3,
            'P1_Target': 0,
            'P2_Target': 5
        },
        'OVERALL': {
            'Overall_Score': 78.5,
            'Overall_Status': 'Good',
            'Total_Weight': 100
        }
    }

    # Test KPI summary table creation
    kpi_summary = create_kpi_summary_table(sample_kpi_results)
    print("\nKPI Summary Table:")
    print(kpi_summary)

    # Test overall score table
    overall_score = create_overall_score_table(sample_kpi_results)
    print("\nOverall Score Table:")
    print(overall_score)

    print("\n" + "="*70)
    print("Module test completed successfully")
