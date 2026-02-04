import os
from datetime import datetime

import pandas as pd
import streamlit as st

from kg_extractor.extractor import run_pipeline
from kg_extractor.llm_client import LlmClient
from kg_extractor.storage import TripleStore, triples_to_dicts
from kg_extractor.web_loader import fetch_main_text


MAX_CHARS = 12000

st.set_page_config(page_title="KG Triple Extractor", layout="wide")

st.title("网页文本三元组抽取 Demo")
st.write(
    "输入网页 URL，系统会抓取网页主要文本并利用 LLM 抽取三元组。"
    "抽取流程包含【多轮核实】与【原文确认】。"
)

with st.sidebar:
    st.header("配置")
    api_key = st.text_input("NVIDIA API Key", type="password", value=os.getenv("NVIDIA_API_KEY", ""))
    base_url = st.text_input(
        "Base URL", value=os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    )
    model = st.text_input("Model", value=os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct"))
    max_chars = st.number_input("最大文本长度", min_value=2000, max_value=50000, value=MAX_CHARS, step=1000)

url = st.text_input("网页地址")

if st.button("开始抽取", type="primary", disabled=not url):
    if not api_key:
        st.error("请先在左侧填写 NVIDIA API Key。")
    else:
        with st.spinner("正在抓取网页内容..."):
            text, _ = fetch_main_text(url)
        if not text:
            st.error("未能解析到网页文本内容。")
        else:
            trimmed_text = text[: int(max_chars)]
            st.subheader("文本预览")
            st.text_area("", trimmed_text, height=200)

            with st.spinner("正在调用 LLM 抽取三元组..."):
                client = LlmClient(api_key=api_key, base_url=base_url, model=model)
                triples = run_pipeline(client, trimmed_text)

            if not triples:
                st.warning("未抽取到有效三元组。")
            else:
                store = TripleStore()
                inserted = store.insert_triples(triples, url)
                st.success(f"已写入数据库 {inserted} 条三元组。")

                df = pd.DataFrame(triples_to_dicts(triples))
                st.subheader("抽取结果")
                st.dataframe(df, use_container_width=True)

st.divider()

store = TripleStore()
all_rows = store.fetch_triples()
if all_rows:
    st.subheader("历史抽取记录")
    history_df = pd.DataFrame(all_rows)
    st.dataframe(history_df, use_container_width=True)

    csv_path = "data/export.csv"
    store.export_csv(csv_path)
    with open(csv_path, "rb") as handle:
        st.download_button(
            label="下载 CSV",
            data=handle,
            file_name=f"kg_triples_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
