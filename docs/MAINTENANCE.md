# 🛠️ Maintenance Guide

Regular maintenance tasks and procedures for the KPI Pipeline.

## Table of Contents

1. [Regular Maintenance Schedule](#regular-maintenance-schedule)
2. [Configuration Updates](#configuration-updates)
3. [Adding New KPIs](#adding-new-kpis)
4. [Troubleshooting Common Issues](#troubleshooting-common-issues)
5. [Version Updates](#version-updates)
6. [Backup Strategy](#backup-strategy)

---

## Regular Maintenance Schedule

### Weekly Tasks

**1. Monitor Pipeline Execution**
- ✅ Verify pipeline runs successfully
- ✅ Check for any error messages
- ✅ Review KPI results for anomalies

```bash
# Run pipeline and check output
python main.py > output_log.txt 2>&1
```

**2. Validate Data Quality**
- ✅ Check input data for completeness
- ✅ Verify row counts are within expected range
- ✅ Look for missing or null values

**3. Review Logs**
- ✅ Check for warnings or errors
- ✅ Monitor execution time (should be < 30 seconds for typical datasets)

### Monthly Tasks

**1. Update Configuration Review**
- ✅ Review thresholds and targets
- ✅ Check if weights need adjustment
- ✅ Verify KPI enablement settings

**2. Run Test Suite**
```bash
python tests/test_pipeline.py
```

**3. Clean Old Data**
```bash
# Archive or remove old output files
cd data/output
# Move to archive folder or delete as needed
```

**4. Update Dependencies**
```bash
pip list --outdated
# Update specific packages if needed
pip install --upgrade pandas pyyaml openpyxl
```

**5. Backup Configuration**
```bash
# Create timestamped backup
cp config/kpi_config.yaml config/backups/kpi_config_$(date +%Y%m%d).yaml
```

### Quarterly Tasks

**1. Major Configuration Review**
- ✅ Review all KPI targets with stakeholders
- ✅ Assess weight distribution
- ✅ Evaluate threshold appropriateness

**2. Performance Analysis**
- ✅ Analyze KPI trends over quarter
- ✅ Identify patterns or anomalies
- ✅ Prepare summary reports

**3. Code Review**
- ✅ Review custom modifications
- ✅ Check for optimization opportunities
- ✅ Update documentation

**4. Dependency Audit**
```bash
# Check for security vulnerabilities
pip list
pip check
# Consider updating Python version if outdated
```

**5. Git Housekeeping**
```bash
# Archive old branches
git branch --merged
git branch -d old-branch-name

# Tag quarterly release
git tag -a "Q1-2025" -m "Q1 2025 Configuration"
git push origin --tags
```

---

## Configuration Updates

### Standard Update Process

**1. Backup Current Configuration**
```bash
cp config/kpi_config.yaml config/kpi_config.yaml.backup
```

**2. Make Changes**
Edit `config/kpi_config.yaml` with your changes

**3. Validate Changes**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/kpi_config.yaml'))"

# Run validation script
python validate_project.py
```

**4. Test with Sample Data**
```bash
# Generate test data
python tests/generate_sample_data.py

# Run tests
python tests/test_pipeline.py
```

**5. Test with Real Data**
```bash
# Run pipeline with real data
python main.py
```

**6. Commit Changes**
```bash
git add config/kpi_config.yaml
git commit -m "Update [describe change] - [reason]"
git push
```

### Common Configuration Changes

#### Update Thresholds

```yaml
# OLD
thresholds:
  aging:
    backlog_days: 10

# NEW
thresholds:
  aging:
    backlog_days: 15
```

**Testing**: Verify backlog counts change as expected

#### Adjust Weights

```yaml
# OLD
global_status_rules:
  scorecard_scoring:
    weight_sm001: 25
    weight_sm002: 40

# NEW
global_status_rules:
  scorecard_scoring:
    weight_sm001: 30  # Increased importance
    weight_sm002: 35  # Decreased slightly
```

**Important**: Ensure weights still sum to 100%

**Testing**: Verify overall score calculation changes

#### Enable/Disable KPIs

```yaml
# Disable SM003
kpis:
  SM003:
    enabled: false
```

**Testing**: Verify SM003 is skipped and weights adjust automatically

---

## Adding New KPIs

### Step-by-Step Process

#### Step 1: Define Requirements

Document the new KPI:
- **Name**: What is it called?
- **Purpose**: What does it measure?
- **Data Source**: What data is needed?
- **Calculation**: How is it calculated?
- **Target**: What is the goal?
- **Weight**: How important is it?

#### Step 2: Update Configuration

Add to `config/kpi_config.yaml`:

```yaml
kpis:
  SM005:
    enabled: true
    kpi_name: "My New KPI"
    target_value: 95
    threshold: 10
    # Add other parameters as needed
```

Update weights:
```yaml
global_status_rules:
  scorecard_scoring:
    weight_sm001: 20  # Adjusted down
    weight_sm002: 35  # Adjusted down
    weight_sm003: 20  # Adjusted down
    weight_sm004: 10  # Same
    weight_sm005: 15  # New KPI
```

#### Step 3: Implement Calculation Logic

Create function in `src/calculate_kpis.py`:

```python
def calculate_sm005(data, config):
    """
    Calculate SM005: My New KPI
    
    Args:
        data: DataFrame with required data
        config: Configuration dictionary
        
    Returns:
        Dictionary with KPI results
    """
    # Extract configuration
    kpi_config = config['kpis']['SM005']
    target = kpi_config['target_value']
    
    # Perform calculations
    # Example: Calculate percentage
    total_items = len(data)
    qualifying_items = len(data[data['some_condition'] == True])
    percentage = (qualifying_items / total_items) * 100 if total_items > 0 else 0
    
    # Determine adherence
    adherence_rate = percentage if percentage <= target else 100
    
    # Determine status
    if adherence_rate >= 95:
        status = "Meeting Target"
        impact = "Low"
    elif adherence_rate >= 80:
        status = "Needs Improvement"
        impact = "Medium"
    else:
        status = "Below Target"
        impact = "High"
    
    # Return standardized result
    return {
        'KPI_Code': 'SM005',
        'KPI_Name': kpi_config['kpi_name'],
        'Adherence_Rate': round(adherence_rate, 1),
        'Status': status,
        'Business_Impact': impact,
        'Total_Items': total_items,
        'Qualifying_Items': qualifying_items,
        'Percentage': round(percentage, 1),
        'Target': target,
    }
```

#### Step 4: Integrate into Pipeline

Update `calculate_all()` in `src/calculate_kpis.py`:

```python
def calculate_all(incidents, requests, config):
    """Calculate all enabled KPIs."""
    results = {}
    
    # Existing KPIs
    if config['kpis']['SM001']['enabled']:
        results['SM001'] = calculate_sm001(incidents, config)
    
    if config['kpis']['SM002']['enabled']:
        results['SM002'] = calculate_sm002(incidents, config)
    
    # ... other KPIs ...
    
    # NEW KPI
    if config['kpis']['SM005']['enabled']:
        results['SM005'] = calculate_sm005(incidents, config)
    
    # Calculate overall score (includes new KPI automatically)
    results['OVERALL'] = calculate_overall(results, config)
    
    return results
```

#### Step 5: Add Transformation Logic (if needed)

If your KPI needs calculated fields, update `src/transform.py`:

```python
def add_incident_flags(incidents, config):
    """Add calculated flags to incidents."""
    # Existing flags
    # ...
    
    # NEW FLAG for SM005
    if config['kpis']['SM005']['enabled']:
        threshold = config['kpis']['SM005']['threshold']
        incidents['sm005_condition'] = incidents['some_field'] > threshold
    
    return incidents
```

#### Step 6: Update Tests

Add test case in `tests/test_pipeline.py`:

```python
def test_sm005_calculation():
    """Test SM005 calculation."""
    # Test implementation
    pass
```

#### Step 7: Update Documentation

Update these files:
- `README.md` - Add to features list
- `docs/TECHNICAL.md` - Document calculation logic
- `docs/CONFIGURATION.md` - Document configuration options
- `CHANGELOG.md` - Note the addition

#### Step 8: Test Thoroughly

```bash
# Run all tests
python tests/test_pipeline.py

# Validate configuration
python validate_project.py

# Run with real data
python main.py
```

#### Step 9: Deploy

```bash
# Commit changes
git add .
git commit -m "Add SM005: My New KPI"

# Update version
# Edit src/__init__.py: __version__ = "1.1.0"

# Tag release
git tag -a "v1.1.0" -m "Added SM005: My New KPI"
git push origin main --tags
```

---

## Troubleshooting Common Issues

### Issue: Pipeline Not Running

**Checklist**:
1. ✅ Virtual environment activated?
2. ✅ Dependencies installed?
3. ✅ Running from project root?
4. ✅ Data files in correct location?
5. ✅ Configuration file valid?

**Quick Fix**:
```bash
python validate_project.py
```

### Issue: Unexpected KPI Results

**Checklist**:
1. ✅ Check configuration thresholds
2. ✅ Verify data quality
3. ✅ Review calculation logic
4. ✅ Compare with previous results

**Debug Steps**:
```bash
# Run with test data
python tests/generate_sample_data.py
python tests/test_pipeline.py

# Check specific KPI logic
python -c "from src import calculate_kpis; help(calculate_kpis.calculate_sm001)"
```

### Issue: Configuration Changes Not Taking Effect

**Solution**:
1. Verify you edited the correct config file
2. Check YAML syntax is valid
3. Restart Python interpreter if running interactively
4. Clear any cached values

### Issue: Performance Degradation

**Solutions**:
- Check data file size (may have grown)
- Review any custom modifications
- Profile code to find bottlenecks
- Consider optimization (see [`TECHNICAL.md`](TECHNICAL.md))

---

## Version Updates

### Updating Python Packages

**Check for updates**:
```bash
pip list --outdated
```

**Update specific package**:
```bash
pip install --upgrade pandas
```

**Update all packages**:
```bash
pip install --upgrade -r requirements.txt
```

**Test after updates**:
```bash
python tests/test_pipeline.py
python main.py
```

### Updating Python Version

**1. Install new Python version** from python.org

**2. Create new virtual environment**:
```bash
python3.11 -m venv .venv_new
```

**3. Activate and install**:
```bash
# Windows
.venv_new\Scripts\activate

# Mac/Linux
source .venv_new/bin/activate

pip install -r requirements.txt
```

**4. Test thoroughly**:
```bash
python tests/test_pipeline.py
python main.py
```

**5. Switch environments**:
```bash
# Backup old environment
mv .venv .venv_old

# Rename new environment
mv .venv_new .venv
```

### Project Version Updates

Update version in `src/__init__.py`:
```python
__version__ = "1.1.0"
```

Commit and tag:
```bash
git add src/__init__.py
git commit -m "Bump version to 1.1.0"
git tag -a "v1.1.0" -m "Version 1.1.0"
git push origin main --tags
```

---

## Backup Strategy

### What to Backup

**Essential**:
- `config/kpi_config.yaml` - Configuration
- `src/` - Source code (if modified)
- `data/input/` - Input data (archive periodically)

**Optional**:
- `data/output/` - Generated reports (if needed long-term)
- `.git/` - Git repository (if not using remote)

### Backup Methods

#### Method 1: Manual Backups

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Copy important files
cp -r config backups/$(date +%Y%m%d)/
cp -r src backups/$(date +%Y%m%d)/
cp -r data/input backups/$(date +%Y%m%d)/
```

#### Method 2: Git Repository

```bash
# Regular commits
git add .
git commit -m "Weekly backup $(date +%Y-%m-%d)"
git push

# Tag important milestones
git tag -a "backup-$(date +%Y%m%d)" -m "Backup"
git push origin --tags
```

#### Method 3: Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="backups/$DATE"

mkdir -p "$BACKUP_DIR"
cp -r config "$BACKUP_DIR/"
cp -r src "$BACKUP_DIR/"
cp main.py "$BACKUP_DIR/"

echo "Backup created: $BACKUP_DIR"
```

Run monthly:
```bash
chmod +x backup.sh
./backup.sh
```

### Restore from Backup

```bash
# Restore configuration
cp backups/20251017/config/kpi_config.yaml config/

# Restore source code
cp -r backups/20251017/src/* src/

# Verify
python validate_project.py
```

---

## Documentation Maintenance

### Keep Documentation Updated

**When to update**:
- After adding new features
- After configuration changes
- After fixing bugs
- Quarterly review

**Files to maintain**:
- `README.md` - Overview and quick start
- `docs/TECHNICAL.md` - Technical details
- `docs/CONFIGURATION.md` - Configuration guide
- `CHANGELOG.md` - Version history

### Documentation Review Checklist

- ✅ Version numbers current?
- ✅ Configuration examples accurate?
- ✅ Screenshots up-to-date? (if any)
- ✅ Links working?
- ✅ Contact information correct?
- ✅ Installation instructions tested?

---

## Getting Help

For maintenance questions:
- **Technical Issues**: See [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- **Configuration**: See [`CONFIGURATION.md`](CONFIGURATION.md)
- **Development**: See [`TECHNICAL.md`](TECHNICAL.md)
- **Contact**: See main README.md

---

**Remember**: Regular maintenance prevents major issues. Schedule time weekly for basic checks!



