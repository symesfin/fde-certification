# The logits trace

`logits_trace.npz` + `logits_trace_meta.json` — **real** model output, recorded
once and committed.

Session 1 runs a real model on your own machine; that is the point of the week.
This trace covers the one case that cannot: a network that lets you install
packages but blocks the model download.

Same model the session uses, so the numbers match either way.

## What is in it

| | |
| --- | --- |
| Model | `LiquidAI/LFM2.5-350M` |
| Prompts | 6 |
| Positions | 12 per prompt, following the greedy path — 72 total |
| Per position | The top 1,000 logits and their token ids |
| Vocabulary | ~17.8k decoded token strings, so no tokenizer is needed |
| Size | ~400 KB |

```python
import numpy as np, json
d = np.load("logits_trace.npz")
meta = json.load(open("logits_trace_meta.json"))

d["logits"]      # (72, 1000) float32 — raw, pre-softmax
d["token_ids"]   # (72, 1000) int32
meta["vocab"]["..."]        # token id -> string
meta["positions"][0]        # which prompt, which step, the context so far
```

## Why top-1,000 and not the full vocabulary

The full distribution is 65,536 entries per position, which would make this
~19 MB for no benefit. At `T=1.0`, nucleus sampling at `p=0.95` never reaches
past a few hundred candidates on these positions — the widest is 489 — so the
top 1,000 is lossless for the sampling this session does.

**With one edge to know about, since the notebook hands you the slider.** Raise
the temperature and the tail flattens, so the 95% set grows. By `T=2.0`, the top
of the slider's range, the median position needs about **766** of the 1,000
stored candidates and the widest needs ~890. Nothing breaks, but you are
approaching the edge of what was recorded, and a "95% of the mass" count read at
the top of the range is an **under**-estimate: the tokens that would have
extended it were never saved.

That is a property of a recorded trace rather than a bug, and it is the honest
version of the limitation this file exists to describe. If you want to explore
above `T=2.0` seriously, regenerate with a larger `K`.

## What a recorded trace can and cannot do

**Can:** everything about a *distribution*. Greedy, temperature, top-k, top-p,
and how each reshapes the same real probabilities. That is Tasks 1–6.

**Cannot:** generation. The trace follows the greedy path, so the moment you
sample anything other than the top token, later positions no longer correspond
to your sequence. Task 7 loads the real model for that — it is a 0.7 GB
download and runs on a laptop CPU.

## Regenerating it

```bash
uv sync --group local
uv run --group local python scripts/make_logits_trace.py
```

> One thing that bit us, recorded here so it does not bite you: LFM2.5 needs its
> BOS token. Tokenizing with `add_special_tokens=False` produces a model that
> emits `<|im_end|>` immediately and a trace full of nothing.
