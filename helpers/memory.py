"""Agent memory on SQLite, with the two things that break it in production.

Tier 2 by convention. Standard library only — `sqlite3` ships with Python, which
is most of why this is the right default.

Week 7 Session 1 builds this store from scratch and makes the argument for
stopping at SQLite rather than reaching for a vector database. This is that store
as an application would run it, with three differences that only show up once
something has been writing to it for a month.

**The FTS index does not watch its table.** `content='memories'` makes the FTS5
table external-content: it holds an index, not the text, and nothing keeps the
two in sync except triggers. With only an INSERT trigger — which is what most
examples on the internet show — editing a memory leaves it findable by text it no
longer contains and unfindable by the text it does. SQLite's own
`integrity-check` passes, because it validates the index against itself.

**Memory grows without limit.** An agent that remembers everything eventually
recalls nothing useful and costs a fortune doing it. `prune()` is not an
optimisation; it is the difference between a memory system and a leak.

**Recall goes into a prompt, and prompts have budgets.** `limit=5` bounds the
number of rows, not their size. Five long memories can be more text than the
question they were meant to inform, and the failure is a context-length error in
production rather than anything you saw in testing.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from typing import Sequence

SCHEMA = """
CREATE TABLE IF NOT EXISTS memories (
    id       INTEGER PRIMARY KEY,
    kind     TEXT NOT NULL,           -- semantic | procedural | episodic
    subject  TEXT,
    content  TEXT NOT NULL,
    created  REAL NOT NULL,
    accessed REAL                     -- last recall, for usage-based eviction
);
CREATE INDEX IF NOT EXISTS memories_kind ON memories(kind);

CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts
    USING fts5(content, subject, content='memories', content_rowid='id');

-- All three. The last two are the ones everyone forgets; without them the index
-- describes text that is no longer in the table and nothing tells you.
CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content, subject)
    VALUES (new.id, new.content, new.subject);
END;
CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content, subject)
    VALUES ('delete', old.id, old.content, old.subject);
END;
CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content, subject)
    VALUES ('delete', old.id, old.content, old.subject);
    INSERT INTO memories_fts(rowid, content, subject)
    VALUES (new.id, new.content, new.subject);
END;
"""


@dataclass
class Memory:
    id: int
    kind: str
    subject: str
    content: str
    created: float


class MemoryStore:
    """One table, one FTS index, three triggers.

        store = MemoryStore("agent.db")
        store.remember("semantic", "The user's team is Revenue Systems.", "user.team")
        store.recall("which team", budget_chars=2000)
    """

    def __init__(self, path: str = ":memory:"):
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)

    # -- writing -----------------------------------------------------------

    def remember(self, kind: str, content: str, subject: str = "") -> int:
        cur = self.db.execute(
            "INSERT INTO memories (kind, subject, content, created) VALUES (?,?,?,?)",
            (kind, subject, content, time.time()),
        )
        self.db.commit()
        return cur.lastrowid

    def update(self, memory_id: int, content: str) -> None:
        """Exists mainly to prove the UPDATE trigger works. A fact that changed
        is the single most common thing a memory system gets wrong."""
        self.db.execute("UPDATE memories SET content = ? WHERE id = ?", (content, memory_id))
        self.db.commit()

    def forget(self, memory_id: int) -> None:
        self.db.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        self.db.commit()

    # -- reading -----------------------------------------------------------

    def recall(self, query: str, *, kind: str | None = None, limit: int = 5,
               budget_chars: int | None = None) -> list[Memory]:
        """Full-text search, bounded by rows AND by characters.

        `budget_chars` is the one that matters in production. `limit` caps how
        many memories you get; it says nothing about how much text that is, and
        the thing downstream is a prompt with a finite context window.
        """
        terms = " OR ".join(f'"{word}"' for word in query.split() if len(word) > 2)
        if not terms:
            return []
        sql = ("SELECT m.id, m.kind, m.subject, m.content, m.created "
               "FROM memories_fts f JOIN memories m ON m.id = f.rowid "
               "WHERE memories_fts MATCH ?")
        params: list = [terms]
        if kind:
            sql += " AND m.kind = ?"
            params.append(kind)
        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        out, used = [], 0
        for row in self.db.execute(sql, params):
            memory = Memory(*row)
            if budget_chars is not None:
                if used + len(memory.content) > budget_chars:
                    break           # ranked order, so we drop the least relevant
                used += len(memory.content)
            out.append(memory)

        if out:
            self.db.execute(
                f"UPDATE memories SET accessed = ? WHERE id IN "
                f"({','.join('?' * len(out))})",
                [time.time(), *[memory.id for memory in out]],
            )
            self.db.commit()
        return out

    # -- keeping it bounded -------------------------------------------------

    def __len__(self) -> int:
        return self.db.execute("SELECT count(*) FROM memories").fetchone()[0]

    def prune(self, *, max_rows: int | None = None, older_than_days: float | None = None,
              kind: str | None = None) -> int:
        """Drop memories. Returns how many went.

        Deletes oldest-first by last access, falling back to creation — a fact
        recalled every day is worth more than one written yesterday and never
        read. Age alone would evict exactly the memories that are working.
        """
        removed = 0
        if older_than_days is not None:
            cutoff = time.time() - older_than_days * 86400
            sql = "DELETE FROM memories WHERE created < ?"
            params: list = [cutoff]
            if kind:
                sql += " AND kind = ?"
                params.append(kind)
            removed += self.db.execute(sql, params).rowcount

        if max_rows is not None and len(self) > max_rows:
            over = len(self) - max_rows
            removed += self.db.execute(
                "DELETE FROM memories WHERE id IN ("
                "  SELECT id FROM memories"
                # Never-read rows go first. Ordering on the timestamp alone
                # is not enough: time.time() ticks about every 15.6 ms on
                # Windows, so a burst of writes and a recall all share one
                # value, SQLite breaks the tie by rowid, and the oldest row
                # is evicted no matter how recently it was used -- which is
                # exactly the memory this function exists to keep.
                "  ORDER BY (accessed IS NULL) DESC,"
                "           COALESCE(accessed, created) ASC LIMIT ?)",
                (over,),
            ).rowcount

        self.db.commit()
        return removed

    def integrity(self) -> bool:
        """True if the FTS index still matches the table.

        Note what SQLite's own `integrity-check` does *not* do: it validates the
        index against itself and passes happily while the index describes rows
        that changed underneath it. This compares against the source, which is
        the check you actually wanted.
        """
        rows = self.db.execute("SELECT id, content FROM memories").fetchall()
        for memory_id, content in rows:
            terms = [word for word in content.split() if len(word) > 2][:1]
            if not terms:
                continue
            hit = self.db.execute(
                "SELECT 1 FROM memories_fts f WHERE f.rowid = ? AND memories_fts MATCH ?",
                (memory_id, f'"{terms[0]}"'),
            ).fetchone()
            if not hit:
                return False
        return True
