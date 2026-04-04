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
# 🛑 核心配置：中文字体与 AI 客户端
# ==========================================
def set_matplot_zh_font():
    """根据操作系统自动设置 Matplotlib 的中文字体，解决方块乱码问题"""
    sys_type = platform.system()
    plt.rcParams['axes.unicode_minus'] = False 
    if sys_type == "Windows":
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
    elif sys_type == "Darwin": # Mac
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'DejaVu Sans']
    else: # Linux
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']

# 初始化配置
set_matplot_zh_font()

# 初始化 DeepSeek 客户端 (兼容 OpenAI 格式)
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
    # 提取累计占比 85% 以下的缺陷作为核心矛盾
    core_issues = pareto_df[pareto_df['累计百分比'] <= 85]
    issues_list = core_issues['缺陷类别'].tolist()
    data_summary = core_issues.to_string(index=False)

    prompt = f"""
    你是一位拥有20年经验的工业质量管理专家，擅长通过帕累托分析进行根因定位。
    
    【现场数据统计】
    以下是占据当前产线 80% 以上问题的核心缺陷数据：
    {data_summary}
    
    【任务】
    请针对核心缺陷（{', '.join(issues_list)}），以资深工艺工程师的口吻撰写一份《产线质量改善建议书》。
    
    【输出要求】
    1. 根因分析：请从“人、机、料、法、环”维度进行专业推测。
    2. 改善行动：给出 3-4 条可立即在车间执行的具体措施。
    3. 预防机制：提出长期的标准化（SOP）或设备维护建议。
    
    请使用专业、简洁的工业术语，以 Markdown 格式输出。
    """

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一位专业的工业质量工程师，回复直接切入主题，不使用废话。"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ AI 分析调用失败: {str(e)}"

# ==========================================
# 🌐 Streamlit 界面布局
# ==========================================
st.set_page_config(page_title="产线缺陷智能归因看板", layout="wide", page_icon="📊")

st.title("📊 产线缺陷帕累托分析与大模型智能归因")
st.caption("基于 Python 数据分析与 DeepSeek AI 专家系统")

# 1. 数据准备
with st.sidebar:
    st.header("控制面板")
    if st.button("🔄 生成/重置模拟数据", use_container_width=True):
        df = generate_mock_data()
        st.success("成功生成 1000 条缺陷记录")
    else:
        try:
            df = pd.read_csv('defect_data.csv')
        except:
            df = generate_mock_data()
    
    st.info("数据说明：模拟实时视觉检测系统抓取的产线缺陷记录。")

# 2. 核心逻辑：帕累托计算
pareto_df = calculate_pareto(df)

# 3. 可视化展示区域
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("帕累托分析图 (Pareto Chart)")
    fig, ax1 = plt.subplots(figsize=(10, 5))
    
    # 画柱状图 (数量)
    bars = ax1.bar(pareto_df['缺陷类别'], pareto_df['数量'], color='#1f77b4', alpha=0.8)
    ax1.set_ylabel('缺陷频数 (次)', fontsize=10)
    ax1.grid(axis='y', linestyle='--', alpha=0.6)
    
    # 画累计百分比折线
    ax2 = ax1.twinx()
    ax2.plot(pareto_df['缺陷类别'], pareto_df['累计百分比'], color='#d62728', marker='D', ms=5, linewidth=2)
    ax2.set_ylabel('累计贡献率 (%)', fontsize=10)
    ax2.set_ylim(0, 110)
    
    # 画 80% 决策基准线
    ax2.axhline(80, color='#ff7f0e', linestyle='--', label='80% 阈值线')
    
    # 自动标注数值
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 3, f'{int(height)}', ha='center', va='bottom')

    st.pyplot(fig)

with col2:
    st.subheader("数据统计明细")
    # 格式化百分比显示
    display_df = pareto_df.copy()
    display_df['累计百分比'] = display_df['累计百分比'].map('{:.2f}%'.format)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

# 4. LLM 智能归因分析区域
st.divider()
st.subheader("🤖 AI 专家智能诊断建议")

# 获取当前头部缺陷列表
head_defects = pareto_df[pareto_df['累计百分比'] <= 85]['缺陷类别'].tolist()

if st.button("🚀 启动 DeepSeek 专家级归因分析", type="primary"):
    if not api_key:
        st.error("未检测到 API Key，请检查 .env 文件！")
    else:
        with st.spinner("AI 专家正在调取历史工艺库并分析当前趋势..."):
            analysis_text = get_ai_analysis(pareto_df)
            
            with st.container(border=True):
                st.markdown(analysis_text)
                
                # 提供下载功能
                st.download_button(
                    label="📥 下载改善建议书",
                    data=analysis_text,
                    file_name="质量改善建议书.md",
                    mime="text/markdown"
                )


st.markdown("---")
st.caption("工业 AI 数字化看板 MVP")