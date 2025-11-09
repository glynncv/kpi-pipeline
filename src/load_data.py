"""
Data loading module for KPI pipeline.
Loads and preprocesses incident and request CSV files.
"""

import pandas as pd
import re
from typing import Dict, Any, List
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


def _parse_date_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Parse specified columns as datetime.

    Args:
        df: DataFrame to process
        columns: List of column names to parse as dates

    Returns:
        DataFrame with parsed date columns
    """
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df


def _calculate_days_metrics(df: pd.DataFrame, has_resolved: bool = True) -> pd.DataFrame:
    """
    Calculate day-based metrics (days open, days to resolve).

    Args:
        df: DataFrame with date columns
        has_resolved: Whether to calculate days_to_resolve metric

    Returns:
        DataFrame with added day metrics
    """
    df = df.copy()
    current_time = pd.Timestamp.now()

    if 'opened_at' in df.columns:
        df['Days_Open'] = (current_time - df['opened_at']).dt.total_seconds() / 86400

    if has_resolved and 'resolved_at' in df.columns and 'opened_at' in df.columns:
        df['Days_To_Resolve'] = (df['resolved_at'] - df['opened_at']).dt.total_seconds() / 86400

    return df


def _rename_incident_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename incident-specific columns to standard names.

    Args:
        df: Incident DataFrame

    Returns:
        DataFrame with renamed columns
    """
    rename_map = {}
    if 'u_resolved' in df.columns:
        rename_map['u_resolved'] = 'resolved_at'
    if 'incident_state' in df.columns:
        rename_map['incident_state'] = 'state'
    if 'location_country' in df.columns:
        rename_map['location_country'] = 'country'

    return df.rename(columns=rename_map) if rename_map else df


def _apply_column_mappings(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Apply column mappings from config to DataFrame.

    Args:
        df: DataFrame to process
        config: Configuration dictionary

    Returns:
        DataFrame with renamed columns
    """
    col_map = config.get('column_mappings', {})
    rename_map = {}

    for standard_name, actual_name in col_map.items():
        # Skip nested dictionaries (like problem_data, task_data)
        if isinstance(actual_name, dict):
            continue
        # Only process string values (column name mappings)
        if isinstance(actual_name, str) and actual_name in df.columns:
            rename_map[actual_name] = standard_name

    return df.rename(columns=rename_map) if rename_map else df


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
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Incidents file not found: {filepath}")

    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} incidents from {filepath}")

    # Apply transformations
    df = _rename_incident_columns(df)
    df = _parse_date_columns(df, ['opened_at', 'resolved_at', 'closed_at', 'sys_created_on'])
    df = _add_priority_number(df, config)
    df = _fill_reassignment_count(df)
    df = _calculate_days_metrics(df, has_resolved=True)

    _log_incident_processing(df)
    return df


def _add_priority_number(df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """Extract numeric priority from priority string column."""
    if 'priority' in df.columns:
        fallback = config['processing']['priority_extraction']['fallback_value']
        df = df.copy()
        df['Priority_Number'] = df['priority'].apply(
            lambda x: extract_priority_number(x, fallback)
        )
    return df


def _fill_reassignment_count(df: pd.DataFrame) -> pd.DataFrame:
    """Fill null reassignment counts with 0."""
    if 'reassignment_count' in df.columns:
        df = df.copy()
        df['reassignment_count'] = df['reassignment_count'].fillna(0).astype(int)
    return df


def _log_incident_processing(df: pd.DataFrame) -> None:
    """Log processing statistics for incidents."""
    date_col_count = sum(df.columns.str.contains('_at'))
    print(f"[OK] Parsed {date_col_count} date columns")

    if 'Priority_Number' in df.columns:
        print(f"[OK] Extracted priority numbers (range: {df['Priority_Number'].min()}-{df['Priority_Number'].max()})")

    if 'reassignment_count' in df.columns:
        null_count = df['reassignment_count'].isna().sum()
        print(f"[OK] Filled {null_count} null reassignment counts")


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
    if not Path(filepath).exists():
        raise FileNotFoundError(f"Requests file not found: {filepath}")

    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} requests from {filepath}")

    # Apply transformations
    df = _apply_column_mappings(df, config)
    df = _parse_date_columns(df, ['opened_at', 'closed_at', 'due_date', 'expected_start', 'sys_created_on'])
    df = _add_days_to_close(df)
    df = _rename_request_location_columns(df)

    _log_request_processing(df)
    return df


def _add_days_to_close(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate days to close for closed requests."""
    df = _calculate_days_metrics(df, has_resolved=False)

    if 'closed_at' in df.columns and 'opened_at' in df.columns:
        df = df.copy()
        df['Days_To_Close'] = (df['closed_at'] - df['opened_at']).dt.total_seconds() / 86400

    return df


def _rename_request_location_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename request-specific location columns for consistency."""
    rename_map = {}
    if 'request_item_u_opened_on_behalf_of_location_country' in df.columns:
        rename_map['request_item_u_opened_on_behalf_of_location_country'] = 'country'

    return df.rename(columns=rename_map) if rename_map else df


def _log_request_processing(df: pd.DataFrame) -> None:
    """Log processing statistics for requests."""
    date_col_count = sum(df.columns.str.contains('_at|date'))
    print(f"[OK] Parsed {date_col_count} date columns")


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
        print(f"\n[OK] Loaded incidents: {len(incidents)} rows")
        print(f"[OK] Columns: {list(incidents.columns[:10])}...")
        
        # Test request loading
        requests = load_requests('data/PYTHON EMEA SCT last 90 days_redacted_clean.csv', config)
        print(f"\n[OK] Loaded requests: {len(requests)} rows")
        print(f"[OK] Columns: {list(requests.columns[:10])}...")
        
    except Exception as e:
        print(f"[FAIL] Error: {e}")
