"""
KPI Pipeline Package
A comprehensive pipeline for calculating and analyzing KPIs from incident and request data.
"""

__version__ = "1.0.0"
__author__ = "[Your Organization]"
__license__ = "MIT"

# Package-level exports
from . import config_loader
from . import load_data
from . import transform
from . import calculate_kpis

__all__ = [
    "config_loader",
    "load_data",
    "transform",
    "calculate_kpis",
]



