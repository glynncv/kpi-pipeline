"""
KPI calculation module for KPI pipeline.
Calculates all KPIs and determines overall status.
"""

import pandas as pd
from typing import Dict, Any, Tuple


def calculate_sm001_major_incidents(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate SM001: Major Incidents (P1 & P2).
    
    Args:
        df: Incident DataFrame with calculated flags
        config: Configuration dictionary
        
    Returns:
        Dictionary with KPI results
    """
    kpi_config = config['kpis']['SM001']
    
    # Count P1 and P2 incidents
    p1_count = df['Is_P1'].sum()
    p2_count = df['Is_P2'].sum()
    total_major = df['Is_Major_Incident'].sum()
    
    # Get targets
    p1_max = kpi_config['targets']['p1_max']
    p2_max = kpi_config['targets']['p2_max']
    
    # Determine status
    if p1_count > p1_max:
        status = "Critical"
        adherence_rate = 0.0
    elif p2_count > p2_max:
        status = "Warning"
        adherence_rate = 50.0
    else:
        status = "Met"
        adherence_rate = 100.0
    
    return {
        'KPI_Code': 'SM001',
        'KPI_Name': kpi_config['name'],
        'P1_Count': int(p1_count),
        'P2_Count': int(p2_count),
        'Total_Major': int(total_major),
        'P1_Target': p1_max,
        'P2_Target': p2_max,
        'Status': status,
        'Adherence_Rate': adherence_rate,
        'Business_Impact': kpi_config['business_impact']
    }


def calculate_sm002_backlog(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate SM002/KR4: ServiceNow Backlog.
    
    Args:
        df: Incident DataFrame with calculated flags
        config: Configuration dictionary
        
    Returns:
        Dictionary with KPI results
    """
    kpi_config = config['kpis']['SM002']
    
    # Count total and backlog
    total_incidents = len(df)
    backlog_count = df['Is_Backlog'].sum()
    backlog_percentage = (backlog_count / total_incidents * 100) if total_incidents > 0 else 0
    
    # Calculate adherence (inverse of backlog %)
    adherence_rate = 100.0 - backlog_percentage
    
    # Get target
    target_adherence = kpi_config['targets']['adherence_min']
    
    # Determine status
    if adherence_rate >= target_adherence:
        status = "Met"
    elif adherence_rate >= 80:
        status = "Warning"
    else:
        status = "Critical"
    
    return {
        'KPI_Code': 'SM002/KR4',
        'KPI_Name': kpi_config['name'],
        'Total_Incidents': int(total_incidents),
        'Backlog_Count': int(backlog_count),
        'Backlog_Percentage': round(backlog_percentage, 1),
        'Adherence_Rate': round(adherence_rate, 1),
        'Target_Adherence': target_adherence,
        'Status': status,
        'Business_Impact': kpi_config['business_impact']
    }


def calculate_kr5_request_aging(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate KR5: Service Request Aging.
    
    Args:
        df: Request DataFrame with calculated flags
        config: Configuration dictionary
        
    Returns:
        Dictionary with KPI results
    """
    kpi_config = config['kpis']['SM003']
    
    # Count total and aged
    total_requests = len(df)
    aged_count = df['Is_Aged'].sum()
    aged_percentage = (aged_count / total_requests * 100) if total_requests > 0 else 0
    
    # Calculate adherence (inverse of aged %)
    adherence_rate = 100.0 - aged_percentage
    
    # Get target
    target_adherence = kpi_config['targets']['adherence_min']
    
    # Determine status
    if adherence_rate >= target_adherence:
        status = "Met"
    elif adherence_rate >= 80:
        status = "Warning"
    else:
        status = "Critical"
    
    return {
        'KPI_Code': 'KR5',
        'KPI_Name': kpi_config['name'],
        'Total_Requests': int(total_requests),
        'Aged_Count': int(aged_count),
        'Aged_Percentage': round(aged_percentage, 1),
        'Adherence_Rate': round(adherence_rate, 1),
        'Target_Adherence': target_adherence,
        'Status': status,
        'Business_Impact': kpi_config['business_impact']
    }


def calculate_sm004_fcr(df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate SM004/KR6: First Call Resolution Rate.
    
    Args:
        df: Incident DataFrame with calculated flags
        config: Configuration dictionary
        
    Returns:
        Dictionary with KPI results
    """
    kpi_config = config['kpis']['SM004']
    
    # Count resolved incidents only
    resolved_df = df[df['Is_Resolved']]
    total_resolved = len(resolved_df)
    
    # Count first call resolutions (zero reassignments + not excluded contact type)
    fcr_count = resolved_df['Is_First_Call_Resolution'].sum()
    fcr_percentage = (fcr_count / total_resolved * 100) if total_resolved > 0 else 0
    
    # Get target
    target_rate = kpi_config['targets']['ftf_rate_min']
    
    # Determine status
    if fcr_percentage >= target_rate:
        status = "Met"
    elif fcr_percentage >= (target_rate - 10):
        status = "Warning"
    else:
        status = "Critical"
    
    return {
        'KPI_Code': 'SM004/KR6',
        'KPI_Name': kpi_config['name'],
        'Total_Resolved': int(total_resolved),
        'FCR_Count': int(fcr_count),
        'FCR_Percentage': round(fcr_percentage, 1),
        'Target_Rate': target_rate,
        'Status': status,
        'Adherence_Rate': round(fcr_percentage, 1),
        'Business_Impact': kpi_config['business_impact']
    }


def _get_kpi_weights(config: Dict[str, Any]) -> Dict[str, float]:
    """
    Get KPI weights, adjusted for disabled KPIs.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of KPI weights
    """
    scorecard = config['global_status_rules']['scorecard_scoring']
    
    # Check if SM003 is enabled
    sm003_enabled = config['kpis']['SM003']['enabled']
    
    if sm003_enabled:
        # Use standard weights
        return {
            'SM001': scorecard['weight_sm001'],
            'SM002': scorecard['weight_sm002'],
            'SM003': scorecard['weight_sm003'],
            'SM004': scorecard['weight_sm004'],
        }
    else:
        # Use adjusted weights when SM003 is disabled
        adjusted = scorecard.get('sm003_disabled_weights', {})
        return {
            'SM001': adjusted.get('weight_sm001', 30),
            'SM002': adjusted.get('weight_sm002', 50),
            'SM004': adjusted.get('weight_sm004', 20),
        }


def calculate_overall_score(kpi_results: Dict[str, Dict], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate overall weighted score across all KPIs.
    
    Args:
        kpi_results: Dictionary of individual KPI results
        config: Configuration dictionary
        
    Returns:
        Dictionary with overall score and status
    """
    # Get weights from configuration
    weights = _get_kpi_weights(config)
    
    # Calculate weighted score
    total_score = 0.0
    total_weight = 0.0
    
    kpi_scores = {}
    
    for kpi_code, weight in weights.items():
        # Map KPI code to result key
        if kpi_code == 'SM001' and 'SM001' in kpi_results:
            adherence = kpi_results['SM001']['Adherence_Rate']
        elif kpi_code == 'SM002' and 'SM002/KR4' in kpi_results:
            adherence = kpi_results['SM002/KR4']['Adherence_Rate']
        elif kpi_code == 'SM004' and 'SM004/KR6' in kpi_results:
            adherence = kpi_results['SM004/KR6']['Adherence_Rate']
        else:
            continue
        
        kpi_scores[kpi_code] = adherence
        total_score += (adherence * weight / 100)
        total_weight += weight
    
    # Calculate weighted average
    overall_score = (total_score / total_weight * 100) if total_weight > 0 else 0
    
    # Determine overall status
    bands = config['global_status_rules']['performance_bands']
    if overall_score >= bands['excellent']:
        overall_status = "Excellent"
    elif overall_score >= bands['good']:
        overall_status = "Good"
    elif overall_score >= bands['needs_improvement']:
        overall_status = "Needs Improvement"
    else:
        overall_status = "Poor"
    
    return {
        'Overall_Score': round(overall_score, 1),
        'Overall_Status': overall_status,
        'Weights_Used': weights,
        'KPI_Scores': kpi_scores,
        'Total_Weight': total_weight
    }


def calculate_all(incidents: pd.DataFrame, requests: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Calculate all enabled KPIs.
    
    Args:
        incidents: Incident DataFrame with calculated flags
        requests: Request DataFrame with calculated flags
        config: Configuration dictionary
        
    Returns:
        Dictionary of all KPI results
    """
    results = {}
    
    # SM001: Major Incidents
    if config['kpis']['SM001']['enabled']:
        results['SM001'] = calculate_sm001_major_incidents(incidents, config)
    
    # SM002/KR4: Backlog
    if config['kpis']['SM002']['enabled']:
        results['SM002/KR4'] = calculate_sm002_backlog(incidents, config)
    
    # KR5: Request Aging (if enabled and data available)
    if config['kpis']['SM003']['enabled'] and requests is not None:
        results['KR5'] = calculate_kr5_request_aging(requests, config)
    
    # SM004/KR6: First Call Resolution
    if config['kpis']['SM004']['enabled']:
        results['SM004/KR6'] = calculate_sm004_fcr(incidents, config)
    
    # Calculate overall score
    results['OVERALL'] = calculate_overall_score(results, config)
    
    return results


if __name__ == "__main__":
    # Test KPI calculations
    import config_loader
    import load_data
    import transform
    
    try:
        config = config_loader.load_config()
        
        # Load and transform incidents
        incidents = load_data.load_incidents(
            'data/PYTHON EMEA IM last 90 days_redacted_clean.csv',
            config
        )
        incidents = transform.add_incident_flags(incidents, config)
        
        # Load and transform requests (if enabled)
        requests = None
        if config['kpis']['SM003']['enabled']:
            requests = load_data.load_requests(
                'data/PYTHON EMEA SCT last 90 days_redacted_clean.csv',
                config
            )
            requests = transform.add_request_flags(requests, config)
        
        # Calculate all KPIs
        results = calculate_all(incidents, requests, config)
        
        print("\n=== KPI CALCULATION RESULTS ===\n")
        
        for kpi_code, kpi_data in results.items():
            if kpi_code == 'OVERALL':
                print(f"\n{'='*50}")
                print(f"OVERALL PERFORMANCE")
                print(f"{'='*50}")
                print(f"Score: {kpi_data['Overall_Score']}%")
                print(f"Status: {kpi_data['Overall_Status']}")
                print(f"Weights: {kpi_data['Weights_Used']}")
            else:
                print(f"\n{kpi_code}: {kpi_data['KPI_Name']}")
                print(f"  Status: {kpi_data['Status']}")
                print(f"  Adherence: {kpi_data['Adherence_Rate']}%")
                
                # Print KPI-specific details
                if 'P1_Count' in kpi_data:
                    print(f"  P1: {kpi_data['P1_Count']} (target: ≤{kpi_data['P1_Target']})")
                    print(f"  P2: {kpi_data['P2_Count']} (target: ≤{kpi_data['P2_Target']})")
                elif 'Backlog_Count' in kpi_data:
                    print(f"  Backlog: {kpi_data['Backlog_Count']} incidents ({kpi_data['Backlog_Percentage']}%)")
                elif 'Aged_Count' in kpi_data:
                    print(f"  Aged: {kpi_data['Aged_Count']} requests ({kpi_data['Aged_Percentage']}%)")
                elif 'FCR_Count' in kpi_data:
                    print(f"  FCR: {kpi_data['FCR_Count']}/{kpi_data['Total_Resolved']} ({kpi_data['FCR_Percentage']}%)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
