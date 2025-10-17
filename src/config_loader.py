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
