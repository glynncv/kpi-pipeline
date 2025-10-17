# .gitkeep Files

This file explains the .gitkeep placeholders.

Git doesn't track empty directories. We use .gitkeep files to preserve
the directory structure in version control.

## Create these files:

```bash
# Windows PowerShell
New-Item -ItemType File -Path "data\inputs\.gitkeep"
New-Item -ItemType File -Path "data\outputs\.gitkeep"
New-Item -ItemType File -Path "logs\.gitkeep"

# Windows Command Prompt
echo. > data\inputs\.gitkeep
echo. > data\outputs\.gitkeep
echo. > logs\.gitkeep

# macOS/Linux
touch data/inputs/.gitkeep
touch data/outputs/.gitkeep
touch logs/.gitkeep
```

These files ensure the directory structure is preserved when cloning
the repository, even if the directories are empty.
