# Changelog

All notable changes to the KPI Pipeline project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- Email report distribution
- Automated scheduling support
- Trend analysis over time periods
- Web dashboard interface
- API endpoints for integrations
- Database connector (replace CSV input)
- Multi-language support
- Additional Problem Management KPIs (PM001-PM005)

---

## [2.1.0] - 2025-11-04

### Added - Problem Management KPI Support

#### Problem Management Features
- **RCA001 - RCA Completion Rate**: Track Root Cause Analysis completion for P1/P2 problems
  - Target: 95% on-time completion
  - P1 RCA timeframe: 7 days
  - P2 RCA timeframe: 14 days
  - Status tracking: GREEN (≥95%), YELLOW (≥85%), RED (<85%)

#### New Modules
- `src/load_problem_data.py`: Load Problem and RCA Task data from CSV files
- `src/transform_problems.py`: Transform Problem and Task data with calculated fields
- `src/calculate_pm_kpis.py`: Calculate Problem Management KPIs
- `src/generate_pm_reports.py`: Generate professional Excel dashboards for PM KPIs

#### Excel Dashboard Export
- Multi-sheet Excel workbook generation
- KPI Summary sheet with metrics, status indicators, and gap analysis
- Problem Details sheet with RCA status and timeline information
- Professional formatting with color coding and conditional formatting
- Auto-adjusted column widths and frozen headers

#### Configuration Enhancements
- Extended `config/kpi_config.yaml` with Problem Management sections
- Added `problem_data` and `task_data` column mappings
- Added RCA stage processing rules
- Added Problem Management thresholds and targets
- Updated scorecard weights to include RCA001

#### Documentation Updates
- Updated README.md with Problem Management features
- Updated QUICK_REFERENCE.md with RCA001 KPI reference
- Added troubleshooting section for Problem Management data

---

## [1.0.0] - 2025-10-17

### Added - Initial Release

#### Core KPI Calculations
- **SM001 - Major Incident Management**: Track P1 and P2 incidents against defined targets
- **SM002 - Backlog Management**: Monitor incidents aged beyond threshold (configurable, default: 10 days)
- **SM003 - Request Aging**: Track service requests exceeding age limits (configurable, default: 30 days)
- **SM004 - First Contact Resolution**: Measure resolution efficiency on first contact
- **Overall Score**: Weighted scorecard with configurable weights and performance banding

#### System Features
- YAML-based configuration system for maximum flexibility
- CSV data input support for incidents and requests
- Automatic date parsing with multiple format support
- Priority extraction from mixed string formats
- Column mapping configuration for different data schemas
- Geographic analysis support (country-level filtering)
- Comprehensive data transformation pipeline
- Business impact assessment (Low/Medium/High)
- Performance banding (Excellent/Good/Needs Improvement)

#### Configuration Management
- Main configuration file with all options (`config/kpi_config.yaml`)
- OKR configuration file (`config/okr_config.yaml`)
- Comprehensive configuration documentation (`docs/CONFIGURATION.md`)
- Flexible threshold and target configuration
- Dynamic weight adjustment when KPIs are disabled
- Configurable performance bands
- Column mapping support

#### Testing & Validation
- Comprehensive test suite (`tests/test_pipeline.py`)
- Sample data generator (`tests/generate_sample_data.py`)
- Project validation tool (`validate_project.py`)
- Configuration validation
- Data loading validation
- Calculation verification tests
- Expected results documentation

#### Setup & Deployment
- Automated setup scripts (Windows and Mac/Linux)
- Virtual environment configuration
- Dependency management (`requirements.txt`)
- Git ignore configuration
- Cross-platform support (Windows, Mac, Linux)

#### Documentation
- Comprehensive README with quick start guide
- Technical documentation (architecture, calculations, API reference)
- Configuration guide with examples
- Troubleshooting guide
- Maintenance procedures
- Project handoff documentation
- GitHub setup guide
- Git workflow documentation
- Quick start guide (5-minute setup)

#### Developer Tools
- Structured project layout following best practices
- PEP 8 compliant code
- Docstrings for all functions
- Type hints where applicable
- Modular architecture for easy extension

### Dependencies
- Python 3.9+
- pandas >= 2.0.0
- pyyaml >= 6.0
- openpyxl >= 3.1.0
- python-dateutil >= 2.8.0

### Technical Details
- **Architecture**: Modular pipeline with separate concerns (load, transform, calculate)
- **Data Processing**: pandas-based for performance
- **Configuration**: YAML for human-readable settings
- **Testing**: Automated test suite with sample data
- **Version Control**: Git-ready with .gitignore
- **Documentation**: Markdown-based comprehensive docs

---

## Version History

### Release Naming Convention

- **Major (X.0.0)**: Breaking changes, major architecture updates
- **Minor (1.X.0)**: New features, backwards compatible
- **Patch (1.0.X)**: Bug fixes, minor improvements

### Future Roadmap

#### Version 1.1.0 (Planned)
- Excel dashboard export with formatting and charts
- Enhanced report templates
- Performance optimizations for large datasets
- Additional filtering options

#### Version 1.2.0 (Planned)
- Email report distribution
- Automated scheduling
- Report history tracking
- Trend analysis features

#### Version 2.0.0 (Future)
- Web-based dashboard
- Database integration
- Real-time data processing
- API endpoints
- Multi-tenant support

---

## How to Update This File

When making changes:

1. **Add to [Unreleased]** section first
2. **Categorize changes** under appropriate headings:
   - `Added` for new features
   - `Changed` for changes in existing functionality
   - `Deprecated` for soon-to-be removed features
   - `Removed` for now removed features
   - `Fixed` for bug fixes
   - `Security` for vulnerability fixes

3. **When releasing**, move [Unreleased] items to new version section:
   ```markdown
   ## [1.1.0] - 2025-MM-DD
   
   ### Added
   - Feature from unreleased
   
   ### Fixed
   - Bug fix from unreleased
   ```

4. **Include issue/PR references** where applicable:
   ```markdown
   - Fixed calculation error in SM002 (#23)
   - Added Excel export feature (#45, #48)
   ```

---

## Contributors

Thank you to all contributors who have helped improve this project!

- Initial development and v1.0.0 release: [Your Organization]

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

## Links

- [Project Repository](https://github.com/[YOUR-USERNAME]/kpi-pipeline)
- [Issue Tracker](https://github.com/[YOUR-USERNAME]/kpi-pipeline/issues)
- [Documentation](docs/)

---

**Note**: This changelog follows [Keep a Changelog](https://keepachangelog.com/) principles. Please maintain this format when adding entries.



