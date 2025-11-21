"""
Geographic Analysis Module for KPI Pipeline.

Analyzes KPI performance by country and location to identify:
- Geographic performance patterns
- Volume tier classification
- Intervention priorities
- Top/bottom performers

Phase 2 - Conversation 1
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List, Optional


def classify_volume_tier(volume: int, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify a location into a volume tier based on incident/request count.
    
    Volume tiers from config:
        - Tier 1: ≥500 (High Volume)
        - Tier 2: 200-499 (Medium Volume)
        - Tier 3: 100-199 (Standard Volume)
        - Tier 4: <100 (Low Volume)
    
    Args:
        volume: Total number of incidents/requests
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


def identify_intervention_priority(
    row: pd.Series,
    config: Dict[str, Any]
) -> str:
    """
    Determine intervention priority for a location based on volume and performance.
    
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
    backlog_threshold = config['kpis']['SM002']['targets']['backlog_max'] * 100  # Convert to %
    fcr_threshold = config['kpis']['SM004']['targets']['ftf_rate_min'] * 1  # Already in percentage (e.g., 80.0 = 80%)
    
    # Determine if performance is poor
    poor_performance = (backlog_pct > backlog_threshold) or (fcr_rate < fcr_threshold)
    
    # Volume tier classification:
    # - High volume: tier_1, tier_2 (≥200)
    # - Medium volume: tier_3 (100-199) 
    # - Low volume: tier_4 (<100)
    is_high_volume = tier in ['tier_1', 'tier_2']
    is_low_volume = tier == 'tier_4'  # Only tier 4 is truly "low volume"
    
    # Determine priority (order matters!)
    if is_high_volume and poor_performance:
        return 'Critical'
    elif is_low_volume and poor_performance:
        # Only tier 4 (very low volume) + poor performance = Monitor
        return 'Monitor'
    elif is_high_volume or poor_performance:
        # High volume (any performance) OR poor performance (tier 2/3) = High
        return 'High'
    else:
        # Low/medium volume + good performance = Standard
        return 'Standard'


def calculate_country_metrics(
    df: pd.DataFrame,
    country_col: str,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate KPI metrics aggregated by country.
    
    Args:
        df: DataFrame with incident/request data and calculated flags
        country_col: Column name for country (e.g., 'location_country')
        config: Configuration dictionary
        
    Returns:
        DataFrame with country-level metrics
    """
    # Group by country
    country_groups = df.groupby(country_col)
    
    # Calculate metrics
    metrics = pd.DataFrame({
        'Country': country_groups.size().index,
        'Total_Volume': country_groups.size().values,
        'Backlog_Count': country_groups['Is_Backlog'].sum().values if 'Is_Backlog' in df.columns else 0,
        'Major_Incident_Count': country_groups['Is_Major_Incident'].sum().values if 'Is_Major_Incident' in df.columns else 0,
        'FCR_Count': country_groups['Is_First_Call_Resolution'].sum().values if 'Is_First_Call_Resolution' in df.columns else 0,
        'Eligible_FCR_Count': country_groups['Is_First_Time_Fix'].sum().values if 'Is_First_Time_Fix' in df.columns else 0,
    })
    
    # Calculate percentages
    metrics['Backlog_Pct'] = (metrics['Backlog_Count'] / metrics['Total_Volume'] * 100).round(2)
    metrics['FCR_Rate'] = (metrics['FCR_Count'] / metrics['Total_Volume'] * 100).round(2)
    metrics['Major_Incident_Rate'] = (metrics['Major_Incident_Count'] / metrics['Total_Volume'] * 100).round(2)
    
    # Classify volume tier
    metrics['Volume_Tier'] = metrics['Total_Volume'].apply(
        lambda x: classify_volume_tier(x, config)['tier']
    )
    metrics['Volume_Tier_Name'] = metrics['Total_Volume'].apply(
        lambda x: classify_volume_tier(x, config)['tier_name']
    )
    
    # Determine intervention priority
    metrics['Intervention_Priority'] = metrics.apply(
        lambda row: identify_intervention_priority(row, config),
        axis=1
    )
    
    # Sort by volume descending
    metrics = metrics.sort_values('Total_Volume', ascending=False)
    
    return metrics


def calculate_location_metrics(
    df: pd.DataFrame,
    location_col: str,
    country_col: str,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate KPI metrics aggregated by location.
    
    Args:
        df: DataFrame with incident/request data and calculated flags
        location_col: Column name for location (e.g., 'location' or 'location_u_site_name')
        country_col: Column name for country
        config: Configuration dictionary
        
    Returns:
        DataFrame with location-level metrics
    """
    # Group by location and country
    location_groups = df.groupby([location_col, country_col])
    
    # Calculate metrics
    # Ensure Location and Country are strings for consistent merging
    location_index = location_groups.size().index
    metrics = pd.DataFrame({
        'Location': [str(loc) for loc, _ in location_index],
        'Country': [str(country) for _, country in location_index],
        'Total_Volume': location_groups.size().values,
        'Backlog_Count': location_groups['Is_Backlog'].sum().values if 'Is_Backlog' in df.columns else 0,
        'Major_Incident_Count': location_groups['Is_Major_Incident'].sum().values if 'Is_Major_Incident' in df.columns else 0,
        'FCR_Count': location_groups['Is_First_Call_Resolution'].sum().values if 'Is_First_Call_Resolution' in df.columns else 0,
        'Eligible_FCR_Count': location_groups['Is_First_Time_Fix'].sum().values if 'Is_First_Time_Fix' in df.columns else 0,
    })
    
    # Calculate percentages
    metrics['Backlog_Pct'] = (metrics['Backlog_Count'] / metrics['Total_Volume'] * 100).round(2)
    metrics['FCR_Rate'] = (metrics['FCR_Count'] / metrics['Total_Volume'] * 100).round(2)
    metrics['Major_Incident_Rate'] = (metrics['Major_Incident_Count'] / metrics['Total_Volume'] * 100).round(2)
    
    # Classify volume tier
    metrics['Volume_Tier'] = metrics['Total_Volume'].apply(
        lambda x: classify_volume_tier(x, config)['tier']
    )
    metrics['Volume_Tier_Name'] = metrics['Total_Volume'].apply(
        lambda x: classify_volume_tier(x, config)['tier_name']
    )
    
    # Determine intervention priority
    metrics['Intervention_Priority'] = metrics.apply(
        lambda row: identify_intervention_priority(row, config),
        axis=1
    )
    
    # Sort by volume descending
    metrics = metrics.sort_values('Total_Volume', ascending=False)
    
    return metrics


def get_top_performers(
    location_df: pd.DataFrame,
    n: int = 10,
    sort_by: str = 'FCR_Rate'
) -> pd.DataFrame:
    """
    Get top N performing locations.
    
    Performance criteria:
        - High FCR rate (primary)
        - Low backlog percentage (secondary)
    
    Args:
        location_df: Location metrics DataFrame
        n: Number of top performers to return
        sort_by: Metric to sort by ('FCR_Rate' or 'Backlog_Pct')
        
    Returns:
        DataFrame with top N performers
    """
    if sort_by == 'FCR_Rate':
        # Sort by FCR descending, then backlog ascending
        top = location_df.sort_values(
            ['FCR_Rate', 'Backlog_Pct'],
            ascending=[False, True]
        ).head(n)
    else:
        # Sort by backlog ascending, then FCR descending
        top = location_df.sort_values(
            ['Backlog_Pct', 'FCR_Rate'],
            ascending=[True, False]
        ).head(n)
    
    return top.copy()


def get_bottom_performers(
    location_df: pd.DataFrame,
    n: int = 10,
    sort_by: str = 'FCR_Rate'
) -> pd.DataFrame:
    """
    Get bottom N performing locations (need intervention).
    
    Performance criteria:
        - Low FCR rate (primary)
        - High backlog percentage (secondary)
    
    Args:
        location_df: Location metrics DataFrame
        n: Number of bottom performers to return
        sort_by: Metric to sort by ('FCR_Rate' or 'Backlog_Pct')
        
    Returns:
        DataFrame with bottom N performers
    """
    if sort_by == 'FCR_Rate':
        # Sort by FCR ascending, then backlog descending
        bottom = location_df.sort_values(
            ['FCR_Rate', 'Backlog_Pct'],
            ascending=[True, False]
        ).head(n)
    else:
        # Sort by backlog descending, then FCR ascending
        bottom = location_df.sort_values(
            ['Backlog_Pct', 'FCR_Rate'],
            ascending=[False, True]
        ).head(n)
    
    return bottom.copy()


def calculate_request_metrics(
    requests: pd.DataFrame,
    location_col: str,
    country_col: str,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate request-specific metrics aggregated by location.
    
    Args:
        requests: Request DataFrame with calculated flags (Is_Aged)
        location_col: Column name for location
        country_col: Column name for country
        config: Configuration dictionary
        
    Returns:
        DataFrame with request metrics by location
    """
    if requests is None or len(requests) == 0:
        return pd.DataFrame()
    
    # Check if required columns exist
    if location_col not in requests.columns or country_col not in requests.columns:
        return pd.DataFrame()
    
    # Group by location and country
    location_groups = requests.groupby([location_col, country_col])
    
    # Calculate metrics
    # Ensure Location and Country are strings for consistent merging
    location_index = location_groups.size().index
    metrics = pd.DataFrame({
        'Location': [str(loc) for loc, _ in location_index],
        'Country': [str(country) for _, country in location_index],
        'Request_Volume': location_groups.size().values,
        'Aged_Request_Count': location_groups['Is_Aged'].sum().values if 'Is_Aged' in requests.columns else 0,
    })
    
    # Calculate percentages
    metrics['Aged_Request_Pct'] = (
        (metrics['Aged_Request_Count'] / metrics['Request_Volume'] * 100).round(2)
        if metrics['Request_Volume'].sum() > 0 else 0
    )
    
    # Calculate adherence rate (inverse of aged %)
    # SM003 target is typically 70% adherence (30% max aged)
    if 'SM003' in config.get('kpis', {}):
        target_aged_pct = config['kpis']['SM003']['targets'].get('aged_max', 30.0)
    else:
        target_aged_pct = 30.0
    metrics['Request_Adherence_Rate'] = (
        100.0 - metrics['Aged_Request_Pct']
    ).round(2)
    
    return metrics


def calculate_pm_metrics(
    problems: pd.DataFrame,
    location_col: str,
    country_col: str,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate Problem Management metrics aggregated by location.
    
    Args:
        problems: Problem DataFrame with calculated flags (Requires_RCA, RCA_OnTime, Is_Major_Problem)
        location_col: Column name for location
        country_col: Column name for country
        config: Configuration dictionary
        
    Returns:
        DataFrame with PM metrics by location
    """
    if problems is None or len(problems) == 0:
        return pd.DataFrame()
    
    # Check if required columns exist
    if location_col not in problems.columns or country_col not in problems.columns:
        return pd.DataFrame()
    
    # Group by location and country
    location_groups = problems.groupby([location_col, country_col])
    
    # Calculate metrics
    # Ensure Location and Country are strings for consistent merging
    location_index = location_groups.size().index
    metrics = pd.DataFrame({
        'Location': [str(loc) for loc, _ in location_index],
        'Country': [str(country) for _, country in location_index],
        'Problem_Volume': location_groups.size().values,
        'Major_Problem_Count': (
            location_groups['Is_Major_Problem'].sum().values 
            if 'Is_Major_Problem' in problems.columns else 0
        ),
        'RCA_Required_Count': (
            location_groups['Requires_RCA'].sum().values 
            if 'Requires_RCA' in problems.columns else 0
        ),
        'RCA_Completed_OnTime_Count': (
            location_groups['RCA_OnTime'].sum().values 
            if 'RCA_OnTime' in problems.columns else 0
        ),
    })
    
    # Calculate RCA completion rate
    metrics['RCA_Completion_Rate'] = (
        (metrics['RCA_Completed_OnTime_Count'] / metrics['RCA_Required_Count'] * 100).round(2)
        if metrics['RCA_Required_Count'].sum() > 0 else 0.0
    )
    
    # Calculate adherence rate (RCA001 target is typically 95%)
    if 'RCA001' in config.get('kpis', {}):
        rca_target = config['kpis']['RCA001']['targets'].get('completion_rate_min', 95.0)
    else:
        rca_target = 95.0
    metrics['RCA_Adherence_Rate'] = metrics['RCA_Completion_Rate'].round(2)
    
    return metrics


def calculate_geographic_okr_scores(
    location_metrics: pd.DataFrame,
    okr_config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate OKR scores (KR3-KR6 and Overall OKR) for each location.
    
    Uses the same scoring logic as OKRCalculator but applied per location.
    
    Args:
        location_metrics: DataFrame with location-level KPI metrics
        okr_config: OKR configuration dictionary
        
    Returns:
        DataFrame with added OKR score columns
    """
    df = location_metrics.copy()
    
    # Initialize OKR score columns
    df['KR3_Score'] = 0.0
    df['KR4_Score'] = 0.0
    df['KR5_Score'] = 0.0
    df['KR6_Score'] = 0.0
    df['Overall_OKR_Score'] = 0.0
    df['Overall_OKR_Status'] = ''
    
    # Calculate KR3 (Major Incidents) - inverse_count scoring
    if 'Major_Incident_Count' in df.columns:
        kr3_config = okr_config['key_results']['KR3']
        target_value = kr3_config['target']['value']
        max_acceptable = kr3_config['scoring'].get('max_acceptable', target_value * 4)
        
        for idx, row in df.iterrows():
            current_value = row.get('Major_Incident_Count', 0)
            raw_score = 100 - (current_value / max_acceptable * 100)
            score = max(0, min(100, raw_score))
            df.at[idx, 'KR3_Score'] = round(score, 1)
    
    # Calculate KR4 (Incident Backlog) - inverse_percentage scoring
    if 'Backlog_Pct' in df.columns:
        kr4_config = okr_config['key_results']['KR4']
        target_value = kr4_config['target']['value']
        
        for idx, row in df.iterrows():
            current_value = row.get('Backlog_Pct', 0)
            raw_score = 100 - (current_value / target_value * 100)
            score = max(0, min(100, raw_score))
            df.at[idx, 'KR4_Score'] = round(score, 1)
    
    # Calculate KR5 (Request Aging) - inverse_percentage scoring
    if 'Aged_Request_Pct' in df.columns:
        kr5_config = okr_config['key_results']['KR5']
        target_value = kr5_config['target']['value']
        
        for idx, row in df.iterrows():
            current_value = row.get('Aged_Request_Pct', 0)
            raw_score = 100 - (current_value / target_value * 100)
            score = max(0, min(100, raw_score))
            df.at[idx, 'KR5_Score'] = round(score, 1)
    
    # Calculate KR6 (First Call Resolution) - direct_percentage scoring
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


def calculate_geographic_overall_score(
    location_metrics: pd.DataFrame,
    config: Dict[str, Any]
) -> pd.DataFrame:
    """
    Calculate overall KPI score for each location using weighted KPI adherence rates.
    
    Args:
        location_metrics: DataFrame with location-level KPI metrics
        config: Configuration dictionary
        
    Returns:
        DataFrame with added overall KPI score columns
    """
    from . import config_loader
    
    df = location_metrics.copy()
    
    # Initialize overall score columns
    df['Overall_KPI_Score'] = 0.0
    df['Overall_KPI_Status'] = ''
    
    # Get KPI weights
    weights = config_loader.get_kpi_weights(config)
    
    # Calculate weighted score for each location
    for idx, row in df.iterrows():
        total_score = 0.0
        total_weight = 0.0
        
        # SM001 adherence
        if 'SM001' in weights and 'Major_Incident_Count' in df.columns:
            # Calculate adherence from major incident count
            # Simplified: if no major incidents, 100%, else calculate based on target
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
        
        # SM002 adherence (from Backlog_Pct)
        if 'SM002' in weights and 'Backlog_Pct' in df.columns:
            backlog_pct = row.get('Backlog_Pct', 0)
            adherence = 100.0 - backlog_pct
            total_score += (adherence * weights['SM002'] / 100)
            total_weight += weights['SM002']
        
        # SM003 adherence (from Request_Adherence_Rate)
        if 'SM003' in weights and 'Request_Adherence_Rate' in df.columns:
            adherence = row.get('Request_Adherence_Rate', 0)
            total_score += (adherence * weights['SM003'] / 100)
            total_weight += weights['SM003']
        
        # SM004 adherence (from FCR_Rate)
        if 'SM004' in weights and 'FCR_Rate' in df.columns:
            fcr_rate = row.get('FCR_Rate', 0)
            adherence = fcr_rate  # FCR rate is already a percentage
            total_score += (adherence * weights['SM004'] / 100)
            total_weight += weights['SM004']
        
        # Calculate overall score
        overall_score = (total_score / total_weight * 100) if total_weight > 0 else 0
        df.at[idx, 'Overall_KPI_Score'] = round(overall_score, 1)
        
        # Determine status based on performance bands
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


def get_intervention_summary(location_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate summary of locations by intervention priority.
    
    Args:
        location_df: Location metrics DataFrame with Intervention_Priority
        
    Returns:
        Dictionary with counts and lists by priority
    """
    priority_counts = location_df['Intervention_Priority'].value_counts().to_dict()
    
    summary = {
        'total_locations': len(location_df),
        'critical_count': priority_counts.get('Critical', 0),
        'high_count': priority_counts.get('High', 0),
        'monitor_count': priority_counts.get('Monitor', 0),
        'standard_count': priority_counts.get('Standard', 0),
        'critical_locations': location_df[
            location_df['Intervention_Priority'] == 'Critical'
        ][['Location', 'Country', 'Total_Volume', 'Backlog_Pct', 'FCR_Rate']].to_dict('records'),
        'high_priority_locations': location_df[
            location_df['Intervention_Priority'] == 'High'
        ][['Location', 'Country', 'Total_Volume', 'Backlog_Pct', 'FCR_Rate']].to_dict('records'),
    }
    
    return summary


def analyze_geography(
    incidents: pd.DataFrame,
    requests: Optional[pd.DataFrame],
    config: Dict[str, Any],
    problems: Optional[pd.DataFrame] = None,
    okr_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main analysis function - analyzes KPI performance by geography.
    
    Combines incidents, requests, and problems (if provided) and calculates:
        - Country-level KPI breakdown
        - Location-level performance ranking with all KPIs and OKRs
        - Volume tier classification
        - Intervention priorities
    
    Args:
        incidents: Incident DataFrame with calculated flags
        requests: Request DataFrame with calculated flags (optional)
        config: Configuration dictionary
        problems: Problem DataFrame with calculated flags (optional)
        okr_config: OKR configuration dictionary (optional, loaded if not provided)
        
    Returns:
        Dictionary containing:
            - country_summary: DataFrame with country metrics
            - location_summary: DataFrame with location metrics (includes all KPIs and OKRs)
            - top_performers: DataFrame with top 10 locations
            - bottom_performers: DataFrame with bottom 10 locations
            - intervention_summary: Dictionary with intervention priorities
    """
    # Load OKR config if not provided
    if okr_config is None:
        try:
            from . import config_loader
            okr_config = config_loader.load_okr_config('config/okr_config.yaml')
        except Exception:
            okr_config = None
    
    # Determine column names from config or data
    # Note: load_data.py renames location_country to 'country'
    country_col = 'country' if 'country' in incidents.columns else 'location_country'
    location_col = 'location'
    
    # Use site name if available and more detailed
    if 'location_u_site_name' in incidents.columns:
        location_col = 'location_u_site_name'
    
    # Calculate incident metrics (base location summary)
    location_summary = calculate_location_metrics(incidents, location_col, country_col, config)
    
    # Ensure Location and Country are strings for consistent merging
    if not location_summary.empty:
        location_summary['Location'] = location_summary['Location'].astype(str)
        location_summary['Country'] = location_summary['Country'].astype(str)
    
    # Calculate request metrics and merge
    if requests is not None and len(requests) > 0:
        # Determine request location column (may differ from incident location column)
        request_location_col = location_col
        if location_col == 'location_u_site_name' and 'location_u_site_name' not in requests.columns:
            # Try alternative location column names for requests
            if 'location' in requests.columns:
                request_location_col = 'location'
            elif 'request_item_u_opened_on_behalf_of_location_u_site_name' in requests.columns:
                requests = requests.copy()
                requests['location_u_site_name'] = requests['request_item_u_opened_on_behalf_of_location_u_site_name']
                request_location_col = 'location_u_site_name'
        
        request_metrics = calculate_request_metrics(requests, request_location_col, country_col, config)
        if not request_metrics.empty:
            # Merge request metrics into location summary
            location_summary = location_summary.merge(
                request_metrics[['Location', 'Country', 'Request_Volume', 'Aged_Request_Count', 
                               'Aged_Request_Pct', 'Request_Adherence_Rate']],
                on=['Location', 'Country'],
                how='outer',
                suffixes=('', '_req')
            )
            # Fill NaN values with 0
            request_cols = ['Request_Volume', 'Aged_Request_Count', 'Aged_Request_Pct', 'Request_Adherence_Rate']
            for col in request_cols:
                if col in location_summary.columns:
                    location_summary[col] = location_summary[col].fillna(0)
    
    # Calculate problem management metrics and merge
    if problems is not None and len(problems) > 0:
        # Map problem location columns to standard names
        # Problems use 'location.country' and 'location.name' or 'location.u_site_name'
        problems_copy = problems.copy()
        problem_country_col = 'country'
        problem_location_col = 'location'
        
        # Check for problem location columns and map them to standard names
        if 'location.country' in problems_copy.columns:
            problems_copy['country'] = problems_copy['location.country']
            problem_country_col = 'country'
        elif 'country' in problems_copy.columns:
            problem_country_col = 'country'
        
        if 'location.name' in problems_copy.columns:
            problems_copy['location'] = problems_copy['location.name']
            problem_location_col = 'location'
        elif 'location.u_site_name' in problems_copy.columns:
            problems_copy['location'] = problems_copy['location.u_site_name']
            problem_location_col = 'location'
        elif 'location' in problems_copy.columns:
            problem_location_col = 'location'
        elif 'location_u_site_name' in problems_copy.columns:
            problems_copy['location'] = problems_copy['location_u_site_name']
            problem_location_col = 'location'
        
        pm_metrics = calculate_pm_metrics(problems_copy, problem_location_col, problem_country_col, config)
        if not pm_metrics.empty:
            # Merge PM metrics into location summary
            location_summary = location_summary.merge(
                pm_metrics[['Location', 'Country', 'Problem_Volume', 'Major_Problem_Count',
                           'RCA_Required_Count', 'RCA_Completed_OnTime_Count',
                           'RCA_Completion_Rate', 'RCA_Adherence_Rate']],
                on=['Location', 'Country'],
                how='outer',
                suffixes=('', '_pm')
            )
            # Fill NaN values with 0
            pm_cols = ['Problem_Volume', 'Major_Problem_Count', 'RCA_Required_Count',
                      'RCA_Completed_OnTime_Count', 'RCA_Completion_Rate', 'RCA_Adherence_Rate']
            for col in pm_cols:
                if col in location_summary.columns:
                    location_summary[col] = location_summary[col].fillna(0)
    
    # Calculate OKR scores if OKR config is available
    if okr_config is not None:
        location_summary = calculate_geographic_okr_scores(location_summary, okr_config)
    
    # Calculate overall KPI score
    location_summary = calculate_geographic_overall_score(location_summary, config)
    
    # Recalculate volume tier based on total volume (incidents + requests if available)
    if 'Request_Volume' in location_summary.columns:
        total_volume = location_summary['Total_Volume'].fillna(0) + location_summary['Request_Volume'].fillna(0)
    else:
        total_volume = location_summary['Total_Volume'].fillna(0)
    
    location_summary['Volume_Tier'] = total_volume.apply(
        lambda x: classify_volume_tier(int(x), config)['tier']
    )
    location_summary['Volume_Tier_Name'] = total_volume.apply(
        lambda x: classify_volume_tier(int(x), config)['tier_name']
    )
    
    # Recalculate intervention priority with updated metrics
    location_summary['Intervention_Priority'] = location_summary.apply(
        lambda row: identify_intervention_priority(row, config),
        axis=1
    )
    
    # Sort by total volume descending
    location_summary = location_summary.sort_values('Total_Volume', ascending=False, na_position='last')
    
    # Calculate country-level metrics (simplified - aggregate from location)
    agg_dict = {
        'Total_Volume': 'sum',
        'Backlog_Count': 'sum',
        'Major_Incident_Count': 'sum',
        'FCR_Count': 'sum',
    }
    
    # Add request columns if they exist
    if 'Request_Volume' in location_summary.columns:
        agg_dict['Request_Volume'] = 'sum'
    if 'Aged_Request_Count' in location_summary.columns:
        agg_dict['Aged_Request_Count'] = 'sum'
    
    # Add problem columns if they exist
    if 'Problem_Volume' in location_summary.columns:
        agg_dict['Problem_Volume'] = 'sum'
    if 'RCA_Required_Count' in location_summary.columns:
        agg_dict['RCA_Required_Count'] = 'sum'
    
    country_summary = location_summary.groupby('Country').agg(agg_dict).reset_index()
    
    # Calculate country percentages
    country_summary['Backlog_Pct'] = (
        (country_summary['Backlog_Count'] / country_summary['Total_Volume'] * 100).round(2)
        if country_summary['Total_Volume'].sum() > 0 else 0
    )
    country_summary['FCR_Rate'] = (
        (country_summary['FCR_Count'] / country_summary['Total_Volume'] * 100).round(2)
        if country_summary['Total_Volume'].sum() > 0 else 0
    )
    country_summary['Major_Incident_Rate'] = (
        (country_summary['Major_Incident_Count'] / country_summary['Total_Volume'] * 100).round(2)
        if country_summary['Total_Volume'].sum() > 0 else 0
    )
    
    if 'Aged_Request_Count' in country_summary.columns:
        country_summary['Aged_Request_Pct'] = (
            (country_summary['Aged_Request_Count'] / country_summary['Request_Volume'] * 100).round(2)
            if country_summary['Request_Volume'].sum() > 0 else 0
        )
    
    # Get top performers (best FCR, lowest backlog)
    top_performers = get_top_performers(location_summary, n=10, sort_by='FCR_Rate')
    
    # Get bottom performers (need intervention)
    bottom_performers = get_bottom_performers(location_summary, n=10, sort_by='FCR_Rate')
    
    # Generate intervention summary
    intervention_summary = get_intervention_summary(location_summary)
    
    return {
        'country_summary': country_summary,
        'location_summary': location_summary,
        'top_performers': top_performers,
        'bottom_performers': bottom_performers,
        'intervention_summary': intervention_summary
    }


# Standalone test code
if __name__ == "__main__":
    """
    Test the geographic analysis module with sample data.
    """
    print("Geographic Analysis Module - Test Mode")
    print("=" * 60)
    
    # This would normally import from other modules
    # For testing, we'll create sample data
    
    # Create sample incident data
    sample_data = pd.DataFrame({
        'location_country': ['USA', 'USA', 'UK', 'UK', 'Germany'] * 50,
        'location': ['Site_A', 'Site_B', 'Site_C', 'Site_D', 'Site_E'] * 50,
        'location_u_site_name': ['New York HQ', 'Chicago Office', 'London Office', 
                                  'Manchester Site', 'Berlin Office'] * 50,
        'Is_Backlog': [True, False, True, False, True] * 50,
        'Is_Major_Incident': [False, False, True, False, False] * 50,
        'Is_First_Call_Resolution': [True, True, False, True, False] * 50,
        'Is_First_Time_Fix': [True, True, True, True, False] * 50,
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
            'SM004': {'targets': {'fcr_min': 0.80}},
        }
    }
    
    # Run analysis
    results = analyze_geography(sample_data, None, sample_config)
    
    print("\n1. COUNTRY SUMMARY")
    print("-" * 60)
    print(results['country_summary'].to_string(index=False))
    
    print("\n2. LOCATION SUMMARY (Top 5)")
    print("-" * 60)
    print(results['location_summary'].head().to_string(index=False))
    
    print("\n3. TOP PERFORMERS")
    print("-" * 60)
    print(results['top_performers'][['Location', 'Country', 'FCR_Rate', 'Backlog_Pct']].to_string(index=False))
    
    print("\n4. INTERVENTION SUMMARY")
    print("-" * 60)
    for key, value in results['intervention_summary'].items():
        if not isinstance(value, list):
            print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
