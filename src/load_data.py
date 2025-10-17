"""
Data loading module for KPI pipeline.
Loads and preprocesses incident and request CSV files.
"""

import pandas as pd
import re
from typing import Dict, Any
from pathlib import Path


def extract_priority_number(priority_str: str, fallback: int = 99) -> int:
    """
    Extract numeric priority from priority string.
    
    Examples:
        "1 - Critical" -> 1
        "2 - High" -> 2
        "3 - Medium" -> 3
        "4 - Low" -> 4
        
    Args:
        priority_str: Priority string from CSV
        fallback: Fallback value for unparseable priorities
        
    Returns:
        Numeric priority (1-4 or fallback value)
    """
    if pd.isna(priority_str):
        return fallback
    
    # Extract first number from string
    match = re.search(r'\d+', str(priority_str))
    if match:
        return int(match.group())
    
    return fallback


def load_incidents(filepath: str, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Load and preprocess incident data from CSV.
    
    Args:
        filepath: Path to incidents CSV file
        config: Configuration dictionary
        
    Returns:
        DataFrame with preprocessed incident data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
    """
    # Check file exists
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Incidents file not found: {filepath}")
    
    # Load CSV
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} incidents from {filepath}")
    
    # Get column mappings
    col_map = config['column_mappings']
    
    # Rename columns to standardized names
    rename_map = {}
    if 'u_resolved' in df.columns:
        rename_map['u_resolved'] = 'resolved_at'
    if 'incident_state' in df.columns:
        rename_map['incident_state'] = 'state'
    if 'location_country' in df.columns:
        rename_map['location_country'] = 'country'
    
    if rename_map:
        df = df.rename(columns=rename_map)
    
    # Parse date columns
    date_columns = ['opened_at', 'resolved_at', 'closed_at', 'sys_created_on']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Extract numeric priority
    if 'priority' in df.columns:
        df['Priority_Number'] = df['priority'].apply(
            lambda x: extract_priority_number(x, config['processing']['priority_extraction']['fallback_value'])
        )
    
    # Handle null reassignment_count (treat as 0)
    if 'reassignment_count' in df.columns:
        df['reassignment_count'] = df['reassignment_count'].fillna(0).astype(int)
    
    # Calculate days to resolve (for resolved incidents)
    if 'resolved_at' in df.columns and 'opened_at' in df.columns:
        df['Days_To_Resolve'] = (df['resolved_at'] - df['opened_at']).dt.total_seconds() / 86400
    
    # Calculate days open (for all incidents)
    if 'opened_at' in df.columns:
        current_time = pd.Timestamp.now()
        df['Days_Open'] = (current_time - df['opened_at']).dt.total_seconds() / 86400
    
    print(f"✓ Parsed {sum(df.columns.str.contains('_at'))} date columns")
    print(f"✓ Extracted priority numbers (range: {df['Priority_Number'].min()}-{df['Priority_Number'].max()})")
    print(f"✓ Filled {df['reassignment_count'].isna().sum()} null reassignment counts")
    
    return df


def load_requests(filepath: str, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Load and preprocess request data from CSV.
    
    Args:
        filepath: Path to requests CSV file
        config: Configuration dictionary
        
    Returns:
        DataFrame with preprocessed request data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
    """
    # Check file exists
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Requests file not found: {filepath}")
    
    # Load CSV
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} requests from {filepath}")
    
    # Parse date columns
    date_columns = ['opened_at', 'closed_at', 'due_date', 'expected_start', 'sys_created_on']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    # Calculate days open
    if 'opened_at' in df.columns:
        current_time = pd.Timestamp.now()
        df['Days_Open'] = (current_time - df['opened_at']).dt.total_seconds() / 86400
    
    # Calculate days to close (for closed requests)
    if 'closed_at' in df.columns and 'opened_at' in df.columns:
        df['Days_To_Close'] = (df['closed_at'] - df['opened_at']).dt.total_seconds() / 86400
    
    # Rename location columns for consistency
    rename_map = {}
    if 'request_item_u_opened_on_behalf_of_location_country' in df.columns:
        rename_map['request_item_u_opened_on_behalf_of_location_country'] = 'country'
    
    if rename_map:
        df = df.rename(columns=rename_map)
    
    print(f"✓ Parsed {sum(df.columns.str.contains('_at|date'))} date columns")
    
    return df


def validate_data(df: pd.DataFrame, required_columns: list) -> bool:
    """
    Validate that DataFrame contains required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        
    Returns:
        True if all required columns present, False otherwise
    """
    missing = set(required_columns) - set(df.columns)
    if missing:
        print(f"Warning: Missing required columns: {missing}")
        return False
    return True


if __name__ == "__main__":
    # Test data loading
    import config_loader
    
    try:
        config = config_loader.load_config()
        
        # Test incident loading
        incidents = load_incidents('data/PYTHON EMEA IM last 90 days_redacted_clean.csv', config)
        print(f"\n✓ Loaded incidents: {len(incidents)} rows")
        print(f"✓ Columns: {list(incidents.columns[:10])}...")
        
        # Test request loading
        requests = load_requests('data/PYTHON EMEA SCT last 90 days_redacted_clean.csv', config)
        print(f"\n✓ Loaded requests: {len(requests)} rows")
        print(f"✓ Columns: {list(requests.columns[:10])}...")
        
    except Exception as e:
        print(f"✗ Error: {e}")
