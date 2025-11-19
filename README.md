# 📊 KPI Pipeline

A comprehensive Python-based pipeline for calculating and analyzing Key Performance Indicators (KPIs) from IT Service Management incident and request data.

## ✨ Overview

This KPI Pipeline automates the calculation of critical service management metrics, providing consistent, repeatable, and transparent KPI reporting. Built with flexibility in mind, it supports multiple data sources, configurable thresholds, and customizable weightings.

## 🎯 Features

### Service Management KPIs
- **SM001 - Major Incident Management**: Track P1 and P2 incidents against defined targets
- **SM002 - Backlog Management**: Monitor incidents aged beyond threshold (default: 10 days)
- **SM003 - Request Aging**: Track service requests exceeding age limits (default: 30 days)  
- **SM004 - First Contact Resolution**: Measure resolution efficiency on first contact

### Problem Management KPIs
- **RCA001 - RCA Completion Rate**: Track Root Cause Analysis completion for P1/P2 problems (target: 95% on-time completion)
- **Excel Dashboard Export**: Professional multi-sheet Excel reports with KPI summaries and detailed problem breakdowns

### System Features
- **Weighted Overall Score**: Configurable scoring across all KPIs with performance banding
- **Geographic Analysis**: Location-level analysis across all KPIs (incidents, requests, problems) and OKRs with volume tiers and intervention priorities
- **YAML Configuration**: Simple, human-readable configuration management
- **Comprehensive Testing**: Validation suite to ensure data accuracy

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for version control)

### Installation

**Option 1: Automated Setup (Recommended)**

For **Windows**:
```bash
.\setup.bat
```

For **Mac/Linux**:
```bash
chmod +x setup.sh
./setup.sh
```

**Option 2: Manual Setup**

1. **Clone the repository**
   ```bash
   git clone [YOUR-REPO-URL]
   cd kpi_pipeline
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment**
   - Windows: `.venv\Scripts\activate`
   - Mac/Linux: `source .venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Prepare your data**
   - Place your incident CSV file in `data/input/`
   - Place your request CSV file in `data/input/` (if using SM003)
   - Place your problem CSV file in `data/` (if using RCA001)
   - Place your task CSV file in `data/` (if using RCA001)
   - See `data/input/README.md` for expected format

6. **Run the pipeline**
   ```bash
   python main.py
   ```

### Advanced Usage

```bash
# Use development environment (smaller test data)
python main.py --env dev

# Save normalized output tables for auditing
python main.py --save-tables

# Save tables as CSV instead of Parquet
python main.py --save-tables --tables-format csv

# Override input files
python main.py --incidents custom_incidents.csv --requests custom_requests.csv
```

## 📁 Project Structure

```
kpi_pipeline/
├── config/
│   ├── kpi_config.yaml           # Main configuration file
│   └── complete_kpi_config.yaml  # Full configuration with all options
├── data/
│   ├── input/                    # Place your CSV files here
│   │   ├── README.md
│   │   └── *.csv
│   └── output/                   # Generated reports appear here
│       └── README.md
├── src/
│   ├── __init__.py
│   ├── config_loader.py          # Configuration management
│   ├── load_data.py              # Data loading and validation
│   ├── load_problem_data.py      # Problem Management data loading
│   ├── transform.py              # Data transformation logic
│   ├── transform_problems.py     # Problem Management transformations
│   ├── calculate_kpis.py         # KPI calculation engine
│   ├── calculate_pm_kpis.py      # Problem Management KPI calculations
│   ├── analysis_output.py        # Normalized output tables (intermediate layer)
│   └── generate_pm_reports.py    # Excel dashboard generation
├── tests/
│   ├── sample_data/              # Generated sample data for testing
│   ├── test_pipeline.py          # Comprehensive test suite
│   └── generate_sample_data.py   # Sample data generator
├── docs/
│   ├── QUICKSTART.md             # 5-minute getting started guide
│   ├── TECHNICAL.md              # Technical architecture details
│   ├── CONFIGURATION.md          # Configuration guide
│   ├── ANALYSIS_OUTPUT.md        # Analysis output layer documentation
│   ├── TROUBLESHOOTING.md        # Common issues and solutions
│   ├── MAINTENANCE.md            # Maintenance and updates
│   ├── HANDOFF.md                # Project handoff documentation
│   ├── GITHUB_SETUP.md           # GitHub setup instructions
│   └── GIT_WORKFLOW.md           # Git workflow documentation
├── main.py                       # Main execution script
├── scripts/                      # Utility scripts
│   ├── run_pm.py                # Problem Management runner
│   ├── run_validation.py        # Validation runner wrapper
│   ├── run_validation_tests.py # Comprehensive validation tests
│   ├── run_validation_tests_standalone.py # Standalone validation tests
│   └── validate_project.py      # Project validation tool
├── requirements.txt              # Python dependencies
├── setup.sh / setup.bat          # Automated setup scripts
├── .gitignore                    # Git ignore patterns
└── README.md                     # This file
```

## ⚙️ Configuration

The pipeline uses YAML configuration files located in the `config/` directory:

- `kpi_config.yaml`: Main configuration (recommended for daily use)
- `complete_kpi_config.yaml`: Full configuration with all available options

### Key Configuration Sections

1. **Column Mappings**: Map your CSV columns to expected field names
2. **Thresholds**: Define targets and limits for each KPI
3. **Weights**: Set importance weightings for overall scoring
4. **KPI Toggles**: Enable/disable specific KPIs

For detailed configuration instructions, see [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md)

## 🧪 Testing

### Run Validation Checks

```bash
python scripts/validate_project.py
```

This checks:
- Python version compatibility
- Required files exist
- YAML configuration validity
- Module imports
- Data file availability
- Git repository status

### Generate Sample Data

```bash
python tests/generate_sample_data.py
```

Creates 50 sample incidents and requests in `tests/sample_data/`

### Run Test Suite

```bash
python tests/test_pipeline.py
```

Validates:
- Configuration loading
- Data loading and structure
- Transformation logic
- KPI calculations
- Expected outputs

## 📖 Documentation

- 📘 [Quick Start Guide](docs/QUICKSTART.md) - Get running in 5 minutes
- 🔧 [Technical Documentation](docs/TECHNICAL.md) - Architecture and implementation details
- ⚙️ [Configuration Guide](docs/CONFIGURATION.md) - Customize KPIs and thresholds
- 📊 [Analysis Output](docs/ANALYSIS_OUTPUT.md) - Normalized output tables and archiving
- 🔍 [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions
- 🛠️ [Maintenance Guide](docs/MAINTENANCE.md) - Regular maintenance tasks
- 📋 [Handoff Documentation](docs/HANDOFF.md) - Project transfer information
- 🐙 [GitHub Setup](docs/GITHUB_SETUP.md) - Deploy to GitHub
- 🌿 [Git Workflow](docs/GIT_WORKFLOW.md) - Development workflow

## 🤝 Contributing

We welcome contributions! Please see [`CONTRIBUTING.md`](CONTRIBUTING.md) for guidelines on:

- Reporting bugs
- Suggesting features
- Code style standards (PEP 8)
- Pull request process

## 📝 License

This project is licensed under the MIT License - see the [`LICENSE`](LICENSE) file for details.

## 📧 Contact

For questions, issues, or support:

- **Project Lead**: [Name] - [email@example.com]
- **Technical Contact**: [Name] - [email@example.com]
- **GitHub Issues**: [YOUR-REPO-URL/issues]

## 🗺️ Roadmap

### Version 2.1 (Current)
- ✅ Core KPI calculations (SM001, SM002, SM003, SM004)
- ✅ Problem Management KPIs (RCA001)
- ✅ Excel dashboard export with formatting
- ✅ YAML configuration
- ✅ Geographic analysis support
- ✅ Comprehensive testing suite

### Future Enhancements
- 📧 Email report distribution
- 🔄 Automated scheduling support
- 📈 Trend analysis over time
- 🌐 Web dashboard interface
- 🔌 API endpoint for integrations
- 📊 Additional Problem Management KPIs (PM001-PM005)

## 🙏 Acknowledgments

Built with:
- [pandas](https://pandas.pydata.org/) - Data manipulation and analysis
- [PyYAML](https://pyyaml.org/) - YAML configuration parsing
- [openpyxl](https://openpyxl.readthedocs.io/) - Excel file generation

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Status**: ✅ Production Ready

For detailed setup and deployment instructions, see the [documentation](docs/).
