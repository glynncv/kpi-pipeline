#!/usr/bin/env python3
"""
Validation Test Runner - Simple wrapper to run validation tests.

Usage:
    python run_validation.py
"""

import sys
import subprocess
import io
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    """Run the validation test suite."""
    print("="*70)
    print("KPI PIPELINE VALIDATION TEST RUNNER")
    print("="*70)
    print()
    
    try:
        # Run the validation tests (standalone version)
        result = subprocess.run([
            sys.executable, 'src/run_validation_tests_standalone.py'
        ], check=True)
        
        print("\n" + "="*70)
        print("VALIDATION TESTS COMPLETED SUCCESSFULLY")
        print("="*70)
        
        return 0
        
    except subprocess.CalledProcessError as e:
        print(f"\nVALIDATION TESTS FAILED (exit code: {e.returncode})")
        return e.returncode
        
    except Exception as e:
        print(f"\nERROR RUNNING VALIDATION TESTS: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
