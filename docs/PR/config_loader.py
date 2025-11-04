"""
Configuration Loader for KPI Pipeline
Loads YAML configuration and provides convenient access methods

Version: 2.1 - Added Problem Management support
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass


class Config:
    """
    Configuration loader and accessor for KPI pipeline
    
    Loads kpi_config.yaml and provides methods to access:
    - Column mappings (CSV columns -> internal field names)
    - Thresholds (backlog days, RCA timeframes, etc.)
    - KPI targets and weights
    - Processing rules
    """
    
    def __init__(self, config_path: str = 'config/kpi_config.yaml'):
        """
        Initialize configuration loader
        
        Args:
            config_path: Path to YAML configuration file
            
        Raises:
            ConfigError: If config file not found or invalid
        """
        self.config_path = Path(config_path)
        
        if not self.config_path.exists():
            raise ConfigError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please ensure kpi_config.yaml exists in the config/ directory"
            )
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            raise ConfigError(f"Error loading configuration: {e}")
        
        # Cache frequently accessed sections
        self._column_mappings = self.config.get('column_mappings', {})
        self._thresholds = self.config.get('thresholds', {})
        self._kpis = self.config.get('kpis', {})
        self._processing = self.config.get('processing', {})
        self._scorecard = self.config.get('scorecard', {})
        self._data_files = self.config.get('data_files', {})
    
    # ============================================================
    # COLUMN MAPPING METHODS
    # ============================================================
    
    def get_incident_column_mapping(self, field_name: str) -> str:
        """
        Get CSV column name for incident field
        
        Args:
            field_name: Internal field name (e.g., 'opened_at')
            
        Returns:
            CSV column name (e.g., 'opened_at')
            
        Example:
            >>> config = Config()
            >>> config.get_incident_column_mapping('opened_at')
            'opened_at'
        """
        return self._column_mappings.get('incident_data', {}).get(field_name)
    
    def get_request_column_mapping(self, field_name: str) -> str:
        """Get CSV column name for request field"""
        return self._column_mappings.get('request_data', {}).get(field_name)
    
    def get_problem_column_mapping(self, field_name: str) -> str:
        """
        Get CSV column name for problem field
        
        Args:
            field_name: Internal field name (e.g., 'u_rca_required')
            
        Returns:
            CSV column name from Problem table export
        """
        return self._column_mappings.get('problem_data', {}).get(field_name)
    
    def get_task_column_mapping(self, field_name: str) -> str:
        """
        Get CSV column name for task field
        
        Args:
            field_name: Internal field name (e.g., 'parent_number')
            
        Returns:
            CSV column name from Task/RCA table export
        """
        return self._column_mappings.get('task_data', {}).get(field_name)
    
    def get_all_incident_columns(self) -> Dict[str, str]:
        """Get all incident column mappings"""
        return self._column_mappings.get('incident_data', {})
    
    def get_all_problem_columns(self) -> Dict[str, str]:
        """Get all problem column mappings"""
        return self._column_mappings.get('problem_data', {})
    
    def get_all_task_columns(self) -> Dict[str, str]:
        """Get all task column mappings"""
        return self._column_mappings.get('task_data', {})
    
    # ============================================================
    # THRESHOLD METHODS
    # ============================================================
    
    def get_backlog_threshold(self) -> int:
        """
        Get incident backlog threshold in days
        
        Returns:
            int: Days threshold (default: 10)
            
        Example:
            >>> config.get_backlog_threshold()
            10
        """
        return self._thresholds.get('aging', {}).get('backlog_days', 10)
    
    def get_request_threshold(self) -> int:
        """
        Get request aging threshold in days
        
        Returns:
            int: Days threshold (default: 30)
        """
        return self._thresholds.get('aging', {}).get('request_aging_days', 30)
    
    def get_rca_timeframe(self, priority: int) -> int:
        """
        Get RCA completion timeframe based on priority
        
        Args:
            priority: Priority number (1, 2, 3, etc.)
            
        Returns:
            int: Days allowed for RCA completion
            
        Example:
            >>> config.get_rca_timeframe(1)  # P1
            7
            >>> config.get_rca_timeframe(2)  # P2
            14
        """
        rca_thresholds = self._thresholds.get('rca', {})
        
        timeframe_map = {
            1: rca_thresholds.get('p1_rca_timeframe_days', 7),
            2: rca_thresholds.get('p2_rca_timeframe_days', 14),
            3: rca_thresholds.get('p3_rca_timeframe_days', 30)
        }
        
        return timeframe_map.get(priority, 30)  # Default to 30 days
    
    def get_major_incident_priorities(self) -> List[int]:
        """
        Get list of priority numbers considered "major" (P1, P2)
        
        Returns:
            List[int]: Priority numbers (default: [1, 2])
        """
        return self._thresholds.get('priority', {}).get('major_incident_levels', [1, 2])
    
    # ============================================================
    # KPI TARGET METHODS
    # ============================================================
    
    def get_kpi_target(self, kpi_id: str, target_name: str) -> Any:
        """
        Get specific target value for a KPI
        
        Args:
            kpi_id: KPI identifier (e.g., 'SM002', 'RCA001')
            target_name: Target field name (e.g., 'backlog_max')
            
        Returns:
            Target value or None if not found
            
        Example:
            >>> config.get_kpi_target('SM002', 'backlog_percentage_max')
            10.0
            >>> config.get_kpi_target('RCA001', 'completion_rate_expected')
            95.0
        """
        kpi_config = self._kpis.get(kpi_id, {})
        return kpi_config.get('targets', {}).get(target_name)
    
    def get_rca_targets(self) -> Dict[str, Any]:
        """
        Get all RCA001 targets
        
        Returns:
            dict: RCA001 target configuration
            
        Example:
            >>> targets = config.get_rca_targets()
            >>> targets['completion_rate_expected']
            95.0
        """
        return self._kpis.get('RCA001', {}).get('targets', {})
    
    def get_kpi_weight(self, kpi_id: str) -> float:
        """
        Get scorecard weight for a KPI
        
        Args:
            kpi_id: KPI identifier
            
        Returns:
            float: Weight percentage (0-100)
        """
        return self._kpis.get(kpi_id, {}).get('weight', 0.0)
    
    def is_kpi_enabled(self, kpi_id: str) -> bool:
        """
        Check if a KPI is enabled
        
        Args:
            kpi_id: KPI identifier
            
        Returns:
            bool: True if enabled
        """
        return self._kpis.get(kpi_id, {}).get('enabled', False)
    
    def get_enabled_kpis(self) -> List[str]:
        """
        Get list of enabled KPI IDs
        
        Returns:
            List[str]: Enabled KPI identifiers
        """
        return [kpi_id for kpi_id, kpi_config in self._kpis.items() 
                if kpi_config.get('enabled', False)]
    
    # ============================================================
    # PROCESSING CONFIGURATION METHODS
    # ============================================================
    
    def get_priority_extraction_config(self) -> Dict[str, Any]:
        """Get priority extraction configuration"""
        return self._processing.get('priority_extraction', {})
    
    def get_null_handling_config(self) -> Dict[str, Any]:
        """
        Get null handling configuration
        
        Returns:
            dict: Null handling rules (e.g., reassignment_count: 0)
        """
        return self._processing.get('null_handling', {})
    
    def get_boolean_processing_config(self) -> Dict[str, List]:
        """
        Get boolean field processing configuration (for RCA delivered, etc.)
        
        Returns:
            dict: Contains 'true_values', 'false_values', 'null_values' lists
        """
        return self._processing.get('boolean_processing', {})
    
    def get_rca_stage_config(self) -> Dict[str, List[str]]:
        """
        Get RCA stage processing configuration
        
        Returns:
            dict: Stage classifications (completed, ontime, late, etc.)
        """
        return self._processing.get('rca_stage_processing', {})
    
    def get_date_parsing_config(self) -> Dict[str, Any]:
        """Get date parsing configuration"""
        return self._processing.get('date_parsing', {})
    
    # ============================================================
    # SCORECARD METHODS
    # ============================================================
    
    def get_active_weights(self) -> Dict[str, float]:
        """
        Get active KPI weights for scorecard calculation
        
        Returns:
            dict: KPI weights (should sum to 100)
        """
        return self._scorecard.get('active_weights', {})
    
    def get_performance_bands(self) -> Dict[str, Dict]:
        """Get performance band definitions"""
        return self._scorecard.get('performance_bands', {})
    
    # ============================================================
    # DATA FILE METHODS
    # ============================================================
    
    def get_incident_filename(self) -> str:
        """Get expected incident CSV filename"""
        return self._data_files.get('incident_file', 
                                    'PYTHON_EMEA_IM_last_90_days_redacted_clean.csv')
    
    def get_request_filename(self) -> str:
        """Get expected request CSV filename"""
        return self._data_files.get('request_file',
                                    'PYTHON_EMEA_SCT_last_90_days_redacted_clean.csv')
    
    def get_problem_filename(self) -> str:
        """Get expected problem CSV filename"""
        return self._data_files.get('problem_file',
                                    'PYTHON_EMEA_PM_P1P2__This_Year_.csv')
    
    def get_task_filename(self) -> str:
        """Get expected task/RCA CSV filename"""
        return self._data_files.get('task_file',
                                    'PYTHON_EMEA_TASK_RCA__This_Year_.csv')
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def get_excluded_fcr_channels(self) -> List[str]:
        """
        Get list of channels excluded from FCR calculation
        
        Returns:
            List[str]: Channel names to exclude (default: ['Self Heal', 'Event'])
        """
        return self._kpis.get('SM004', {}).get('excluded_channels', 
                                                ['Self Heal', 'Event'])
    
    def get_config_version(self) -> str:
        """Get configuration version"""
        return self.config.get('metadata', {}).get('version', 'unknown')
    
    def get_organization(self) -> str:
        """Get organization name"""
        return self.config.get('metadata', {}).get('organization', 'unknown')
    
    def print_summary(self):
        """Print configuration summary for debugging"""
        print("=" * 80)
        print(f"KPI Configuration Summary")
        print("=" * 80)
        print(f"Version: {self.get_config_version()}")
        print(f"Organization: {self.get_organization()}")
        print(f"\nEnabled KPIs: {', '.join(self.get_enabled_kpis())}")
        print(f"\nThresholds:")
        print(f"  Incident backlog: {self.get_backlog_threshold()} days")
        print(f"  Request aging: {self.get_request_threshold()} days")
        print(f"  P1 RCA timeframe: {self.get_rca_timeframe(1)} days")
        print(f"  P2 RCA timeframe: {self.get_rca_timeframe(2)} days")
        print(f"\nData Files:")
        print(f"  Incidents: {self.get_incident_filename()}")
        print(f"  Requests: {self.get_request_filename()}")
        print(f"  Problems: {self.get_problem_filename()}")
        print(f"  Tasks: {self.get_task_filename()}")
        print("=" * 80)


def test_config():
    """Test configuration loader with example usage"""
    try:
        config = Config()
        
        print("\n✓ Configuration loaded successfully!")
        config.print_summary()
        
        # Test some specific values
        print("\n" + "=" * 80)
        print("Sample Value Tests:")
        print("=" * 80)
        
        print(f"SM002 backlog target: {config.get_kpi_target('SM002', 'backlog_percentage_max')}%")
        print(f"RCA001 expected rate: {config.get_kpi_target('RCA001', 'completion_rate_expected')}%")
        print(f"Major incident levels: {config.get_major_incident_priorities()}")
        print(f"FCR excluded channels: {config.get_excluded_fcr_channels()}")
        
        print("\n" + "=" * 80)
        print("Column Mapping Tests:")
        print("=" * 80)
        print(f"Incident 'opened_at' maps to: '{config.get_incident_column_mapping('opened_at')}'")
        print(f"Problem 'u_rca_required' maps to: '{config.get_problem_column_mapping('u_rca_required')}'")
        print(f"Task 'parent_number' maps to: '{config.get_task_column_mapping('parent_number')}'")
        
        print("\n✓ All tests passed!")
        
        return config
        
    except ConfigError as e:
        print(f"\n✗ Configuration Error: {e}")
        return None


if __name__ == '__main__':
    # Run tests when module is executed directly
    test_config()
