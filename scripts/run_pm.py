"""Run Problem Management KPI Pipeline"""
import sys
from pathlib import Path

# Add parent directory to path so we can import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import (
    config_loader,
    load_problem_data,
    transform_problems,
    calculate_pm_kpis,
    generate_pm_reports
)

def main():
    """Main execution function."""
    print("=" * 60)
    print("Problem Management KPI Pipeline")
    print("=" * 60)
    
    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = config_loader.load_config()
        
        # Load data
        print("\n2. Loading problem data...")
        problems, tasks = load_problem_data.load_all_problem_data('data/input', config)
        
        if problems is None or tasks is None:
            print("\n[ERROR] Problem Management data files not found!")
            print("Please ensure files are in data/input/ directory:")
            print("  - PYTHON EMEA PM P1P2 (This Year).csv")
            print("  - PYTHON EMEA TASK RCA (This Year).csv")
            return 1
        
        # Transform data
        print("\n3. Transforming data...")
        transformed = transform_problems.transform_all_problem_data(problems, tasks)
        print(f"   [OK] Transformed {len(transformed)} problems")
        
        # Calculate KPIs
        print("\n4. Calculating KPIs...")
        kpis = calculate_pm_kpis.calculate_all_pm_kpis(transformed, config)
        rca = kpis['RCA001']
        
        print(f"\n   RCA001 Results:")
        print(f"   - Completion Rate: {rca['completion_rate']:.1f}%")
        print(f"   - Target: {rca['target']:.1f}%")
        print(f"   - Status: {rca['status']}")
        print(f"   - Completed: {rca['completed_ontime']}/{rca['total_requiring_rca']}")
        
        # Generate Excel dashboard
        print("\n5. Generating Excel dashboard...")
        filepath = generate_pm_reports.export_pm_dashboard(kpis, transformed)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Problem Management KPI pipeline complete!")
        print(f"Dashboard saved to: {filepath}")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

