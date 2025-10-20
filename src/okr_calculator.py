"""
OKR Calculator Module
=====================
Calculates OKR R002 (Service Delivery Excellence) scores based on KPI results.

Key Results:
- KR4: Incident Backlog Management (links to SM002)
- KR5: Request Backlog Management (links to SM003)
- KR6: First Time Fix Rate (links to SM004)

Author: IT Service Management Team
Version: 1.0
"""

import yaml
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import sys
import io

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OKRCalculator:
    """
    Calculate OKR R002 scores based on KPI calculation results.
    
    This calculator:
    1. Takes KPI results as input
    2. Maps KPIs to Key Results (KR4, KR5, KR6)
    3. Calculates individual KR scores (0-100 scale)
    4. Calculates weighted overall OKR score
    5. Determines status and performance bands
    """
    
    def __init__(self, okr_config_path: str, kpi_results: Dict[str, Any]):
        """
        Initialize OKR Calculator.
        
        Args:
            okr_config_path: Path to okr_config.yaml file
            kpi_results: Dictionary of KPI calculation results
                        Expected keys: 'SM001', 'SM002', 'SM003', 'SM004'
        """
        self.config = self._load_config(okr_config_path)
        self.kpi_results = kpi_results
        self.okr_scores = {}
        
        logger.info(f"OKRCalculator initialized with {len(kpi_results)} KPI results")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load OKR configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Loaded OKR config: {config['metadata']['okr_name']}")
            return config
        except FileNotFoundError:
            logger.error(f"OKR config file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing OKR config YAML: {e}")
            raise
    
    def calculate_kr_score(self, kr_id: str) -> Dict[str, Any]:
        """
        Calculate score for a single Key Result (0-100 scale).
        
        Scoring methods:
        - inverse_percentage: Lower is better (KR4, KR5 backlog metrics)
        - direct_percentage: Higher is better (KR6 quality metric)
        
        Args:
            kr_id: Key Result ID ('KR4', 'KR5', or 'KR6')
        
        Returns:
            Dictionary containing:
                - kr_id: Key Result identifier
                - name: KR name
                - current_value: Current metric value
                - target_value: Target metric value
                - score: Calculated score (0-100)
                - status: Performance status with emoji
                - gap_to_target: Difference from target
                - deadline: Target deadline date
                - days_remaining: Days until deadline
                - owner: Responsible owner
        """
        kr_config = self.config['key_results'][kr_id]
        
        # Get linked KPI result
        kpi_id = kr_config['calculation_source']['kpi_id']
        
        # Handle compound KPI keys (e.g., "SM002/KR4" instead of "SM002")
        # Try compound key first, then fall back to simple key
        kpi_result = None
        if kr_id in ['KR3', 'KR4', 'KR5', 'KR6']:
            # Try compound key format: "SM002/KR4"
            compound_key = f"{kpi_id}/{kr_id}"
            kpi_result = self.kpi_results.get(compound_key)
        
        # Fall back to simple key if compound not found
        if not kpi_result:
            kpi_result = self.kpi_results.get(kpi_id)
        
        if not kpi_result:
            logger.warning(f"KPI {kpi_id} not found for {kr_id} (tried {kpi_id} and {compound_key if kr_id in ['KR3', 'KR4', 'KR5', 'KR6'] else kpi_id})")
            return {
                'kr_id': kr_id,
                'name': kr_config['name'],
                'score': 0,
                'status': '⚠️ ERROR',
                'message': f'KPI {kpi_id} not found in results'
            }
        
        # Extract current value from KPI result
        current_value = self._extract_current_value(kpi_id, kpi_result)
        target_value = kr_config['target']['value']
        
        # Calculate score based on scoring method
        scoring_method = kr_config['scoring']['method']
        
        if scoring_method == 'inverse_percentage':
            # Lower is better (backlog metrics)
            # Formula: 100 - (current/target * 100)
            # Example: If current=25%, target=10%: 100 - (25/10*100) = -150 → clamp to 0
            raw_score = 100 - (current_value / target_value * 100)
        
        elif scoring_method == 'direct_percentage':
            # Higher is better (quality metrics)
            # Formula: (current/target) * 100
            # Example: If current=31.8%, target=80%: (31.8/80)*100 = 39.75
            raw_score = (current_value / target_value) * 100
        
        elif scoring_method == 'inverse_count':
            # Lower count is better (major incidents)
            # Formula: 100 - (current_count / max_acceptable * 100)
            # Example: If current=18, max_acceptable=20: 100 - (18/20*100) = 10
            max_acceptable = kr_config['scoring'].get('max_acceptable', target_value * 4)
            raw_score = 100 - (current_value / max_acceptable * 100)
        
        else:
            logger.error(f"Unknown scoring method: {scoring_method}")
            raw_score = 0
        
        # Clamp score to 0-100 range
        clamp_min = kr_config['scoring'].get('clamp_min', 0)
        clamp_max = kr_config['scoring'].get('clamp_max', 100)
        score = max(clamp_min, min(clamp_max, raw_score))
        
        # Determine status based on performance bands
        status = self._get_kr_status(score, kr_config['scoring']['performance_bands'])
        
        # Calculate gap to target
        gap_to_target = current_value - target_value
        
        # Calculate days remaining to deadline
        deadline_str = kr_config['deadline']['date']
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        days_remaining = (deadline - datetime.now()).days
        
        result = {
            'kr_id': kr_id,
            'name': kr_config['name'],
            'description': kr_config['description'],
            'current_value': round(current_value, 1),
            'target_value': target_value,
            'target_operator': kr_config['target']['operator'],
            'score': round(score, 1),
            'status': status,
            'gap_to_target': round(gap_to_target, 1),
            'deadline': deadline_str,
            'days_remaining': days_remaining,
            'criticality': kr_config['deadline']['criticality'],
            'owner': kr_config['owner'],
            'business_impact': kr_config['business_impact'],
            'linked_kpi': kpi_id
        }
        
        logger.info(f"{kr_id} calculated: Score={result['score']}, Status={result['status']}")
        
        return result
    
    def calculate_overall_okr(self) -> Dict[str, Any]:
        """
        Calculate overall OKR R002 weighted score.
        
        Formula: (KR4_score × 0.40) + (KR5_score × 0.30) + (KR6_score × 0.30)
        
        Returns:
            Dictionary containing:
                - okr_id: OKR identifier
                - okr_name: OKR name
                - objective: OKR objective description
                - overall_score: Weighted score (0-100)
                - overall_status: Performance status
                - key_results: Individual KR scores
                - weights: KR weights used
                - as_of_date: Calculation timestamp
        """
        logger.info("Calculating overall OKR R002 score...")
        
        # Calculate individual KR scores
        kr_scores = {}
        for kr_id in ['KR3', 'KR4', 'KR5', 'KR6']:
            kr_scores[kr_id] = self.calculate_kr_score(kr_id)
        
        # Get weights from config
        weights = self.config['weighting']['weights']
        
        # Validate weights sum to 100
        weight_sum = sum(weights.values())
        if weight_sum != 100:
            logger.warning(f"Weights sum to {weight_sum}, expected 100. Normalizing...")
            # Normalize weights
            for kr in weights:
                weights[kr] = weights[kr] / weight_sum * 100
        
        # Calculate weighted overall score
        overall_score = (
            kr_scores['KR3']['score'] * (weights['KR3'] / 100) +
            kr_scores['KR4']['score'] * (weights['KR4'] / 100) +
            kr_scores['KR5']['score'] * (weights['KR5'] / 100) +
            kr_scores['KR6']['score'] * (weights['KR6'] / 100)
        )
        
        # Determine overall status based on performance bands
        bands = self.config['weighting']['overall_score']['performance_bands']
        overall_status = self._get_overall_status(overall_score, bands)
        
        # Build result
        result = {
            'okr_id': self.config['metadata']['okr_id'],
            'okr_name': self.config['metadata']['okr_name'],
            'objective': self.config['objective']['description'],
            'overall_score': round(overall_score, 1),
            'overall_status': overall_status,
            'key_results': kr_scores,
            'weights': weights,
            'as_of_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'owner': self.config['metadata']['owner'],
            'year': self.config['metadata']['year']
        }
        
        logger.info(f"Overall OKR R002 Score: {result['overall_score']} - {result['overall_status']}")
        
        return result
    
    def _extract_current_value(self, kpi_id: str, kpi_result: Dict) -> float:
        """
        Extract the relevant metric value from KPI calculation result.
        
        Maps KPI results to the metric needed for KR scoring:
        - SM001 → total_major (for KR3)
        - SM002 → backlog_percentage (for KR4)
        - SM003 → aged_percentage (for KR5)
        - SM004 → ftf_rate (for KR6)
        
        Args:
            kpi_id: KPI identifier ('SM001', 'SM002', 'SM003', 'SM004')
            kpi_result: KPI calculation result dictionary
        
        Returns:
            Current value for the KR metric
        """
        if kpi_id == 'SM001':  # KR3 - Major Incidents
            # SM001 calculates total_major (P1 + P2)
            return float(kpi_result.get('Total_Major', 
                                       kpi_result.get('total_major', 0.0)))
        
        elif kpi_id == 'SM002':  # KR4 - Incident Backlog
            # SM002 calculates backlog_percentage
            return kpi_result.get('Backlog_Percentage',
                                 kpi_result.get('backlog_percentage', 0.0))
        
        elif kpi_id == 'SM003':  # KR5 - Request Backlog
            # SM003 calculates aged_percentage or request_backlog_percentage
            return kpi_result.get('Aged_Percentage',
                                 kpi_result.get('aged_percentage', 
                                               kpi_result.get('request_backlog_percentage', 0.0)))
        
        elif kpi_id == 'SM004':  # KR6 - First Time Fix
            # SM004 calculates ftf_rate or fcr_rate
            return kpi_result.get('FCR_Percentage',
                                 kpi_result.get('ftf_rate',
                                               kpi_result.get('fcr_rate', 0.0)))
        
        else:
            logger.warning(f"Unknown KPI ID: {kpi_id}")
            return 0.0
    
    def _get_kr_status(self, score: float, bands: Dict) -> str:
        """
        Determine KR status based on performance bands.
        
        Args:
            score: Calculated KR score (0-100)
            bands: Performance bands from config
        
        Returns:
            Status string with emoji indicator
        """
        if score >= bands['excellent']['min_score']:
            return '🟢 EXCELLENT'
        elif score >= bands['good']['min_score']:
            return '🟡 GOOD'
        elif score >= bands['at_risk']['min_score']:
            return '🟠 AT RISK'
        else:
            return '🔴 CRITICAL'
    
    def _get_overall_status(self, score: float, bands: Dict) -> str:
        """
        Determine overall OKR status based on performance bands.
        
        Args:
            score: Overall weighted OKR score (0-100)
            bands: Overall performance bands from config
        
        Returns:
            Status string with emoji indicator
        """
        # Check bands in order (excellent → critical)
        for band_name in ['excellent', 'on_track', 'at_risk', 'critical']:
            band = bands[band_name]
            if score >= band['min_score']:
                return band['status']
        
        # Fallback to critical if no band matched
        return bands['critical']['status']
    
    def get_action_triggers(self) -> Dict[str, list]:
        """
        Identify triggered actions based on current OKR performance.
        
        Returns:
            Dictionary of triggered actions by KR:
                - 'critical': Actions requiring immediate attention
                - 'warning': Actions requiring monitoring
        """
        okr_result = self.calculate_overall_okr()
        kr_results = okr_result['key_results']
        
        triggers = {
            'critical': [],
            'warning': []
        }
        
        # Check KR3 triggers (Major Incidents)
        kr3 = kr_results['KR3']
        kr3_triggers = self.config.get('action_triggers', {}).get('KR3', {})
        
        if kr3_triggers.get('critical'):
            # Check if total major > 15 or P1 count > 0
            if kr3['current_value'] > 15:
                triggers['critical'].append({
                    'kr_id': 'KR3',
                    'action': kr3_triggers['critical']['action'],
                    'escalation': kr3_triggers['critical']['escalation']
                })
        
        if kr3_triggers.get('warning'):
            if kr3['current_value'] > 5:
                triggers['warning'].append({
                    'kr_id': 'KR3',
                    'action': kr3_triggers['warning']['action'],
                    'escalation': kr3_triggers['warning']['escalation']
                })
        
        # Check KR4 triggers
        kr4 = kr_results['KR4']
        kr4_triggers = self.config.get('action_triggers', {}).get('KR4', {})
        
        if kr4_triggers.get('critical'):
            condition = kr4_triggers['critical']['condition']
            # Evaluate condition (simplified - just check days and backlog)
            if kr4['days_remaining'] < 7 and kr4['current_value'] > 15:
                triggers['critical'].append({
                    'kr_id': 'KR4',
                    'action': kr4_triggers['critical']['action'],
                    'escalation': kr4_triggers['critical']['escalation']
                })
        
        if kr4_triggers.get('warning'):
            if kr4['current_value'] > 10:
                triggers['warning'].append({
                    'kr_id': 'KR4',
                    'action': kr4_triggers['warning']['action'],
                    'escalation': kr4_triggers['warning']['escalation']
                })
        
        # Check KR5 triggers
        kr5 = kr_results['KR5']
        kr5_triggers = self.config.get('action_triggers', {}).get('KR5', {})
        
        if kr5_triggers.get('warning'):
            if kr5['current_value'] > 10:
                triggers['warning'].append({
                    'kr_id': 'KR5',
                    'action': kr5_triggers['warning']['action'],
                    'escalation': kr5_triggers['warning']['escalation']
                })
        
        # Check KR6 triggers
        kr6 = kr_results['KR6']
        kr6_triggers = self.config.get('action_triggers', {}).get('KR6', {})
        
        if kr6_triggers.get('critical'):
            if kr6['current_value'] < 50:
                triggers['critical'].append({
                    'kr_id': 'KR6',
                    'action': kr6_triggers['critical']['action'],
                    'escalation': kr6_triggers['critical']['escalation']
                })
        
        if kr6_triggers.get('warning'):
            if kr6['current_value'] < 70:
                triggers['warning'].append({
                    'kr_id': 'KR6',
                    'action': kr6_triggers['warning']['action'],
                    'escalation': kr6_triggers['warning']['escalation']
                })
        
        logger.info(f"Action triggers: {len(triggers['critical'])} critical, {len(triggers['warning'])} warnings")
        
        return triggers
    
    def generate_summary_report(self) -> str:
        """
        Generate a text summary report of OKR performance.
        
        Returns:
            Formatted string report
        """
        okr_result = self.calculate_overall_okr()
        
        report = []
        report.append("=" * 60)
        report.append(f"OKR R002: {okr_result['okr_name']}")
        report.append("=" * 60)
        report.append(f"As of: {okr_result['as_of_date']}")
        report.append(f"Overall Score: {okr_result['overall_score']}/100")
        report.append(f"Status: {okr_result['overall_status']}")
        report.append("")
        report.append("Key Results:")
        report.append("-" * 60)
        
        for kr_id, kr in okr_result['key_results'].items():
            report.append(f"\n{kr['name']} ({kr_id})")
            report.append(f"  Score: {kr['score']}/100 - {kr['status']}")
            report.append(f"  Current: {kr['current_value']}{kr['target_operator']}{kr['target_value']} (target)")
            report.append(f"  Gap: {kr['gap_to_target']}")
            report.append(f"  Deadline: {kr['deadline']} ({kr['days_remaining']} days)")
            report.append(f"  Owner: {kr['owner']}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """
    Example usage of OKRCalculator.
    
    This demonstrates how to use the calculator with sample KPI results.
    """
    # Sample KPI results (normally from kpi_calculator.py)
    sample_kpi_results = {
        'SM001': {
            'P1_Count': 0,
            'P2_Count': 3,
            'Total_Major': 3,
            'Adherence_Rate': 100.0
        },
        'SM002/KR4': {
            'Backlog_Count': 610,
            'Total_Incidents': 2438,
            'Backlog_Percentage': 25.0,
            'Adherence_Rate': 75.0
        },
        'SM003/KR5': {
            'Aged_Count': 288,
            'Total_Requests': 6383,
            'Aged_Percentage': 4.5,
            'Adherence_Rate': 95.5
        },
        'SM004/KR6': {
            'FCR_Count': 2052,
            'Total_Resolved': 6452,
            'FCR_Percentage': 31.8,
            'Adherence_Rate': 39.8
        }
    }
    
    # Initialize calculator
    okr_calc = OKRCalculator('config/okr_config.yaml', sample_kpi_results)
    
    # Calculate overall OKR
    okr_result = okr_calc.calculate_overall_okr()
    
    # Print summary
    print(okr_calc.generate_summary_report())
    
    # Get action triggers
    triggers = okr_calc.get_action_triggers()
    
    if triggers['critical']:
        print("\n🔴 CRITICAL ACTIONS REQUIRED:")
        for trigger in triggers['critical']:
            print(f"  - {trigger['kr_id']}: {trigger['action']}")
            print(f"    Escalate to: {trigger['escalation']}")
    
    if triggers['warning']:
        print("\n🟡 WARNING ACTIONS:")
        for trigger in triggers['warning']:
            print(f"  - {trigger['kr_id']}: {trigger['action']}")
            print(f"    Escalate to: {trigger['escalation']}")


if __name__ == '__main__':
    main()
