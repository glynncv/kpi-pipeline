"""
Markdown Export Module
======================
Exports KPI and OKR results to formatted Markdown files.

Generates professional Markdown reports that mirror the console output
with tables, status indicators, and action items.

Author: IT Service Management Team
Version: 1.0
"""

from datetime import datetime
from typing import Dict, Any, Optional


class MarkdownExporter:
    """Export KPI and OKR results to Markdown."""
    
    def __init__(self, kpi_results: Dict[str, Any], okr_result: Optional[Dict[str, Any]] = None):
        """
        Initialize Markdown exporter.
        
        Args:
            kpi_results: Dictionary of KPI calculation results
            okr_result: Optional OKR calculation result
        """
        self.kpi_results = kpi_results
        self.okr_result = okr_result
        self.lines = []
    
    def _add_line(self, text: str = ""):
        """Add a line to the output."""
        self.lines.append(text)
    
    def _add_header(self, text: str, level: int = 1):
        """Add a Markdown header."""
        self._add_line(f"{'#' * level} {text}")
        self._add_line()
    
    def _add_table(self, headers: list, rows: list):
        """Add a Markdown table."""
        # Header row
        self._add_line("| " + " | ".join(headers) + " |")
        # Separator row
        self._add_line("| " + " | ".join(["---"] * len(headers)) + " |")
        # Data rows
        for row in rows:
            self._add_line("| " + " | ".join(str(cell) for cell in row) + " |")
        self._add_line()
    
    def export(self, filename: str) -> str:
        """
        Export results to Markdown file.
        
        Args:
            filename: Output filename (without path)
            
        Returns:
            Full path to created file
        """
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Add timestamp to filename if not present
        if not any(char.isdigit() for char in filename):
            name_parts = filename.rsplit('.', 1)
            filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}" if len(name_parts) > 1 else f"{filename}_{timestamp}.md"
        
        filepath = f"data/output/{filename}"
        
        # Build report
        self._build_report()
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.lines))
        
        return filepath
    
    def _build_report(self):
        """Build the complete Markdown report."""
        # Title
        self._add_header("KPI & OKR Performance Report", 1)
        self._add_line(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._add_line()
        self._add_line("---")
        self._add_line()
        
        # KPI Summary
        self._add_kpi_summary()
        
        # OKR Summary
        if self.okr_result:
            self._add_okr_summary()
        
        # Detailed KPI Results
        self._add_kpi_details()
        
        # Detailed OKR Results
        if self.okr_result:
            self._add_okr_details()
        
        # Action Items
        if self.okr_result:
            self._add_action_items()
    
    def _add_kpi_summary(self):
        """Add KPI summary table."""
        self._add_header("KPI Results - Summary", 2)
        
        # Build table rows
        rows = []
        for kpi_code, kpi_data in self.kpi_results.items():
            if kpi_code == 'OVERALL':
                continue
            
            # Get summary details
            if 'P1_Count' in kpi_data:
                details = f"{kpi_data['P1_Count']} P1, {kpi_data['P2_Count']} P2"
            elif 'Backlog_Count' in kpi_data:
                details = f"{kpi_data['Backlog_Percentage']}% backlog"
            elif 'Aged_Count' in kpi_data:
                details = f"{kpi_data['Aged_Percentage']}% aged"
            elif 'FCR_Count' in kpi_data:
                details = f"{kpi_data['FCR_Percentage']}% FCR"
            else:
                details = "-"
            
            # Add status emoji
            status = kpi_data['Status']
            if 'Critical' in status:
                status_icon = "🔴"
            elif 'Warning' in status:
                status_icon = "⚠️"
            else:
                status_icon = "✅"
            
            rows.append([
                kpi_code,
                f"{status_icon} {status}",
                f"{kpi_data['Adherence_Rate']}%",
                details
            ])
        
        self._add_table(['KPI', 'Status', 'Adherence', 'Key Metric'], rows)
        
        # Overall KPI Performance
        if 'OVERALL' in self.kpi_results:
            overall = self.kpi_results['OVERALL']
            self._add_line(f"**Overall KPI Score:** {overall['Overall_Score']}% ({overall['Overall_Status']})")
            self._add_line()
            weights = overall['Weights_Used']
            self._add_line(f"**Weights:** SM001={weights.get('SM001', 0)}%, SM002={weights.get('SM002', 0)}%, SM003={weights.get('SM003', 0)}%, SM004={weights.get('SM004', 0)}%")
            self._add_line()
        
        self._add_line("---")
        self._add_line()
    
    def _add_okr_summary(self):
        """Add OKR summary table."""
        self._add_header("OKR R002: Service Delivery Excellence", 2)
        
        self._add_line(f"**Overall OKR Score:** {self.okr_result['overall_score']}/100")
        self._add_line(f"**Status:** {self.okr_result['overall_status']}")
        weights = self.okr_result['weights']
        self._add_line(f"**Weights:** KR4={weights['KR4']}%, KR5={weights['KR5']}%, KR6={weights['KR6']}%")
        self._add_line()
        
        # Build KR table
        rows = []
        for kr_id, kr_data in self.okr_result['key_results'].items():
            rows.append([
                kr_id,
                kr_data['name'],
                str(kr_data['current_value']),
                f"{kr_data['target_operator']}{kr_data['target_value']}",
                f"{kr_data['score']}%",
                kr_data['status'],
                str(kr_data['gap_to_target'])
            ])
        
        self._add_table(
            ['KR', 'Name', 'Current', 'Target', 'Score', 'Status', 'Gap'],
            rows
        )
        
        self._add_line("---")
        self._add_line()
    
    def _add_kpi_details(self):
        """Add detailed KPI results."""
        self._add_header("KPI Results - Detailed", 2)
        
        for kpi_code, kpi_data in self.kpi_results.items():
            if kpi_code == 'OVERALL':
                continue
            
            self._add_header(f"{kpi_code}: {kpi_data['KPI_Name']}", 3)
            
            self._add_line(f"- **Status:** {kpi_data['Status']}")
            self._add_line(f"- **Adherence:** {kpi_data['Adherence_Rate']}%")
            self._add_line(f"- **Business Impact:** {kpi_data['Business_Impact']}")
            
            # KPI-specific details
            if 'P1_Count' in kpi_data:
                self._add_line(f"- **P1 Count:** {kpi_data['P1_Count']} (target: ≤{kpi_data['P1_Target']})")
                self._add_line(f"- **P2 Count:** {kpi_data['P2_Count']} (target: ≤{kpi_data['P2_Target']})")
                self._add_line(f"- **Total Major:** {kpi_data['Total_Major']}")
            
            elif 'Backlog_Count' in kpi_data:
                self._add_line(f"- **Total Incidents:** {kpi_data['Total_Incidents']}")
                self._add_line(f"- **Backlog Count:** {kpi_data['Backlog_Count']}")
                self._add_line(f"- **Backlog Percentage:** {kpi_data['Backlog_Percentage']}%")
                self._add_line(f"- **Target Adherence:** ≥{kpi_data['Target_Adherence']}%")
            
            elif 'Aged_Count' in kpi_data:
                self._add_line(f"- **Total Requests:** {kpi_data['Total_Requests']}")
                self._add_line(f"- **Aged Count:** {kpi_data['Aged_Count']}")
                self._add_line(f"- **Aged Percentage:** {kpi_data['Aged_Percentage']}%")
                self._add_line(f"- **Target Adherence:** ≥{kpi_data['Target_Adherence']}%")
            
            elif 'FCR_Count' in kpi_data:
                self._add_line(f"- **Total Resolved:** {kpi_data['Total_Resolved']}")
                self._add_line(f"- **FCR Count:** {kpi_data['FCR_Count']}")
                self._add_line(f"- **FCR Percentage:** {kpi_data['FCR_Percentage']}%")
                self._add_line(f"- **Target Rate:** ≥{kpi_data['Target_Rate']}%")
            
            self._add_line()
        
        self._add_line("---")
        self._add_line()
    
    def _add_okr_details(self):
        """Add detailed OKR results."""
        self._add_header("Key Results - Detailed", 2)
        
        for kr_id, kr_data in self.okr_result['key_results'].items():
            self._add_header(f"{kr_id}: {kr_data['name']}", 3)
            
            self._add_line(f"- **Score:** {kr_data['score']}%")
            self._add_line(f"- **Status:** {kr_data['status']}")
            self._add_line(f"- **Current:** {kr_data['current_value']} {kr_data['target_operator']} {kr_data['target_value']} (target)")
            self._add_line(f"- **Gap:** {kr_data['gap_to_target']}")
            self._add_line(f"- **Deadline:** {kr_data['deadline']} ({kr_data['days_remaining']} days)")
            self._add_line(f"- **Owner:** {kr_data['owner']}")
            self._add_line(f"- **Criticality:** {kr_data['criticality']}")
            self._add_line()
        
        self._add_line("---")
        self._add_line()
    
    def _add_action_items(self):
        """Add action items section."""
        # Note: We would need to pass action triggers separately
        # For now, generate based on KR status
        self._add_header("Action Items", 2)
        
        critical_actions = []
        warning_actions = []
        
        for kr_id, kr_data in self.okr_result['key_results'].items():
            if kr_data['score'] < 50:
                if 'Backlog' in kr_data['name']:
                    action = f"Reduce backlog from {kr_data['current_value']}% to {kr_data['target_value']}%"
                elif 'Fix Rate' in kr_data['name']:
                    action = f"Improve rate from {kr_data['current_value']}% to {kr_data['target_value']}%"
                else:
                    action = f"Close gap of {abs(kr_data['gap_to_target'])}"
                
                critical_actions.append({
                    'kr_id': kr_id,
                    'name': kr_data['name'],
                    'action': action,
                    'owner': kr_data['owner']
                })
            elif kr_data['score'] < 70:
                warning_actions.append({
                    'kr_id': kr_id,
                    'name': kr_data['name'],
                    'action': f"Monitor and improve from {kr_data['score']}%",
                    'owner': kr_data['owner']
                })
        
        if critical_actions:
            self._add_header("🔴 Critical Actions", 3)
            for item in critical_actions:
                self._add_line(f"- **{item['kr_id']}:** {item['action']}")
                self._add_line(f"  - Owner: {item['owner']}")
            self._add_line()
        
        if warning_actions:
            self._add_header("🟡 Warning Actions", 3)
            for item in warning_actions:
                self._add_line(f"- **{item['kr_id']}:** {item['action']}")
                self._add_line(f"  - Owner: {item['owner']}")
            self._add_line()
        
        if not critical_actions and not warning_actions:
            self._add_line("✅ No critical or warning actions required - all metrics performing well.")
            self._add_line()


def export_to_markdown(kpi_results: Dict[str, Any], okr_result: Optional[Dict[str, Any]] = None, 
                      filename: str = "kpi_report.md") -> str:
    """
    Export KPI and OKR results to Markdown.
    
    Args:
        kpi_results: Dictionary of KPI calculation results
        okr_result: Optional OKR calculation result
        filename: Output filename
        
    Returns:
        Path to created Markdown file
    """
    exporter = MarkdownExporter(kpi_results, okr_result)
    filepath = exporter.export(filename)
    return filepath


if __name__ == "__main__":
    # Test with sample data
    print("Markdown export module loaded successfully")
    print("Use export_to_markdown(kpi_results, okr_result) to create reports")

