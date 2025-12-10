# KPI Pipeline - Codebase Outputs Summary

## 📊 Overview

The **KPI Pipeline** is an IT Service Management (ITSM) analytics system that transforms raw incident, request, and problem data into actionable business intelligence through automated KPI calculations, OKR tracking, and executive-ready Excel dashboards.

---

## 🎯 Primary Outputs

### 1. **KPI Report (Excel Dashboard)**
**Filename:** `data/output/KPI_Report_[env]_[timestamp].xlsx`

This is a **multi-sheet executive dashboard** containing:

#### 📑 **Sheet 1: Executive Summary**
- Overall KPI Scorecard Score (0-100 weighted scale)
- Overall OKR R002 Score (Service Delivery Excellence)
- Performance band indicators (🟢 Excellent / 🟡 Good / 🟠 At Risk / 🔴 Critical)
- High-level status for all KPIs and Key Results

#### 📑 **Sheet 2: KPI Scorecard**
Complete KPI performance table:
- **SM001** - Major Incidents (P1/P2 counts vs targets)
- **SM002** - Backlog Management (% incidents >10 days)
- **SM003** - Request Aging (% requests >30 days)
- **SM004** - First Time Fix Rate (% with 0 reassignments)
- **RCA001** - RCA Completion Rate (% on-time for P1/P2 problems)

#### 📑 **Sheets 3-7: Detailed KPI Breakdowns**
- **SM001 - Major Incidents**: Detailed P1/P2 incident lists with numbers, descriptions, opened dates
- **SM002 - Backlog Analysis**: All incidents aged >10 days with age calculations
- **SM004 - Request Aging**: Service requests aged >30 days
- **SM004 - First Time Fix**: Breakdown of reassignment counts and FCR metrics

#### 📑 **Sheet 8: OKR R002 Summary**
OKR R002 - Service Delivery Excellence:
- **KR3**: Major Incidents Management (20% weight)
- **KR4**: Incident Backlog Management (35% weight)
- **KR5**: Request Backlog Management (25% weight)
- **KR6**: First Time Fix Rate (20% weight)
- Weighted overall score with performance bands
- Days remaining to deadlines

#### 📑 **Sheet 9: Key Results Detail**
Granular breakdown for each Key Result:
- Current vs Target comparison
- Gap analysis
- Scoring methodology
- Performance trend indicators

#### 📑 **Sheet 10: Action Items**
Automated action triggers:
- **🔴 Critical Actions**: Immediate escalation required
  - P1 incidents present
  - Backlog >15%
  - RCA completion <80%
- **🟡 Warning Actions**: Scheduled intervention needed
  - Backlog >10%
  - FCR <70%
  - RCA completion <90%

#### 📑 **Sheet 11: Geographic Analysis**
Location-based performance intelligence:
- **Volume Tiers**:
  - Tier 1: ≥500 incidents/requests (High Volume)
  - Tier 2: 200-499 (Medium Volume)
  - Tier 3: 100-199 (Standard Volume)
  - Tier 4: <100 (Low Volume)
- **Intervention Priorities**:
  - Critical: High volume + poor performance
  - High: High volume OR poor performance
  - Monitor: Low volume + poor performance
  - Standard: Meeting all targets
- Country/location-level KPI and OKR scores

---

### 2. **Problem Management Dashboard (Excel)**
**Filename:** `data/output/PM_Dashboard_[timestamp].xlsx`

This dashboard focuses on **Root Cause Analysis (RCA) tracking**:

#### 📑 **Sheet 1: Summary**
- RCA001 KPI overview
- Overall RCA completion rates
- P1 vs P2 RCA performance
- On-time vs Late breakdown

#### 📑 **Sheet 2: Problem Details**
Complete problem inventory with:
- Problem numbers, priorities, opened dates
- RCA status (Completed/In Progress/Paused)
- RCA completion dates
- Days to complete RCA
- Breach status

#### 📑 **Sheet 3: P1 Problems**
Priority 1 problem analysis:
- Expected RCA timeframe: 7 days
- Completion tracking
- Late RCA identification

#### 📑 **Sheet 4: P2 Problems**
Priority 2 problem analysis:
- Expected RCA timeframe: 14 days
- Completion tracking
- Performance metrics

#### 📑 **Sheet 5: Late RCA**
Problems with late or missing RCA:
- Days overdue
- Impact assessment
- Escalation priorities

#### 📑 **Sheet 6: On-Time RCA**
Successfully completed RCAs:
- Best practice examples
- Completion time analysis
- Performance patterns

---

### 3. **Console Output (Real-time Terminal)**

During pipeline execution, the console displays:

```
========================================
    KPI PIPELINE EXECUTION
========================================

Environment: prod
Report Period: Last 90 days
Timestamp: 2025-12-05 14:32:15

[Step 1/8] Loading configuration...       ✓
[Step 2/8] Loading incident data...       ✓ (1,234 incidents loaded)
[Step 3/8] Loading request data...        ✓ (567 requests loaded)
[Step 4/8] Transforming data...           ✓
[Step 5/8] Calculating KPIs...            ✓
[Step 6/8] Calculating OKR scores...      ✓
[Step 7/8] Running geographic analysis... ✓
[Step 8/8] Generating Excel reports...    ✓

========================================
         KPI RESULTS
========================================

SM001 - Major Incidents:          🟢 PASS
  P1 Count: 0 (Target: 0)
  P2 Count: 3 (Target: ≤5)
  Total Major: 3

SM002 - Backlog Management:       🟢 EXCELLENT
  Backlog %: 4.2% (Target: ≤10%)
  Adherence: 95.8%
  Backlog Count: 52 / 1,234

SM003 - Request Aging:            🟡 GOOD
  Aged %: 22.5% (Target: ≤30%)
  Adherence: 77.5%
  Aged Count: 128 / 567

SM004 - First Time Fix:           🟢 EXCELLENT
  FCR Rate: 84.3% (Target: ≥80%)
  FTF Count: 1,040 / 1,234

RCA001 - RCA Completion:          🟢 EXCELLENT
  Completion Rate: 92.1% (Target: ≥90%)
  On-time: 35 / 38 problems

========================================
         OKR R002 SUMMARY
========================================
Service Delivery Excellence

Overall Score: 87.3 / 100         🟡 ON TRACK

KR3 (Major Incidents):     95.0   🟢 (Weight: 20%)
KR4 (Incident Backlog):    91.6   🟢 (Weight: 35%)
KR5 (Request Backlog):     75.0   🟡 (Weight: 25%)
KR6 (First Time Fix):      84.3   🟡 (Weight: 20%)

========================================
      GEOGRAPHIC HIGHLIGHTS
========================================

Top Performing Locations:
  1. Germany (Tier 1): 94.2 score
  2. France (Tier 2): 91.8 score
  3. Spain (Tier 3): 88.5 score

Locations Requiring Attention:
  1. Italy (Tier 2): 62.3 score - HIGH PRIORITY
  2. Poland (Tier 3): 68.9 score - MONITOR

========================================
         ACTION ITEMS
========================================

⚠️  WARNING ACTIONS (2):
  • KR5: Request backlog 22.5% (approaching 30% threshold)
    → Schedule weekly backlog review meeting

  • Geographic: Italy showing 15.2% incident backlog
    → High priority intervention required

========================================
         REPORTS GENERATED
========================================

✓ KPI_Report_prod_20251205_143215.xlsx
  Location: data/output/
  Sheets: 11

✓ PM_Dashboard_20251205_143215.xlsx
  Location: data/output/
  Sheets: 6

Execution completed in 8.4 seconds
```

---

## 📈 Data Flow Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                          INPUT DATA                              │
│  CSV Files from ServiceNow Exports (data/input/)                │
├─────────────────────────────────────────────────────────────────┤
│  • Incidents CSV      (PYTHON EMEA IM)                          │
│  • Requests CSV       (PYTHON EMEA SCT)                         │
│  • Problems CSV       (PYTHON EMEA PM P1P2)                     │
│  • Tasks/RCA CSV      (PYTHON EMEA TASK RCA)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   CONFIGURATION LAYER                            │
│  YAML Configuration Files (config/)                              │
├─────────────────────────────────────────────────────────────────┤
│  • kpi_config.yaml    - KPI targets, thresholds, column maps    │
│  • okr_config.yaml    - OKR weights, scoring bands, deadlines   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                   PROCESSING PIPELINE                            │
│  Python Modules (src/)                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Step 1: config_loader.py                                       │
│          Load YAML configs → Config Dictionary                  │
│                                                                  │
│  Step 2: load_data.py + load_problem_data.py                   │
│          Parse CSVs → pandas DataFrames                         │
│          • Date parsing & validation                            │
│          • Priority extraction (1-4)                            │
│          • Column mapping                                       │
│                                                                  │
│  Step 3: transform.py + transform_problems.py                   │
│          Add calculated fields:                                 │
│          • Is_P1, Is_P2, Is_Major_Incident                     │
│          • Is_Backlog (age >10 days)                           │
│          • Is_Aged (age >30 days)                              │
│          • Is_First_Call_Resolution                            │
│          • Age_Days                                             │
│          • RCA status flags                                     │
│                                                                  │
│  Step 4: calculate_kpis.py + calculate_pm_kpis.py              │
│          Calculate metrics:                                     │
│          • SM001: P1/P2 counts                                  │
│          • SM002: Backlog % (>10 days)                         │
│          • SM003: Request aging % (>30 days)                   │
│          • SM004: First Time Fix %                              │
│          • RCA001: RCA completion %                             │
│          → KPI Results Dictionary                               │
│                                                                  │
│  Step 5: okr_calculator.py                                      │
│          Map KPIs to Key Results:                               │
│          • KR3 ← SM001 (Major Incidents)                       │
│          • KR4 ← SM002 (Incident Backlog)                      │
│          • KR5 ← SM003 (Request Backlog)                       │
│          • KR6 ← SM004 (First Time Fix)                        │
│          Apply weights & scoring formulas                       │
│          → OKR Results Dictionary (0-100 scores)                │
│                                                                  │
│  Step 6: geographic_analysis.py                                 │
│          Group by country/location:                             │
│          • Calculate volume tiers                               │
│          • Compute location-level KPIs                          │
│          • Determine intervention priorities                    │
│          → Geographic Results                                   │
│                                                                  │
│  Step 7: sdm_analysis.py                                        │
│          Group by Service Delivery Manager:                     │
│          • Calculate SDM-level KPIs                             │
│          • Compute OKR scores per SDM                           │
│          → SDM Results                                          │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT GENERATION                            │
│  Report Generation Modules                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  generate_reports.py                                             │
│  ├─ Create Excel workbook                                       │
│  ├─ Add 11 formatted sheets                                     │
│  ├─ Apply color-coded status indicators                         │
│  ├─ Format tables with auto-width columns                       │
│  └─ Save: KPI_Report_[env]_[timestamp].xlsx                    │
│                                                                  │
│  generate_pm_reports.py                                          │
│  ├─ Create PM Dashboard workbook                                │
│  ├─ Add 6 RCA-focused sheets                                    │
│  ├─ Include P1/P2 analysis                                      │
│  └─ Save: PM_Dashboard_[timestamp].xlsx                         │
│                                                                  │
│  Console Display                                                 │
│  ├─ Print real-time progress                                    │
│  ├─ Display KPI results with status                             │
│  ├─ Show OKR scores and bands                                   │
│  ├─ List action triggers                                        │
│  └─ Summarize geographic highlights                             │
│                                                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                       FINAL OUTPUTS                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 KPI_Report_prod_YYYYMMDD_HHMMSS.xlsx                        │
│     └─ 11 sheets with executive dashboards                      │
│                                                                  │
│  📊 PM_Dashboard_YYYYMMDD_HHMMSS.xlsx                           │
│     └─ 6 sheets with RCA tracking                               │
│                                                                  │
│  💻 Console Output                                               │
│     └─ Real-time progress, scores, action items                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Metrics Produced

### KPI Metrics (SM Series)
| KPI | Metric Name | Output Value | Target |
|-----|-------------|--------------|--------|
| **SM001** | Major Incidents | P1 Count, P2 Count | P1≤0, P2≤5 |
| **SM002** | Incident Backlog | % aged >10 days | ≤10% |
| **SM003** | Request Aging | % aged >30 days | ≤30% |
| **SM004** | First Time Fix | % with 0 reassignments | ≥80% |
| **RCA001** | RCA Completion | % on-time RCA | ≥90% |

### OKR Metrics (R002 Series)
| Key Result | Metric Name | Weight | Score Range |
|------------|-------------|--------|-------------|
| **KR3** | Major Incidents Management | 20% | 0-100 |
| **KR4** | Incident Backlog Management | 35% | 0-100 |
| **KR5** | Request Backlog Management | 25% | 0-100 |
| **KR6** | First Time Fix Rate | 20% | 0-100 |
| **R002** | Overall Service Delivery Excellence | 100% | 0-100 (weighted) |

### Geographic Metrics
- **Volume Tier** (1-4 based on incident/request count)
- **Location-level KPI scores**
- **Intervention Priority** (Critical/High/Monitor/Standard)
- **Country/Location performance rankings**

### Problem Management Metrics
- **RCA Completion Rate** (% on-time)
- **Late RCA Count** (breached SLA)
- **On-Time RCA Count** (met SLA)
- **Days to Complete RCA** (P1: 7 days, P2: 14 days)

---

## 📋 Performance Bands

All outputs use consistent color-coded performance indicators:

- **🟢 EXCELLENT** (90-100): All targets exceeded
- **🟡 GOOD/ON TRACK** (70-89): Meeting most targets
- **🟠 AT RISK** (50-69): Multiple areas need attention
- **🔴 CRITICAL** (0-49): Immediate intervention required

---

## 🚀 Usage

To generate all outputs:
```bash
# Production environment (full data)
python main.py --env prod

# Development environment (sample data)
python main.py --env dev

# Problem Management only
python scripts/run_pm.py
```

---

## 📂 Output File Locations

All generated files are saved to:
```
/home/user/kpi-pipeline/data/output/

├── KPI_Report_prod_20251205_143215.xlsx
├── KPI_Report_dev_20251204_091033.xlsx
├── PM_Dashboard_20251205_143215.xlsx
└── PM_Dashboard_20251204_091040.xlsx
```

Filenames include:
- Environment prefix (prod/dev)
- Timestamp (YYYYMMDD_HHMMSS)
- Prevents overwriting previous reports

---

## 🎨 Excel Formatting Features

All Excel outputs include:

✅ **Professional Styling**
- Color-coded status cells (green/yellow/orange/red)
- Auto-adjusted column widths
- Header row formatting
- Freeze panes for navigation

✅ **Data Validation**
- Number formatting (decimals, percentages)
- Date formatting (ISO 8601)
- Currency/count formatting where applicable

✅ **Conditional Formatting**
- Performance band highlighting
- Threshold-based cell colors
- Trend indicators

✅ **User Experience**
- Descriptive sheet names
- Clear column headers
- Summary tables at top of each sheet
- Detailed data below summaries

---

## 📊 Business Value

These outputs enable:

1. **Executive Visibility**: High-level OKR scores for leadership
2. **Operational Action**: Specific incident/request lists requiring attention
3. **Geographic Insights**: Location-based resource allocation
4. **Problem Prevention**: RCA tracking to reduce repeat incidents
5. **Performance Trends**: Historical comparison (when run regularly)
6. **Automated Escalation**: Action triggers identify critical issues

---

**Generated:** 2025-12-05
**Version:** KPI Pipeline 2.1
**Last Updated:** This document
