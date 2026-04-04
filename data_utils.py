import pandas as pd
import numpy as np

def generate_mock_data(n=1000):
    """Generate mock defect records CSV in English to ensure cross-platform compatibility."""
    defects = ['Scratch', 'Inclusion', 'Contamination', 'Missing Part', 'Deformation', 'Crack']
    # Mock 80/20 distribution: the first two issues account for ~75%
    weights = [0.45, 0.30, 0.10, 0.08, 0.05, 0.02]
    
    data = {
        'Timestamp': pd.date_range(start='2024-01-01', periods=n, freq='min'),
        'Line_ID': np.random.choice(['Line-A', 'Line-B', 'Line-C'], n),
        'Product_Batch': [f'BATCH-{i:03d}' for i in np.random.randint(100, 110, n)],
        'Defect_Category': np.random.choice(defects, size=n, p=weights),
        'AI_Confidence': np.random.uniform(0.85, 0.99, n)
    }
    df = pd.DataFrame(data)
    df.to_csv('defect_data.csv', index=False)
    return df

def calculate_pareto(df):
    """Calculate Pareto analysis data based on defect categories."""
    # Count frequencies
    counts = df['Defect_Category'].value_counts().reset_index()
    counts.columns = ['Defect_Category', 'Count']
    counts = counts.sort_values(by='Count', ascending=False)
    
    # Calculate Cumulative Percentage
    counts['Cumulative_Percentage'] = counts['Count'].cumsum() / counts['Count'].sum() * 100
    return counts