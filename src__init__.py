"""
KPI Pipeline - ServiceNow ITSM KPI Calculation Engine

This package provides automated calculation of ServiceNow ITSM KPIs
for tracking OKR R002 (Service Delivery Excellence).

Modules:
    config_loader: YAML configuration loading and validation
    load_data: CSV data loading and normalization
    transform: Data transformations and calculated fields
    calculate_kpis: KPI calculation engine
    generate_reports: Excel report generation

Example:
    from src.config_loader import load_config
    from src.calculate_kpis import KPICalculator
    
    config = load_config("config/kpi_config.yaml")
    calculator = KPICalculator(config)
    results = calculator.calculate_all(incidents, requests)
"""

__version__ = "1.0.0"
__author__ = "IT Service Management Team"

# Make key classes available at package level
from .config_loader import load_config
from .load_data import load_incident_data, load_request_data
from .transform import transform_incident_data, add_calculated_fields
from .calculate_kpis import KPICalculator
from .generate_reports import ExcelReportGenerator

__all__ = [
    "load_config",
    "load_incident_data",
    "load_request_data",
    "transform_incident_data",
    "add_calculated_fields",
    "KPICalculator",
    "ExcelReportGenerator",
]
