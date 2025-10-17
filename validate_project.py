"""
Project Validation Script
Validates project setup before deployment or execution.
"""

import sys
import os
from pathlib import Path
import subprocess

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def check_python_version():
    """Check if Python version meets requirements."""
    print("\n[1/6] Checking Python version...")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✓ Python {version_str} (requirement: 3.9+)")
        return True
    else:
        print(f"  ✗ Python {version_str} (requirement: 3.9+)")
        print(f"    Please upgrade to Python 3.9 or higher")
        return False


def check_file_existence():
    """Check if all required files exist."""
    print("\n[2/6] Checking required files...")
    
    required_files = [
        'main.py',
        'requirements.txt',
        'config/kpi_config.yaml',
        'src/__init__.py',
        'src/config_loader.py',
        'src/load_data.py',
        'src/transform.py',
        'src/calculate_kpis.py',
        '.gitignore',
        'setup.sh',
        'setup.bat',
    ]
    
    optional_files = [
        'README.md',
        'LICENSE',
        'CONTRIBUTING.md',
        'CHANGELOG.md',
    ]
    
    all_ok = True
    
    # Check required files
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (REQUIRED)")
            all_ok = False
    
    # Check optional files
    print("\n  Optional files:")
    for file_path in optional_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ℹ {file_path} (recommended)")
    
    return all_ok


def check_yaml_validity():
    """Check if YAML configuration files are valid."""
    print("\n[3/6] Checking YAML configuration...")
    
    try:
        import yaml
        
        yaml_files = [
            'config/kpi_config.yaml',
            'config/complete_kpi_config.yaml',
        ]
        
        all_ok = True
        for yaml_file in yaml_files:
            if os.path.exists(yaml_file):
                try:
                    with open(yaml_file, 'r') as f:
                        config = yaml.safe_load(f)
                    print(f"  ✓ {yaml_file} - Valid")
                    
                    # Check for key sections
                    if 'kpis' in config:
                        kpi_count = len([k for k in config['kpis'] if config['kpis'][k].get('enabled', True)])
                        print(f"    └─ {kpi_count} KPIs enabled")
                    
                except yaml.YAMLError as e:
                    print(f"  ✗ {yaml_file} - Invalid YAML: {e}")
                    all_ok = False
            else:
                print(f"  ℹ {yaml_file} - Not found (optional)")
        
        return all_ok
        
    except ImportError:
        print("  ✗ PyYAML not installed - cannot validate YAML files")
        print("    Run: pip install -r requirements.txt")
        return False


def check_imports():
    """Check if all modules can be imported."""
    print("\n[4/6] Checking module imports...")
    
    modules_to_check = [
        ('pandas', 'pandas'),
        ('yaml', 'pyyaml'),
        ('openpyxl', 'openpyxl'),
        ('dateutil', 'python-dateutil'),
    ]
    
    all_ok = True
    for module_name, package_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"  ✓ {module_name}")
        except ImportError:
            print(f"  ✗ {module_name} (package: {package_name})")
            all_ok = False
    
    if not all_ok:
        print("\n  Install missing packages:")
        print("    pip install -r requirements.txt")
    
    # Check project modules
    print("\n  Project modules:")
    sys.path.insert(0, str(Path(__file__).parent))
    
    project_modules = [
        'src.config_loader',
        'src.load_data',
        'src.transform',
        'src.calculate_kpis',
    ]
    
    for module in project_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            print(f"  ✗ {module}: {e}")
            all_ok = False
    
    return all_ok


def check_data_files():
    """Check if data files exist."""
    print("\n[5/6] Checking data files...")
    
    data_dir = Path('data/input')
    
    if not data_dir.exists():
        print(f"  ℹ {data_dir} directory not found")
        return True  # Not a critical error
    
    csv_files = list(data_dir.glob('*.csv'))
    
    if len(csv_files) == 0:
        print(f"  ℹ No CSV files found in {data_dir}")
        print(f"    Place your data files in data/input/ before running the pipeline")
    else:
        print(f"  ✓ Found {len(csv_files)} CSV file(s):")
        for csv_file in csv_files:
            file_size = csv_file.stat().st_size / 1024  # KB
            print(f"    - {csv_file.name} ({file_size:.1f} KB)")
    
    return True


def check_git_status():
    """Check git repository status."""
    print("\n[6/6] Checking git repository...")
    
    try:
        # Check if git is initialized
        result = subprocess.run(
            ['git', 'status'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("  ✓ Git repository initialized")
            
            # Check for uncommitted changes
            if 'nothing to commit' in result.stdout:
                print("  ✓ No uncommitted changes")
            else:
                print("  ℹ There are uncommitted changes")
                
            # Check current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if branch_result.returncode == 0:
                branch = branch_result.stdout.strip()
                if branch:
                    print(f"  ✓ Current branch: {branch}")
            
            # Check remote
            remote_result = subprocess.run(
                ['git', 'remote', '-v'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if remote_result.returncode == 0 and remote_result.stdout:
                print(f"  ✓ Remote configured")
            else:
                print(f"  ℹ No remote repository configured")
            
            return True
        else:
            print("  ℹ Git repository not initialized")
            print("    Run: git init")
            return True  # Not a critical error
            
    except FileNotFoundError:
        print("  ℹ Git not found - install git to enable version control")
        return True  # Not a critical error
    except Exception as e:
        print(f"  ℹ Could not check git status: {e}")
        return True  # Not a critical error


def main():
    """Run all validation checks."""
    print("="*70)
    print("PROJECT VALIDATION")
    print("="*70)
    
    results = {}
    
    # Run all checks
    results['python_version'] = check_python_version()
    results['file_existence'] = check_file_existence()
    results['yaml_validity'] = check_yaml_validity()
    results['imports'] = check_imports()
    results['data_files'] = check_data_files()
    results['git_status'] = check_git_status()
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check_name, passed_check in results.items():
        status = "✓ PASSED" if passed_check else "✗ FAILED"
        print(f"{check_name.replace('_', ' ').title()}: {status}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✓ ALL VALIDATION CHECKS PASSED!")
        print("\nYou can now run the pipeline:")
        print("  python main.py")
    else:
        print(f"\n✗ {total - passed} CHECK(S) FAILED")
        print("\nPlease fix the issues above before running the pipeline.")
    
    print("="*70)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())



