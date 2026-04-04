import pandas as pd
import numpy as np

def generate_mock_data(n=1000):
    """生成模拟的缺陷记录 CSV"""
    defects = ['划伤', '异物', '脏污', '漏装', '变形', '裂纹']
    # 模拟 80/20 分布：让前两个缺陷占约 75%
    weights = [0.45, 0.30, 0.10, 0.08, 0.05, 0.02]
    
    data = {
        '时间戳': pd.date_range(start='2024-01-01', periods=n, freq='min'),
        '产线编号': np.random.choice(['Line-A', 'Line-B', 'Line-C'], n),
        '产品批次': [f'BATCH-{i:03d}' for i in np.random.randint(100, 110, n)],
        '缺陷类别': np.random.choice(defects, size=n, p=weights),
        'AI置信度': np.random.uniform(0.85, 0.99, n)
    }
    df = pd.DataFrame(data)
    df.to_csv('defect_data.csv', index=False)
    return df

def calculate_pareto(df):
    """计算帕累托分析所需数据"""
    counts = df['缺陷类别'].value_counts().reset_index()
    counts.columns = ['缺陷类别', '数量']
    counts = counts.sort_values(by='数量', ascending=False)
    
    # 计算累计百分比
    counts['累计百分比'] = counts['数量'].cumsum() / counts['数量'].sum() * 100
    return counts