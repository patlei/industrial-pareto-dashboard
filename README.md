# 🚀 工业产线缺陷智能归因看板 (Industrial AI Pareto Dashboard)

本项目是针对 **AI Native 候选人笔试题** 开发的 MVP（最小可行性产品）。它通过结合传统的帕累托分析（Pareto Analysis 与 **DeepSeek 大语言模型**，实现了从底层数据采集到高层决策建议的自动化闭环。

---

## 📖 项目背景
在工业视觉检测（SVI）场景中，产线每天产生海量缺陷数据。质量主管（QA）面临的痛点是：
1. **数据淹没**：难以从成千上万条记录中快速定位核心矛盾。
2. **知识断层**：非资深员工难以根据数据直接给出工艺改进建议。

本工具通过 **80/20 法则** 自动提取头部缺陷，并调用 **DeepSeek AI 专家系统** 进行工业级的根因归因与对策建议。

---

## ✨ 核心功能
* **自动化数据处理**：基于 Pandas 实现 1000+ 条检测记录的实时统计。
* **标准帕累托可视化**：双坐标轴看板，动态标注 80% 决策基准线。
* **LLM Data-to-Text**：将结构化统计数据转化为非结构化的《质量改善建议书》。
* **DeepSeek 深度集成**：采用“资深工艺工程师”角色建模，提供人机料法环（5M1E）维度的专业分析。
* **跨平台兼容**：自适应 Windows/Mac/Linux 的中文字体渲染方案。

---

## 🛠️ 技术栈
* **开发语言**：Python 3.9+
* **前端框架**：Streamlit (用于快速构建数据 Web 应用)
* **数据分析**：Pandas, NumPy
* **可视化**：Matplotlib (定制化 Pareto Chart)
* **大模型 API**：DeepSeek (OpenAI SDK 兼容模式)

---

## 🚀 快速启动

### 1. 克隆项目与环境准备
```bash
# 创建并激活虚拟环境
python -m venv venv
source venv/bin/activate  # Windows 使用 .\venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key
在项目根目录下创建 `.env` 文件，并填入您的 DeepSeek Key：
```text
DEEPSEEK_API_KEY=your_sk_key_here
```

### 3. 运行应用
```bash
streamlit run app.py
```

---

## 🧠 AI 逻辑实现说明 (Prompt Engineering)
项目采用了**结构化 Prompt** 技术，强制 AI 遵循工业诊断逻辑：
1.  **角色设定**：20 年经验的质量专家。
2.  **动态上下文**：仅提取累计占比前 80% 的核心缺陷，避免噪声干扰。
3.  **思维链引导**：强制要求从“人、机、料、法、环”维度拆解，确保建议的可执行性。

---

## 📂 文件结构
* `app.py`: 主程序，负责 Streamlit UI 逻辑与 AI 调用。
* `data_utils.py`: 核心算法逻辑，包含模拟数据生成与帕累托计算。
* `defect_data.csv`: 自动生成的模拟缺陷数据集。
* `.env`: 环境变量配置（不进入版本控制）。

---

