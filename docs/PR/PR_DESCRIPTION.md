# Pull Request: Problem Management KPI Tracking (RCA001)

## 📋 Overview

This PR introduces Problem Management KPI tracking capabilities to the KPI pipeline, specifically implementing **RCA001: RCA Completion Rate**. This feature tracks Root Cause Analysis (RCA) completion performance for P1/P2 problems and integrates it into the overall scorecard.

## 🎯 Business Value

- **Measure RCA completion performance** for major problems (P1/P2)
- **Target**: 95% of P1/P2 problems requiring RCA complete on-time
- **SLA**: P1 = 7 days, P2 = 14 days from problem opened date
- **Scorecard Weight**: 15% of overall performance score

## 📊 Current Status

### ✅ Session 1 Complete (Included in this PR)
- Enhanced configuration system with Problem Management support
- Config loader extensions with PM-specific methods
- Problem data loader implementation
- All tested with real EMEA data (49 P2 problems, 52 RCA tasks)

### ⏳ Session 2 (Next Steps - Not in this PR)
- Data transformation module (`transform_problems.py`)
- Join Problems with Tasks
- Calculated field generation

### 🔮 Future Sessions
- KPI calculation logic
- Excel report integration
- Main pipeline integration

## 📁 Files Changed

### New Documentation
- `docs/PR/PM_Implementation_Plan.md` - Complete implementation plan
- `docs/PR/Session1_Summary.md` - Session 1 completion summary
- `docs/PR/Session1_Handoff.md` - Detailed handoff documentation
- `docs/PR/START_SESSION_2.md` - Session 2 specification and guide

### Reference Implementation (For Review)
- `docs/PR/config_loader.py` - Enhanced config loader with PM methods
- `docs/PR/kpi_config.yaml` - Configuration with Problem Management support
- `docs/PR/load_problem_data.py` - Problem data loader implementation

## 🔧 Implementation Details

### Configuration Enhancements
- Added Problem Management column mappings
- Added Task (RCA) column mappings
- RCA001 KPI definition with targets (90% minimum, 95% expected)
- RCA timeframes (P1: 7 days, P2: 14 days)
- Boolean and stage processing rules
- Updated scorecard weighting (RCA001: 15%)

### Config Loader Extensions
New methods added:
- `get_problem_column_mapping(field_name)` - Get Problem table column names
- `get_task_column_mapping(field_name)` - Get Task table column names
- `get_rca_timeframe(priority)` - Get RCA completion timeframe by priority
- `get_rca_targets()` - Get RCA001 target configuration
- `get_boolean_processing_config()` - Get boolean field processing rules
- `get_rca_stage_config()` - Get RCA stage classification rules

### Data Loader
- `load_problem_data()` - Loads Problem CSV with latin-1 encoding
- `load_task_data()` - Loads RCA Task CSV
- `load_all_problem_data()` - Convenience function to load both
- Data quality validation and coverage reporting
- Handles special characters in EMEA exports

## 📈 Data Characteristics

Based on actual EMEA data:
- **49 P2 problems** (no P1s in current dataset)
- **39 require RCA** (80%)
- **52 RCA tasks** total
- **38 problems have matching tasks** (77.6% coverage)
- **Current completion rate**: ~74% (29 on-time, 15 late) - **below 95% target**

## 🎨 Design Decisions

1. **Task file as primary source** - More reliable than Problem table RCA fields
2. **LEFT JOIN strategy** - Keep all problems (even those without tasks)
3. **Multiple tasks per problem** - Prioritize: Achieved > Breached > In Progress > Paused
4. **Latin-1 encoding** - Handle special characters in EMEA exports

## ✅ Testing

### Session 1 Tests (Completed)
- ✅ Configuration loads successfully (version 2.1)
- ✅ Can access all RCA thresholds (7, 14 days)
- ✅ Can access RCA targets (90%, 95%)
- ✅ Loads 49 problems from CSV
- ✅ Loads 52 tasks from CSV
- ✅ Validates data quality (no nulls in critical fields)
- ✅ Reports task coverage (77.6%)

### Next Steps (Session 2)
- Priority extraction testing
- Calculated field validation
- Join operation testing
- End-to-end transformation validation

## 🚀 Integration Plan

### Files to Merge (After PR Review)
1. **`config/kpi_config.yaml`** - Merge Problem Management configuration
2. **`src/config_loader.py`** - Merge PM-specific methods
3. **`src/load_problem_data.py`** - Add new data loader module

### Files to Create (Future Sessions)
1. **`src/transform_problems.py`** - Data transformation (Session 2)
2. **`src/calculate_problem_kpis.py`** - KPI calculation (Session 3)
3. Updates to `src/main.py` - Pipeline integration
4. Updates to `src/generate_reports.py` - Excel report integration

## 📝 Breaking Changes

None - this is a feature addition that doesn't modify existing functionality.

## 🔄 Dependencies

- No new Python dependencies required
- Uses existing pandas, yaml libraries
- Compatible with current pipeline structure

## 📚 Documentation

- Implementation plan with detailed specifications
- Session handoff documents for continuity
- Code examples and test cases included
- Configuration schema documented

## ⚠️ Notes

- Configuration file needs to be merged carefully to preserve existing settings
- Data files expected: `PYTHON_EMEA_PM_P1P2__This_Year_.csv` and `PYTHON_EMEA_TASK_RCA__This_Year_.csv`
- Pipeline will gracefully skip Problem Management KPIs if data files are not available

## 🎯 Success Criteria

- [x] Configuration supports Problem Management
- [x] Config loader has PM methods
- [x] Data loader implemented and tested
- [x] Documentation complete
- [ ] Code reviewed and approved
- [ ] Configuration merged
- [ ] Data loader integrated

## 👥 Review Checklist

- [ ] Review configuration changes
- [ ] Review config loader extensions
- [ ] Review data loader implementation
- [ ] Validate test results
- [ ] Check documentation completeness
- [ ] Verify backward compatibility

---

**Related Issues**: Problem Management KPI Implementation
**Type**: Feature Addition
**Priority**: High
**Estimated Effort**: Session 1 Complete, Session 2-5 Remaining

