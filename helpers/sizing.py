"""How much memory serving this model actually needs.

Tier 2 by convention. Standard library only.

Week 2 lists download sizes, which is the number people plan with and the wrong
one. A 7B model is a ~14 GB download at fp16 and will not serve 32k context to
eight concurrent users on a 16 GB card, because the **KV cache is not in the
download**. It is allocated per request, it grows linearly with context length
and batch size, and at long context it routinely exceeds the weights.

That gap is where "we tried it on my laptop and it was fine" becomes "it OOMs in
staging". This module does the arithmetic, and it takes the model's real
`config.json` rather than numbers anyone typed from memory — the layer count and
head geometry that drive the cache are in the file the weights shipped with.

The estimate is deliberately a *floor* plus a stated overhead. Real servers add
fragmentation, CUDA graphs, and their own paging; vLLM will happily reserve most
of a card up front. Treat the output as "you certainly need at least this", never
as a budget you can fill.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

# Bytes per parameter, by how the weights are stored.
PRECISION_BYTES = {
    "fp32": 4.0, "float32": 4.0,
    "fp16": 2.0, "bf16": 2.0, "float16": 2.0, "bfloat16": 2.0,
    "fp8": 1.0, "int8": 1.0, "q8": 1.0,
    "int4": 0.5, "q4": 0.5, "awq": 0.5, "gptq": 0.5, "nf4": 0.5,
}


@dataclass
class Geometry:
    """The four numbers from config.json that decide the cache."""

    params: float                 # total parameters
    layers: int
    hidden: int
    heads: int
    kv_heads: int                 # < heads means grouped-query attention
    name: str = ""

    @property
    def head_dim(self) -> int:
        return self.hidden // self.heads if self.heads else 0

    @property
    def gqa_ratio(self) -> float:
        return self.heads / self.kv_heads if self.kv_heads else 1.0


def from_config(path: str | Path, params: float | None = None) -> Geometry:
    """Read a Hugging Face `config.json`. Use the file, not your memory.

    `params` is not in config.json; pass the parameter count from the model card
    if you want the weight figure too. The cache figure does not need it.
    """
    cfg = json.loads(Path(path).read_text("utf-8"))
    # Some configs nest the language model (VLMs, for one).
    if "text_config" in cfg and "num_hidden_layers" not in cfg:
        cfg = {**cfg, **cfg["text_config"]}
    heads = int(cfg.get("num_attention_heads") or 0)
    return Geometry(
        params=params or 0.0,
        layers=int(cfg.get("num_hidden_layers") or 0),
        hidden=int(cfg.get("hidden_size") or 0),
        heads=heads,
        kv_heads=int(cfg.get("num_key_value_heads") or heads or 1),
        name=str(cfg.get("_name_or_path") or Path(path).parent.name),
    )


def weights_gb(params: float, precision: str = "bf16") -> float:
    """Parameters x bytes-per-parameter. The number on the download page."""
    key = precision.lower()
    if key not in PRECISION_BYTES:
        raise ValueError(
            f"unknown precision {precision!r}; known: {', '.join(sorted(PRECISION_BYTES))}"
        )
    return params * PRECISION_BYTES[key] / 1e9


def kv_cache_gb(geo: Geometry, *, context: int, batch: int = 1,
                precision: str = "fp16") -> float:
    """The part that is not in the download.

    Two tensors (K and V) per layer, sized by the *key/value* head count rather
    than the attention head count — grouped-query attention shrinks this by the
    GQA ratio, which is why a modern 7B serves far more context than a 2023 one
    with the same parameter count.
    """
    bytes_per = PRECISION_BYTES.get(precision.lower(), 2.0)
    per_token = 2 * geo.layers * geo.kv_heads * geo.head_dim * bytes_per
    return per_token * context * batch / 1e9


@dataclass
class Estimate:
    weights: float
    kv_cache: float
    overhead: float
    context: int
    batch: int
    precision: str
    geometry: Geometry
    overhead_fraction: float = 0.15

    @property
    def total(self) -> float:
        return self.weights + self.kv_cache + self.overhead

    @property
    def cache_share(self) -> float:
        return self.kv_cache / self.total if self.total else 0.0

    def fits(self, device_gb: float) -> bool:
        return self.total <= device_gb

    def max_context(self, device_gb: float) -> int:
        """Longest context that fits, at this batch size. 0 means the weights
        alone do not fit and no context length will save you.

        Solved rather than scaled: overhead is a fraction of (weights + cache),
        so it grows with the context you are solving for. Using the overhead
        computed at the *current* context silently overshoots.

            (weights + per_token * ctx * batch) * (1 + f) = device
        """
        if not self.context or not self.batch:
            return 0
        per_token = self.kv_cache / (self.context * self.batch)
        budget = device_gb / (1 + self.overhead_fraction) - self.weights
        if budget <= 0 or per_token <= 0:
            return 0
        return int(budget / (per_token * self.batch))

    def __str__(self) -> str:
        return (
            f"{self.geometry.name or 'model'} @ {self.precision}, "
            f"ctx {self.context:,} x batch {self.batch}: "
            f"{self.weights:.1f} GB weights + {self.kv_cache:.1f} GB KV "
            f"+ {self.overhead:.1f} GB overhead = {self.total:.1f} GB "
            f"({self.cache_share:.0%} cache)"
        )


def estimate(geo: Geometry, *, context: int = 4096, batch: int = 1,
             precision: str = "bf16", kv_precision: str = "fp16",
             overhead: float = 0.15) -> Estimate:
    """Weights + cache + a stated overhead fraction.

    `overhead` covers activations, the runtime, and fragmentation. 15% is a
    conservative floor for a well-behaved server and nowhere near enough for a
    badly configured one — measure yours and replace this number.
    """
    weights = weights_gb(geo.params, precision) if geo.params else 0.0
    kv = kv_cache_gb(geo, context=context, batch=batch, precision=kv_precision)
    return Estimate(weights=weights, kv_cache=kv, overhead=(weights + kv) * overhead,
                    context=context, batch=batch, precision=precision, geometry=geo,
                    overhead_fraction=overhead)
