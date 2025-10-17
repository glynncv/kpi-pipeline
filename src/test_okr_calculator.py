"""
Test Script for OKR Calculator
===============================
Demonstrates the OKR calculator with sample KPI results.

This script:
1. Creates sample KPI results matching current performance
2. Initializes the OKR calculator
3. Calculates individual KR scores
4. Calculates overall OKR R002 score
5. Identifies action triggers
6. Generates a summary report
"""

import sys
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from okr_calculator import OKRCalculator
import json


def create_sample_kpi_results():
    """
    Create sample KPI results based on current performance data.
    
    These values match the current state from the OKR definitions document:
    - KR4 (SM002): 25% backlog (610 of 2438 incidents)
    - KR5 (SM003): 4.5% aged (288 of 6383 requests)
    - KR6 (SM004): 31.8% FTF (2052 of 6452 eligible)
    """
    return {
        'SM001': {
            'P1_Count': 0,
            'P2_Count': 3,
            'Total_Major': 3,
            'Adherence_Rate': 100.0,
            'Status': 'Met'
        },
        'SM002/KR4': {
            'Backlog_Count': 610,
            'Total_Incidents': 2438,
            'Backlog_Percentage': 25.0,
            'Adherence_Rate': 75.0,
            'Status': 'Critical'
        },
        'SM003/KR5': {
            'Aged_Count': 288,
            'Total_Requests': 6383,
            'Aged_Percentage': 4.5,
            'Adherence_Rate': 95.5,
            'Status': 'Met'
        },
        'SM004/KR6': {
            'FCR_Count': 2052,
            'Total_Resolved': 6452,
            'FCR_Percentage': 31.8,
            'Adherence_Rate': 39.8,
            'Status': 'Critical'
        }
    }


def main():
    """Run OKR calculator test."""
    
    print("=" * 70)
    print("OKR CALCULATOR TEST")
    print("=" * 70)
    print()
    
    # Step 1: Create sample KPI results
    print("Step 1: Loading sample KPI results...")
    kpi_results = create_sample_kpi_results()
    print(f"  ✓ Loaded {len(kpi_results)} KPI results")
    print()
    
    # Step 2: Initialize OKR calculator
    print("Step 2: Initializing OKR calculator...")
    try:
        okr_calc = OKRCalculator('config/okr_config.yaml', kpi_results)
        print("  ✓ OKR calculator initialized")
    except FileNotFoundError:
        print("  ✗ Error: config/okr_config.yaml not found")
        print("  Make sure okr_config.yaml is in the config/ directory")
        return
    print()
    
    # Step 3: Calculate individual KR scores
    print("Step 3: Calculating individual Key Result scores...")
    print()
    
    for kr_id in ['KR4', 'KR5', 'KR6']:
        kr_result = okr_calc.calculate_kr_score(kr_id)
        print(f"  {kr_id}: {kr_result['name']}")
        print(f"    Current: {kr_result['current_value']}{kr_result['target_operator']}{kr_result['target_value']} (target)")
        print(f"    Score: {kr_result['score']}/100")
        print(f"    Status: {kr_result['status']}")
        print(f"    Gap: {kr_result['gap_to_target']}")
        print(f"    Deadline: {kr_result['deadline']} ({kr_result['days_remaining']} days)")
        print(f"    Owner: {kr_result['owner']}")
        print()
    
    # Step 4: Calculate overall OKR score
    print("Step 4: Calculating overall OKR R002 score...")
    okr_result = okr_calc.calculate_overall_okr()
    print()
    print(f"  Overall OKR Score: {okr_result['overall_score']}/100")
    print(f"  Status: {okr_result['overall_status']}")
    print(f"  Weights: KR4={okr_result['weights']['KR4']}%, KR5={okr_result['weights']['KR5']}%, KR6={okr_result['weights']['KR6']}%")
    print()
    
    # Step 5: Show calculation breakdown
    print("Step 5: Calculation breakdown...")
    kr_scores = okr_result['key_results']
    weights = okr_result['weights']
    
    print(f"  Formula: (KR4 × {weights['KR4']/100}) + (KR5 × {weights['KR5']/100}) + (KR6 × {weights['KR6']/100})")
    print(f"  Calculation: ({kr_scores['KR4']['score']} × {weights['KR4']/100}) + "
          f"({kr_scores['KR5']['score']} × {weights['KR5']/100}) + "
          f"({kr_scores['KR6']['score']} × {weights['KR6']/100})")
    
    kr4_contribution = kr_scores['KR4']['score'] * (weights['KR4'] / 100)
    kr5_contribution = kr_scores['KR5']['score'] * (weights['KR5'] / 100)
    kr6_contribution = kr_scores['KR6']['score'] * (weights['KR6'] / 100)
    
    print(f"           = {kr4_contribution:.1f} + {kr5_contribution:.1f} + {kr6_contribution:.1f}")
    print(f"           = {okr_result['overall_score']}")
    print()
    
    # Step 6: Get action triggers
    print("Step 6: Identifying action triggers...")
    triggers = okr_calc.get_action_triggers()
    
    if triggers['critical']:
        print()
        print("  🔴 CRITICAL ACTIONS REQUIRED:")
        for trigger in triggers['critical']:
            print(f"    {trigger['kr_id']}: {trigger['action']}")
            print(f"      → Escalate to: {trigger['escalation']}")
    
    if triggers['warning']:
        print()
        print("  🟡 WARNING ACTIONS:")
        for trigger in triggers['warning']:
            print(f"    {trigger['kr_id']}: {trigger['action']}")
            print(f"      → Escalate to: {trigger['escalation']}")
    
    if not triggers['critical'] and not triggers['warning']:
        print("  ✓ No action triggers - all KRs performing well")
    
    print()
    
    # Step 7: Generate summary report
    print("=" * 70)
    print("SUMMARY REPORT")
    print("=" * 70)
    print(okr_calc.generate_summary_report())
    
    # Step 8: Export results to JSON
    print()
    print("Step 8: Exporting results to JSON...")
    
    output = {
        'okr_result': okr_result,
        'action_triggers': triggers,
        'kpi_results': kpi_results
    }
    
    with open('okr_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("  ✓ Results saved to okr_results.json")
    print()
    
    # Step 9: Key insights
    print("=" * 70)
    print("KEY INSIGHTS")
    print("=" * 70)
    print()
    
    # Analyze each KR
    print("KR Performance Analysis:")
    print()
    
    if kr_scores['KR4']['score'] < 50:
        print("  🔴 KR4 (Incident Backlog) - CRITICAL")
        print(f"     Current: {kr_scores['KR4']['current_value']}% backlog")
        print(f"     Target: {kr_scores['KR4']['target_value']}%")
        print(f"     Gap: {kr_scores['KR4']['gap_to_target']}%")
        print(f"     Action: Need to clear ~{int(kr_scores['KR4']['current_value'] - kr_scores['KR4']['target_value'])}% of backlog")
        print()
    
    if kr_scores['KR5']['score'] >= 90:
        print("  🟢 KR5 (Request Backlog) - EXCELLENT")
        print(f"     Current: {kr_scores['KR5']['current_value']}% aged")
        print(f"     Target: {kr_scores['KR5']['target_value']}%")
        print(f"     Status: Exceeding target by {abs(kr_scores['KR5']['gap_to_target'])}%")
        print()
    
    if kr_scores['KR6']['score'] < 50:
        print("  🔴 KR6 (First Time Fix) - CRITICAL")
        print(f"     Current: {kr_scores['KR6']['current_value']}% FTF")
        print(f"     Target: {kr_scores['KR6']['target_value']}%")
        print(f"     Gap: {kr_scores['KR6']['gap_to_target']}%")
        print(f"     Action: Need to improve FTF rate by ~{abs(kr_scores['KR6']['gap_to_target'])}%")
        print()
    
    print("Overall Recommendation:")
    if okr_result['overall_score'] < 50:
        print("  🔴 URGENT: Multiple KRs are significantly below target")
        print("     Recommend executive escalation and resource allocation")
    elif okr_result['overall_score'] < 70:
        print("  🟠 ATTENTION: OKR needs improvement")
        print("     Focus on lowest-scoring KRs for quick wins")
    elif okr_result['overall_score'] < 90:
        print("  🟡 ON TRACK: Continue current efforts")
        print("     Monitor progress and adjust as needed")
    else:
        print("  🟢 EXCELLENT: OKR performance is strong")
        print("     Maintain current practices")
    
    print()
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == '__main__':
    main()
