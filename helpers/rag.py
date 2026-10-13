"""Retrieval plumbing, so later weeks do not re-teach Week 3.

Tier 2. Import explicitly (`from helpers import rag`) and declare any heavy
dependencies in your notebook's PEP 723 block.

**These are not the lesson.** Week 3 builds chunking, embedding, and cosine
similarity from scratch, in the notebook, where you can read them. What lives
here is the finished version, so that Week 4's eval harness and Week 7's memory
work can import it instead of copying it.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from pathlib import Path


def load_corpus(directory: Path, pattern: str = "*.md") -> list[dict]:
    """Read a directory of documents into `{source, text}` records.

    Skips `README.md`, which in this repo describes a corpus rather than being
    part of one.
    """
    docs = []
    for path in sorted(directory.glob(pattern)):
        if path.name == "README.md":
            continue
        docs.append({"source": path.name, "text": path.read_text(encoding="utf-8")})
    return docs


def load_jsonl_corpus(path: Path, *, source_key: str = "title",
                      text_key: str = "text") -> list[dict]:
    """Read a JSONL corpus into the same `{source, text}` records.

    One JSON object per line. Use this when the corpus is a dataset rather than
    a directory of files -- which is the usual case once you are working from
    something you downloaded rather than something you wrote.

    Every other key on the line is preserved, so labels ride along with the
    document instead of living in a second file you have to keep in step.
    """
    docs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        docs.append({
            **record,
            "source": record[source_key],
            "text": record[text_key],
        })
    return docs


def chunk(text: str, size: int = 900, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks, preferring paragraph boundaries.

    Character-based rather than token-based: it is within a few percent for
    English prose and needs no tokenizer. Overlap exists so a sentence spanning
    a boundary is still retrievable from at least one chunk.
    """
    if size <= overlap:
        raise ValueError("size must exceed overlap")

    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = f"{current}\n\n{para}" if current else para
            continue
        if current:
            chunks.append(current)
        # A single paragraph longer than `size` gets split on its own.
        while len(para) > size:
            chunks.append(para[:size])
            para = para[size - overlap :]
        current = para

    if current:
        chunks.append(current)
    return chunks


def chunk_corpus(docs: Iterable[dict], **kwargs) -> list[dict]:
    """Chunk every document, keeping the source filename on each chunk.

    Provenance is not optional. A retrieved passage a user cannot trace back to
    a document is not evidence, it is a rumour.
    """
    out = []
    for doc in docs:
        for index, piece in enumerate(chunk(doc["text"], **kwargs)):
            out.append({"source": doc["source"], "index": index, "text": piece})
    return out


def format_docs(hits: Sequence[dict], *, max_chars: int | None = None) -> str:
    """Render retrieved chunks for a prompt, with their sources.

    Sources are included so the model can cite them and so a wrong answer can be
    traced to the passage that caused it.
    """
    blocks = []
    used = 0
    for hit in hits:
        block = f"[{hit['source']}]\n{hit['text']}"
        if max_chars is not None and used + len(block) > max_chars:
            break
        blocks.append(block)
        used += len(block)
    return "\n\n---\n\n".join(blocks)
