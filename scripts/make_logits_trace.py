#!/usr/bin/env python3
"""Record real logits into a small committed file.

Week 2 runs a real model on the student's own machine — that is the point of the
week. This trace exists for the one case that path cannot cover: someone who can
install packages but cannot download model weights, because their network blocks
Hugging Face.

Same model the session uses, so the numbers match either way.

    uv run --group local python scripts/make_logits_trace.py

Needs the `local` dependency group (torch, transformers), which is why the
output is committed rather than regenerated per student.
"""

import json
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "LiquidAI/LFM2.5-350M"
TOP_K = 1000      # top-p 0.95 tops out at 489 candidates at T=1.0, so this is
                  # lossless for the sampling the sessions do. It is NOT enough
                  # at the top of the temperature slider: by T=2.0 the median
                  # position needs ~766 of these. See data/README.md.
STEPS = 12

PROMPTS = [
    "The capital of France is",
    "To deploy a container you first need to",
    "The three most important things about retrieval are",
    "She opened the door and found",
    "In one sentence, machine learning is",
    "The incident started when the database",
]

_ROOT = Path(__file__).resolve().parent.parent

# Two destinations, deliberately. Notebooks must be standalone -- a session that
# reaches into another week's directory for a data file cannot be reordered, and
# its .ipynb mirror will not run on its own. So both weeks that teach on this
# trace get their own copy, and this script keeps them identical.
OUTS = [
    _ROOT / "02_Open_Weights" / "sessions" / "data",
    _ROOT / "06_Guardrails" / "sessions" / "data",
]


def main() -> None:
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.float32)
    model.eval()

    logits_out, ids_out, meta = [], [], []
    seen_tokens: set[int] = set()

    for prompt_index, prompt in enumerate(PROMPTS):
        # Keep special tokens: LFM2.5 needs its BOS, and without it the model
        # emits <|im_end|> immediately. Verified the hard way.
        ids = tok(prompt, return_tensors="pt").input_ids

        for step in range(STEPS):
            with torch.no_grad():
                logits = model(ids).logits[0, -1].float()
            top = torch.topk(logits, TOP_K)

            logits_out.append(top.values.numpy().astype(np.float32))
            ids_out.append(top.indices.numpy().astype(np.int32))
            seen_tokens.update(top.indices.tolist())
            meta.append({
                "prompt_index": prompt_index,
                "prompt": prompt,
                "step": step,
                "context": tok.decode(ids[0]),
            })

            # Advance greedily, so the recorded path is reproducible.
            ids = torch.cat([ids, top.indices[:1].unsqueeze(0)], dim=1)

        print(f"[{prompt_index + 1}/{len(PROMPTS)}] {tok.decode(ids[0])!r}")

    # Decode only the ids that actually appear, so no tokenizer is needed to read it.
    meta_json = json.dumps({
        "model": MODEL,
        "top_k": TOP_K,
        "steps_per_prompt": STEPS,
        "prompts": PROMPTS,
        "positions": meta,
        "vocab": {str(token_id): tok.decode([token_id]) for token_id in sorted(seen_tokens)},
    })

    for out in OUTS:
        out.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(
            out / "logits_trace.npz",
            logits=np.stack(logits_out),
            token_ids=np.stack(ids_out),
        )
        (out / "logits_trace_meta.json").write_text(meta_json, encoding="utf-8")
        print(f"wrote {out.relative_to(_ROOT)}")

    print(f"\nlogits {np.stack(logits_out).shape} | vocab {len(seen_tokens)}")


if __name__ == "__main__":
    main()
