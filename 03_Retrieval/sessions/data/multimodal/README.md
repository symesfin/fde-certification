# The multimodal corpus

**Six charts, six memos, one 45-second video — one fictional regional broadband
operator, "Northline Broadband".**

Everything here is fictional and machine-generated for teaching multimodal
retrieval. The company, the figures, the memos and the narration describe no real
company, person or product. It is a re-skin of the CC0 "ACME Robotics FY2024" demo
corpus from the AI Makerspace AI Engineering certification, redrawn so the numbers
belong to the operator the retrieval sessions follow.

## The design choice that matters

Four of the six numbers — ticket volume, churn, latency and the root-cause split —
appear in **no text file**. A question about them can only be answered by
retrieving a chart and reading it. Headcount and NPS appear in both a chart and a
memo on purpose, so caption-based retrieval has somewhere to win.

## The files

| File | What is in it |
| --- | --- |
| `images/` | six charts (PNG). The numeric facts live in the pixels |
| `text/` | six short memos (Markdown) |
| `video/review.mp4` | a ~45 s narrated-slide video (silent; visuals only) |
| `video/review_transcript.json` | timestamped transcript, as a speech-to-text model would emit it |
| `video/keyframes/` | one reference frame per slide, for machines without OpenCV |
| `parses.jsonl` | a reference parse of each chart, written from the source values — the fallback when no vision model is configured, and the answer key for checking one |
| `data_dictionary.json` | what each file contains, and the question it answers |

Regenerate with:

```bash
uv run --with matplotlib --with imageio --with imageio-ffmpeg python scripts/make_multimodal_corpus.py
```

## Licence

Released under **Creative Commons Zero v1.0 (CC0)** — public-domain dedication.
See `LICENSE`.

> Worth noticing rather than skipping: the corpus this was redrawn from was also
> CC0, which is the only reason redrawing it was a five-minute decision rather
> than a legal review. Check the licence before the data reaches your repository.
