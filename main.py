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
import os
from datetime import datetime

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src import config_loader
from src import load_data
from src import transform
from src import calculate_kpis
from src.okr_calculator import OKRCalculator
from src.export_excel import export_to_excel


def main():
    """Execute the KPI pipeline."""
    print("="*70)
    print("KPI PIPELINE - EXECUTION")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Step 1: Load Configuration
        print("[1/7] Loading configuration...")
        config = config_loader.load_config()
        print(f"✓ Configuration loaded: {config['metadata']['organization']}")
        
        # Step 2: Load Data
        print("\n[2/7] Loading data files...")
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
        print("\n[3/7] Transforming data (adding calculated fields)...")
        incidents = transform.add_incident_flags(incidents, config)
        print(f"✓ Added incident flags")
        
        if requests is not None:
            requests = transform.add_request_flags(requests, config)
            print(f"✓ Added request flags")
        
        # Step 4: Calculate KPIs
        print("\n[4/7] Calculating KPIs...")
        kpi_results = calculate_kpis.calculate_all(incidents, requests, config)
        print(f"✓ Calculated {len(kpi_results)-1} KPIs + overall score")
        
        # Step 5: Calculate OKR
        print("\n[5/7] Calculating OKR R002...")
        try:
            okr_calc = OKRCalculator('config/okr_config.yaml', kpi_results)
            okr_result = okr_calc.calculate_overall_okr()
            okr_triggers = okr_calc.get_action_triggers()
            print(f"✓ OKR R002 Score: {okr_result['overall_score']}/100 - {okr_result['overall_status']}")
        except FileNotFoundError:
            print("⚠ OKR config not found - skipping OKR calculation")
            okr_result = None
            okr_triggers = None
        except Exception as e:
            print(f"⚠ OKR calculation error: {e}")
            okr_result = None
            okr_triggers = None
        
        # Step 6: Export to Excel
        print("\n[6/7] Exporting to Excel...")
        try:
            excel_file = export_to_excel(kpi_results, okr_result, 
                                        filename=f"kpi_okr_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
            print(f"✓ Excel report saved: {excel_file}")
        except Exception as e:
            print(f"⚠ Excel export error: {e}")
        
        # Step 7: Display Results
        print("\n[7/7] Results:")
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
        
        # Display OKR Results
        if okr_result:
            print("\n" + "="*70)
            print("OKR R002: SERVICE DELIVERY EXCELLENCE")
            print("="*70)
            print(f"\nOverall OKR Score: {okr_result['overall_score']}/100")
            print(f"Status: {okr_result['overall_status']}")
            print(f"Weights: KR4={okr_result['weights']['KR4']}%, KR5={okr_result['weights']['KR5']}%, KR6={okr_result['weights']['KR6']}%")
            
            print("\nKey Results:")
            for kr_id, kr_data in okr_result['key_results'].items():
                print(f"\n{kr_id}: {kr_data['name']}")
                print(f"  Score: {kr_data['score']}/100 - {kr_data['status']}")
                print(f"  Current: {kr_data['current_value']}{kr_data['target_operator']}{kr_data['target_value']} (target)")
                print(f"  Gap: {kr_data['gap_to_target']}")
                print(f"  Deadline: {kr_data['deadline']} ({kr_data['days_remaining']} days)")
            
            # Display Action Triggers
            if okr_triggers and (okr_triggers['critical'] or okr_triggers['warning']):
                print("\n" + "="*70)
                print("ACTION ITEMS")
                print("="*70)
                
                if okr_triggers['critical']:
                    print("\n🔴 CRITICAL ACTIONS:")
                    for trigger in okr_triggers['critical']:
                        print(f"  {trigger['kr_id']}: {trigger['action']}")
                        print(f"    → Escalate to: {trigger['escalation']}")
                
                if okr_triggers['warning']:
                    print("\n🟡 WARNING ACTIONS:")
                    for trigger in okr_triggers['warning']:
                        print(f"  {trigger['kr_id']}: {trigger['action']}")
                        print(f"    → Escalate to: {trigger['escalation']}")
        
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
