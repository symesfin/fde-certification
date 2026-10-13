"""A vector store that is a numpy array and a JSON file.

Tier 2. Needs numpy.

There is a strong instinct to reach for Chroma or Qdrant here. For the corpus
sizes in this course — and for most enterprise use cases, which are far smaller
than people assume — a normalised matrix and `M @ q` is faster, has no server,
no index to keep in sync with your source of truth, and no dependency to get
approved.

The honest boundary: a flat scan is linear in corpus size. At a few tens of
thousands of chunks it is still sub-millisecond. Past roughly a million you want
an approximate index, and at that point the two things you lose here — a real
ANN structure and someone else operating it — start to be worth paying for.

Until then, this is not a toy. It is the correct choice.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


@dataclass
class Hit:
    score: float
    text: str
    metadata: dict

    @property
    def source(self) -> str:
        return self.metadata.get("source", "?")


class VectorStore:
    """Persisted flat store: vectors in .npy, records in .jsonl.

        store = VectorStore("index")
        store.add(vectors, chunks)          # chunks are dicts with "text"
        store.save()
        hits = store.search(query_vector, k=3)

    Vectors are assumed L2-normalised (helpers.embeddings does this), so the
    dot product is cosine similarity.
    """

    def __init__(self, path: str | Path | None = None):
        import numpy as np

        self.path = Path(path) if path else None
        self.vectors = np.zeros((0, 0), dtype="float32")
        self.records: list[dict] = []
        if self.path and (self.path.with_suffix(".npy")).exists():
            self.load()

    def __len__(self) -> int:
        return len(self.records)

    def add(self, vectors, records: Sequence[dict]) -> None:
        import numpy as np

        vectors = np.asarray(vectors, dtype="float32")
        if len(vectors) != len(records):
            raise ValueError(
                f"{len(vectors)} vectors but {len(records)} records — these must "
                f"line up, or your search results will cite the wrong document"
            )
        if self.vectors.size and vectors.shape[1] != self.vectors.shape[1]:
            raise ValueError(
                f"dimension mismatch: store holds {self.vectors.shape[1]}-dim "
                f"vectors, got {vectors.shape[1]}. Different embedding model?"
            )
        self.vectors = vectors if not self.vectors.size else np.vstack([self.vectors, vectors])
        self.records.extend(dict(record) for record in records)

    def search(self, query_vector, k: int = 3, *, where: dict | None = None) -> list[Hit]:
        """Top-k by cosine. `where` filters on record metadata BEFORE ranking.

        Filtering before ranking is not a detail. If your corpus spans access
        levels, filtering *after* retrieval leaks — the fact that a document
        matched is itself information. See Week 9.
        """
        import numpy as np

        if not len(self):
            return []
        query = np.asarray(query_vector, dtype="float32").ravel()
        scores = self.vectors @ query

        allowed = np.ones(len(self.records), dtype=bool)
        if where:
            for key, value in where.items():
                wanted = set(value) if isinstance(value, (list, set, tuple)) else {value}
                allowed &= np.array(
                    [record.get(key) in wanted for record in self.records], dtype=bool
                )
            scores = np.where(allowed, scores, -np.inf)

        order = np.argsort(-scores)[:k]
        return [
            Hit(float(scores[index]), self.records[index].get("text", ""), self.records[index])
            for index in order
            if np.isfinite(scores[index])
        ]

    def save(self, path: str | Path | None = None) -> Path:
        import numpy as np

        target = Path(path) if path else self.path
        if target is None:
            raise ValueError("no path given and none set on the store")
        target.parent.mkdir(parents=True, exist_ok=True)
        np.save(target.with_suffix(".npy"), self.vectors)
        target.with_suffix(".jsonl").write_text(
            "\n".join(json.dumps(record, ensure_ascii=False) for record in self.records) + "\n",
            encoding="utf-8",
        )
        self.path = target
        return target

    def load(self, path: str | Path | None = None) -> "VectorStore":
        import numpy as np

        target = Path(path) if path else self.path
        self.vectors = np.load(target.with_suffix(".npy"))
        text = target.with_suffix(".jsonl").read_text(encoding="utf-8")
        self.records = [json.loads(line) for line in text.splitlines() if line.strip()]
        if len(self.vectors) != len(self.records):
            raise ValueError(
                f"corrupt store at {target}: {len(self.vectors)} vectors, "
                f"{len(self.records)} records"
            )
        self.path = target
        return self
