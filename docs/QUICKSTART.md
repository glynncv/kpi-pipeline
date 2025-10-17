# 🚀 Quick Start Guide

Get your KPI Pipeline running in 5 minutes!

## Step 1: Install Python (if needed)

**Check if you have Python 3.9+:**
```bash
python --version
```

If you need to install Python, download from [python.org](https://www.python.org/downloads/)

## Step 2: Set Up the Project

**Windows Users:**
```bash
.\setup.bat
```

**Mac/Linux Users:**
```bash
./setup.sh
```

**What this does:**
- ✅ Creates virtual environment
- ✅ Installs required packages
- ✅ Validates setup

**Expected output:**
```
==================================================
KPI Pipeline - Setup Script
==================================================

[1/4] Checking Python version...
✓ Found Python 3.x.x

[2/4] Creating virtual environment...
✓ Virtual environment created

[3/4] Activating virtual environment...
✓ Virtual environment activated

[4/4] Installing requirements...
✓ Requirements installed

==================================================
✓ Setup completed successfully!
==================================================
```

## Step 3: Prepare Your Data

1. **Navigate to the data input folder:**
   ```
   data/input/
   ```

2. **Place your CSV files:**
   - Incident data (required)
   - Request data (required only if using SM003)

3. **Expected file format:**
   - CSV format with headers
   - Required columns: `number`, `priority`, `state`, `opened_at`, `u_resolved`
   - See `data/input/README.md` for detailed schema

**Example files:**
```
data/input/
├── PYTHON EMEA IM (last 90 days)_redacted_clean.csv
└── PYTHON EMEA SCT (last 90 days)_redacted_clean.csv
```

## Step 4: Configure KPIs (Optional)

The default configuration works out-of-the-box, but you can customize:

1. **Open configuration file:**
   ```
   config/kpi_config.yaml
   ```

2. **Common customizations:**
   - Enable/disable specific KPIs
   - Adjust thresholds and targets
   - Modify weightings for overall score

See [`CONFIGURATION.md`](CONFIGURATION.md) for details.

## Step 5: Run the Pipeline

```bash
python main.py
```

**What to expect:**

```
======================================================================
KPI PIPELINE - EXECUTION
======================================================================
Start Time: 2025-10-17 14:30:00

[1/5] Loading configuration...
✓ Configuration loaded: IT Service Management

[2/5] Loading data files...
✓ Loaded 1250 incidents
✓ Loaded 850 requests

[3/5] Transforming data (adding calculated fields)...
✓ Added incident flags
✓ Added request flags

[4/5] Calculating KPIs...
✓ Calculated 4 KPIs + overall score

[5/5] Results:

======================================================================
KPI RESULTS
======================================================================

SM001: Major Incident Management
  Status: Meeting Target
  Adherence: 95.2%
  Business Impact: Low
  P1: 2 (target: ≤3)
  P2: 15 (target: ≤20)
  Total Major: 17

SM002: Backlog Management
  Status: Meeting Target
  Adherence: 96.8%
  Business Impact: Low
  Total: 1250
  Backlog: 40 (3.2%)
  Target: ≥95% adherence

SM003: Request Aging
  Status: Needs Improvement
  Adherence: 88.2%
  Business Impact: Medium
  Total: 850
  Aged: 100 (11.8%)
  Target: ≥95% adherence

SM004: First Contact Resolution
  Status: Meeting Target
  Adherence: 75.5%
  Business Impact: Low
  Total Resolved: 1100
  FCR: 830 (75.5%)
  Target: ≥70%

======================================================================
OVERALL PERFORMANCE
======================================================================
Score: 89.1%
Status: Good
Weights: SM001:25%, SM002:40%, SM003:25%, SM004:10%

======================================================================
✓ Pipeline completed successfully
End Time: 2025-10-17 14:30:15
======================================================================
```

## ✅ What If Everything Works?

**Congratulations! You're ready to:**
- Run the pipeline regularly with your data
- Customize KPIs to your needs
- Integrate into your reporting workflow

**Next steps:**
1. Review [`CONFIGURATION.md`](CONFIGURATION.md) to customize KPIs
2. Set up automated scheduling (cron/Task Scheduler)
3. Explore [`TECHNICAL.md`](TECHNICAL.md) for advanced features

## ❌ What If Something Goes Wrong?

### Error: "Configuration file not found"
**Solution:** Ensure you're running from the project root directory
```bash
cd path/to/kpi_pipeline
python main.py
```

### Error: "ModuleNotFoundError"
**Solution:** Activate virtual environment and install dependencies
```bash
# Windows
.venv\Scripts\activate
pip install -r requirements.txt

# Mac/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

### Error: "CSV file not found"
**Solution:** Place CSV files in `data/input/` directory
```bash
# Check if files exist
ls data/input/
```

### Error: "Python version not supported"
**Solution:** Upgrade to Python 3.9 or higher
```bash
python --version  # Check current version
# Download from python.org
```

### Still having issues?
1. Run the validation tool: `python validate_project.py`
2. Check [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
3. Review error messages carefully
4. Contact support (see README.md)

## 🧪 Verify Installation

Run the validation script to check your setup:
```bash
python validate_project.py
```

This checks:
- ✅ Python version
- ✅ Required files
- ✅ Configuration validity
- ✅ Module imports
- ✅ Data files
- ✅ Git repository

## 🎯 Tips for Success

1. **Start with sample data** - Generate test data to verify setup:
   ```bash
   python tests/generate_sample_data.py
   ```

2. **Run tests** - Validate calculations:
   ```bash
   python tests/test_pipeline.py
   ```

3. **Check configuration** - Use the complete config as reference:
   ```
   config/complete_kpi_config.yaml
   ```

4. **Review outputs** - Check console output for warnings or issues

5. **Keep backups** - Always keep original data files safe

## 📚 Additional Resources

- **Configuration**: [`CONFIGURATION.md`](CONFIGURATION.md)
- **Technical Details**: [`TECHNICAL.md`](TECHNICAL.md)
- **Troubleshooting**: [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- **Maintenance**: [`MAINTENANCE.md`](MAINTENANCE.md)

---

**Need more help?** See the [main README](../README.md) or contact the project team.



