"""
Generate sample data for testing the KPI pipeline.
Creates small CSV files with realistic data structure.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


def generate_sample_incidents(num_rows=50):
    """Generate sample incident data."""
    
    print(f"Generating {num_rows} sample incidents...")
    
    # Base date for calculations
    base_date = datetime.now()
    
    # Generate data
    data = {
        'number': [f'INC{str(i).zfill(7)}' for i in range(1000, 1000 + num_rows)],
        'priority': [f'{random.choice([1, 1, 2, 2, 2, 3, 3, 3, 3, 4])} - {random.choice(["High", "Medium", "Low"])}' 
                     for _ in range(num_rows)],
        'incident_state': [random.choice(['Resolved', 'Resolved', 'Resolved', 'Closed', 'Closed', 'In Progress', 'New']) 
                          for _ in range(num_rows)],
        'opened_at': [(base_date - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d %H:%M:%S') 
                      for _ in range(num_rows)],
        'reassignment_count': [random.randint(0, 5) for _ in range(num_rows)],
        'location_country': [random.choice(['Germany', 'UK', 'France', 'Spain', 'Italy', 'Netherlands']) 
                            for _ in range(num_rows)],
        'contact_type': [random.choice(['Phone', 'Email', 'Self-service', 'Walk-in']) 
                        for _ in range(num_rows)],
    }
    
    # Add resolved_at dates (80% of incidents are resolved)
    resolved_dates = []
    for i in range(num_rows):
        if random.random() < 0.8:  # 80% resolved
            opened = datetime.strptime(data['opened_at'][i], '%Y-%m-%d %H:%M:%S')
            resolved = opened + timedelta(days=random.randint(1, 20), hours=random.randint(0, 23))
            resolved_dates.append(resolved.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            resolved_dates.append('')
    
    data['u_resolved'] = resolved_dates
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some additional columns that might be in real data
    df['assignment_group'] = [random.choice(['IT Support', 'Network Team', 'App Support', 'Database Team']) 
                               for _ in range(num_rows)]
    df['category'] = [random.choice(['Hardware', 'Software', 'Network', 'Access']) 
                      for _ in range(num_rows)]
    
    return df


def generate_sample_requests(num_rows=50):
    """Generate sample request data."""
    
    print(f"Generating {num_rows} sample requests...")
    
    # Base date for calculations
    base_date = datetime.now()
    
    # Generate data
    data = {
        'number': [f'REQ{str(i).zfill(7)}' for i in range(2000, 2000 + num_rows)],
        'state': [random.choice(['Closed', 'Closed', 'Closed', 'Resolved', 'In Progress', 'Pending']) 
                 for _ in range(num_rows)],
        'opened_at': [(base_date - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d %H:%M:%S') 
                      for _ in range(num_rows)],
        'location_country': [random.choice(['Germany', 'UK', 'France', 'Spain', 'Italy', 'Netherlands']) 
                            for _ in range(num_rows)],
        'contact_type': [random.choice(['Phone', 'Email', 'Self-service', 'Walk-in']) 
                        for _ in range(num_rows)],
    }
    
    # Add resolved_at dates (85% of requests are resolved)
    resolved_dates = []
    for i in range(num_rows):
        if random.random() < 0.85:  # 85% resolved
            opened = datetime.strptime(data['opened_at'][i], '%Y-%m-%d %H:%M:%S')
            resolved = opened + timedelta(days=random.randint(1, 45), hours=random.randint(0, 23))
            resolved_dates.append(resolved.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            resolved_dates.append('')
    
    data['u_resolved'] = resolved_dates
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add some additional columns
    df['assignment_group'] = [random.choice(['Service Desk', 'IT Support', 'Business Support']) 
                               for _ in range(num_rows)]
    df['category'] = [random.choice(['Account', 'Access Request', 'Information', 'Provisioning']) 
                      for _ in range(num_rows)]
    
    return df


def main():
    """Generate and save sample data files."""
    
    print("="*70)
    print("SAMPLE DATA GENERATOR")
    print("="*70)
    print()
    
    # Create output directory
    output_dir = 'tests/sample_data'
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()
    
    # Generate incidents
    print("[1/2] Generating sample incidents...")
    incidents_df = generate_sample_incidents(50)
    incidents_file = os.path.join(output_dir, 'sample_incidents.csv')
    incidents_df.to_csv(incidents_file, index=False)
    print(f"✓ Saved: {incidents_file}")
    print(f"  Rows: {len(incidents_df)}, Columns: {len(incidents_df.columns)}")
    print()
    
    # Generate requests
    print("[2/2] Generating sample requests...")
    requests_df = generate_sample_requests(50)
    requests_file = os.path.join(output_dir, 'sample_requests.csv')
    requests_df.to_csv(requests_file, index=False)
    print(f"✓ Saved: {requests_file}")
    print(f"  Rows: {len(requests_df)}, Columns: {len(requests_df.columns)}")
    print()
    
    # Summary
    print("="*70)
    print("✓ Sample data generated successfully!")
    print("="*70)
    print()
    print("You can now run tests using:")
    print("  python tests/test_pipeline.py")
    print()
    print("Note: The test suite will automatically use sample data if available,")
    print("otherwise it will fall back to real data in data/input/")
    print("="*70)


if __name__ == "__main__":
    main()



