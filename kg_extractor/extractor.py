import json
from dataclasses import dataclass
from typing import List

from kg_extractor.llm_client import LlmClient


@dataclass
class Triple:
    head: str
    relation: str
    tail: str
    evidence: str


SYSTEM_INSTRUCTIONS = (
    "你是一个知识图谱抽取助手。输出必须是严格的JSON。"
)


def _parse_triples(raw: str) -> List[Triple]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError(f"LLM did not return valid JSON: {raw}")

    if isinstance(payload, dict):
        items = payload.get("triples", [])
    elif isinstance(payload, list):
        items = payload
    else:
        raise ValueError("Unexpected JSON structure from LLM.")

    triples = []
    for item in items:
        head = str(item.get("head", "")).strip()
        relation = str(item.get("relation", "")).strip()
        tail = str(item.get("tail", "")).strip()
        evidence = str(item.get("evidence", "")).strip()
        if head and relation and tail and evidence:
            triples.append(Triple(head=head, relation=relation, tail=tail, evidence=evidence))
    return triples


def extract_triples(client: LlmClient, text: str) -> List[Triple]:
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {
            "role": "user",
            "content": (
                "请从下面的网页文本中抽取知识图谱三元组。"
                "输出JSON数组，每个元素包含head, relation, tail, evidence(原文句子)。"
                "不要翻译原文，证据句子必须来自原文。\n\n"
                f"网页文本:\n{text}"
            ),
        },
    ]
    raw = client.chat(messages)
    return _parse_triples(raw)


def verify_triples(client: LlmClient, text: str, triples: List[Triple]) -> List[Triple]:
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {
            "role": "user",
            "content": (
                "你是【多轮核实】角色，请检查三元组的质量。"
                "头实体和尾实体必须是具体实体节点，关系清晰明确。"
                "如果不满足，删除该三元组或修正为更明确的实体关系。"
                "输出严格JSON数组，字段: head, relation, tail, evidence。\n\n"
                f"网页文本:\n{text}\n\n"
                f"待核实三元组JSON:\n{json.dumps([t.__dict__ for t in triples], ensure_ascii=False)}"
            ),
        },
    ]
    raw = client.chat(messages)
    return _parse_triples(raw)


def confirm_triples(client: LlmClient, text: str, triples: List[Triple]) -> List[Triple]:
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTIONS},
        {
            "role": "user",
            "content": (
                "你是【原文确认】角色，作为严格事实核查员。"
                "仅保留与原文表达一致的三元组，确保证据句子在原文中。"
                "若不一致则删除。输出严格JSON数组，字段: head, relation, tail, evidence。\n\n"
                f"网页文本:\n{text}\n\n"
                f"待确认三元组JSON:\n{json.dumps([t.__dict__ for t in triples], ensure_ascii=False)}"
            ),
        },
    ]
    raw = client.chat(messages)
    return _parse_triples(raw)


def run_pipeline(client: LlmClient, text: str) -> List[Triple]:
    initial = extract_triples(client, text)
    verified = verify_triples(client, text, initial)
    confirmed = confirm_triples(client, text, verified)
    return confirmed
