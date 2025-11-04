"""
Configuration loader for KPI pipeline.
Loads and validates the YAML configuration file.
"""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config/kpi_config.yaml") -> Dict[str, Any]:
    """
    Load KPI configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        Dictionary containing configuration data
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        yaml.YAMLError: If configuration file is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Validate required sections
    required_sections = ['column_mappings', 'thresholds', 'kpis']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    return config


def load_okr_config(okr_config_path: str = "config/okr_config.yaml") -> Dict[str, Any]:
    """
    Load OKR configuration from YAML file.
    
    Args:
        okr_config_path: Path to the OKR YAML configuration file
        
    Returns:
        Dictionary containing OKR configuration data
        
    Raises:
        FileNotFoundError: If OKR configuration file doesn't exist
        yaml.YAMLError: If OKR configuration file is invalid
    """
    config_file = Path(okr_config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"OKR configuration file not found: {okr_config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def load_all_configs(kpi_config_path: str = "config/kpi_config.yaml", 
                     okr_config_path: str = "config/okr_config.yaml") -> Dict[str, Any]:
    """
    Load both KPI and OKR configurations and merge them.
    
    Args:
        kpi_config_path: Path to the KPI YAML configuration file
        okr_config_path: Path to the OKR YAML configuration file
        
    Returns:
        Dictionary containing merged configuration data
        
    Raises:
        FileNotFoundError: If any configuration file doesn't exist
        yaml.YAMLError: If any configuration file is invalid
    """
    kpi_config = load_config(kpi_config_path)
    okr_config = load_okr_config(okr_config_path)
    
    # Merge configs
    merged_config = kpi_config.copy()
    merged_config['okr'] = okr_config
    
    return merged_config


def get_column_mapping(config: Dict[str, Any], field_name: str) -> str:
    """
    Get the CSV column name for a given field.
    
    Args:
        config: Configuration dictionary
        field_name: Internal field name (e.g., 'resolved_at')
        
    Returns:
        CSV column name (e.g., 'u_resolved')
    """
    return config['column_mappings'].get(field_name, field_name)


def get_threshold(config: Dict[str, Any], threshold_type: str, threshold_name: str) -> Any:
    """
    Get a specific threshold value from configuration.
    
    Args:
        config: Configuration dictionary
        threshold_type: Type of threshold (e.g., 'aging', 'priority')
        threshold_name: Name of threshold (e.g., 'backlog_days')
        
    Returns:
        Threshold value
    """
    return config['thresholds'][threshold_type][threshold_name]


def get_kpi_config(config: Dict[str, Any], kpi_code: str) -> Dict[str, Any]:
    """
    Get configuration for a specific KPI.
    
    Args:
        config: Configuration dictionary
        kpi_code: KPI code (e.g., 'SM001', 'SM002')
        
    Returns:
        KPI configuration dictionary
        
    Raises:
        KeyError: If KPI code doesn't exist in configuration
    """
    if kpi_code not in config['kpis']:
        raise KeyError(f"KPI {kpi_code} not found in configuration")
    
    return config['kpis'][kpi_code]


def is_kpi_enabled(config: Dict[str, Any], kpi_code: str) -> bool:
    """
    Check if a KPI is enabled in the configuration.
    
    Args:
        config: Configuration dictionary
        kpi_code: KPI code (e.g., 'SM001', 'SM002')
        
    Returns:
        True if KPI is enabled, False otherwise
    """
    kpi_config = get_kpi_config(config, kpi_code)
    return kpi_config.get('enabled', False)


def get_kpi_weights(config: Dict[str, Any]) -> Dict[str, float]:
    """
    Get KPI weights, adjusting for disabled KPIs.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of KPI weights
    """
    scoring = config['global_status_rules']['scorecard_scoring']
    
    # Check if SM003 is disabled
    if not is_kpi_enabled(config, 'SM003'):
        return {
            'SM001': scoring['sm003_disabled_weights']['weight_sm001'],
            'SM002': scoring['sm003_disabled_weights']['weight_sm002'],
            'SM004': scoring['sm003_disabled_weights']['weight_sm004']
        }
    else:
        return {
            'SM001': scoring['weight_sm001'],
            'SM002': scoring['weight_sm002'],
            'SM003': scoring['weight_sm003'],
            'SM004': scoring['weight_sm004']
        }


# ============================================================
# PROBLEM MANAGEMENT HELPER FUNCTIONS
# ============================================================

def get_problem_column_mapping(config: Dict[str, Any], field_name: str) -> str:
    """
    Get CSV column name for problem field
    
    Args:
        config: Configuration dictionary
        field_name: Internal field name (e.g., 'u_rca_required')
        
    Returns:
        CSV column name from Problem table export
    """
    column_mappings = config.get('column_mappings', {})
    problem_data = column_mappings.get('problem_data', {})
    return problem_data.get(field_name)


def get_task_column_mapping(config: Dict[str, Any], field_name: str) -> str:
    """
    Get CSV column name for task field
    
    Args:
        config: Configuration dictionary
        field_name: Internal field name (e.g., 'parent_number')
        
    Returns:
        CSV column name from Task/RCA table export
    """
    column_mappings = config.get('column_mappings', {})
    task_data = column_mappings.get('task_data', {})
    return task_data.get(field_name)


def get_rca_timeframe(config: Dict[str, Any], priority: int) -> int:
    """
    Get RCA completion timeframe based on priority
    
    Args:
        config: Configuration dictionary
        priority: Priority number (1, 2, 3, etc.)
        
    Returns:
        int: Days allowed for RCA completion
        
    Example:
        >>> get_rca_timeframe(config, 1)  # P1
        7
        >>> get_rca_timeframe(config, 2)  # P2
        14
    """
    thresholds = config.get('thresholds', {})
    rca_thresholds = thresholds.get('rca', {})
    
    timeframe_map = {
        1: rca_thresholds.get('p1_rca_timeframe_days', 7),
        2: rca_thresholds.get('p2_rca_timeframe_days', 14),
        3: rca_thresholds.get('p3_rca_timeframe_days', 30)
    }
    
    return timeframe_map.get(priority, 30)  # Default to 30 days


def get_rca_targets(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get all RCA001 targets
    
    Args:
        config: Configuration dictionary
        
    Returns:
        dict: RCA001 target configuration
        
    Example:
        >>> targets = get_rca_targets(config)
        >>> targets['completion_rate_expected']
        95.0
    """
    kpis = config.get('kpis', {})
    rca001 = kpis.get('RCA001', {})
    return rca001.get('targets', {})


def get_boolean_processing_config(config: Dict[str, Any]) -> Dict[str, list]:
    """
    Get boolean field processing configuration (for RCA delivered, etc.)
    
    Args:
        config: Configuration dictionary
        
    Returns:
        dict: Contains 'true_values', 'false_values', 'null_values' lists
    """
    processing = config.get('processing', {})
    return processing.get('boolean_processing', {})


def get_rca_stage_config(config: Dict[str, Any]) -> Dict[str, list]:
    """
    Get RCA stage processing configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        dict: Stage classifications (completed, ontime, late, etc.)
    """
    processing = config.get('processing', {})
    return processing.get('rca_stage_processing', {})


def get_problem_filename(config: Dict[str, Any]) -> str:
    """Get expected problem CSV filename"""
    data_files = config.get('data_files', {})
    return data_files.get('problem_file', 'PYTHON_EMEA_PM_P1P2__This_Year_.csv')


def get_task_filename(config: Dict[str, Any]) -> str:
    """Get expected task/RCA CSV filename"""
    data_files = config.get('data_files', {})
    return data_files.get('task_file', 'PYTHON_EMEA_TASK_RCA__This_Year_.csv')


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = load_config()
        print("✓ Configuration loaded successfully")
        print(f"✓ Organization: {config['metadata']['organization']}")
        print(f"✓ Version: {config['metadata']['version']}")
        print(f"✓ KPIs configured: {len(config['kpis'])}")
        
        # Test KPI weights
        weights = get_kpi_weights(config)
        print(f"✓ KPI weights: {weights}")
        print(f"✓ Total weight: {sum(weights.values())}%")
        
    except Exception as e:
        print(f"✗ Error loading configuration: {e}")
