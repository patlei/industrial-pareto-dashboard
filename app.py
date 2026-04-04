import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform
import os
from openai import OpenAI
from dotenv import load_dotenv
from data_utils import generate_mock_data, calculate_pareto

# 加载环境变量 (用于读取 .env 中的 API Key)
load_dotenv()

# ==========================================
# 🛑 核心配置：图表字体与 AI 客户端
# ==========================================
def set_matplot_font():
    """设置标准英文无衬线字体，确保 Linux/Streamlit Cloud 部署不乱码"""
    plt.rcParams['axes.unicode_minus'] = False 
    # 使用通用的 Arial 或 sans-serif，英文环境下完美支持
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']

# 执行配置
set_matplot_font()

# 初始化 DeepSeek 客户端 (兼容环境变量与 Streamlit Secrets)
api_key = os.getenv("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# ==========================================
# 🤖 AI 归因分析逻辑
# ==========================================
def get_ai_analysis(pareto_df):
    """提取头部缺陷并调用 DeepSeek 生成专家建议"""
    # 提取累计占比 85% 以下的核心缺陷
    core_issues = pareto_df[pareto_df['Cumulative_Percentage'] <= 85]
    issues_list = core_issues['Defect_Category'].tolist()
    data_summary = core_issues.to_string(index=False)

    prompt = f"""
    You are a senior industrial quality expert with 20 years of experience.
    
    【Data Summary】
    Top defects accounting for ~80% of issues:
    {data_summary}
    
    【Task】
    Based on the core issues ({', '.join(issues_list)}), please write a "Quality Improvement Proposal" as a senior engineer.
    
    【Requirements】
    1. Root Cause Analysis: Hypothesize causes using 5M1E (Man, Machine, Material, Method, Measurement, Environment).
    2. Action Plan: Provide 3-4 executable corrective actions.
    3. Prevention: Suggest long-term SOP or maintenance strategies.
    
    Please provide the report in Professional Chinese (简体中文) as the final audience is the local factory management, but use professional industrial terminology. Format in Markdown.
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a professional industrial quality engineer."},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI Analysis Failed: {str(e)}"

# ==========================================
# 🌐 Streamlit 界面布局
# ==========================================
st.set_page_config(page_title="Industrial Defect Intelligence Dashboard", layout="wide", page_icon="📊")

st.title("📊 Pareto Analysis & AI-Powered Root Cause Dashboard")
st.caption("Data-driven insights powered by Python & DeepSeek AI Expert System")

# 1. 数据准备
with st.sidebar:
    st.header("Control Panel")
    if st.button("🔄 Reset/Generate Data", use_container_width=True):
        df = generate_mock_data()
        st.success("Successfully generated 1000 records")
    else:
        try:
            df = pd.read_csv('defect_data.csv')
        except:
            df = generate_mock_data()
    
    st.info("Source: Real-time visual inspection system records.")

# 2. 核心逻辑：帕累托计算
pareto_df = calculate_pareto(df)

# 3. 可视化展示区域
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Pareto Chart (Statistical Insight)")
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # 画柱状图 (Defect Count)
    bars = ax1.bar(pareto_df['Defect_Category'], pareto_df['Count'], color='#1f77b4', alpha=0.8)
    ax1.set_ylabel('Defect Count', fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    # 画累计百分比折线 (Cumulative Percentage)
    ax2 = ax1.twinx()
    ax2.plot(pareto_df['Defect_Category'], pareto_df['Cumulative_Percentage'], color='#d62728', marker='D', ms=5, linewidth=2)
    ax2.set_ylabel('Cumulative Percentage (%)', fontsize=10)
    ax2.set_ylim(0, 110)
    
    # 画 80% 决策基准线
    ax2.axhline(80, color='#ff7f0e', linestyle='--', label='80% Threshold')
    
    # 自动标注数值
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 3, f'{int(height)}', ha='center', va='bottom')

    st.pyplot(fig)

with col2:
    st.subheader("Data Details")
    # 格式化百分比显示
    display_df = pareto_df.copy()
    display_df['Cumulative_Percentage'] = display_df['Cumulative_Percentage'].map('{:.2f}%'.format)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# 4. LLM 智能归因分析区域
st.divider()
st.subheader("🤖 AI Expert Diagnostic Insights")

if st.button("🚀 Run DeepSeek Root Cause Analysis", type="primary"):
    if not api_key:
        st.error("API Key not found! Please check .env or Streamlit Secrets.")
    else:
        with st.spinner("Expert AI is analyzing patterns and retrieving industrial knowledge..."):
            analysis_text = get_ai_analysis(pareto_df)
            
            with st.container(border=True):
                st.markdown(analysis_text)
                
                # 提供下载功能
                st.download_button(
                    label="📥 Download Improvement Proposal",
                    data=analysis_text,
                    file_name="Quality_Improvement_Proposal.md",
                    mime="text/markdown"
                )

st.markdown("---")
st.caption("Industrial AI Digital Dashboard MVP - Candidate Demo")