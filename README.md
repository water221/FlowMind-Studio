
# 🌊 FlowMind Studio

**一个基于 LangGraph 的多模态、多 Agent 自动化媒体创作集群 (集成于飞书平台)**

[![LangGraph](https://img.shields.io/badge/LangGraph-State_Machine-blue)](#)
[![Multimodal](https://img.shields.io/badge/AI-Multimodal_Agents-orange)](#)
[![Feishu](https://img.shields.io/badge/Integration-Feishu_Bot-00D6B9)](#)

FlowMind Studio 是一个端到端的智能内容工坊。通过在飞书输入简单的灵感文字、参考图片或热点链接，系统底层的多个 AI Agent 将进行自主拆解、多模态信息提取、文案创作、视觉 API 调度（图像/视频生成）以及严格的质量回溯审查，最终向用户交付可直接发布的图文笔记或短视频物料。

## ✨ 核心亮点 (Key Features)

* **🧠 复杂状态机编排 (LangGraph)**：摒弃了传统的线性单一 Chain 结构，采用 LangGraph 构建具有**非线性路由**和**条件回溯 (Backtracking)** 能力的 Agent 协作网络。
* **🤝 多 Agent 角色协同**：
  * **Analyst (感知器)**：融合解析多模态输入（图/文/外部链接），输出结构化 Brief。
  * **Copywriter (主笔)**：跨平台文案创作与多模态 Prompt 拆解。
  * **Generator (生成器)**：精准调度 DALL-E 3 / 视频生成等商业 API 进行视觉物料渲染。
  * **Editor (主编)**：自动化多模态内容对齐审查，不合格自动打回重做。
* **👁️ 多模态 I/O**：原生支持 Vision 大模型与复杂的函数调用 (Function Calling)，实现全链路的“多模态进，多模态出”。
* **💬 飞书原生集成**：无需打开网页，在飞书对话框内完成所有交互与文件接收。

## 🎬 效果演示 (Demo)

*(此处预留给你的飞书操作录屏 GIF 或视频链接，展示从输入一句话到输出成套图文/视频的完整过程)*

## 🏗️ 系统架构 (Architecture)

系统通过一个核心的 `StudioState` 字典在不同节点间传递上下文。当且仅当 Editor Agent 评估生成的图文/视频与初始输入意图完美对齐时，工作流才会结束并推送到客户端。

```text
[用户输入: 图/文/链接] 
       │ (Webhook)
       ▼
[Agent A: 意图解析] ──► [Agent B: 文案与分镜] ──► [Agent C: 多模态生成]
                               ▲                           │
                               │      [不合格，打回重做]        ▼
                               └───────────────────── [Agent D: 质量审核]
                                                           │ (通过)
                                                           ▼
                                                [输出物料推送到飞书]

# 🚀 快速开始 (Quick Start)
## 环境依赖
- Python 3.10+
- 推荐使用虚拟环境进行安装：

```Bash
git clone [https://github.com/water221/FlowMind-Studio.git](https://github.com/water221/FlowMind-Studio.git)
cd FlowMind-Studio
pip install -r requirements.txt
```
## 环境变量配置
在根目录创建 .env 文件，并配置以下必要的 API Keys：
```bash
代码段
OPENAI_API_KEY=sk-xxxxxx
FEISHU_APP_ID=cli_xxxxxx
FEISHU_APP_SECRET=xxxxxx
# 如果使用其他视频或视觉生成 API，在此补充
```

## 运行服务
```
Bash
python main.py
(详细的飞书事件订阅配置请参考 docs/feishu_setup.md)
```

👨‍💻 作者与联系方式 (Author)
开发者: 非鱼 (Fei Yu)

技术探讨 & 更多 AI 干货: 欢迎关注，获取本项目的深度解析与最新更新。

If you find this project helpful, please give it a ⭐️!
