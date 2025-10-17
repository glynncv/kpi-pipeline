# Project Directory Structure

Copy this structure exactly when setting up in Cursor:

```
kpi-pipeline/                          ← Root project folder
│
├── src/                               ← Source code package
│   ├── __init__.py                    ⚠️ RENAME: src__init__.py → __init__.py
│   ├── config_loader.py               ✓ From Conversation 1
│   ├── load_data.py                   ✓ From Conversation 2
│   ├── transform.py                   ✓ From Conversation 3
│   ├── calculate_kpis.py              ✓ From Conversation 4
│   └── generate_reports.py            ✓ From Conversation 5
│
├── config/                            ← Configuration files
│   ├── kpi_config.yaml                ✓ From kpi-config-yaml.txt
│   └── complete_kpi_config.yaml       ✓ From complete-kpi-config-yaml.txt
│
├── data/                              ← Data directory
│   ├── inputs/                        ← Input CSV files
│   │   ├── .gitkeep                   ℹ️ Optional: keeps folder in Git
│   │   ├── PYTHON EMEA IM (last 90 days)_redacted_clean.csv
│   │   └── PYTHON EMEA SCT last 90 days_redacted_clean.csv
│   │
│   └── outputs/                       ← Generated Excel reports
│       └── .gitkeep                   ℹ️ Optional: keeps folder in Git
│
├── logs/                              ← Log files (optional)
│   └── .gitkeep                       ℹ️ Optional: keeps folder in Git
│
├── venv/                              ← Virtual environment (created by setup)
│   └── ...                            ⚠️ DO NOT COMMIT TO GIT
│
├── main.py                            ✓ From Conversation 5 - Entry point
│
├── requirements.txt                   ✓ From this deployment package
├── .gitignore                         ⚠️ RENAME: gitignore.txt → .gitignore
│
├── README.md                          ✓ From this deployment package
├── DEPLOYMENT_CHECKLIST.md            ✓ From this deployment package
├── DEPLOYMENT_SUMMARY.md              ✓ From this deployment package
├── QUICK_REFERENCE.md                 ✓ From this deployment package
├── GITKEEP_INSTRUCTIONS.md            ✓ From this deployment package
└── START_HERE.md                      ✓ From this deployment package

```

## File Count Verification

After copying all files, you should have:

### Source Code (7 files)
- [ ] src/__init__.py
- [ ] src/config_loader.py
- [ ] src/load_data.py
- [ ] src/transform.py
- [ ] src/calculate_kpis.py
- [ ] src/generate_reports.py
- [ ] main.py

### Configuration (2 files)
- [ ] config/kpi_config.yaml
- [ ] config/complete_kpi_config.yaml

### Documentation (6 files)
- [ ] README.md
- [ ] DEPLOYMENT_CHECKLIST.md
- [ ] DEPLOYMENT_SUMMARY.md
- [ ] QUICK_REFERENCE.md
- [ ] GITKEEP_INSTRUCTIONS.md
- [ ] START_HERE.md

### Infrastructure (2 files)
- [ ] requirements.txt
- [ ] .gitignore

### Data Files (2 files)
- [ ] data/inputs/PYTHON EMEA IM (last 90 days)_redacted_clean.csv
- [ ] data/inputs/PYTHON EMEA SCT last 90 days_redacted_clean.csv

**Total**: 19 files (excluding .gitkeep placeholders and venv/)

## Important Notes

### Files to Rename
1. `gitignore.txt` → `.gitignore` (note the leading dot)
2. `src__init__.py` → `src/__init__.py` (place in src folder)

### Empty Directories to Create
```bash
mkdir -p data/outputs
mkdir -p logs
```

### Optional: Add .gitkeep Files
```bash
touch data/inputs/.gitkeep
touch data/outputs/.gitkeep
touch logs/.gitkeep
```

This preserves empty directories in Git.

### DO NOT Commit
- `venv/` - Virtual environment (too large, platform-specific)
- `data/inputs/*.csv` - Sensitive ServiceNow data
- `data/outputs/*.xlsx` - Generated reports (can be regenerated)
- `*.pyc`, `__pycache__/` - Python compiled files

The `.gitignore` file handles this automatically.

## Quick Setup Commands

### Create All Directories
```bash
# Windows
mkdir src config data\inputs data\outputs logs

# macOS/Linux
mkdir -p src config data/inputs data/outputs logs
```

### Verify Structure
```bash
# List all files and directories
# Windows
tree /F

# macOS/Linux
tree
# or
find . -type f -name "*.py" -o -name "*.yaml" -o -name "*.md" -o -name "*.txt"
```

## Cursor IDE Tips

### Open Project
1. File → Open Folder
2. Select `kpi-pipeline` folder
3. Trust workspace if prompted

### Set Python Interpreter
1. Ctrl+Shift+P (Cmd+Shift+P on Mac)
2. Type "Python: Select Interpreter"
3. Choose `./venv/bin/python` or `./venv/Scripts/python.exe`

### Open Terminal
- View → Terminal (or Ctrl+` / Cmd+`)
- Should open in project root
- Activate venv before running commands

---

**Use this as a reference** when organizing files in Cursor.
Check off each file as you copy it to ensure nothing is missed.
