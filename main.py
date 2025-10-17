"""
KPI Pipeline - Main Execution Script

This script runs the complete KPI pipeline:
1. Loads configuration
2. Loads incident and request data
3. Transforms data (adds calculated fields)
4. Calculates KPIs
5. Displays results

Usage:
    python main.py
"""

import sys
from datetime import datetime

from src import config_loader
from src import load_data
from src import transform
from src import calculate_kpis


def main():
    """Execute the KPI pipeline."""
    print("="*70)
    print("KPI PIPELINE - EXECUTION")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Step 1: Load Configuration
        print("[1/5] Loading configuration...")
        config = config_loader.load_config()
        print(f"✓ Configuration loaded: {config['metadata']['organization']}")
        
        # Step 2: Load Data
        print("\n[2/5] Loading data files...")
        incidents = load_data.load_incidents(
            'data/input/PYTHON EMEA IM (last 90 days)_redacted_clean.csv',
            config
        )
        print(f"✓ Loaded {len(incidents)} incidents")
        
        requests = None
        if config['kpis']['SM003']['enabled']:
            requests = load_data.load_requests(
                'data/input/PYTHON EMEA SCT (last 90 days)_redacted_clean.csv',
                config
            )
            print(f"✓ Loaded {len(requests)} requests")
        else:
            print("ℹ Request aging (SM003) disabled - skipping request data")
        
        # Step 3: Transform Data
        print("\n[3/5] Transforming data (adding calculated fields)...")
        incidents = transform.add_incident_flags(incidents, config)
        print(f"✓ Added incident flags")
        
        if requests is not None:
            requests = transform.add_request_flags(requests, config)
            print(f"✓ Added request flags")
        
        # Step 4: Calculate KPIs
        print("\n[4/5] Calculating KPIs...")
        kpi_results = calculate_kpis.calculate_all(incidents, requests, config)
        print(f"✓ Calculated {len(kpi_results)-1} KPIs + overall score")
        
        # Step 5: Display Results
        print("\n[5/5] Results:")
        print("\n" + "="*70)
        print("KPI RESULTS")
        print("="*70)
        
        for kpi_code, kpi_data in kpi_results.items():
            if kpi_code == 'OVERALL':
                print(f"\n{'='*70}")
                print(f"OVERALL PERFORMANCE")
                print(f"{'='*70}")
                print(f"Score: {kpi_data['Overall_Score']}%")
                print(f"Status: {kpi_data['Overall_Status']}")
                print(f"Weights: {kpi_data['Weights_Used']}")
            else:
                print(f"\n{kpi_code}: {kpi_data['KPI_Name']}")
                print(f"  Status: {kpi_data['Status']}")
                print(f"  Adherence: {kpi_data['Adherence_Rate']}%")
                print(f"  Business Impact: {kpi_data['Business_Impact']}")
                
                # Print KPI-specific details
                if 'P1_Count' in kpi_data:
                    print(f"  P1: {kpi_data['P1_Count']} (target: ≤{kpi_data['P1_Target']})")
                    print(f"  P2: {kpi_data['P2_Count']} (target: ≤{kpi_data['P2_Target']})")
                    print(f"  Total Major: {kpi_data['Total_Major']}")
                elif 'Backlog_Count' in kpi_data:
                    print(f"  Total: {kpi_data['Total_Incidents']}")
                    print(f"  Backlog: {kpi_data['Backlog_Count']} ({kpi_data['Backlog_Percentage']}%)")
                    print(f"  Target: ≥{kpi_data['Target_Adherence']}% adherence")
                elif 'Aged_Count' in kpi_data:
                    print(f"  Total: {kpi_data['Total_Requests']}")
                    print(f"  Aged: {kpi_data['Aged_Count']} ({kpi_data['Aged_Percentage']}%)")
                    print(f"  Target: ≥{kpi_data['Target_Adherence']}% adherence")
                elif 'FCR_Count' in kpi_data:
                    print(f"  Total Resolved: {kpi_data['Total_Resolved']}")
                    print(f"  FCR: {kpi_data['FCR_Count']} ({kpi_data['FCR_Percentage']}%)")
                    print(f"  Target: ≥{kpi_data['Target_Rate']}%")
        
        print("\n" + "="*70)
        print(f"✓ Pipeline completed successfully")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPlease ensure CSV files are in the data/input/ directory:")
        print("  - data/input/PYTHON EMEA IM (last 90 days)_redacted_clean.csv")
        print("  - data/input/PYTHON EMEA SCT (last 90 days)_redacted_clean.csv")
        return 1
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
