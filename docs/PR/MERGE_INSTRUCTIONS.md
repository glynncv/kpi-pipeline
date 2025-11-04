# How to Merge the Problem Management PR

## Option 1: Merge via GitHub (Recommended)

1. **Go to GitHub**: Visit https://github.com/glynncv/kpi-pipeline/pulls
2. **Open the PR**: Find "feat: Problem Management KPI Tracking (RCA001) - Session 1 Complete"
3. **Review**: Make sure all checks pass and code looks good
4. **Merge**: Click "Merge pull request" button
5. **Confirm**: Click "Confirm merge"
6. **Update local main**:
   ```bash
   git checkout main
   git pull origin main
   ```

## Option 2: Merge Locally (Command Line)

If you want to merge locally without using GitHub:

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge the feature branch
git merge feature/problem-management-rca001

# Push to remote
git push origin main
```

## Option 3: Merge Locally Now (Quick)

Run these commands:

```powershell
git checkout main
git pull origin main
git merge feature/problem-management-rca001
git push origin main
```

## After Merging

Once merged, you'll need to integrate the actual code:
1. Copy `docs/PR/config_loader.py` changes into `src/config_loader.py`
2. Merge `docs/PR/kpi_config.yaml` into `config/kpi_config.yaml`
3. Copy `docs/PR/load_problem_data.py` to `src/load_problem_data.py`

Or the code might already be ready to use if the reference implementations are complete.

