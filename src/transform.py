"""
Transform module for KPI pipeline.
Adds calculated fields to incident and request data.
"""

import pandas as pd
from typing import Dict, Any


def add_incident_flags(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Add calculated boolean flags to incident DataFrame.
    
    Flags added:
        - Is_Major_Incident: Priority 1 or 2
        - Is_Backlog: Incident aged beyond threshold
        - Is_First_Time_Fix: Zero reassignments
        - Is_First_Call_Resolution: Zero reassignments AND excluded contact types
        
    Args:
        df: Incident DataFrame
        config: Configuration dictionary
        
    Returns:
        DataFrame with added flag columns
    """
    df = df.copy()
    
    # Get thresholds from config
    major_priorities = config['thresholds']['priority']['major_incident_levels']
    backlog_threshold = config['thresholds']['aging']['backlog_days']
    
    # Flag: Major Incident (P1 or P2)
    df['Is_Major_Incident'] = df['Priority_Number'].isin(major_priorities)
    
    # Flag: Backlog
    # Business rule: (Resolved AND >10 days) OR (Not Resolved AND >10 days)
    resolved_mask = df['resolved_at'].notna()
    aged_resolved = resolved_mask & (df['Days_To_Resolve'] > backlog_threshold)
    aged_unresolved = (~resolved_mask) & (df['Days_Open'] > backlog_threshold)
    df['Is_Backlog'] = aged_resolved | aged_unresolved
    
    # Flag: First Time Fix (zero reassignments)
    df['Is_First_Time_Fix'] = df['reassignment_count'] == 0
    
    # Flag: First Call Resolution (First Time Fix + not excluded contact type)
    excluded_contact_types = config['kpis']['SM004'].get('exclusions', {}).get('contact_types', [])
    
    if 'contact_type' in df.columns:
        not_excluded = ~df['contact_type'].isin(excluded_contact_types)
        df['Is_First_Call_Resolution'] = df['Is_First_Time_Fix'] & not_excluded
    else:
        # If no contact_type column, FCR = FTF
        df['Is_First_Call_Resolution'] = df['Is_First_Time_Fix']
    
    # Additional useful flags
    df['Is_Resolved'] = df['resolved_at'].notna()
    df['Is_P1'] = df['Priority_Number'] == 1
    df['Is_P2'] = df['Priority_Number'] == 2
    
    return df


def add_request_flags(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Add calculated boolean flags to request DataFrame.
    
    Flags added:
        - Is_Aged: Request aged beyond threshold
        - Is_Closed: Request is closed
        
    Args:
        df: Request DataFrame
        config: Configuration dictionary
        
    Returns:
        DataFrame with added flag columns
    """
    df = df.copy()
    
    # Get threshold from config
    aging_threshold = config['thresholds']['aging'].get('request_aging_days', 30)
    
    # Flag: Aged Request
    # Business rule: Open for more than threshold days
    df['Is_Aged'] = df['Days_Open'] > aging_threshold
    
    # Flag: Closed
    df['Is_Closed'] = df['closed_at'].notna()
    
    return df


def create_summary_stats(df: pd.DataFrame, group_by: str = None) -> pd.DataFrame:
    """
    Create summary statistics DataFrame.
    
    Args:
        df: Input DataFrame
        group_by: Optional column to group by
        
    Returns:
        Summary statistics DataFrame
    """
    if group_by and group_by in df.columns:
        return df.groupby(group_by).agg({
            'number': 'count',
            'Is_Major_Incident': 'sum',
            'Is_Backlog': 'sum',
            'Is_First_Time_Fix': 'sum'
        }).rename(columns={'number': 'Total_Count'})
    else:
        return pd.DataFrame({
            'Total_Count': [len(df)],
            'Major_Incidents': [df['Is_Major_Incident'].sum()],
            'Backlog': [df['Is_Backlog'].sum()],
            'First_Time_Fix': [df['Is_First_Time_Fix'].sum()]
        })


if __name__ == "__main__":
    # Test transform functions
    import config_loader
    import load_data
    
    try:
        config = config_loader.load_config()
        
        # Load and transform incidents
        incidents = load_data.load_incidents(
            'data/PYTHON EMEA IM last 90 days_redacted_clean.csv', 
            config
        )
        incidents = add_incident_flags(incidents, config)
        
        print("\n=== INCIDENT TRANSFORM RESULTS ===")
        print(f"Total incidents: {len(incidents)}")
        print(f"Major incidents (P1+P2): {incidents['Is_Major_Incident'].sum()}")
        print(f"  - P1: {incidents['Is_P1'].sum()}")
        print(f"  - P2: {incidents['Is_P2'].sum()}")
        print(f"Backlog incidents: {incidents['Is_Backlog'].sum()} ({incidents['Is_Backlog'].sum()/len(incidents)*100:.1f}%)")
        print(f"First Time Fix: {incidents['Is_First_Time_Fix'].sum()} ({incidents['Is_First_Time_Fix'].sum()/len(incidents)*100:.1f}%)")
        print(f"First Call Resolution: {incidents['Is_First_Call_Resolution'].sum()} ({incidents['Is_First_Call_Resolution'].sum()/len(incidents)*100:.1f}%)")
        
        # Load and transform requests (if enabled)
        if config_loader.is_kpi_enabled(config, 'SM003'):
            requests = load_data.load_requests(
                'data/PYTHON EMEA SCT last 90 days_redacted_clean.csv',
                config
            )
            requests = add_request_flags(requests, config)
            
            print("\n=== REQUEST TRANSFORM RESULTS ===")
            print(f"Total requests: {len(requests)}")
            print(f"Aged requests: {requests['Is_Aged'].sum()} ({requests['Is_Aged'].sum()/len(requests)*100:.1f}%)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
