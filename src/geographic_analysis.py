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
    metrics = pd.DataFrame({
        'Location': [loc for loc, _ in location_groups.size().index],
        'Country': [country for _, country in location_groups.size().index],
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
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Main analysis function - analyzes KPI performance by geography.
    
    Combines incidents and requests (if provided) and calculates:
        - Country-level KPI breakdown
        - Location-level performance ranking
        - Volume tier classification
        - Intervention priorities
    
    Args:
        incidents: Incident DataFrame with calculated flags
        requests: Request DataFrame with calculated flags (optional)
        config: Configuration dictionary
        
    Returns:
        Dictionary containing:
            - country_summary: DataFrame with country metrics
            - location_summary: DataFrame with location metrics
            - top_performers: DataFrame with top 10 locations
            - bottom_performers: DataFrame with bottom 10 locations
            - intervention_summary: Dictionary with intervention priorities
    """
    # Determine column names from config or data
    # Note: load_data.py renames location_country to 'country'
    country_col = 'country' if 'country' in incidents.columns else 'location_country'
    location_col = 'location'
    
    # Use site name if available and more detailed
    if 'location_u_site_name' in incidents.columns:
        location_col = 'location_u_site_name'
    
    # Combine incidents and requests if both provided
    if requests is not None and len(requests) > 0:
        # Standardize columns for combining
        incidents_subset = incidents.copy()
        requests_subset = requests.copy()
        
        # Make sure both have the necessary columns
        if country_col in requests.columns and location_col in requests.columns:
            combined = pd.concat([incidents_subset, requests_subset], ignore_index=True)
        else:
            combined = incidents.copy()
    else:
        combined = incidents.copy()
    
    # Calculate country-level metrics
    country_summary = calculate_country_metrics(combined, country_col, config)
    
    # Calculate location-level metrics
    location_summary = calculate_location_metrics(combined, location_col, country_col, config)
    
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
