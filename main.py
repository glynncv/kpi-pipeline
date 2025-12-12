"""
KPI Pipeline - Main Execution Script

This script runs the complete KPI pipeline:
1. Loads configuration
2. Loads incident and request data
3. Transforms data (adds calculated fields)
4. Calculates KPIs
5. Calculates OKR scores
5.5. Calculates geographic analysis (with OKR scores per location)
5.6. Processes Problem Management KPIs and generates PM Dashboard
5.7. Calculates SDM analysis (with OKR scores per SDM)
6. Displays results
7. Generates Excel KPI Report
8. Summary and completion

Usage:
    python main.py                              # Use prod environment (default)
    python main.py --env dev                    # Use dev environment (small test data)
    python main.py --incidents path/to/file.csv # Override incidents file
    python main.py --requests path/to/file.csv  # Override requests file

Output Files:
    - data/output/KPI_Report_{env}_{timestamp}.xlsx
    - data/output/PM_Dashboard_{timestamp}.xlsx (if PM data available)
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
from src import sdm_analysis
from src.okr_calculator import OKRCalculator
from src import load_problem_data
from src import transform_problems
from src import calculate_pm_kpis
from src import generate_pm_reports


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
    
    parser.add_argument(
        '--save-tables',
        action='store_true',
        help='Save normalized output tables to data/output/tables/ directory'
    )
    
    parser.add_argument(
        '--tables-format',
        choices=['csv', 'parquet', 'json'],
        default='csv',
        help='Format for saved tables: csv (default), parquet, or json'
    )

    return parser.parse_args()


def save_output_tables(geo_results, sdm_results, incidents, requests, problems,
                       kpi_results, okr_results, output_dir, table_format='csv'):
    """
    Save normalized output tables to files.
    
    Args:
        geo_results: Geographic analysis results dictionary
        sdm_results: SDM analysis results dictionary
        incidents: Transformed incidents DataFrame
        requests: Transformed requests DataFrame (or empty DataFrame)
        problems: Transformed problems DataFrame (or None)
        kpi_results: KPI results dictionary
        okr_results: OKR results dictionary
        output_dir: Base output directory
        table_format: Format to save ('csv', 'parquet', or 'json')
    
    Returns:
        List of saved file paths
    """
    tables_dir = Path(output_dir) / 'tables'
    tables_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved_files = []
    
    print(f"\nSaving output tables ({table_format} format)...")
    
    # Helper function to save DataFrame
    def save_df(df, name, index=False):
        if df is None or df.empty:
            return None
        
        if table_format == 'csv':
            filepath = tables_dir / f"{name}_{timestamp}.csv"
            df.to_csv(filepath, index=index)
        elif table_format == 'parquet':
            try:
                filepath = tables_dir / f"{name}_{timestamp}.parquet"
                df.to_parquet(filepath, index=index)
            except ImportError:
                print(f"⚠ Warning: pyarrow not available, falling back to CSV for {name}")
                filepath = tables_dir / f"{name}_{timestamp}.csv"
                df.to_csv(filepath, index=index)
        elif table_format == 'json':
            filepath = tables_dir / f"{name}_{timestamp}.json"
            df.to_json(filepath, orient='records', date_format='iso', index=index)
        else:
            return None
        
        saved_files.append(str(filepath))
        return filepath
    
    # Save geographic analysis tables
    if geo_results:
        if not geo_results['location_summary'].empty:
            save_df(geo_results['location_summary'], 'geographic_summary')
        
        if 'country_summary' in geo_results and not geo_results['country_summary'].empty:
            save_df(geo_results['country_summary'], 'country_summary')
        
        if 'top_performers' in geo_results and not geo_results['top_performers'].empty:
            save_df(geo_results['top_performers'], 'geographic_top_performers')
        
        if 'bottom_performers' in geo_results and not geo_results['bottom_performers'].empty:
            save_df(geo_results['bottom_performers'], 'geographic_bottom_performers')
    
    # Save SDM analysis tables
    if sdm_results and not sdm_results['sdm_summary'].empty:
        save_df(sdm_results['sdm_summary'], 'sdm_summary')
        
        if 'top_performers' in sdm_results and not sdm_results['top_performers'].empty:
            save_df(sdm_results['top_performers'], 'sdm_top_performers')
        
        if 'bottom_performers' in sdm_results and not sdm_results['bottom_performers'].empty:
            save_df(sdm_results['bottom_performers'], 'sdm_bottom_performers')
    
    # Save normalized data tables
    if not incidents.empty:
        save_df(incidents, 'incidents_normalized')
    
    if requests is not None and not requests.empty:
        save_df(requests, 'requests_normalized')
    
    if problems is not None and not problems.empty:
        save_df(problems, 'problems_normalized')
    
    # Create and save KPI summary table
    kpi_summary_data = []
    for kpi_code, kpi_data in kpi_results.items():
        if kpi_code == 'OVERALL':
            continue
        kpi_summary_data.append({
            'KPI_Code': kpi_code,
            'KPI_Name': kpi_data.get('KPI_Name', ''),
            'Status': kpi_data.get('Status', ''),
            'Adherence_Rate': kpi_data.get('Adherence_Rate', 0),
            'Business_Impact': kpi_data.get('Business_Impact', '')
        })
    
    if kpi_summary_data:
        kpi_summary_df = pd.DataFrame(kpi_summary_data)
        save_df(kpi_summary_df, 'kpi_summary')
    
    print(f"✓ Saved {len(saved_files)} table files to {tables_dir}")
    return saved_files


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
    
    # Normalize input directory path (handles forward/backward slashes)
    input_dir = str(Path(input_dir))
    
    if args.incidents:
        # If absolute path or contains directory separator, use as-is
        if Path(args.incidents).is_absolute() or os.sep in args.incidents:
            incidents_path = str(Path(args.incidents))
        else:
            incidents_path = str(Path(input_dir) / args.incidents)
    else:
        incidents_path = str(Path(input_dir) / incidents_file)
    
    if args.requests:
        if Path(args.requests).is_absolute() or os.sep in args.requests:
            requests_path = str(Path(args.requests))
        else:
            requests_path = str(Path(input_dir) / args.requests)
    else:
        requests_path = str(Path(input_dir) / requests_file)
    
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
        print("[1/8] Loading configuration...")
        config = config_loader.load_all_configs(args.config, 'config/okr_config.yaml')
        print(f"✓ Configuration loaded: {config['metadata']['organization']}")
        
        # Get data file paths from config and CLI args
        incidents_path, requests_path, env = get_data_file_paths(config, args)
        
        # Display environment info
        env_desc = config['data_sources']['environments'][env]['description']
        print(f"✓ Environment: {env} ({env_desc})")

        # Create output directory early (used by PM reports and main KPI report)
        output_dir = "data/output"
        os.makedirs(output_dir, exist_ok=True)

        # Step 2: Load Data
        print("\n[2/8] Loading data files...")
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
        print("\n[3/8] Transforming data (adding calculated fields)...")
        incidents = transform.add_incident_flags(incidents, config)
        print(f"✓ Added incident flags")
        
        if requests is not None:
            requests = transform.add_request_flags(requests, config)
            print(f"✓ Added request flags")
        
        # Step 4: Calculate KPIs
        print("\n[4/8] Calculating KPIs...")
        kpi_results = calculate_kpis.calculate_all(incidents, requests, config)
        print(f"✓ Calculated {len(kpi_results)-1} KPIs + overall score")
        
        # Step 5: Calculate OKR Scores
        print("\n[5/8] Calculating OKR scores...")
        
        okr_calc = OKRCalculator('config/okr_config.yaml', kpi_results)
        okr_results = okr_calc.calculate_overall_okr()
        action_triggers = okr_calc.get_action_triggers()
        
        print(f"✓ Calculated OKR R002 with {len(okr_results['key_results'])} Key Results")
        print(f"✓ Overall OKR Score: {okr_results['overall_score']}%")
        
        # Step 5.5: Calculate Geographic Analysis
        print("\n[5.5/8] Calculating geographic analysis...")

        # Load problem data if available (for PM KPIs in geographic analysis)
        problems = None
        if config['kpis'].get('RCA001', {}).get('enabled', False):
            try:
                problems_raw, tasks_raw = load_problem_data.load_all_problem_data(
                    'data/input', config
                )
                if problems_raw is not None and tasks_raw is not None:
                    problems = transform_problems.transform_all_problem_data(problems_raw, tasks_raw)
                    print(f"✓ Loaded {len(problems)} problems for geographic analysis")
            except Exception as e:
                print(f"ℹ Problem data not available for geographic analysis: {e}")
                problems = None

        # Load OKR config for geographic OKR scores
        okr_config = None
        try:
            okr_config = config_loader.load_okr_config('config/okr_config.yaml')
        except Exception as e:
            print(f"ℹ OKR config not available: {e}")

        geo_results = geographic_analysis.analyze_geography(
            incidents=incidents,
            requests=requests if requests is not None else pd.DataFrame(),
            config=config,
            problems=problems,
            okr_config=okr_config
        )
        print(f"✓ Analyzed {len(geo_results['location_summary'])} locations")
        print(f"✓ Found {geo_results['intervention_summary']['critical_count']} critical locations")

        # Step 5.6: Process Problem Management (if enabled and data available)
        pm_report_path = None
        if config.get('kpis', {}).get('RCA001', {}).get('enabled', False) and problems is not None:
            print("\n[5.6/8] Processing Problem Management KPIs...")
            try:
                # Calculate PM KPIs using problems already loaded in Step 5.5
                pm_kpis = calculate_pm_kpis.calculate_all_pm_kpis(problems, config)
                rca = pm_kpis['RCA001']

                print(f"✓ RCA001 Completion Rate: {rca['completion_rate']:.1f}%")
                print(f"✓ Status: {rca['status']}")

                # Generate PM dashboard
                pm_report_path = generate_pm_reports.export_pm_dashboard(
                    pm_kpis,
                    problems,
                    output_dir=output_dir
                )
                print(f"✓ PM Dashboard saved to: {pm_report_path}")
            except Exception as pm_error:
                print(f"ℹ Problem Management processing skipped: {pm_error}")

        # Step 5.7: Calculate SDM Analysis
        print("\n[5.7/8] Calculating SDM analysis...")

        sdm_results = sdm_analysis.analyze_sdm(
            incidents=incidents,
            requests=requests if requests is not None else pd.DataFrame(),
            config=config,
            problems=problems,
            okr_config=okr_config
        )

        if sdm_results['sdm_summary'].empty:
            print("ℹ No SDM data available (no 'it_operations_manager' column found)")
        else:
            print(f"✓ Analyzed {len(sdm_results['sdm_summary'])} SDMs")
            print(f"✓ Found {sdm_results['intervention_summary']['critical_count']} critical SDMs")

        # Step 6: Display Results
        print("\n[6/8] Results:")
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
        print("\n[7/8] Generating Excel report...")

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
            sdm_results=sdm_results,
            config=config,
            output_path=output_file
        )
        
        print(f"✓ Excel report generated successfully")
        
        if pm_report_path:
            print(f"✓ PM Dashboard generated: {pm_report_path}")
        
        # Step 8: Save output tables if requested
        if args.save_tables:
            try:
                saved_files = save_output_tables(
                    geo_results=geo_results,
                    sdm_results=sdm_results,
                    incidents=incidents,
                    requests=requests if requests is not None else pd.DataFrame(),
                    problems=problems,
                    kpi_results=kpi_results,
                    okr_results=okr_results,
                    output_dir=output_dir,
                    table_format=args.tables_format
                )
                if saved_files:
                    print(f"✓ Output tables saved: {len(saved_files)} files")
            except Exception as table_error:
                print(f"⚠ Warning: Failed to save output tables: {table_error}")
        
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
