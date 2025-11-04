"""
KPI Pipeline - Main Execution Script

This script runs the complete KPI pipeline:
1. Loads configuration
2. Loads incident and request data
3. Transforms data (adds calculated fields)
4. Calculates KPIs
5. Calculates OKR scores
6. Displays results
7. Generates Excel report

Usage:
    python main.py                              # Use prod environment (default)
    python main.py --env dev                    # Use dev environment (small test data)
    python main.py --incidents path/to/file.csv # Override incidents file
    python main.py --requests path/to/file.csv  # Override requests file
"""

import sys
import os
import argparse
import io
from datetime import datetime
from pathlib import Path
import pandas as pd

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src import config_loader
from src import load_data
from src import transform
from src import calculate_kpis
from src import generate_reports
from src import geographic_analysis
from src.okr_calculator import OKRCalculator


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='KPI Pipeline - Calculate and report KPI metrics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Use production data (default)
  python main.py --env dev                          # Use dev test data (faster)
  python main.py --incidents custom_incidents.csv   # Override incidents file
  python main.py --requests custom_requests.csv     # Override requests file
  python main.py --input-dir data/archive           # Use different input directory
        """
    )
    
    parser.add_argument(
        '--env',
        choices=['dev', 'prod'],
        help='Environment to use (dev/prod). Overrides config default.'
    )
    
    parser.add_argument(
        '--incidents',
        help='Path to incidents CSV file (overrides environment setting)'
    )
    
    parser.add_argument(
        '--requests',
        help='Path to requests CSV file (overrides environment setting)'
    )
    
    parser.add_argument(
        '--input-dir',
        help='Input directory path (overrides environment setting)'
    )
    
    parser.add_argument(
        '--config',
        default='config/kpi_config.yaml',
        help='Path to KPI config file (default: config/kpi_config.yaml)'
    )
    
    return parser.parse_args()


def get_data_file_paths(config, args):
    """
    Get data file paths from config and apply CLI overrides.
    
    Args:
        config: Loaded configuration dictionary
        args: Parsed command-line arguments
    
    Returns:
        Tuple of (incidents_path, requests_path, environment_name)
    """
    # Get environment setting
    env = args.env if args.env else config['data_sources']['active_environment']
    
    # Get environment config
    env_config = config['data_sources']['environments'][env]
    
    # Build paths from config
    input_dir = env_config['input_directory']
    incidents_file = env_config['incidents_file']
    requests_file = env_config['requests_file']
    
    # Apply CLI overrides
    if args.input_dir:
        input_dir = args.input_dir
    
    if args.incidents:
        # If absolute path or contains directory separator, use as-is
        if Path(args.incidents).is_absolute() or os.sep in args.incidents:
            incidents_path = args.incidents
        else:
            incidents_path = os.path.join(input_dir, args.incidents)
    else:
        incidents_path = os.path.join(input_dir, incidents_file)
    
    if args.requests:
        if Path(args.requests).is_absolute() or os.sep in args.requests:
            requests_path = args.requests
        else:
            requests_path = os.path.join(input_dir, args.requests)
    else:
        requests_path = os.path.join(input_dir, requests_file)
    
    return incidents_path, requests_path, env


def main():
    """Execute the KPI pipeline."""
    # Parse command-line arguments
    args = parse_arguments()
    
    print("="*70)
    print("KPI PIPELINE - EXECUTION")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Step 1: Load Configuration
        print("[1/7] Loading configuration...")
        config = config_loader.load_all_configs(args.config, 'config/okr_config.yaml')
        print(f"✓ Configuration loaded: {config['metadata']['organization']}")
        
        # Get data file paths from config and CLI args
        incidents_path, requests_path, env = get_data_file_paths(config, args)
        
        # Display environment info
        env_desc = config['data_sources']['environments'][env]['description']
        print(f"✓ Environment: {env} ({env_desc})")
        
        # Step 2: Load Data
        print("\n[2/7] Loading data files...")
        print(f"  Incidents: {incidents_path}")
        incidents = load_data.load_incidents(incidents_path, config)
        print(f"✓ Loaded {len(incidents)} incidents")
        
        requests = None
        if config['kpis']['SM003']['enabled']:
            print(f"  Requests: {requests_path}")
            requests = load_data.load_requests(requests_path, config)
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
        
        # Step 5: Calculate OKR Scores
        print("\n[5/7] Calculating OKR scores...")
        
        okr_calc = OKRCalculator('config/okr_config.yaml', kpi_results)
        okr_results = okr_calc.calculate_overall_okr()
        action_triggers = okr_calc.get_action_triggers()
        
        print(f"✓ Calculated OKR R002 with {len(okr_results['key_results'])} Key Results")
        print(f"✓ Overall OKR Score: {okr_results['overall_score']}%")
        
        # Step 5.5: Calculate Geographic Analysis
        print("\n[5.5/7] Calculating geographic analysis...")
        geo_results = geographic_analysis.analyze_geography(
            incidents=incidents,
            requests=requests if requests is not None else pd.DataFrame(),
            config=config
        )
        print(f"✓ Analyzed {len(geo_results['location_summary'])} locations")
        print(f"✓ Found {geo_results['intervention_summary']['critical_count']} critical locations")
        
        # Step 6: Display Results
        print("\n[6/7] Results:")
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
        print("\n" + "="*70)
        print("OKR R002 RESULTS")
        print("="*70)
        print(f"\nObjective: {okr_results['objective']}")
        print(f"Overall Score: {okr_results['overall_score']}%")
        print(f"Status: {okr_results['overall_status']}")
        print(f"\nKey Results:")
        print("-"*70)
        
        for kr_id in ['KR3', 'KR4', 'KR5', 'KR6']:
            kr = okr_results['key_results'][kr_id]
            print(f"\n{kr_id}: {kr['name']}")
            print(f"  Score: {kr['score']}%")
            print(f"  Status: {kr['status']}")
            print(f"  Current: {kr['current_value']} {kr['target_operator']} {kr['target_value']} (target)")
            print(f"  Gap to Target: {kr['gap_to_target']}")
            print(f"  Owner: {kr['owner']}")
        
        # Display Action Triggers
        if action_triggers['critical'] or action_triggers['warning']:
            print("\n" + "="*70)
            print("ACTION TRIGGERS")
            print("="*70)
            
            if action_triggers['critical']:
                print("\n🔴 CRITICAL ACTIONS REQUIRED:")
                for trigger in action_triggers['critical']:
                    print(f"  {trigger['kr_id']}: {trigger['action']}")
                    print(f"    → Escalate to: {trigger['escalation']}")
            
            if action_triggers['warning']:
                print("\n🟡 WARNING ACTIONS:")
                for trigger in action_triggers['warning']:
                    print(f"  {trigger['kr_id']}: {trigger['action']}")
                    print(f"    → Escalate to: {trigger['escalation']}")
        
        # Step 7: Generate Excel Report
        print("\n[7/7] Generating Excel report...")
        
        # Create output directory
        output_dir = "data/output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        env_suffix = f"_{env}" if env != "prod" else ""
        output_file = f"{output_dir}/KPI_Report{env_suffix}_{timestamp}.xlsx"
        
        print(f"  Output file: {output_file}")
        
        # Generate Excel report (with OKR data)
        generate_reports.generate_excel_report(
            kpi_results=kpi_results,
            okr_results=okr_results,
            action_triggers=action_triggers,
            incidents=incidents,
            requests=requests if requests is not None else pd.DataFrame(),
            geo_results=geo_results,
            config=config,
            output_path=output_file
        )
        
        print(f"✓ Excel report generated successfully")
        
        print("\n" + "="*70)
        print(f"✓ Pipeline completed successfully")
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\n✗ ERROR: {e}")
        print("\nFile not found. Check:")
        print("  1. The input directory exists")
        print("  2. The CSV files are in the correct location")
        print("  3. File names match the configuration")
        print("\nUse --help to see available options:")
        print("  python main.py --help")
        print("\nOr specify files directly:")
        print("  python main.py --incidents path/to/incidents.csv --requests path/to/requests.csv")
        return 1
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
