# 🌿 Git Workflow Documentation

Best practices for version control and collaboration on the KPI Pipeline project.

## Overview

This document outlines the Git workflow for the KPI Pipeline project, including branching strategy, commit conventions, and release process.

---

## Branching Strategy

### Branch Types

```
main (protected)
├── develop
│   ├── feature/add-kpi-sm005
│   ├── feature/excel-export
│   └── bugfix/config-validation
└── hotfix/critical-calculation-fix
```

### Main Branches

#### `main`
- **Purpose**: Production-ready code
- **Protection**: Protected, requires pull request
- **Updates**: Only from `develop` or `hotfix` branches
- **Tags**: All releases tagged here

#### `develop`
- **Purpose**: Integration branch for features
- **Protection**: Optional protection
- **Updates**: From feature branches
- **Merges to**: `main` for releases

### Supporting Branches

#### Feature Branches
- **Naming**: `feature/<description>`
- **Created from**: `develop`
- **Merged into**: `develop`
- **Purpose**: New features or enhancements

**Examples**:
- `feature/add-kpi-sm005`
- `feature/excel-dashboard`
- `feature/email-reports`

#### Bugfix Branches
- **Naming**: `bugfix/<description>`
- **Created from**: `develop`
- **Merged into**: `develop`
- **Purpose**: Non-critical bug fixes

**Examples**:
- `bugfix/date-parsing`
- `bugfix/config-validation`
- `bugfix/calculation-error`

#### Hotfix Branches
- **Naming**: `hotfix/<description>`
- **Created from**: `main`
- **Merged into**: `main` AND `develop`
- **Purpose**: Critical production fixes

**Examples**:
- `hotfix/critical-calculation`
- `hotfix/data-loading-crash`

---

## Commit Message Conventions

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Formatting (no code change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

**Good commits**:

```bash
feat(kpi): Add SM005 calculation for response time

Implemented new KPI to track average response time for P1 incidents.
Includes configuration options and test cases.

Closes #15
```

```bash
fix(config): Correct weight calculation when SM003 disabled

Weight distribution was incorrect when SM003 was disabled.
Updated to properly redistribute weights to other KPIs.

Fixes #23
```

```bash
docs(readme): Update installation instructions

Added troubleshooting section for Windows users.
Clarified Python version requirements.
```

**Bad commits** (avoid):

```bash
# Too vague
fixed stuff

# No context
update

# Multiple unrelated changes
Added SM005, fixed bug, updated docs, refactored transform.py
```

### Commit Best Practices

1. **One logical change per commit**
   ```bash
   # Good: Separate commits
   git commit -m "feat(kpi): Add SM005 calculation"
   git commit -m "test(kpi): Add tests for SM005"
   git commit -m "docs(technical): Document SM005 logic"
   
   # Bad: Everything together
   git commit -m "Add SM005 with tests and docs"
   ```

2. **Write clear, descriptive messages**
   - First line: Summary (50 chars or less)
   - Blank line
   - Detailed explanation if needed

3. **Reference issues**
   ```bash
   Closes #15
   Fixes #23
   Relates to #45
   ```

---

## Workflow Examples

### Working on a New Feature

**1. Start from updated develop**:
```bash
git checkout develop
git pull origin develop
```

**2. Create feature branch**:
```bash
git checkout -b feature/excel-export
```

**3. Make changes and commit**:
```bash
# Make changes to files
git add src/excel_exporter.py
git commit -m "feat(export): Add Excel export functionality

Implemented Excel export with formatting and charts.
Supports multiple sheets for different KPIs."

# Continue working
git add tests/test_excel_export.py
git commit -m "test(export): Add tests for Excel export"
```

**4. Keep branch updated**:
```bash
# Regularly sync with develop
git checkout develop
git pull origin develop
git checkout feature/excel-export
git merge develop
```

**5. Push to remote**:
```bash
git push origin feature/excel-export
```

**6. Create pull request**:
- Go to GitHub
- Click "Compare & pull request"
- Fill in description
- Request reviewers
- Link related issues

**7. After approval, merge**:
```bash
# Squash and merge via GitHub UI
# Or locally:
git checkout develop
git merge --no-ff feature/excel-export
git push origin develop
```

**8. Delete feature branch**:
```bash
git branch -d feature/excel-export
git push origin --delete feature/excel-export
```

### Fixing a Bug

**1. Create bugfix branch**:
```bash
git checkout develop
git pull origin develop
git checkout -b bugfix/date-parsing
```

**2. Fix and test**:
```bash
# Make fix
git add src/load_data.py
git commit -m "fix(data): Handle timezone-aware dates correctly

Date parsing was failing for timestamps with timezone info.
Added timezone conversion to handle both aware and naive datetimes.

Fixes #34"

# Run tests
python tests/test_pipeline.py
```

**3. Push and create PR**:
```bash
git push origin bugfix/date-parsing
# Create PR on GitHub
```

### Hotfix for Production

**1. Create hotfix from main**:
```bash
git checkout main
git pull origin main
git checkout -b hotfix/critical-calculation
```

**2. Make fix**:
```bash
git add src/calculate_kpis.py
git commit -m "fix(kpi): Correct SM002 adherence calculation

Critical bug: backlog percentage was calculated incorrectly
for incidents without resolution date.

Fixes #56"
```

**3. Test thoroughly**:
```bash
python tests/test_pipeline.py
python main.py
```

**4. Merge to main**:
```bash
git checkout main
git merge --no-ff hotfix/critical-calculation
git tag -a v1.0.1 -m "Hotfix: SM002 calculation correction"
git push origin main --tags
```

**5. Also merge to develop**:
```bash
git checkout develop
git merge --no-ff hotfix/critical-calculation
git push origin develop
```

**6. Delete hotfix branch**:
```bash
git branch -d hotfix/critical-calculation
git push origin --delete hotfix/critical-calculation
```

---

## Release Process

### Version Numbering

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features, backwards compatible (e.g., 1.0.0 → 1.1.0)
- **PATCH**: Bug fixes, backwards compatible (e.g., 1.0.0 → 1.0.1)

### Creating a Release

**1. Prepare release branch**:
```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.1.0
```

**2. Update version**:
```python
# src/__init__.py
__version__ = "1.1.0"
```

**3. Update CHANGELOG**:
```markdown
## [1.1.0] - 2025-10-17

### Added
- Excel dashboard export with charts
- Email report distribution

### Fixed
- Date parsing for timezone-aware timestamps

### Changed
- Improved performance for large datasets
```

**4. Commit version bump**:
```bash
git add src/__init__.py CHANGELOG.md
git commit -m "chore(release): Bump version to 1.1.0"
```

**5. Final testing**:
```bash
python validate_project.py
python tests/test_pipeline.py
python main.py
```

**6. Merge to main**:
```bash
git checkout main
git merge --no-ff release/v1.1.0
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin main --tags
```

**7. Merge back to develop**:
```bash
git checkout develop
git merge --no-ff release/v1.1.0
git push origin develop
```

**8. Delete release branch**:
```bash
git branch -d release/v1.1.0
```

**9. Create GitHub release**:
- Go to repository → Releases
- Click "Draft a new release"
- Select tag v1.1.0
- Add release notes from CHANGELOG
- Publish release

---

## Pull Request Guidelines

### Creating a Pull Request

**1. Good PR title**:
```
feat(kpi): Add SM005 response time calculation
fix(config): Correct weight distribution
docs(readme): Update installation instructions
```

**2. PR description template**:
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Added SM005 calculation function
- Updated configuration schema
- Added test cases

## Testing
- [ ] Tests pass locally
- [ ] Validation script passes
- [ ] Tested with real data

## Related Issues
Closes #15
Relates to #20

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows PEP 8 style
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] CHANGELOG updated (if applicable)
```

### Reviewing a Pull Request

**Reviewer checklist**:
- ✅ Code quality and style
- ✅ Tests included and passing
- ✅ Documentation updated
- ✅ No merge conflicts
- ✅ Follows project conventions
- ✅ Appropriate commit messages

**Review comments**:
```markdown
# Good feedback
"Consider using a list comprehension here for better performance"
"This function would benefit from a docstring"
"Great solution! Just one minor suggestion..."

# Not helpful
"This is wrong"
"Change this"
```

---

## Collaboration Best Practices

### Before You Start

1. **Pull latest changes**:
   ```bash
   git checkout develop
   git pull origin develop
   ```

2. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature
   ```

3. **Keep commits atomic**: One logical change per commit

### While Working

1. **Commit frequently**: Small, logical commits
2. **Write good messages**: Clear and descriptive
3. **Test before committing**: Ensure code works
4. **Sync regularly**: Pull changes from develop often

### Before Pushing

1. **Review your changes**:
   ```bash
   git diff
   git status
   ```

2. **Run validation**:
   ```bash
   python validate_project.py
   python tests/test_pipeline.py
   ```

3. **Check commit history**:
   ```bash
   git log --oneline
   ```

4. **Clean up if needed**:
   ```bash
   # Squash multiple commits
   git rebase -i HEAD~3
   ```

---

## Useful Git Commands

### Status and History

```bash
# Check status
git status

# View commit history
git log --oneline --graph --all

# View changes
git diff
git diff --staged

# View file history
git log -p filename
```

### Branch Management

```bash
# List branches
git branch -a

# Create and switch
git checkout -b new-branch

# Switch branches
git checkout branch-name

# Delete branch
git branch -d branch-name

# Delete remote branch
git push origin --delete branch-name
```

### Syncing

```bash
# Pull latest
git pull origin main

# Fetch without merging
git fetch origin

# Push changes
git push origin branch-name

# Push tags
git push origin --tags
```

### Undoing Changes

```bash
# Discard unstaged changes
git checkout -- filename

# Unstage file
git reset HEAD filename

# Amend last commit
git commit --amend

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - DANGEROUS
git reset --hard HEAD~1
```

### Stashing

```bash
# Stash changes
git stash save "Work in progress"

# List stashes
git stash list

# Apply stash
git stash apply stash@{0}

# Pop stash (apply and remove)
git stash pop
```

---

## Handling Conflicts

### Merge Conflicts

**1. When conflict occurs**:
```bash
git merge feature-branch
# CONFLICT (content): Merge conflict in src/calculate_kpis.py
```

**2. Find conflicted files**:
```bash
git status
# Both modified: src/calculate_kpis.py
```

**3. Resolve conflicts**:
```python
# Open file, look for markers
<<<<<<< HEAD
current_code = "version in current branch"
=======
incoming_code = "version in feature branch"
>>>>>>> feature-branch

# Edit to keep desired changes
final_code = "resolved version"
```

**4. Mark as resolved**:
```bash
git add src/calculate_kpis.py
git commit -m "merge: Resolve conflicts in calculate_kpis"
```

---

## Security Best Practices

### Never Commit

- ❌ Passwords or API keys
- ❌ Real customer data
- ❌ Private configuration files
- ❌ Large binary files
- ❌ Virtual environments

### Use .gitignore

Already configured in `.gitignore`:
```
.venv/
data/input/*.csv
.env
*.log
```

### If Accidentally Committed

```bash
# Remove from history (use carefully)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# Or use BFG Repo-Cleaner (easier)
bfg --delete-files sensitive_file.txt
```

---

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [GitHub Guides](https://guides.github.com/)
- [Pro Git Book](https://git-scm.com/book/en/v2)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

---

## Questions?

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) or contact the project maintainer.

**Happy collaborating!** 🚀



