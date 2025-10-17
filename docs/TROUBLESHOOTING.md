# 🔍 Troubleshooting Guide

Common issues and their solutions.

## Quick Diagnostic

Run the validation script first:
```bash
python validate_project.py
```

This will identify most common issues automatically.

---

## Data Loading Issues

### Issue: "FileNotFoundError: CSV file not found"

**Symptoms**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/input/...'
```

**Causes**:
1. CSV file not in correct location
2. Incorrect file name
3. Running from wrong directory

**Solutions**:

**1. Check file location**:
```bash
# List files in data/input
ls data/input/        # Mac/Linux
dir data\input\       # Windows
```

**2. Verify file names**:
Expected format: `data/input/[filename].csv`

**3. Check current directory**:
```bash
# Should be in project root
pwd   # Mac/Linux
cd    # Windows
```
If not in project root:
```bash
cd path/to/kpi_pipeline
```

**4. Update file paths in main.py** (if using different names):
```python
incidents = load_data.load_incidents(
    'data/input/YOUR_ACTUAL_FILENAME.csv',  # Update this
    config
)
```

### Issue: "KeyError: Column not found"

**Symptoms**:
```
KeyError: 'priority'
```

**Cause**: CSV missing required columns or column names don't match configuration

**Solutions**:

**1. Check CSV columns**:
```python
import pandas as pd
df = pd.read_csv('data/input/your_file.csv')
print(df.columns.tolist())
```

**2. Update column mappings** in `config/kpi_config.yaml`:
```yaml
column_mappings:
  number: "ticket_number"  # Map to your actual column name
  priority: "priority_level"
  # ... etc
```

**3. Verify required columns exist**:
- Incidents: `number`, `priority`, `state`, `opened_at`, `u_resolved`, `reassignment_count`
- Requests: `number`, `state`, `opened_at`, `u_resolved`

### Issue: "Date parsing errors"

**Symptoms**:
```
ValueError: time data '...' does not match format '%Y-%m-%d %H:%M:%S'
```

**Cause**: Date format in CSV doesn't match expected format

**Solutions**:

**1. Enable auto-detection**:
```yaml
processing:
  date_parsing:
    auto_detect: true
```

**2. Add your date format**:
```yaml
processing:
  date_parsing:
    auto_detect: true
    formats:
      - "%Y-%m-%d %H:%M:%S"
      - "%d/%m/%Y %H:%M"      # Add your format
      - "%m-%d-%Y %I:%M:%S %p"
```

Common date formats:
- `%Y-%m-%d %H:%M:%S` → 2025-10-17 14:30:00
- `%d/%m/%Y %H:%M` → 17/10/2025 14:30
- `%m-%d-%Y` → 10-17-2025

### Issue: "Empty DataFrame" or "No data loaded"

**Symptoms**:
```
Loaded 0 incidents
```

**Causes**:
1. CSV file is empty
2. File encoding issues
3. Incorrect delimiter

**Solutions**:

**1. Check file content**:
```bash
head data/input/your_file.csv  # First 10 lines
```

**2. Check file encoding**:
```python
# Try different encodings
df = pd.read_csv('file.csv', encoding='utf-8')
df = pd.read_csv('file.csv', encoding='latin1')
df = pd.read_csv('file.csv', encoding='cp1252')
```

**3. Check delimiter**:
```python
# If using semicolon or tab instead of comma
df = pd.read_csv('file.csv', sep=';')
df = pd.read_csv('file.csv', sep='\t')
```

---

## Configuration Issues

### Issue: "Configuration file not found"

**Symptoms**:
```
FileNotFoundError: Configuration file not found: config/kpi_config.yaml
```

**Solutions**:

**1. Verify file exists**:
```bash
ls config/kpi_config.yaml      # Mac/Linux
dir config\kpi_config.yaml     # Windows
```

**2. Check running from project root**:
```bash
pwd  # Should show: .../kpi_pipeline
```

**3. Specify full path** (temporary workaround):
```python
config = config_loader.load_config('C:/full/path/to/config/kpi_config.yaml')
```

### Issue: "YAML parsing error"

**Symptoms**:
```
yaml.scanner.ScannerError: mapping values are not allowed here
```

**Cause**: Invalid YAML syntax

**Solutions**:

**1. Check indentation** (must use spaces, not tabs):
```yaml
# WRONG (uses tabs or mixed)
kpis:
	SM001:
  enabled: true

# CORRECT (uses spaces consistently)
kpis:
  SM001:
    enabled: true
```

**2. Check colons and quotes**:
```yaml
# WRONG
kpi_name Major Incident Management

# CORRECT
kpi_name: "Major Incident Management"
```

**3. Validate YAML**:
```bash
# Use Python to validate
python -c "import yaml; yaml.safe_load(open('config/kpi_config.yaml'))"
```

**4. Use online validator**: yamllint.com

### Issue: "Missing required configuration key"

**Symptoms**:
```
KeyError: 'kpis'
```

**Cause**: Configuration file missing required sections

**Solution**: Compare with `config/complete_kpi_config.yaml` and add missing sections

---

## Calculation Issues

### Issue: "All KPIs show 0% or 100%"

**Cause**: Data not being filtered or transformed correctly

**Solutions**:

**1. Check data transformation**:
```bash
# Run test suite to validate
python tests/test_pipeline.py
```

**2. Verify date columns**:
```python
# Check if dates are being parsed
print(incidents['opened_at'].dtype)  # Should be datetime64
print(incidents['u_resolved'].dtype)  # Should be datetime64
```

**3. Check for null values**:
```python
print(incidents.isnull().sum())
```

### Issue: "SM003 not running"

**Symptoms**: SM003 skipped or not in results

**Causes**:
1. SM003 disabled in configuration
2. Request data file not found
3. Request data failed to load

**Solutions**:

**1. Check if enabled**:
```yaml
kpis:
  SM003:
    enabled: true  # Must be true
```

**2. Verify request file exists**:
```bash
ls data/input/*request*.csv  # Or similar pattern
```

**3. Check console output** for errors during request loading

### Issue: "Adherence rates seem incorrect"

**Symptoms**: Results don't match manual calculations

**Solutions**:

**1. Check thresholds**:
```yaml
thresholds:
  aging:
    backlog_days: 10        # Verify these values
    request_aging_days: 30
```

**2. Verify targets**:
```yaml
kpis:
  SM001:
    p1_target: 3
    p2_target: 20
    target_adherence: 95  # Check these match expectations
```

**3. Review calculation logic**:
See [`TECHNICAL.md`](TECHNICAL.md) for detailed calculation formulas

**4. Generate test data and compare**:
```bash
python tests/generate_sample_data.py
python tests/test_pipeline.py
```

---

## Excel Output Issues

### Issue: "ModuleNotFoundError: No module named 'openpyxl'"

**Symptoms**:
```
ModuleNotFoundError: No module named 'openpyxl'
```

**Cause**: openpyxl package not installed

**Solution**:
```bash
pip install openpyxl
# Or reinstall all requirements
pip install -r requirements.txt
```

### Issue: "Permission denied writing Excel file"

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: 'data/output/report.xlsx'
```

**Cause**: File is open in Excel

**Solution**: Close the Excel file and run again

---

## Import Issues

### Issue: "ModuleNotFoundError: No module named 'src'"

**Symptoms**:
```
ModuleNotFoundError: No module named 'src'
```

**Causes**:
1. Virtual environment not activated
2. Running from wrong directory
3. src/__init__.py missing

**Solutions**:

**1. Activate virtual environment**:
```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

**2. Check current directory**:
```bash
pwd  # Should be in project root
```

**3. Verify src/__init__.py exists**:
```bash
ls src/__init__.py
```

**4. Add to Python path** (temporary workaround):
```python
import sys
sys.path.insert(0, 'path/to/kpi_pipeline')
```

### Issue: "ImportError: cannot import name 'config_loader'"

**Cause**: Import statement incorrect

**Solution**: Check import format in main.py:
```python
# CORRECT
from src import config_loader
from src import load_data

# WRONG
import config_loader
import load_data
```

---

## Environment Issues

### Issue: "Python version not supported"

**Symptoms**:
```
SyntaxError: invalid syntax
```
(or features not working)

**Cause**: Python version < 3.9

**Solution**:

**1. Check Python version**:
```bash
python --version
```

**2. Upgrade Python**: Download from python.org

**3. Use specific Python version**:
```bash
python3.9 -m venv .venv
# Or
python3.10 -m venv .venv
```

### Issue: "Package installation fails"

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:

**1. Upgrade pip**:
```bash
python -m pip install --upgrade pip
```

**2. Install packages individually**:
```bash
pip install pandas
pip install pyyaml
pip install openpyxl
pip install python-dateutil
```

**3. Check internet connection**

**4. Use proxy** (if behind corporate firewall):
```bash
pip install --proxy=http://proxy:port -r requirements.txt
```

---

## Git Issues

### Issue: "Git not found"

**Cause**: Git not installed

**Solution**: Download from git-scm.com

**Note**: Git is optional for running the pipeline, only needed for version control

### Issue: "Permission denied (publickey)"

**Symptoms**: When pushing to GitHub

**Solution**:
1. Set up SSH keys: https://docs.github.com/en/authentication
2. Or use HTTPS instead: `git remote set-url origin https://github.com/[USER]/[REPO].git`

---

## Performance Issues

### Issue: "Pipeline runs very slowly"

**Causes**:
1. Large dataset (>100,000 rows)
2. Inefficient data types
3. Multiple redundant calculations

**Solutions**:

**1. Check data size**:
```python
import pandas as pd
df = pd.read_csv('data/input/file.csv')
print(f"Rows: {len(df)}, Memory: {df.memory_usage().sum() / 1024**2:.2f} MB")
```

**2. Optimize data types**:
```python
# Use categorical for repeated values
df['country'] = df['country'].astype('category')
df['state'] = df['state'].astype('category')
```

**3. Filter early**:
```python
# Filter to date range before processing
df = df[df['opened_at'] >= '2025-01-01']
```

### Issue: "Out of memory errors"

**Cause**: Dataset too large for available RAM

**Solutions**:

**1. Process in chunks**:
```python
for chunk in pd.read_csv('file.csv', chunksize=10000):
    # Process each chunk
    pass
```

**2. Use only required columns**:
```python
df = pd.read_csv('file.csv', usecols=['number', 'priority', 'opened_at'])
```

**3. Upgrade RAM or use database backend**

---

## Getting Additional Help

### 1. Run Diagnostics
```bash
python validate_project.py
```

### 2. Check Logs
Review console output for error messages and stack traces

### 3. Test with Sample Data
```bash
python tests/generate_sample_data.py
python tests/test_pipeline.py
```

### 4. Review Documentation
- [`TECHNICAL.md`](TECHNICAL.md) - Technical details
- [`CONFIGURATION.md`](CONFIGURATION.md) - Configuration help
- [`QUICKSTART.md`](QUICKSTART.md) - Setup guide

### 5. Contact Support
- Project Lead: [email]
- Technical Contact: [email]
- GitHub Issues: [repo]/issues

---

## Still Having Issues?

When reporting issues, include:

1. **Error message** (full stack trace)
2. **Python version**: `python --version`
3. **Environment**: OS, virtual environment status
4. **Steps to reproduce**
5. **Configuration** (sanitized YAML)
6. **Data sample** (anonymized, first few rows)
7. **Console output** (full output from running main.py)

This helps us diagnose and fix issues faster!



