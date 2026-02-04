# 网页文本三元组抽取 Demo

本项目提供一个 Streamlit Demo：输入网页 URL，抓取网页主要文本，并通过 LLM 抽取知识图谱三元组，包含【多轮核实】与【原文确认】两步质量控制。数据会落地到 SQLite，支持 CSV 导出。

## 项目结构

```
kg_abstract/
├── app.py
├── kg_extractor/
│   ├── __init__.py
│   ├── extractor.py
│   ├── llm_client.py
│   ├── storage.py
│   └── web_loader.py
├── data/
│   └── kg_triples.db
└── requirements.txt
```

## 快速开始

1. 安装依赖

```bash
pip install -r requirements.txt
```

2. 设置 API Key（建议使用环境变量）

```bash
export NVIDIA_API_KEY="your-key"
export NVIDIA_BASE_URL="https://integrate.api.nvidia.com/v1"
export NVIDIA_MODEL="meta/llama-3.3-70b-instruct"
```

3. 启动应用

```bash
streamlit run app.py
```

## 功能说明

- **网页抓取与正文提取**：优先使用 `trafilatura` 提取正文，失败则回退到 `BeautifulSoup`。
- **三元组抽取流程**：
  1. 初次抽取三元组并保留证据句（原文）。
  2. 【多轮核实】检查实体与关系的明确性。
  3. 【原文确认】严格核查与原文一致性。
- **数据存储**：SQLite 表字段包含 `head`, `relation`, `tail`, `evidence`, `url`, `created_at`。
- **CSV 导出**：UI 内置导出按钮，下载当前数据库内容。
