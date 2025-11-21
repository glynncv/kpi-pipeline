"""
SDM (Service Delivery Manager) Analysis Module for KPI Pipeline.

Analyzes KPI performance by SDM to identify:
- SDM performance patterns
- Volume tier classification
- Intervention priorities
- Top/bottom performers

Similar to geographic_analysis but groups by SDM instead of location.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


def calculate_sdm_incident_metrics(
    incidents: pd.DataFrame,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate incident KPI metrics aggregated by SDM.

    Args:
        incidents: DataFrame with incident data and calculated flags
        config: Configuration dictionary

    Returns:
        DataFrame with SDM-level incident metrics
    """
    if 'sdm' not in incidents.columns:
        return pd.DataFrame()

    # Filter out empty/null SDM values
    df = incidents[incidents['sdm'].notna() & (incidents['sdm'] != '')].copy()

    if df.empty:
        return pd.DataFrame()

    # Group by SDM
    sdm_groups = df.groupby('sdm')

    # Calculate metrics
    metrics = pd.DataFrame({
        'SDM': sdm_groups.size().index,
        'Incident_Volume': sdm_groups.size().values,
        'Backlog_Count': (
            sdm_groups['Is_Backlog'].sum().values
            if 'Is_Backlog' in df.columns else 0
        ),
        'Major_Incident_Count': (
            sdm_groups['Is_Major_Incident'].sum().values
            if 'Is_Major_Incident' in df.columns else 0
        ),
        'FCR_Count': (
            sdm_groups['Is_First_Call_Resolution'].sum().values
            if 'Is_First_Call_Resolution' in df.columns else 0
        ),
    })

    # Calculate percentages
    metrics['Backlog_Pct'] = (
        metrics['Backlog_Count'] / metrics['Incident_Volume'] * 100
    ).round(2)
    metrics['FCR_Rate'] = (
        metrics['FCR_Count'] / metrics['Incident_Volume'] * 100
    ).round(2)
    metrics['Major_Incident_Rate'] = (
        metrics['Major_Incident_Count'] / metrics['Incident_Volume'] * 100
    ).round(2)

    return metrics


def calculate_sdm_request_metrics(
    requests: pd.DataFrame,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate request KPI metrics aggregated by SDM.

    Args:
        requests: Request DataFrame with calculated flags
        config: Configuration dictionary

    Returns:
        DataFrame with SDM-level request metrics
    """
    if requests is None or requests.empty or 'sdm' not in requests.columns:
        return pd.DataFrame()

    # Filter out empty/null SDM values
    df = requests[requests['sdm'].notna() & (requests['sdm'] != '')].copy()

    if df.empty:
        return pd.DataFrame()

    # Group by SDM
    sdm_groups = df.groupby('sdm')

    # Calculate metrics
    metrics = pd.DataFrame({
        'SDM': sdm_groups.size().index,
        'Request_Volume': sdm_groups.size().values,
        'Aged_Request_Count': (
            sdm_groups['Is_Aged'].sum().values
            if 'Is_Aged' in requests.columns else 0
        ),
    })

    # Calculate percentages
    metrics['Aged_Request_Pct'] = (
        metrics['Aged_Request_Count'] / metrics['Request_Volume'] * 100
    ).round(2)
    metrics['Request_Adherence_Rate'] = (100.0 - metrics['Aged_Request_Pct']).round(2)

    return metrics


def calculate_sdm_problem_metrics(
    problems: pd.DataFrame,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate Problem Management metrics aggregated by SDM.

    Args:
        problems: Problem DataFrame with calculated flags
        config: Configuration dictionary

    Returns:
        DataFrame with SDM-level PM metrics
    """
    if problems is None or problems.empty or 'sdm' not in problems.columns:
        return pd.DataFrame()

    # Filter out empty/null SDM values
    df = problems[problems['sdm'].notna() & (problems['sdm'] != '')].copy()

    if df.empty:
        return pd.DataFrame()

    # Group by SDM
    sdm_groups = df.groupby('sdm')

    # Calculate metrics
    metrics = pd.DataFrame({
        'SDM': sdm_groups.size().index,
        'Problem_Volume': sdm_groups.size().values,
        'Major_Problem_Count': (
            sdm_groups['Is_Major_Problem'].sum().values
            if 'Is_Major_Problem' in problems.columns else 0
        ),
        'RCA_Required_Count': (
            sdm_groups['Requires_RCA'].sum().values
            if 'Requires_RCA' in problems.columns else 0
        ),
        'RCA_Completed_OnTime_Count': (
            sdm_groups['RCA_OnTime'].sum().values
            if 'RCA_OnTime' in problems.columns else 0
        ),
    })

    # Calculate RCA completion rate
    metrics['RCA_Completion_Rate'] = np.where(
        metrics['RCA_Required_Count'] > 0,
        (metrics['RCA_Completed_OnTime_Count'] / metrics['RCA_Required_Count'] * 100).round(2),
        0.0
    )

    return metrics


def classify_sdm_volume_tier(volume: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify an SDM into a volume tier based on total ticket count.

    Uses the same volume tiers as geographic analysis.

    Args:
        volume: Total number of tickets
        config: Configuration dictionary with volume_tiers

    Returns:
        Dictionary with tier classification details
    """
    volume_tiers = config['okr']['geographic_analysis']['volume_tiers']

    # Determine tier based on thresholds
    if volume >= volume_tiers['tier_1']['threshold']:
        tier = 'tier_1'
    elif volume >= volume_tiers['tier_2']['threshold']:
        tier = 'tier_2'
    elif volume >= volume_tiers['tier_3']['threshold']:
        tier = 'tier_3'
    else:
        tier = 'tier_4'

    tier_info = volume_tiers[tier]

    return {
        'tier': tier,
        'tier_name': tier_info['name'],
        'tier_description': tier_info['description'],
        'volume': volume
    }


def identify_sdm_intervention_priority(
    row: pd.Series,
    config: Dict[str, Any]
) -> str:
    """
    Determine intervention priority for an SDM based on volume and performance.

    Priority levels:
        - Critical: High volume AND poor performance
        - High: High volume OR poor performance
        - Monitor: Low volume with poor performance
        - Standard: Meeting all targets

    Args:
        row: DataFrame row with tier, backlog_pct, fcr_rate
        config: Configuration dictionary

    Returns:
        Intervention priority: 'Critical', 'High', 'Monitor', or 'Standard'
    """
    tier = row.get('Volume_Tier', 'tier_4')
    backlog_pct = row.get('Backlog_Pct', 0.0)
    fcr_rate = row.get('FCR_Rate', 100.0)

    # Get performance thresholds
    backlog_threshold = config['kpis']['SM002']['targets']['backlog_max'] * 100
    fcr_threshold = config['kpis']['SM004']['targets']['ftf_rate_min']

    # Determine if performance is poor
    poor_performance = (backlog_pct > backlog_threshold) or (fcr_rate < fcr_threshold)

    # Volume tier classification
    is_high_volume = tier in ['tier_1', 'tier_2']
    is_low_volume = tier == 'tier_4'

    # Determine priority
    if is_high_volume and poor_performance:
        return 'Critical'
    elif is_low_volume and poor_performance:
        return 'Monitor'
    elif is_high_volume or poor_performance:
        return 'High'
    else:
        return 'Standard'


def calculate_sdm_okr_scores(
    sdm_metrics: pd.DataFrame,
    okr_config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate OKR scores (KR3-KR6 and Overall OKR) for each SDM.

    Args:
        sdm_metrics: DataFrame with SDM-level KPI metrics
        okr_config: OKR configuration dictionary

    Returns:
        DataFrame with added OKR score columns
    """
    df = sdm_metrics.copy()

    # Initialize OKR score columns
    df['KR3_Score'] = 0.0
    df['KR4_Score'] = 0.0
    df['KR5_Score'] = 0.0
    df['KR6_Score'] = 0.0
    df['Overall_OKR_Score'] = 0.0
    df['Overall_OKR_Status'] = ''

    # Calculate KR3 (Major Incidents)
    if 'Major_Incident_Count' in df.columns:
        kr3_config = okr_config['key_results']['KR3']
        target_value = kr3_config['target']['value']
        max_acceptable = kr3_config['scoring'].get('max_acceptable', target_value * 4)

        for idx, row in df.iterrows():
            current_value = row.get('Major_Incident_Count', 0)
            raw_score = 100 - (current_value / max_acceptable * 100)
            score = max(0, min(100, raw_score))
            df.at[idx, 'KR3_Score'] = round(score, 1)

    # Calculate KR4 (Incident Backlog)
    if 'Backlog_Pct' in df.columns:
        kr4_config = okr_config['key_results']['KR4']
        target_value = kr4_config['target']['value']

        for idx, row in df.iterrows():
            current_value = row.get('Backlog_Pct', 0)
            raw_score = 100 - (current_value / target_value * 100)
            score = max(0, min(100, raw_score))
            df.at[idx, 'KR4_Score'] = round(score, 1)

    # Calculate KR5 (Request Aging)
    if 'Aged_Request_Pct' in df.columns:
        kr5_config = okr_config['key_results']['KR5']
        target_value = kr5_config['target']['value']

        for idx, row in df.iterrows():
            current_value = row.get('Aged_Request_Pct', 0)
            raw_score = 100 - (current_value / target_value * 100)
            score = max(0, min(100, raw_score))
            df.at[idx, 'KR5_Score'] = round(score, 1)

    # Calculate KR6 (First Call Resolution)
    if 'FCR_Rate' in df.columns:
        kr6_config = okr_config['key_results']['KR6']
        target_value = kr6_config['target']['value']

        for idx, row in df.iterrows():
            current_value = row.get('FCR_Rate', 0)
            raw_score = (current_value / target_value) * 100
            score = max(0, min(100, raw_score))
            df.at[idx, 'KR6_Score'] = round(score, 1)

    # Calculate Overall OKR Score (weighted average)
    weights = okr_config['weighting']['weights']
    for idx, row in df.iterrows():
        overall_score = (
            row.get('KR3_Score', 0) * (weights['KR3'] / 100) +
            row.get('KR4_Score', 0) * (weights['KR4'] / 100) +
            row.get('KR5_Score', 0) * (weights['KR5'] / 100) +
            row.get('KR6_Score', 0) * (weights['KR6'] / 100)
        )
        df.at[idx, 'Overall_OKR_Score'] = round(overall_score, 1)

        # Determine overall OKR status
        bands = okr_config['weighting']['overall_score']['performance_bands']
        status_value = ''
        if overall_score >= bands['excellent']['min_score']:
            status_value = bands['excellent']['status']
        elif overall_score >= bands['on_track']['min_score']:
            status_value = bands['on_track']['status']
        elif overall_score >= bands['at_risk']['min_score']:
            status_value = bands['at_risk']['status']
        else:
            status_value = bands['critical']['status']
        
        # Sanitize emojis for CSV compatibility
        status_value = status_value.replace('🔴 CRITICAL', '[CRITICAL]')
        status_value = status_value.replace('🟡 ON TRACK', '[ON TRACK]')
        status_value = status_value.replace('🟠 AT RISK', '[AT RISK]')
        status_value = status_value.replace('🟢 EXCELLENT', '[EXCELLENT]')
        status_value = status_value.replace('🟢', '[ON TRACK]')
        status_value = status_value.replace('🔴', '[CRITICAL]')
        status_value = status_value.replace('🟡', '[AT RISK]')
        status_value = status_value.replace('🟠', '[AT RISK]')
        
        df.at[idx, 'Overall_OKR_Status'] = status_value

    return df


def calculate_sdm_overall_score(
    sdm_metrics: pd.DataFrame,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate overall KPI score for each SDM using weighted KPI adherence rates.

    Args:
        sdm_metrics: DataFrame with SDM-level KPI metrics
        config: Configuration dictionary

    Returns:
        DataFrame with added overall KPI score columns
    """
    from . import config_loader

    df = sdm_metrics.copy()

    # Initialize overall score columns
    df['Overall_KPI_Score'] = 0.0
    df['Overall_KPI_Status'] = ''

    # Get KPI weights
    weights = config_loader.get_kpi_weights(config)

    # Calculate weighted score for each SDM
    for idx, row in df.iterrows():
        total_score = 0.0
        total_weight = 0.0

        # SM001 adherence
        if 'SM001' in weights and 'Major_Incident_Count' in df.columns:
            major_count = row.get('Major_Incident_Count', 0)
            p2_target = config['kpis']['SM001']['targets'].get('p2_max', 5)
            if major_count == 0:
                adherence = 100.0
            elif major_count <= p2_target:
                adherence = 50.0
            else:
                adherence = 0.0
            total_score += (adherence * weights['SM001'] / 100)
            total_weight += weights['SM001']

        # SM002 adherence
        if 'SM002' in weights and 'Backlog_Pct' in df.columns:
            backlog_pct = row.get('Backlog_Pct', 0)
            adherence = 100.0 - backlog_pct
            total_score += (adherence * weights['SM002'] / 100)
            total_weight += weights['SM002']

        # SM003 adherence
        if 'SM003' in weights and 'Request_Adherence_Rate' in df.columns:
            adherence = row.get('Request_Adherence_Rate', 0)
            total_score += (adherence * weights['SM003'] / 100)
            total_weight += weights['SM003']

        # SM004 adherence
        if 'SM004' in weights and 'FCR_Rate' in df.columns:
            fcr_rate = row.get('FCR_Rate', 0)
            total_score += (fcr_rate * weights['SM004'] / 100)
            total_weight += weights['SM004']

        # Calculate overall score
        overall_score = (total_score / total_weight * 100) if total_weight > 0 else 0
        df.at[idx, 'Overall_KPI_Score'] = round(overall_score, 1)

        # Determine status
        bands = config['global_status_rules']['performance_bands']
        if overall_score >= bands['excellent']:
            df.at[idx, 'Overall_KPI_Status'] = 'Excellent'
        elif overall_score >= bands['good']:
            df.at[idx, 'Overall_KPI_Status'] = 'Good'
        elif overall_score >= bands['needs_improvement']:
            df.at[idx, 'Overall_KPI_Status'] = 'Needs Improvement'
        else:
            df.at[idx, 'Overall_KPI_Status'] = 'Poor'

    return df


def get_sdm_intervention_summary(sdm_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of SDMs by intervention priority.

    Args:
        sdm_df: SDM metrics DataFrame with Intervention_Priority

    Returns:
        Dictionary with counts and lists by priority
    """
    priority_counts = sdm_df['Intervention_Priority'].value_counts().to_dict()

    summary = {
        'total_sdms': len(sdm_df),
        'critical_count': priority_counts.get('Critical', 0),
        'high_count': priority_counts.get('High', 0),
        'monitor_count': priority_counts.get('Monitor', 0),
        'standard_count': priority_counts.get('Standard', 0),
        'critical_sdms': sdm_df[
            sdm_df['Intervention_Priority'] == 'Critical'
        ][['SDM', 'Total_Volume', 'Backlog_Pct', 'FCR_Rate']].to_dict('records'),
        'high_priority_sdms': sdm_df[
            sdm_df['Intervention_Priority'] == 'High'
        ][['SDM', 'Total_Volume', 'Backlog_Pct', 'FCR_Rate']].to_dict('records'),
    }

    return summary


def analyze_sdm(
    incidents: pd.DataFrame,
    requests: Optional[pd.DataFrame],
    config: Dict[str, Any],
    problems: Optional[pd.DataFrame] = None,
    okr_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main analysis function - analyzes KPI performance by SDM.

    Combines incidents, requests, and problems (if provided) and calculates:
        - SDM-level KPI breakdown
        - Volume tier classification
        - OKR scores per SDM
        - Intervention priorities

    Args:
        incidents: Incident DataFrame with calculated flags and 'sdm' column
        requests: Request DataFrame with calculated flags (optional)
        config: Configuration dictionary
        problems: Problem DataFrame with calculated flags (optional)
        okr_config: OKR configuration dictionary (optional)

    Returns:
        Dictionary containing:
            - sdm_summary: DataFrame with SDM metrics
            - top_performers: DataFrame with top 10 SDMs
            - bottom_performers: DataFrame with bottom 10 SDMs
            - intervention_summary: Dictionary with intervention priorities
    """
    # Load OKR config if not provided
    if okr_config is None:
        try:
            from . import config_loader
            okr_config = config_loader.load_okr_config('config/okr_config.yaml')
        except Exception:
            okr_config = None

    # Check if SDM column exists
    if 'sdm' not in incidents.columns:
        return {
            'sdm_summary': pd.DataFrame(),
            'top_performers': pd.DataFrame(),
            'bottom_performers': pd.DataFrame(),
            'intervention_summary': {
                'total_sdms': 0,
                'critical_count': 0,
                'high_count': 0,
                'monitor_count': 0,
                'standard_count': 0,
                'critical_sdms': [],
                'high_priority_sdms': [],
            }
        }

    # Calculate incident metrics (base SDM summary)
    sdm_summary = calculate_sdm_incident_metrics(incidents, config)

    if sdm_summary.empty:
        return {
            'sdm_summary': pd.DataFrame(),
            'top_performers': pd.DataFrame(),
            'bottom_performers': pd.DataFrame(),
            'intervention_summary': {
                'total_sdms': 0,
                'critical_count': 0,
                'high_count': 0,
                'monitor_count': 0,
                'standard_count': 0,
                'critical_sdms': [],
                'high_priority_sdms': [],
            }
        }

    # Calculate request metrics and merge
    if requests is not None and not requests.empty:
        request_metrics = calculate_sdm_request_metrics(requests, config)
        if not request_metrics.empty:
            sdm_summary = sdm_summary.merge(
                request_metrics[['SDM', 'Request_Volume', 'Aged_Request_Count',
                                'Aged_Request_Pct', 'Request_Adherence_Rate']],
                on='SDM',
                how='outer'
            )
            # Fill NaN values
            for col in ['Request_Volume', 'Aged_Request_Count',
                       'Aged_Request_Pct', 'Request_Adherence_Rate']:
                if col in sdm_summary.columns:
                    sdm_summary[col] = sdm_summary[col].fillna(0)

    # Calculate problem metrics and merge
    if problems is not None and not problems.empty:
        problem_metrics = calculate_sdm_problem_metrics(problems, config)
        if not problem_metrics.empty:
            sdm_summary = sdm_summary.merge(
                problem_metrics[['SDM', 'Problem_Volume', 'Major_Problem_Count',
                                'RCA_Required_Count', 'RCA_Completed_OnTime_Count',
                                'RCA_Completion_Rate']],
                on='SDM',
                how='outer'
            )
            # Fill NaN values
            for col in ['Problem_Volume', 'Major_Problem_Count',
                       'RCA_Required_Count', 'RCA_Completed_OnTime_Count',
                       'RCA_Completion_Rate']:
                if col in sdm_summary.columns:
                    sdm_summary[col] = sdm_summary[col].fillna(0)

    # Calculate total volume
    sdm_summary['Total_Volume'] = sdm_summary['Incident_Volume'].fillna(0)
    if 'Request_Volume' in sdm_summary.columns:
        sdm_summary['Total_Volume'] += sdm_summary['Request_Volume'].fillna(0)
    if 'Problem_Volume' in sdm_summary.columns:
        sdm_summary['Total_Volume'] += sdm_summary['Problem_Volume'].fillna(0)

    # Classify volume tier
    sdm_summary['Volume_Tier'] = sdm_summary['Total_Volume'].apply(
        lambda x: classify_sdm_volume_tier(int(x), config)['tier']
    )
    sdm_summary['Volume_Tier_Name'] = sdm_summary['Total_Volume'].apply(
        lambda x: classify_sdm_volume_tier(int(x), config)['tier_name']
    )

    # Determine intervention priority
    sdm_summary['Intervention_Priority'] = sdm_summary.apply(
        lambda row: identify_sdm_intervention_priority(row, config),
        axis=1
    )

    # Calculate OKR scores if config available
    if okr_config is not None:
        sdm_summary = calculate_sdm_okr_scores(sdm_summary, okr_config)

    # Calculate overall KPI score
    sdm_summary = calculate_sdm_overall_score(sdm_summary, config)

    # Sort by total volume descending
    sdm_summary = sdm_summary.sort_values('Total_Volume', ascending=False)

    # Get top performers (best FCR, lowest backlog)
    top_performers = sdm_summary.sort_values(
        ['FCR_Rate', 'Backlog_Pct'],
        ascending=[False, True]
    ).head(10).copy()

    # Get bottom performers
    bottom_performers = sdm_summary.sort_values(
        ['FCR_Rate', 'Backlog_Pct'],
        ascending=[True, False]
    ).head(10).copy()

    # Generate intervention summary
    intervention_summary = get_sdm_intervention_summary(sdm_summary)

    return {
        'sdm_summary': sdm_summary,
        'top_performers': top_performers,
        'bottom_performers': bottom_performers,
        'intervention_summary': intervention_summary
    }


if __name__ == "__main__":
    """Test the SDM analysis module with sample data."""
    print("SDM Analysis Module - Test Mode")
    print("=" * 60)

    # Create sample data
    sample_data = pd.DataFrame({
        'sdm': ['John Smith', 'Jane Doe', 'Bob Wilson', 'Alice Brown', 'Charlie Davis'] * 50,
        'Is_Backlog': [True, False, True, False, True] * 50,
        'Is_Major_Incident': [False, False, True, False, False] * 50,
        'Is_First_Call_Resolution': [True, True, False, True, False] * 50,
    })

    # Create sample config
    sample_config = {
        'okr': {
            'geographic_analysis': {
                'volume_tiers': {
                    'tier_1': {'threshold': 500, 'name': 'High Volume', 'description': '≥500'},
                    'tier_2': {'threshold': 200, 'name': 'Medium Volume', 'description': '200-499'},
                    'tier_3': {'threshold': 100, 'name': 'Standard Volume', 'description': '100-199'},
                    'tier_4': {'threshold': 0, 'name': 'Low Volume', 'description': '<100'},
                }
            }
        },
        'kpis': {
            'SM002': {'targets': {'backlog_max': 0.10}},
            'SM004': {'targets': {'ftf_rate_min': 80.0}},
        },
        'global_status_rules': {
            'performance_bands': {
                'excellent': 95,
                'good': 80,
                'needs_improvement': 60,
            }
        }
    }

    # Run analysis
    results = analyze_sdm(sample_data, None, sample_config)

    print("\n1. SDM SUMMARY")
    print("-" * 60)
    if not results['sdm_summary'].empty:
        cols = ['SDM', 'Total_Volume', 'Backlog_Pct', 'FCR_Rate', 'Intervention_Priority']
        print(results['sdm_summary'][cols].to_string(index=False))
    else:
        print("No SDM data available")

    print("\n2. INTERVENTION SUMMARY")
    print("-" * 60)
    for key, value in results['intervention_summary'].items():
        if not isinstance(value, list):
            print(f"{key}: {value}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
