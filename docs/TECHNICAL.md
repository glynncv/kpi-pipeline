# 🔧 Technical Documentation

Comprehensive technical reference for the KPI Pipeline.

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                        KPI Pipeline                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ CSV Files    │──────▶│ Data Loader  │                    │
│  │ (Incidents   │      │ (load_data)  │                    │
│  │  & Requests) │      └──────┬───────┘                    │
│  └──────────────┘             │                             │
│                                ▼                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │ YAML Config  │──────▶│ Transformer  │                    │
│  │              │      │ (transform)  │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                                ▼                             │
│                        ┌──────────────┐                    │
│                        │ KPI Engine   │                    │
│                        │ (calculate_  │                    │
│                        │  kpis)       │                    │
│                        └──────┬───────┘                    │
│                                ▼                             │
│                        ┌──────────────┐                    │
│                        │ Results      │                    │
│                        │ (Console/    │                    │
│                        │  Excel)      │                    │
│                        └──────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

### Module Structure

#### 1. **config_loader.py**
- **Purpose**: Load and validate YAML configuration
- **Key Functions**:
  - `load_config(config_path)`: Load YAML configuration
  - Validates required sections and keys
  - Provides defaults for missing optional values

#### 2. **load_data.py**
- **Purpose**: Load and validate CSV data files
- **Key Functions**:
  - `load_incidents(file_path, config)`: Load incident data
  - `load_requests(file_path, config)`: Load request data
- **Features**:
  - Automatic date parsing
  - Priority extraction from mixed strings
  - Column mapping from configuration
  - Data validation and type conversion

#### 3. **transform.py**
- **Purpose**: Add calculated fields to raw data
- **Key Functions**:
  - `add_incident_flags(incidents, config)`: Add incident-specific flags
  - `add_request_flags(requests, config)`: Add request-specific flags
- **Calculated Fields**:
  - `is_major_incident`: Boolean flag for P1/P2
  - `is_backlog`: Boolean flag for aged incidents
  - `is_aged`: Boolean flag for aged requests
  - `age_days`: Numeric age in days
  - `is_first_contact_resolution`: Boolean flag for FCR

#### 4. **calculate_kpis.py**
- **Purpose**: Calculate all KPI metrics
- **Key Functions**:
  - `calculate_all(incidents, requests, config)`: Master calculation function
  - `calculate_sm001(incidents, config)`: Major incident management
  - `calculate_sm002(incidents, config)`: Backlog management
  - `calculate_sm003(requests, config)`: Request aging
  - `calculate_sm004(incidents, config)`: First contact resolution
  - `calculate_overall(kpi_results, config)`: Overall weighted score

## Configuration Reference

### Complete YAML Structure

```yaml
metadata:
  version: "1.0"
  description: "KPI Processing Configuration"
  organization: "IT Service Management"
  schema_version: "2.0"

column_mappings:
  number: "number"                    # Ticket number field
  priority: "priority"                # Priority field
  state: "incident_state"             # State/status field
  opened_at: "opened_at"              # Open timestamp
  resolved_at: "u_resolved"           # Resolution timestamp
  reassignment_count: "reassignment_count"
  country: "location_country"         # Geographic location
  contact_type: "contact_type"        # Channel (phone, email, etc.)

processing:
  priority_extraction:
    regex_pattern: "\\d+"             # Extract priority number
    fallback_value: 99                # Default if extraction fails
  date_parsing:
    auto_detect: true                 # Auto-detect date formats
    formats:
      - "%Y-%m-%d %H:%M:%S"
  signature_fields:                   # Fields for deduplication
    - "number"
    - "priority"
    - "state"

thresholds:
  priority:
    major_incident_levels: [1, 2]     # P1 and P2 are major
  aging:
    backlog_days: 10                  # Incidents aged > 10 days
    request_aging_days: 30            # Requests aged > 30 days
  performance_bands:
    excellent: 90                     # ≥90% = Excellent
    good: 80                          # 80-89% = Good
    needs_improvement: 60             # <80% = Needs Improvement

global_status_rules:
  scorecard_scoring:
    weight_sm001: 25                  # Major incidents: 25%
    weight_sm002: 40                  # Backlog: 40%
    weight_sm003: 25                  # Request aging: 25%
    weight_sm004: 10                  # FCR: 10%
    sm003_disabled_weights:           # If SM003 disabled:
      weight_sm001: 30
      weight_sm002: 50
      weight_sm004: 20

kpis:
  SM001:                              # Major Incident Management
    enabled: true
    kpi_name: "Major Incident Management"
    p1_target: 3
    p2_target: 20
    target_adherence: 95              # Target: ≥95% adherence
  
  SM002:                              # Backlog Management
    enabled: true
    kpi_name: "Backlog Management"
    target_adherence: 95
  
  SM003:                              # Request Aging
    enabled: true
    kpi_name: "Request Aging"
    target_adherence: 95
  
  SM004:                              # First Contact Resolution
    enabled: true
    kpi_name: "First Contact Resolution"
    target_rate: 70                   # Target: ≥70% FCR rate
    fcr_criteria:
      max_reassignments: 0            # Zero reassignments
      must_be_resolved: true          # Must be in resolved state
```

## KPI Calculation Logic

### SM001: Major Incident Management

**Purpose**: Track major (P1/P2) incidents against defined targets

**Calculation**:
```python
# Count P1 and P2 incidents
p1_count = incidents[priority == 1].count()
p2_count = incidents[priority == 2].count()
total_major = p1_count + p2_count

# Check against targets
p1_within_target = p1_count <= p1_target
p2_within_target = p2_count <= p2_target

# Adherence calculation
if p1_within_target AND p2_within_target:
    adherence = 100%
else:
    adherence = calculated based on overages

# Business impact
if adherence >= 95%: "Low"
elif adherence >= 80%: "Medium"
else: "High"
```

**Example**:
```
Input:
  P1 incidents: 2 (target: 3)
  P2 incidents: 15 (target: 20)

Output:
  Adherence: 100%
  Status: Meeting Target
  Business Impact: Low
```

### SM002: Backlog Management

**Purpose**: Monitor incidents aged beyond threshold

**Calculation**:
```python
# Calculate age for unresolved incidents
for incident in unresolved_incidents:
    if resolved_at is empty:
        age_days = (today - opened_at).days
        is_backlog = age_days > backlog_threshold (10 days)

# Calculate metrics
backlog_count = incidents[is_backlog == True].count()
backlog_percentage = (backlog_count / total_incidents) * 100
adherence_rate = 100 - backlog_percentage

# Status
if adherence >= 95%: "Meeting Target"
elif adherence >= 80%: "Needs Improvement"
else: "Below Target"
```

**Example**:
```
Input:
  Total incidents: 1000
  Backlog (>10 days): 30
  
Output:
  Backlog percentage: 3.0%
  Adherence: 97.0%
  Status: Meeting Target
```

### SM003: Request Aging

**Purpose**: Track service requests exceeding age limits

**Calculation**:
```python
# Calculate age for unresolved requests
for request in unresolved_requests:
    if resolved_at is empty:
        age_days = (today - opened_at).days
        is_aged = age_days > aging_threshold (30 days)

# Calculate metrics
aged_count = requests[is_aged == True].count()
aged_percentage = (aged_count / total_requests) * 100
adherence_rate = 100 - aged_percentage

# Status (same logic as SM002)
```

**Example**:
```
Input:
  Total requests: 800
  Aged (>30 days): 50
  
Output:
  Aged percentage: 6.25%
  Adherence: 93.75%
  Status: Needs Improvement
```

### SM004: First Contact Resolution

**Purpose**: Measure resolution efficiency on first contact

**Calculation**:
```python
# Identify FCR
for incident in resolved_incidents:
    is_fcr = (
        reassignment_count == 0 AND
        state in ['Resolved', 'Closed']
    )

# Calculate metrics
fcr_count = incidents[is_fcr == True].count()
total_resolved = resolved_incidents.count()
fcr_percentage = (fcr_count / total_resolved) * 100

# Status
if fcr_percentage >= target_rate (70%): "Meeting Target"
else: "Below Target"
```

**Example**:
```
Input:
  Total resolved: 900
  FCR incidents: 675
  
Output:
  FCR rate: 75.0%
  Status: Meeting Target
```

### Overall Score

**Purpose**: Weighted average of all enabled KPIs

**Calculation**:
```python
# Default weights (SM003 enabled)
weights = {
    'SM001': 25%,
    'SM002': 40%,
    'SM003': 25%,
    'SM004': 10%
}

# If SM003 disabled, adjust weights
if not SM003.enabled:
    weights = {
        'SM001': 30%,
        'SM002': 50%,
        'SM004': 20%
    }

# Calculate weighted score
overall_score = sum(kpi_adherence * weight for each enabled KPI)

# Performance band
if overall_score >= 90%: "Excellent"
elif overall_score >= 80%: "Good"
else: "Needs Improvement"
```

**Example**:
```
Input:
  SM001: 100% × 25% = 25.0
  SM002: 97% × 40% = 38.8
  SM003: 93.75% × 25% = 23.4
  SM004: 75% × 10% = 7.5
  
Output:
  Overall Score: 94.7%
  Status: Excellent
```

## Data Model

### Incident Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| number | string | Yes | Unique incident identifier |
| priority | string/int | Yes | Priority level (1-4) |
| incident_state | string | Yes | Current state |
| opened_at | datetime | Yes | Open timestamp |
| u_resolved | datetime | No | Resolution timestamp |
| reassignment_count | int | Yes | Number of reassignments |
| location_country | string | No | Country location |
| contact_type | string | No | Contact channel |

### Request Schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| number | string | Yes | Unique request identifier |
| state | string | Yes | Current state |
| opened_at | datetime | Yes | Open timestamp |
| u_resolved | datetime | No | Resolution timestamp |
| location_country | string | No | Country location |
| contact_type | string | No | Contact channel |

## Function API Reference

### config_loader.load_config()

```python
def load_config(config_path: str = "config/kpi_config.yaml") -> Dict[str, Any]:
    """
    Load KPI configuration from YAML file.
    
    Args:
        config_path: Path to YAML configuration file
        
    Returns:
        Dictionary containing configuration data
        
    Raises:
        FileNotFoundError: If configuration file doesn't exist
        yaml.YAMLError: If configuration file is invalid
    """
```

### load_data.load_incidents()

```python
def load_incidents(file_path: str, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Load incident data from CSV file.
    
    Args:
        file_path: Path to CSV file
        config: Configuration dictionary
        
    Returns:
        DataFrame with loaded and validated incident data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
```

### transform.add_incident_flags()

```python
def add_incident_flags(incidents: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
    """
    Add calculated flags to incident data.
    
    Args:
        incidents: Incident DataFrame
        config: Configuration dictionary
        
    Returns:
        DataFrame with added calculated fields
    """
```

### calculate_kpis.calculate_all()

```python
def calculate_all(incidents: pd.DataFrame, requests: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate all enabled KPIs.
    
    Args:
        incidents: Transformed incident DataFrame
        requests: Transformed request DataFrame (or None)
        config: Configuration dictionary
        
    Returns:
        Dictionary with KPI results for all enabled KPIs plus OVERALL
    """
```

## Extension Guide

### Adding a New KPI

**1. Update Configuration** (`config/kpi_config.yaml`):

```yaml
kpis:
  SM005:
    enabled: true
    kpi_name: "My New KPI"
    target_value: 95
    # ... other parameters
```

**2. Create Calculation Function** (`src/calculate_kpis.py`):

```python
def calculate_sm005(data, config):
    """Calculate SM005: My New KPI."""
    
    # Extract configuration
    kpi_config = config['kpis']['SM005']
    target = kpi_config['target_value']
    
    # Perform calculations
    # ... your logic here
    
    # Return standardized result
    return {
        'KPI_Code': 'SM005',
        'KPI_Name': kpi_config['kpi_name'],
        'Adherence_Rate': adherence_rate,
        'Status': status,
        'Business_Impact': impact,
        # ... other fields
    }
```

**3. Integrate into Pipeline** (`src/calculate_kpis.py`):

```python
def calculate_all(incidents, requests, config):
    results = {}
    
    # Existing KPIs
    # ...
    
    # Add new KPI
    if config['kpis']['SM005']['enabled']:
        results['SM005'] = calculate_sm005(incidents, config)
    
    # Calculate overall
    results['OVERALL'] = calculate_overall(results, config)
    
    return results
```

**4. Update Weights** (if applicable):

```yaml
global_status_rules:
  scorecard_scoring:
    weight_sm001: 20
    weight_sm002: 35
    weight_sm003: 20
    weight_sm004: 10
    weight_sm005: 15  # New KPI weight
```

## Performance Considerations

### Data Volume

- **Tested with**: Up to 100,000 records
- **Memory usage**: ~500MB for 50,000 records
- **Execution time**: ~5-10 seconds for typical dataset

### Optimization Tips

1. **Use appropriate data types**: Convert to pandas categorical for repeated values
2. **Filter early**: Apply filters before calculations
3. **Vectorize operations**: Avoid Python loops, use pandas vectorized operations
4. **Cache configuration**: Load configuration once, reuse across calls

### Scaling

For very large datasets (>500,000 records):
- Consider chunked processing
- Use Dask for distributed computing
- Implement database backend instead of CSV

## Error Handling

### Common Exceptions

| Exception | Cause | Solution |
|-----------|-------|----------|
| FileNotFoundError | CSV or YAML not found | Check file paths |
| KeyError | Missing configuration key | Validate YAML structure |
| ValueError | Invalid data type | Check data format |
| pandas.errors.ParserError | Malformed CSV | Validate CSV format |

### Logging

Currently outputs to console. To add file logging:

```python
import logging

logging.basicConfig(
    filename='kpi_pipeline.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

---

For more information, see:
- [`CONFIGURATION.md`](CONFIGURATION.md) - Configuration guide
- [`MAINTENANCE.md`](MAINTENANCE.md) - Maintenance procedures
- [Source code](../src/) - Implementation details



