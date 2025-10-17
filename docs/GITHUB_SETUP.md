# 🐙 GitHub Setup Guide

Step-by-step guide to deploy your KPI Pipeline to GitHub.

## Prerequisites

Before starting, ensure you have:

- ✅ Git installed ([download here](https://git-scm.com/downloads))
- ✅ GitHub account ([sign up here](https://github.com/signup))
- ✅ Project validation passed (`python validate_project.py`)
- ✅ All files ready (run deployment checklist)

---

## Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Recommended)

**1. Go to GitHub and log in**

**2. Create new repository**:
- Click the `+` icon (top right) → "New repository"

**3. Configure repository**:
```
Repository name: kpi-pipeline
Description: Automated KPI calculation pipeline for IT Service Management
Visibility: □ Public (or ☑ Private for internal use)

DO NOT initialize with:
□ README (we already have one)
□ .gitignore (we already have one)
□ License (we'll add it separately)
```

**4. Click "Create repository"**

**5. Note the repository URL**:
```
https://github.com/[YOUR-USERNAME]/kpi-pipeline.git
```

### Option B: Via GitHub CLI

```bash
# Install GitHub CLI: https://cli.github.com/

# Login
gh auth login

# Create repository
gh repo create kpi-pipeline --private --description "Automated KPI calculation pipeline"
```

---

## Step 2: Connect Local Repository

### Initialize and Connect

**1. Open terminal in project directory**:
```bash
cd path/to/kpi_pipeline
```

**2. Initialize git repository** (if not already done):
```bash
git init
```

**3. Add all files to staging**:
```bash
git add .
```

**4. Create first commit**:
```bash
git commit -m "Initial commit: KPI Pipeline v1.0.0"
```

**5. Rename branch to main** (if needed):
```bash
git branch -M main
```

**6. Add remote repository**:
```bash
git remote add origin https://github.com/[YOUR-USERNAME]/kpi-pipeline.git
```

**Replace `[YOUR-USERNAME]` with your actual GitHub username!**

**7. Verify remote**:
```bash
git remote -v
```

Expected output:
```
origin  https://github.com/[YOUR-USERNAME]/kpi-pipeline.git (fetch)
origin  https://github.com/[YOUR-USERNAME]/kpi-pipeline.git (push)
```

**8. Push to GitHub**:
```bash
git push -u origin main
```

**If prompted**, enter your GitHub credentials or personal access token.

### Troubleshooting Authentication

**Issue**: "Support for password authentication was removed"

**Solution**: Use Personal Access Token (PAT)

1. **Generate PAT**:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token"
   - **Copy the token** (you won't see it again!)

2. **Use PAT as password**:
   ```bash
   git push -u origin main
   Username: [YOUR-USERNAME]
   Password: [PASTE-YOUR-PAT-HERE]
   ```

3. **Store credentials** (optional):
   ```bash
   git config --global credential.helper store
   ```

---

## Step 3: Configure Repository Settings

### Basic Settings

**1. Go to repository on GitHub**:
```
https://github.com/[YOUR-USERNAME]/kpi-pipeline
```

**2. Click "Settings" tab**

**3. General settings**:
- ✅ Repository name: `kpi-pipeline`
- ✅ Description: "Automated KPI calculation pipeline for IT Service Management"
- ✅ Website: (optional) your documentation site
- ✅ Topics: Add tags for discoverability

**Suggested topics**:
```
kpi, python, data-analysis, itil, service-management, automation, pandas, yaml
```

### Add Topics

Click "⚙️" next to "About" → Add topics:
- `kpi`
- `python`
- `data-analysis`
- `itsm`
- `automation`
- `pandas`

### Branch Protection (Recommended for Team Projects)

**1. Go to**: Settings → Branches

**2. Click "Add rule"**

**3. Branch name pattern**: `main`

**4. Enable**:
- ☑ Require pull request reviews before merging
- ☑ Require status checks to pass before merging
- ☑ Include administrators (optional)

**5. Click "Create"**

### Configure GitHub Pages (Optional Documentation Site)

**1. Go to**: Settings → Pages

**2. Source**: Deploy from a branch

**3. Branch**: `main` / `docs`

**4. Click "Save"

**5. Access docs at**:
```
https://[YOUR-USERNAME].github.io/kpi-pipeline/
```

---

## Step 4: Create First Release

### Tag and Release v1.0.0

**1. Create version tag**:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0

Features:
- SM001: Major Incident Management
- SM002: Backlog Management  
- SM003: Request Aging
- SM004: First Contact Resolution
- YAML configuration system
- Comprehensive testing suite
- Full documentation"

git push origin v1.0.0
```

**2. Create release on GitHub**:
- Go to repository → Releases
- Click "Create a new release"
- Choose tag: `v1.0.0`
- Release title: `v1.0.0 - Initial Release`
- Description:

```markdown
# 🎉 Initial Release - KPI Pipeline v1.0.0

## Features

### KPI Calculations
- ✅ **SM001**: Major Incident Management (P1/P2 tracking)
- ✅ **SM002**: Backlog Management (aging analysis)
- ✅ **SM003**: Request Aging (service request tracking)
- ✅ **SM004**: First Contact Resolution (efficiency metrics)
- ✅ **Overall Score**: Weighted scorecard with performance banding

### System Features
- ✅ YAML-based configuration
- ✅ CSV data input
- ✅ Comprehensive test suite
- ✅ Project validation tools
- ✅ Setup automation scripts
- ✅ Full documentation suite

## Installation

```bash
git clone https://github.com/[YOUR-USERNAME]/kpi-pipeline.git
cd kpi-pipeline
./setup.sh  # Mac/Linux
.\setup.bat  # Windows
```

## Quick Start

See [Quick Start Guide](docs/QUICKSTART.md)

## Documentation

- [README](README.md) - Overview
- [Technical Documentation](docs/TECHNICAL.md)
- [Configuration Guide](docs/CONFIGURATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Requirements

- Python 3.9+
- pandas >= 2.0.0
- pyyaml >= 6.0
- openpyxl >= 3.1.0

## License

MIT License - see [LICENSE](LICENSE) file
```

**3. Click "Publish release"**

---

## Step 5: Verify Upload

### Verification Checklist

**Visit your repository and check**:

- ✅ README.md displays correctly on homepage
- ✅ All files and folders visible
- ✅ .gitignore is working (no `.pyc`, `__pycache__`, `.venv` files)
- ✅ Configuration files present in `config/`
- ✅ Documentation visible in `docs/`
- ✅ Tests visible in `tests/`
- ✅ Source code in `src/`
- ✅ License file present
- ✅ Release created (check Releases tab)
- ✅ Topics/tags added

### Test Clone

**Test from different location**:
```bash
cd ~/Desktop
git clone https://github.com/[YOUR-USERNAME]/kpi-pipeline.git test-clone
cd test-clone

# Run setup
./setup.sh  # or .\setup.bat on Windows

# Run validation
python validate_project.py

# Run tests
python tests/test_pipeline.py
```

**Expected**: All validation and tests pass

---

## Step 6: Share with Team

### Share Repository Access

**For Private Repositories**:

**1. Go to**: Settings → Collaborators

**2. Click "Add people"**

**3. Enter GitHub username or email**

**4. Choose permission level**:
- **Read**: View only
- **Write**: Can push changes
- **Admin**: Full control

**5. Click "Add [username] to this repository"**

### Provide Team Instructions

**Share this information with your team**:

```markdown
# KPI Pipeline - Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/[YOUR-USERNAME]/kpi-pipeline.git
cd kpi-pipeline
```

## 2. Run Setup

**Windows**:
```bash
.\setup.bat
```

**Mac/Linux**:
```bash
./setup.sh
```

## 3. Add Your Data

Place CSV files in `data/input/`:
- Incident data: `data/input/[your_incidents].csv`
- Request data: `data/input/[your_requests].csv`

## 4. Run Pipeline

```bash
python main.py
```

## 5. Documentation

See [Quick Start Guide](docs/QUICKSTART.md) for details

## Questions?

Contact: [your-email@example.com]
```

### Create Team Documentation

**Add to repository wiki** (optional):

1. Go to repository → Wiki
2. Click "Create the first page"
3. Add team-specific information:
   - Data export procedures
   - Report distribution process
   - Support contacts
   - Meeting schedules

---

## Post-Deployment Tasks

### Set Up Notifications

**1. Watch repository**:
- Click "Watch" button → Choose notification level
- Recommended: "All Activity" for maintainers

**2. Configure email notifications**:
- GitHub → Settings → Notifications
- Choose preferences for repositories you watch

### Create Project Board (Optional)

**For tracking enhancements**:

1. Go to repository → Projects
2. Click "Create a project"
3. Choose template: "Basic kanban"
4. Add columns: Backlog, In Progress, Done
5. Add future enhancement items

### Set Up GitHub Actions (Advanced)

**Automated testing on push**:

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      - name: Run tests
        run: python tests/test_pipeline.py
```

---

## Maintenance

### Regular Updates

**Weekly**:
- Push new data and results (if tracking)
- Commit configuration changes

```bash
git add .
git commit -m "Update: [describe change]"
git push
```

**Monthly**:
- Review open issues
- Update documentation
- Tag maintenance releases

```bash
git tag -a v1.0.1 -m "Maintenance release"
git push origin v1.0.1
```

### Backup Strategy

**GitHub IS your backup**, but also:
- Keep local clone updated
- Export releases periodically
- Document critical configuration changes

---

## Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution**: Set up SSH key or use HTTPS with PAT

**SSH Setup**:
```bash
# Generate key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add to GitHub
# GitHub → Settings → SSH and GPG keys → New SSH key
# Paste contents of ~/.ssh/id_ed25519.pub
```

### Issue: "Push rejected - non-fast-forward"

**Solution**: Pull latest changes first

```bash
git pull origin main
git push origin main
```

### Issue: "Large files rejected"

**Solution**: Use Git LFS for large files

```bash
git lfs install
git lfs track "*.csv"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

### Issue: "Repository not found"

**Solution**: Check repository URL and permissions

```bash
# Check current remote
git remote -v

# Update if wrong
git remote set-url origin https://github.com/[CORRECT-USERNAME]/kpi-pipeline.git
```

---

## Next Steps

✅ **You've successfully deployed to GitHub!**

**Now**:
1. ✅ Repository is live and accessible
2. ✅ Team can clone and use
3. ✅ Version controlled and backed up
4. ✅ Professional presentation

**Continue with**:
- Regular maintenance (see [`MAINTENANCE.md`](MAINTENANCE.md))
- Team training
- Continuous improvement
- Monitor usage and feedback

---

## Resources

- [GitHub Documentation](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Desktop](https://desktop.github.com/) - GUI alternative
- [`GIT_WORKFLOW.md`](GIT_WORKFLOW.md) - Development workflow

**Questions?** Contact the project maintainer or open an issue on GitHub!



