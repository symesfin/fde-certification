"""Embedding a corpus, the way you would actually ship it.

Tier 2. Import explicitly and declare the heavy dependencies in your notebook's
PEP 723 block.

Week 3 Session 1 builds the naive version first — one call per chunk — because
you should see the shape before you see the machinery. This is what that turns
into once it has to survive a real corpus, an unreliable network, and a rerun
tomorrow morning:

    batching   one request per N texts instead of per text
    retries    transient failures are normal, not exceptional
    caching    never pay twice for text that has not changed
    fallback   a local model when there is no embedding API to call
    progress   because a 4,000-chunk run needs to show it is alive

None of it is clever. All of it is the difference between a notebook and
something you can leave running.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Literal, Sequence

Backend = Literal["api", "local", "auto"]


# --------------------------------------------------------------------- cache


class _Cache:
    """Content-addressed, on disk. The key is (model, text) so switching models
    never silently reuses the wrong vectors — which is a genuinely nasty bug,
    because nothing errors and retrieval just quietly gets worse.
    """

    def __init__(self, directory: Path | None):
        self.dir = Path(directory) if directory else None
        if self.dir:
            self.dir.mkdir(parents=True, exist_ok=True)

    def _key(self, model: str, text: str) -> str:
        return hashlib.sha256(f"{model}\x00{text}".encode()).hexdigest()[:32]

    def get(self, model: str, text: str):
        if not self.dir:
            return None
        import numpy as np

        path = self.dir / f"{self._key(model, text)}.npy"
        try:
            return np.load(path) if path.exists() else None
        except Exception:
            return None      # a corrupt cache entry is a miss, never a crash

    def put(self, model: str, text: str, vector) -> None:
        if not self.dir:
            return
        import numpy as np

        tmp = self.dir / f".{self._key(model, text)}.tmp.npy"
        np.save(tmp, vector)
        tmp.replace(self.dir / f"{self._key(model, text)}.npy")   # atomic


# ------------------------------------------------------------------ embedder


def _unreachable(exc: Exception) -> bool:
    """Is this "the server is not there", as opposed to "the server said no"?

    A 4xx/5xx means something answered. A connection error, a DNS failure, or a
    refused socket means nothing did -- and only the second is worth falling back
    for, because a 401 will fail on the local model too.
    """
    text = f"{type(exc).__name__} {exc}".lower()
    return any(marker in text for marker in (
        "connection error", "connection refused", "connectionerror",
        "name or service not known", "failed to establish", "max retries exceeded",
        "apiconnectionerror", "nodename nor servname",
    ))


def _serves_chat_not_embeddings(exc: Exception) -> bool:
    """Did a reachable server tell us it does not do embeddings at all?

    This is a common and confusing shape: one endpoint serves chat, lists an
    embedding model in `/v1/models`, and returns 501 the moment you ask it to
    embed anything -- llama.cpp does exactly this unless started with
    `--embeddings`. The model appearing in the list is not a promise.

    Unlike a 401 or a 400, no retry and no correction on our side fixes it, and
    unlike those it is *not* a reason to stop: a local model can genuinely stand
    in. So it falls back rather than failing, and says why.
    """
    text = f"{type(exc).__name__} {exc}".lower()
    if getattr(exc, "status_code", None) == 501 or " 501 " in f" {text} ":
        return True
    return "does not support embeddings" in text or "not_supported_error" in text


@dataclass
class EmbedStats:
    """What actually happened. Report these — they are the numbers people ask about."""

    texts: int = 0
    cached: int = 0
    requested: int = 0
    batches: int = 0
    retries: int = 0
    seconds: float = 0.0
    fell_back: bool = False

    def __str__(self) -> str:
        hit = self.cached / self.texts if self.texts else 0
        rate = self.texts / self.seconds if self.seconds else 0
        return (
            f"{self.texts} texts in {self.seconds:.1f}s ({rate:.1f}/s) · "
            f"{self.batches} batches · {hit:.0%} cache hit · {self.retries} retries"
            + (" · FELL BACK to the local model" if self.fell_back else "")
        )


class Embedder:
    """One object that turns a list of strings into a matrix, and keeps working.

        emb = Embedder(CFG, cache_dir=".embed_cache")
        vectors = emb.embed(texts)          # (n, dim), L2-normalised
        print(emb.stats)

    `backend="auto"` uses the API when one is configured and falls back to a
    local sentence-transformers model when it is not — so a student with no
    embedding endpoint is never blocked.
    """

    def __init__(
        self,
        cfg,
        *,
        backend: Backend = "auto",
        batch_size: int = 32,
        cache_dir: str | Path | None = None,
        max_retries: int = 4,
        timeout: float = 600.0,
        local_model: str = "BAAI/bge-small-en-v1.5",
        allow_local_fallback: bool = True,
    ):
        self.cfg = cfg
        self.batch_size = max(1, batch_size)
        self.max_retries = max_retries
        # Explicit, because the failure it prevents is expensive and confusing.
        # A batch that outruns the client timeout is cancelled server-side, the
        # completed work is discarded, and the retry re-sends the *same* batch to
        # fail identically. `batch_size` is bounded above by roughly
        # `timeout / per-item cost`, and that bound moves when documents get
        # longer — see Week 3 Session 1.
        self.timeout = timeout
        self.local_model = local_model
        self.allow_local_fallback = allow_local_fallback
        self.backend = self._resolve(backend)
        self.model_id = cfg.embed_model if self.backend == "api" else local_model
        self.cache = _Cache(cache_dir)
        self.stats = EmbedStats()
        self._local = None

    def _resolve(self, backend: Backend) -> str:
        if backend != "auto":
            return backend
        # An API is "configured" if we have somewhere to send the request.
        if getattr(self.cfg, "embed_api_base", None) or os.getenv("OPENAI_API_KEY"):
            return "api"
        return "local"

    # -- backends ----------------------------------------------------------

    def _embed_api(self, batch: Sequence[str]):
        import numpy as np
        from litellm import embedding

        response = embedding(
            **self.cfg.embed_kwargs(), input=list(batch), timeout=self.timeout
        )
        # Providers are not required to preserve order; index is authoritative.
        rows = sorted(response.data, key=lambda item: item.get("index", 0))
        return np.array([row["embedding"] for row in rows], dtype=np.float32)

    def _embed_local(self, batch: Sequence[str]):
        import numpy as np

        if self._local is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ModuleNotFoundError:
                raise ModuleNotFoundError(
                    "No embedding API is configured and sentence-transformers is "
                    "not installed. Either set EMBED_API_BASE in .env, or:\n"
                    "    uv sync --group local"
                ) from None
            self._local = SentenceTransformer(self.local_model)
        return np.asarray(
            self._local.encode(list(batch), batch_size=self.batch_size),
            dtype=np.float32,
        )

    def _call_with_retry(self, batch: Sequence[str]):
        """Transient failures are normal. Back off, then give up loudly.

        Keeps its own loop rather than calling `llm.with_retry` because the
        message it raises is batch-specific, and that message is the whole
        value — but it shares `llm.is_retryable`, so a 400 fails immediately
        here for the same reason it does everywhere else.
        """
        from .llm import is_retryable

        delay = 1.0
        for attempt in range(self.max_retries):
            try:
                return (self._embed_api if self.backend == "api" else self._embed_local)(batch)
            except Exception as exc:
                # An endpoint that is *configured* is not an endpoint that is
                # *reachable*. `_resolve` cannot tell the difference -- it runs
                # before any request -- so a server that is down used to retry
                # three times and then fail the notebook. Fall back to the local
                # model instead: slower and smaller, but the session continues.
                no_embeddings = _serves_chat_not_embeddings(exc)
                if self.backend == "api" and self.allow_local_fallback and (
                    _unreachable(exc) or no_embeddings
                ):
                    self.backend = "local"
                    self.model_id = self.local_model
                    self.stats.fell_back = True
                    warnings.warn(
                        (
                            "Embedding endpoint answered, but does not serve "
                            "embeddings (501). A model listed in /v1/models is "
                            "not a promise that the endpoint is enabled — "
                            "llama.cpp needs `--embeddings`. "
                            if no_embeddings
                            else f"Embedding endpoint unreachable ({type(exc).__name__}). "
                        )
                        + f"Falling back to the local model {self.local_model!r}. "
                        f"Vectors from a different model are NOT comparable with "
                        f"any you embedded earlier -- re-embed the whole corpus, "
                        f"or fix the endpoint and re-run.",
                        RuntimeWarning,
                        stacklevel=2,
                    )
                    continue
                if not is_retryable(exc):
                    raise RuntimeError(
                        f"embedding failed permanently and was not retried "
                        f"({self.backend} backend, batch of {len(batch)}): {exc}\n\n"
                        f"Retrying will not help — check the model name, the "
                        f"credentials, and that the endpoint serves embeddings "
                        f"rather than only chat."
                    ) from exc
                if attempt == self.max_retries - 1:
                    # Retrying an oversized batch just fails the same way, slower.
                    # Say so, because the raw timeout error points nowhere useful.
                    hint = ""
                    # "timed out" is what LiteLLM actually says, and it carries
                    # status 408; matching only the word "timeout" meant the
                    # hint below never appeared for a real timeout.
                    error_text = f"{type(exc).__name__} {exc}".lower()
                    timed_out = (
                        getattr(exc, "status_code", None) == 408
                        or "timeout" in error_text
                        or "timed out" in error_text
                    )
                    if timed_out:
                        longest = max((len(text) for text in batch), default=0)
                        hint = (
                            f"\n\nThis looks like a timeout, not a broken endpoint. "
                            f"You sent {len(batch)} texts (longest {longest} chars) "
                            f"with timeout={self.timeout}s. Retrying the same batch "
                            f"cannot help. Lower batch_size until one request fits "
                            f"comfortably inside the timeout, or raise timeout=."
                        )
                    raise RuntimeError(
                        f"embedding failed after {self.max_retries} attempts "
                        f"({self.backend} backend, batch of {len(batch)}): {exc}{hint}"
                    ) from exc
                self.stats.retries += 1
                # Jitter: without it every client that failed against the
                # same endpoint retries in lockstep and arrives together.
                time.sleep(delay * (0.5 + random.random()))
                delay *= 2

    # -- the one method you call -------------------------------------------

    def embed(
        self,
        texts: Sequence[str],
        *,
        normalize: bool = True,
        progress: Callable[[int, int], None] | None = None,
    ):
        """Embed every text. Returns `(len(texts), dim)` float32.

        Normalised by default, because then a dot product *is* cosine similarity
        and every downstream search is one matrix multiply.
        """
        import numpy as np

        started = time.perf_counter()
        texts = list(texts)
        self.stats = EmbedStats(texts=len(texts))

        # An empty corpus is a caller bug upstream — an unfiltered glob, a
        # directory that moved. Return the right-shaped empty array rather than
        # letting np.vstack raise "need at least one array to concatenate",
        # which sends you looking in entirely the wrong place.
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)

        out: list = [None] * len(texts)

        # 1. Serve what we already have.
        pending: list[int] = []
        for index, text in enumerate(texts):
            hit = self.cache.get(self.model_id, text)
            if hit is not None:
                out[index] = hit
                self.stats.cached += 1
            else:
                pending.append(index)

        # 2. Batch the rest.
        for start in range(0, len(pending), self.batch_size):
            idx = pending[start : start + self.batch_size]
            vectors = self._call_with_retry([texts[index] for index in idx])
            self.stats.batches += 1
            self.stats.requested += len(idx)
            for index, vec in zip(idx, vectors):
                out[index] = vec
                self.cache.put(self.model_id, texts[index], vec)
            if progress:
                progress(self.stats.cached + self.stats.requested, len(texts))

        matrix = np.vstack([np.asarray(vector, dtype=np.float32) for vector in out])
        if normalize:
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            matrix = matrix / np.maximum(norms, 1e-12)   # never divide by zero

        self.stats.seconds = time.perf_counter() - started
        return matrix


# ------------------------------------------------------------ sanity check


def sanity_check(embedder: "Embedder") -> dict:
    """Confirm the embeddings actually discriminate before you trust anything.

    Two calls. It catches a pooling misconfiguration, a dead model, and a
    returns-the-same-vector-for-everything server — none of which raise an
    error, and all of which make every downstream result meaningless.

    Run this first. Always.
    """
    probes = [
        "the warehouse scanner network is down",
        "quarterly financial invoicing deadlines",   # unrelated
        "depot scanners lost connectivity",          # related to the first
    ]
    vectors = embedder.embed(probes)
    unrelated = float(vectors[0] @ vectors[1])
    related = float(vectors[0] @ vectors[2])
    ok = related - unrelated > 0.05
    return {
        "unrelated": round(unrelated, 3),
        "related": round(related, 3),
        "separation": round(related - unrelated, 3),
        "ok": ok,
        "verdict": (
            "embeddings discriminate — safe to proceed"
            if ok
            else "BROKEN: every text embeds almost identically. Check the "
                 "pooling mode (decoder models need last-token, not CLS), "
                 "and that the model actually loaded."
        ),
    }
