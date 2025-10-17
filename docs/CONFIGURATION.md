# ⚙️ Configuration Guide

Learn how to customize every aspect of the KPI Pipeline.

## Overview

The KPI Pipeline uses YAML configuration files for maximum flexibility. All settings are human-readable and easy to modify.

**Configuration files:**
- `config/kpi_config.yaml` - Main configuration (use this for daily operations)
- `config/complete_kpi_config.yaml` - Reference with all available options

## Quick Configuration Changes

### Enable/Disable KPIs

To disable a KPI (e.g., SM003 - Request Aging):

```yaml
kpis:
  SM003:
    enabled: false  # Change to false
```

**Note**: When SM003 is disabled, weights automatically adjust:
- SM001: 25% → 30%
- SM002: 40% → 50%
- SM004: 10% → 20%

### Change Thresholds

Adjust aging thresholds:

```yaml
thresholds:
  aging:
    backlog_days: 15        # Default: 10
    request_aging_days: 45  # Default: 30
```

### Modify Targets

Change KPI targets:

```yaml
kpis:
  SM001:
    p1_target: 5            # Default: 3
    p2_target: 25           # Default: 20
    target_adherence: 90    # Default: 95
  
  SM004:
    target_rate: 75         # Default: 70
```

### Adjust Weights

Customize importance of each KPI:

```yaml
global_status_rules:
  scorecard_scoring:
    weight_sm001: 30  # Default: 25
    weight_sm002: 35  # Default: 40
    weight_sm003: 25  # Default: 25
    weight_sm004: 10  # Default: 10
    # Total must equal 100
```

## Common Customization Scenarios

### Scenario 1: Focus on Major Incidents

**Goal**: Make major incident management more important

```yaml
global_status_rules:
  scorecard_scoring:
    weight_sm001: 40  # Increase from 25
    weight_sm002: 30  # Decrease from 40
    weight_sm003: 20  # Decrease from 25
    weight_sm004: 10  # Keep at 10

kpis:
  SM001:
    p1_target: 2      # Stricter target
    p2_target: 15     # Stricter target
    target_adherence: 98  # Higher adherence required
```

### Scenario 2: Relaxed Backlog Criteria

**Goal**: Allow longer aging before flagging as backlog

```yaml
thresholds:
  aging:
    backlog_days: 15  # Increase from 10

kpis:
  SM002:
    target_adherence: 90  # Reduce from 95
```

### Scenario 3: Emphasize First Contact Resolution

**Goal**: Make FCR the primary metric

```yaml
global_status_rules:
  scorecard_scoring:
    weight_sm001: 20
    weight_sm002: 30
    weight_sm003: 20
    weight_sm004: 30  # Increase from 10

kpis:
  SM004:
    target_rate: 80  # Increase from 70
    fcr_criteria:
      max_reassignments: 0
      must_be_resolved: true
```

### Scenario 4: Skip Request Data

**Goal**: Only analyze incidents (no request data)

```yaml
kpis:
  SM003:
    enabled: false  # Disable request aging KPI
```

**Result**: Pipeline will skip loading request data entirely and adjust weights automatically.

### Scenario 5: Different Performance Bands

**Goal**: Adjust what qualifies as "Excellent" vs "Good"

```yaml
thresholds:
  performance_bands:
    excellent: 95     # Default: 90 (stricter)
    good: 85          # Default: 80 (stricter)
    needs_improvement: 70  # Default: 60 (stricter)
```

## Configuration Sections Explained

### 1. Metadata

```yaml
metadata:
  version: "1.0"
  description: "KPI Processing Configuration"
  organization: "IT Service Management"
  schema_version: "2.0"
```

**Purpose**: Document configuration version and ownership  
**When to change**: Update when making significant configuration changes

### 2. Column Mappings

```yaml
column_mappings:
  number: "number"
  priority: "priority"
  state: "incident_state"
  opened_at: "opened_at"
  resolved_at: "u_resolved"
  reassignment_count: "reassignment_count"
  country: "location_country"
  contact_type: "contact_type"
```

**Purpose**: Map CSV column names to expected field names  
**When to change**: When your CSV uses different column names

**Example**: If your CSV has "Ticket_Number" instead of "number":
```yaml
column_mappings:
  number: "Ticket_Number"  # Change this
```

### 3. Processing Rules

```yaml
processing:
  priority_extraction:
    regex_pattern: "\\d+"
    fallback_value: 99
  date_parsing:
    auto_detect: true
    formats: 
      - "%Y-%m-%d %H:%M:%S"
  signature_fields:
    - "number"
    - "priority"
    - "state"
```

**Purpose**: Define how to parse and extract data  

**Priority extraction**: Handles mixed priority formats like "1 - High"
- `regex_pattern`: Pattern to extract number
- `fallback_value`: Value to use if extraction fails

**Date parsing**:
- `auto_detect`: Let pandas auto-detect date formats
- `formats`: Explicit formats to try (if auto_detect fails)

**Signature fields**: Fields used for row identification/deduplication

### 4. Thresholds

```yaml
thresholds:
  priority:
    major_incident_levels: [1, 2]
  aging:
    backlog_days: 10
    request_aging_days: 30
  performance_bands:
    excellent: 90
    good: 80
    needs_improvement: 60
```

**Purpose**: Define numeric limits and bands

**When to change**:
- `major_incident_levels`: Rarely (industry standard: P1/P2)
- `aging` thresholds: Based on your SLA requirements
- `performance_bands`: Based on organizational standards

### 5. Global Status Rules

```yaml
global_status_rules:
  scorecard_scoring:
    weight_sm001: 25
    weight_sm002: 40
    weight_sm003: 25
    weight_sm004: 10
    sm003_disabled_weights:
      weight_sm001: 30
      weight_sm002: 50
      weight_sm004: 20
```

**Purpose**: Define how overall score is calculated

**Important**: Weights must sum to 100

**sm003_disabled_weights**: Automatic fallback weights when SM003 is disabled

### 6. KPI Definitions

Each KPI has its own configuration block:

```yaml
kpis:
  SM001:
    enabled: true
    kpi_name: "Major Incident Management"
    p1_target: 3
    p2_target: 20
    target_adherence: 95
  
  SM002:
    enabled: true
    kpi_name: "Backlog Management"
    target_adherence: 95
  
  SM003:
    enabled: true
    kpi_name: "Request Aging"
    target_adherence: 95
  
  SM004:
    enabled: true
    kpi_name: "First Contact Resolution"
    target_rate: 70
    fcr_criteria:
      max_reassignments: 0
      must_be_resolved: true
```

## Validation

### Test Your Configuration

After making changes, validate configuration:

```bash
python validate_project.py
```

This checks:
- ✅ YAML syntax is valid
- ✅ Required sections exist
- ✅ Values are within acceptable ranges

### Run a Test

Run the pipeline with test data:

```bash
# Generate sample data
python tests/generate_sample_data.py

# Run test suite
python tests/test_pipeline.py
```

## Configuration Best Practices

### 1. Version Control
- Commit configuration changes to git
- Document why changes were made
- Tag significant configuration versions

```bash
git add config/kpi_config.yaml
git commit -m "Update SM001 targets for Q1 2025"
git tag -a "config-v1.1" -m "Stricter major incident targets"
```

### 2. Backup Before Changes
```bash
cp config/kpi_config.yaml config/kpi_config.yaml.backup
```

### 3. Validate After Changes
```bash
# Quick validation
python -c "import yaml; yaml.safe_load(open('config/kpi_config.yaml'))"

# Full validation
python validate_project.py
```

### 4. Document Custom Settings
Add comments to explain non-standard values:

```yaml
kpis:
  SM001:
    p1_target: 5  # Increased due to project rollouts in Q1
    p2_target: 25
```

### 5. Use Complete Config as Reference
Keep `config/complete_kpi_config.yaml` as a reference - don't edit it directly.

## Troubleshooting Configuration Issues

### Error: "YAML parsing error"

**Cause**: Invalid YAML syntax  
**Solution**: Check for:
- Proper indentation (use spaces, not tabs)
- Missing colons
- Unquoted strings with special characters

**Tool to help**: Online YAML validator (yamllint.com)

### Error: "Missing required key"

**Cause**: Configuration missing a required section  
**Solution**: Compare with `complete_kpi_config.yaml` and add missing sections

### Unexpected KPI Results

**Cause**: Configuration doesn't match expectations  
**Solution**: 
1. Review threshold values
2. Check target adherence settings
3. Verify weights sum to 100
4. Run test suite to validate

### KPI Not Running

**Cause**: KPI disabled or missing data  
**Solution**:
```yaml
kpis:
  SM003:
    enabled: true  # Ensure set to true
```

## Environment-Specific Configurations

### Development

```yaml
# config/kpi_config.dev.yaml
metadata:
  environment: "development"

thresholds:
  aging:
    backlog_days: 5  # Stricter for testing
```

### Production

```yaml
# config/kpi_config.prod.yaml
metadata:
  environment: "production"

thresholds:
  aging:
    backlog_days: 10  # Standard SLA
```

**Usage**:
```python
# In main.py or as command-line argument
config = config_loader.load_config('config/kpi_config.prod.yaml')
```

## Advanced: Dynamic Configuration

For programmatic configuration updates:

```python
import yaml

# Load config
with open('config/kpi_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Modify
config['kpis']['SM001']['p1_target'] = 5

# Save
with open('config/kpi_config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
```

## Getting Help

- **Configuration issues**: Check [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- **Technical details**: See [`TECHNICAL.md`](TECHNICAL.md)
- **Questions**: Contact the project team

---

**Need more examples?** Check `config/complete_kpi_config.yaml` for all available options.



