import csv
import sqlite3
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from kg_extractor.extractor import Triple


class TripleStore:
    def __init__(self, db_path: str = "data/kg_triples.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS triples (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    head TEXT NOT NULL,
                    relation TEXT NOT NULL,
                    tail TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    url TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def insert_triples(self, triples: Iterable[Triple], url: str) -> int:
        rows = [
            (
                triple.head,
                triple.relation,
                triple.tail,
                triple.evidence,
                url,
                datetime.utcnow().isoformat(),
            )
            for triple in triples
        ]
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                """
                INSERT INTO triples (head, relation, tail, evidence, url, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )
            conn.commit()
        return len(rows)

    def fetch_triples(self) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT head, relation, tail, evidence, url, created_at FROM triples ORDER BY id DESC"
            )
            return [
                {
                    "head": row[0],
                    "relation": row[1],
                    "tail": row[2],
                    "evidence": row[3],
                    "url": row[4],
                    "timestamp": row[5],
                }
                for row in cursor.fetchall()
            ]

    def export_csv(self, path: str) -> None:
        rows = self.fetch_triples()
        with open(path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["head", "relation", "tail", "evidence", "url", "timestamp"]
            )
            writer.writeheader()
            writer.writerows(rows)


def triples_to_dicts(triples: Iterable[Triple]) -> List[dict]:
    return [asdict(triple) for triple in triples]
