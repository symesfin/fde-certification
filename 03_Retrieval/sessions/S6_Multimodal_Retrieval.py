# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo==0.23.16",
#     "python-dotenv>=1.2",
#     "litellm>=1.90",
#     "numpy>=2.0",
#     "pillow>=11.0",
#     "qdrant-client>=1.12",
#     "fastembed>=0.7",
#     "opencv-python-headless>=4.10",
#     "llama-index-core>=0.14",
# ]
# ///

import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Session 6: Multimodal Retrieval

    *One worker, one decision, one person who has to sign it.*

    Nadia's tickets are not all text. Attached to them are screenshots of the
    customer's modem status page with the error code in the corner, the
    runbooks — eighty PDFs on SharePoint, a third of them scanned — the
    photographs technicians take in street cabinets, and the recording of
    every support call. The assistant has to find those too, and the page her
    manager signs needs one more line: *how the attachments get indexed, and
    what that costs.*

    Three facts about those attachments shape every decision below. A
    screenshot has the customer's account number on it, so whatever reads it
    runs inside the network. A number read out of a picture by a model is a
    guess until something checks it. And the firm already pays for a document
    scanner that has been through procurement; a vision model has not.

    You will use a vision-language model two different ways — once as a
    *parser* that turns a chart into a searchable record, once as a *reader*
    that answers from the actual pixels — and build three ways of retrieving
    across text and images on the same vector database, measured against the
    same questions. Then the same pipeline, extended to video with timestamp
    citations. The output is a decision about how the non-text content in
    your own corpus gets indexed, with the number that justifies it.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Table of Contents

    - 🚀 The one-step version first
    - Task 1: The corpus, and the numbers that live only in pixels
    - Task 2: The vision model as parser
    - Task 3: Strategy A — describe once, index as text
    - Task 4: Strategy B — one shared space for pixels and words
    - Task 5: Strategy C — separate stores, fused by rank
    - ❓ Question #5
    - ❓ Question #6
    - Task 6: Narrow, then read — answering from the pixels
    - ❓ Question #7
    - Task 7: Measure it, and probe it with your own queries
    - Task 8: Video — two aligned streams and a timestamp
    - ❓ Question #8
    - Conclusion
    - Additional Context
    - Bonus Tasks

    > 📓 **Not covered here:** OCR itself, which is a tool you call, and
    > training a joint image–text space from scratch — the pretrained one is
    > used as a shape to recognise. Nadia's screenshots are described, not
    > shipped: the charts below have an answer key, and hers do not yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 📖 Official documentation

    Everything this notebook uses, from the people who maintain it.

    | Tool | What you use it for here | Docs |
    | --- | --- | --- |
    | LiteLLM | `completion()` with image content parts for the vision model; `embedding()` for text vectors | [docs.litellm.ai — vision](https://docs.litellm.ai/docs/completion/vision) · [embeddings](https://docs.litellm.ai/docs/embedding/supported_embedding) |
    | Qdrant (`qdrant-client`) | the vector database every strategy writes to, running inside the notebook process | [qdrant.tech/documentation](https://qdrant.tech/documentation/) |
    | FastEmbed | the CLIP text and image towers as ONNX models — no PyTorch | [qdrant.github.io/fastembed](https://qdrant.github.io/fastembed/) |
    | LlamaIndex (`llama-index-core`) | the one-step opener: `MultiModalVectorStoreIndex` over a text store and an image store | [developers.llamaindex.ai — multi-modal retrieval](https://developers.llamaindex.ai/python/examples/multi_modal/multi_modal_retrieval/) |
    | numpy | normalising vectors and the rank fusion | [numpy.org/doc](https://numpy.org/doc/stable/) |
    | Pillow | reading the charts and keyframes | [pillow.readthedocs.io](https://pillow.readthedocs.io/en/stable/) |
    | OpenCV | sampling keyframes from the video | [docs.opencv.org](https://docs.opencv.org/4.x/) |
    | marimo | `mo.image`, `mo.hstack` and the run buttons | [docs.marimo.io](https://docs.marimo.io/) |

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Your retrieval pipeline ranks text against text. Real corpora are not all
    text: they have charts, scans, screenshots, slides and video. Nadia's has
    all of them, attached to tickets by customers and technicians who were in
    a hurry.

    The instinct is that this needs a different kind of search. Mostly it does
    not. A text embedding model cannot see, and a vision model cannot be
    indexed — so every working design is a way of getting the picture into a
    space where comparison is already defined, and then it is the same nearest-
    neighbour search your text retrieval runs. There are three such ways, and
    this notebook builds all three on one vector database so they can be
    measured against each other.

    **The vision model does two different jobs, and keeping them apart is most
    of the lesson.**

    | Job | When | What it produces |
    | --- | --- | --- |
    | **Parsing** | at ingestion, once per image | a description, a table, OCR text — something you can index |
    | **Reading** | at query time, on a handful of candidates | an answer grounded in the actual pixels |

    **Estimated time:** 30–40 minutes

    ---
    ## Setup
    """)
    return


@app.cell
def _(mo):
    import base64
    import json
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(mo.notebook_dir()).parent.parent))
    from helpers import nb, ui

    CFG = nb.bootstrap()
    DATA = Path(mo.notebook_dir()) / "data" / "multimodal"
    print(f"✅ {CFG.root.name}   vision model: {CFG.vlm_model or 'not configured'}   corpus: {DATA.relative_to(CFG.root)}")
    return CFG, DATA, Path, base64, json, ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 🚀 The one-step version first

    Before building anything, here is what a framework gives you. Six charts
    and six memos go into one index, a question comes back with hits from
    both, and a vision model answers from the top chart. LlamaIndex's
    `MultiModalVectorStoreIndex` keeps a text store and an image store, queries
    both, and returns the two lists — the shape this notebook will build by
    hand. The only code that is ours is two small adapters, because the
    framework's own CLIP wrapper wants PyTorch and a GitHub install, and the
    ONNX version below is the one that passes a laptop's egress rules.

    Press the button, read the answer, and keep one question in mind: *what
    did it decide for me?* Every task after this one is an answer to that.
    """)
    return


@app.cell
def _(mo):
    li_button = mo.ui.run_button(label="🚀 Build the index with LlamaIndex and ask one question")
    li_button
    return (li_button,)


@app.cell
def _(CFG, DATA, Path, base64, li_button, mo, ui):
    mo.stop(not li_button.value, mo.md("*Press the button: one index, one question, one answer.*"))

    import litellm
    from llama_index.core.base.embeddings.base import BaseEmbedding
    from llama_index.core.bridge.pydantic import PrivateAttr
    from llama_index.core.embeddings.multi_modal_base import MultiModalEmbedding
    from llama_index.core.indices import MultiModalVectorStoreIndex
    from llama_index.core.schema import Document, ImageDocument, ImageNode

    LI_CACHE = Path.home() / ".cache" / "fastembed"
    LI_QUESTION = "Which quarter had the most support tickets?"

    class LlamaTextEmbedder(BaseEmbedding):
        """Text store: a small local model served as ONNX — no key, no bill."""

        _model: object = PrivateAttr()

        def __init__(self, **kwargs):
            from fastembed import TextEmbedding

            super().__init__(**kwargs)
            self._model = TextEmbedding("BAAI/bge-small-en-v1.5", cache_dir=str(LI_CACHE))

        def _get_text_embedding(self, text):
            return next(iter(self._model.embed([text]))).tolist()

        def _get_query_embedding(self, query):
            return self._get_text_embedding(query)

        async def _aget_query_embedding(self, query):
            return self._get_text_embedding(query)

    class LlamaClipEmbedder(MultiModalEmbedding):
        """Image store: CLIP's two towers as ONNX. A text query goes through the text tower."""

        _text_tower: object = PrivateAttr()
        _image_tower: object = PrivateAttr()

        def __init__(self, **kwargs):
            from fastembed import ImageEmbedding, TextEmbedding

            super().__init__(**kwargs)
            self._text_tower = TextEmbedding("Qdrant/clip-ViT-B-32-text", cache_dir=str(LI_CACHE))
            self._image_tower = ImageEmbedding("Qdrant/clip-ViT-B-32-vision", cache_dir=str(LI_CACHE))

        def _get_image_embedding(self, img_file_path):
            return next(iter(self._image_tower.embed([str(img_file_path)]))).tolist()

        def _get_text_embedding(self, text):
            return next(iter(self._text_tower.embed([text]))).tolist()

        def _get_query_embedding(self, query):
            return self._get_text_embedding(query)

        async def _aget_query_embedding(self, query):
            return self._get_text_embedding(query)

        async def _aget_image_embedding(self, img_file_path):
            return self._get_image_embedding(img_file_path)

    # One index over both folders. Memos become Documents, charts become ImageDocuments.
    LI_DOCS = [
        Document(text=memo_path.read_text("utf-8"), metadata={"file_path": str(memo_path)})
        for memo_path in sorted((DATA / "text").glob("*.md"))
    ] + [
        ImageDocument(image_path=str(chart_path), metadata={"file_path": str(chart_path)})
        for chart_path in sorted((DATA / "images").glob("*.png"))
    ]

    try:
        with mo.status.spinner(title="LlamaIndex: embedding 12 records (first run downloads two small ONNX models)…"):
            LI_INDEX = MultiModalVectorStoreIndex.from_documents(
                LI_DOCS, embed_model=LlamaTextEmbedder(), image_embed_model=LlamaClipEmbedder()
            )
            li_hits = LI_INDEX.as_retriever(similarity_top_k=3, image_similarity_top_k=3).retrieve(LI_QUESTION)
    except Exception as li_error:
        mo.stop(
            True,
            mo.callout(
                mo.md(
                    f"**The framework needs the same model downloads the hand-built version does** — "
                    f"and this machine could not fetch them (`{type(li_error).__name__}: {str(li_error)[:160]}`). "
                    "Carry on: Strategy B below shows the blocked-download alternatives, and nothing "
                    "else in this notebook depends on this cell."
                ),
                kind="warn",
            ),
        )

    li_rows = [
        {
            "store": "image" if isinstance(li_hit.node, ImageNode) else "text",
            "id": Path(li_hit.node.metadata.get("file_path", "?")).name,
            "score": round(li_hit.score or 0.0, 3),
        }
        for li_hit in li_hits
    ]
    li_top_chart = next((li_hit.node.metadata["file_path"] for li_hit in li_hits if isinstance(li_hit.node, ImageNode)), None)

    if CFG.has_vlm and li_top_chart:
        li_response = litellm.completion(
            timeout=600,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Answer from the chart, one sentence, with the number: {LI_QUESTION}"},
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/png;base64," + base64.b64encode(open(li_top_chart, "rb").read()).decode()},
                        },
                    ],
                }
            ],
            max_tokens=120,
            **CFG.vlm_kwargs(),
        )
        li_answer = (li_response.choices[0].message.content or "").strip()
    else:
        li_answer = "*(no `VLM_MODEL` configured — the retrieval above still ran; the answer step needs a vision model)*"

    mo.vstack(
        [
            ui.table(li_rows, title=f"LlamaIndex · '{LI_QUESTION}' — top 3 from each store"),
            mo.md(f"**Answer from `{Path(li_top_chart).name if li_top_chart else '—'}`:** {li_answer}"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Thirty lines, and it works. Now the question: **what did it decide for
    you?** Each row below is a decision the framework made silently, and the
    task where you make it on purpose.

    | The framework decided… | …and here you decide it |
    | --- | --- |
    | charts are indexed as pixels only — no description, no numbers you can search for | Task 2, the vision model as parser; Task 3, Strategy A |
    | text queries are compared to images inside CLIP's space, which ranks "a pie chart" well and "Q3 tickets" badly | Task 4, Strategy B, and the modality gap measured |
    | two stores, two top-3 lists, *and no rule for merging them* — you got six hits, not a ranking | Task 5, Strategy C, reciprocal rank fusion |
    | the top image is handed to the vision model unverified | Task 6, narrow-then-read, and Task 2's numbers check |
    | no score — it looks right on one question | Task 7, recall@3 on two gold sets, and your own probes |
    | video is not a document type | Task 8 |
    | the text embedder is a local model, so there was no token count to report | Task 3's embedding cost line, the number your write-up needs |

    None of those are wrong defaults. They are *defaults*, and the page Nadia's
    manager signs has to say which ones were kept and why. The rest of this
    notebook is that page, built one decision at a time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 1 — The corpus, and the numbers that live only in pixels

    Six charts, six memos and one 45-second slide video from a fictional
    regional broadband operator: a year's support review. Not Nadia's
    screenshots — those have no ground truth yet, which is the same reason
    the text retrieval session ran on Wikipedia. What the charts show breaking
    will break on her screenshots the same way, and the charts come with an
    answer key.

    **The design choice that matters:** four of the six numbers appear in no
    text file. Ticket volume, churn, latency and the root-cause split exist
    only as pixels. A question about them can be answered only by retrieving
    the right chart *and* reading it — which is exactly the two jobs from the
    table above, and the thing a text-only pipeline cannot do at all.
    """)
    return


@app.cell
def _(DATA, json, ui):
    from dataclasses import dataclass, field

    @dataclass
    class RawRecord:
        id: str  # filename, a stable identifier
        modality: str  # "text" or "image"
        path: str  # where the file lives on disk
        text: str | None = None  # body text, for text records only

    RAW_RECORDS = [
        RawRecord(memo.name, "text", str(memo), memo.read_text(encoding="utf-8"))
        for memo in sorted((DATA / "text").glob("*.md"))
    ] + [
        RawRecord(chart.name, "image", str(chart))
        for chart in sorted((DATA / "images").glob("*.png"))
    ]

    DICTIONARY = json.loads((DATA / "data_dictionary.json").read_text(encoding="utf-8"))

    ui.table(
        [
            {
                "file": name,
                "about": info["about"],
                "the question it answers": info["demo_question"],
                "only in pixels?": "✅" if info["pixels_only"] else "also in a memo",
            }
            for name, info in DICTIONARY["images"].items()
        ],
        title=f"{len(RAW_RECORDS)} records: {sum(1 for record in RAW_RECORDS if record.modality == 'text')} memos, "
        f"{sum(1 for record in RAW_RECORDS if record.modality == 'image')} charts",
    )
    return RAW_RECORDS, dataclass, field


@app.cell
def _(RAW_RECORDS, mo):
    mo.hstack(
        [
            mo.vstack([mo.image(record.path, width=210), mo.md(f"<sub>`{record.id}`</sub>")])
            for record in RAW_RECORDS
            if record.modality == "image"
        ],
        justify="start",
        wrap=True,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **The answer key is "what the chart was drawn from", not "what a model
    > said about it".** That distinction is the whole of Task 2's last cell,
    > and it is Nadia's second fact — a number read out of a picture by a model
    > is a guess until something checks it.

    ---
    ## Task 2 — The vision model as parser

    First job: turn each **image** into a **structured record** — kind, title,
    takeaway, data points — that can be embedded and searched like any other
    text. One model call per chart. The model receives the image as base64
    inside a content part, the same shape every OpenAI-compatible endpoint
    accepts, which is why the call goes through `CFG.vlm_kwargs()` and not a
    vendor SDK.

    Point `VLM_MODEL` at any OpenAI-compatible endpoint serving a multimodal
    model. There is no fallback to `LLM_MODEL` on purpose — a text-only model
    will accept an image payload and answer confidently about nothing. For
    Nadia the endpoint is inside the network or it does not exist: a modem
    screenshot is customer data with a status light on it.

    If no vision model is configured, the reference parses that ship with the
    corpus are used instead, and everything downstream still runs.
    """)
    return


@app.cell
def _(CFG, base64, json):
    from litellm import completion

    PARSE_PROMPT = (
        "You are parsing a figure for a retrieval system. Return STRICT JSON with keys: "
        "kind, title, takeaway, data_points (a list of short strings). Read the numbers off "
        "the chart. Be concise and factual. Output JSON only - no markdown, no commentary."
    )

    def image_part(path: str) -> dict:
        """One image, as the content part every OpenAI-compatible endpoint accepts."""
        suffix = path.rsplit(".", 1)[-1].lower()
        mime = "image/jpeg" if suffix in ("jpg", "jpeg") else "image/png"
        encoded = base64.b64encode(open(path, "rb").read()).decode()
        return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{encoded}"}}

    def vlm_text(response) -> str:
        """The text of a completion, with any code fence stripped."""
        text = response.choices[0].message.content or ""
        return text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    def vlm_parse_image(path: str) -> dict:
        """Job #1, ingestion: one image in, one structured record out."""
        response = completion(
            timeout=600,
            messages=[
                {"role": "system", "content": "Output only JSON."},
                {"role": "user", "content": [{"type": "text", "text": PARSE_PROMPT}, image_part(path)]},
            ],
            max_tokens=400,
            **CFG.vlm_kwargs(),
        )
        return json.loads(vlm_text(response))

    return completion, image_part, vlm_parse_image, vlm_text


@app.cell
def _(CFG, mo):
    parse_button = mo.ui.run_button(
        label=f"🔍  Parse 6 charts with {CFG.vlm_model or 'VLM_MODEL (unset)'}",
        disabled=not CFG.has_vlm,
    )
    mo.vstack(
        [
            parse_button,
            mo.md(
                "<sub>Six model calls, a few seconds each. Until pressed — or if no vision model "
                "is configured — the reference parses in `parses.jsonl` are used.</sub>"
            ),
        ]
    )
    return (parse_button,)


@app.cell
def _(CFG, DATA, RAW_RECORDS, json, mo, parse_button, ui, vlm_parse_image):
    REFERENCE_PARSES = {
        row["file"]: row
        for row in (json.loads(line) for line in (DATA / "parses.jsonl").read_text(encoding="utf-8").splitlines() if line.strip())
    }

    if parse_button.value and CFG.has_vlm:
        with mo.status.spinner(title="Parsing charts…"):
            PARSED_CHARTS = {
                record.id: vlm_parse_image(record.path)
                for record in RAW_RECORDS
                if record.modality == "image"
            }
        PARSE_SOURCE = f"live: {CFG.vlm_model}"
    else:
        PARSED_CHARTS = {name: {key: row[key] for key in ("kind", "title", "takeaway", "data_points")} for name, row in REFERENCE_PARSES.items()}
        PARSE_SOURCE = "reference parses shipped with the corpus"

    mo.vstack(
        [
            mo.md(f"**Parse source:** {PARSE_SOURCE}"),
            ui.table(
                [
                    {
                        "chart": name,
                        "kind": parse.get("kind", ""),
                        "takeaway": parse.get("takeaway", ""),
                        "data points": " · ".join(parse.get("data_points", [])),
                    }
                    for name, parse in PARSED_CHARTS.items()
                ]
            ),
        ]
    )
    return PARSED_CHARTS, PARSE_SOURCE, REFERENCE_PARSES


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Check the numbers before you index them.** The reference parse was
    written from the values the charts were drawn with, so it is an answer
    key. The cell below pulls every number out of each parse and compares the
    two sets. When the live parse is in use this is the verification pass
    Nadia's page cannot do without; when the reference is in use it is trivially
    clean, and that is the point — you should know which one you are looking at.
    """)
    return


@app.cell
def _(PARSED_CHARTS, PARSE_SOURCE, REFERENCE_PARSES, ui):
    import re

    def numbers_in(parse: dict) -> set[str]:
        """Every number in a parse, as text, so 27 and 27.0 and '27k' all meet."""
        blob = " ".join([parse.get("title", ""), parse.get("takeaway", ""), *parse.get("data_points", [])])
        return {match.replace(",", "") for match in re.findall(r"\d+(?:[.,]\d+)?", blob)}

    PARSE_CHECK = []
    for chart_name, reference in REFERENCE_PARSES.items():
        expected = numbers_in(reference)
        found = numbers_in(PARSED_CHARTS.get(chart_name, {}))
        PARSE_CHECK.append(
            {
                "chart": chart_name,
                "numbers expected": len(expected),
                "found by the parse": len(expected & found),
                "missed": ", ".join(sorted(expected - found)) or "—",
                "invented": ", ".join(sorted(found - expected)) or "—",
            }
        )

    ui.table(PARSE_CHECK, title=f"Numbers in the parse vs. the answer key ({PARSE_SOURCE})")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **🏢 In the enterprise:** this six-call loop is a batch job. At nine
    > hundred screenshots it needs retries, a JSON-schema check on every parse,
    > a dead-letter file for the ones that fail it, and a record of which
    > prompt and which model produced each caption — because when the prompt
    > changes, every caption made with the old one is stale and the index has
    > to know. The "invented" column above is the number that decides whether
    > the parse is allowed to feed the index unreviewed.

    **Build one list of chunks.** A memo's chunk is its body; a chart's chunk
    is the caption assembled from its parse. Every chunk keeps `source_path`
    back to the original file — the parse is for *finding* the chart, and the
    pixels are what you show the model when it answers.
    """)
    return


@app.cell
def _(PARSED_CHARTS, RAW_RECORDS, dataclass, field, ui):
    @dataclass
    class Chunk:
        id: str
        modality: str
        content: str  # the text that gets embedded
        source_path: str  # the original file, for the pixels at answer time
        meta: dict = field(default_factory=dict)

    CHUNKS = []
    for raw_record in RAW_RECORDS:
        if raw_record.modality == "text":
            CHUNKS.append(Chunk(raw_record.id, "text", raw_record.text, raw_record.path))
        else:
            parse = PARSED_CHARTS[raw_record.id]
            caption = f"{parse['title']}. {parse['takeaway']} Data: {', '.join(parse['data_points'])}."
            CHUNKS.append(Chunk(raw_record.id, "image", caption, raw_record.path, meta={"parsed": parse}))

    TEXT_CHUNKS = [chunk for chunk in CHUNKS if chunk.modality == "text"]
    IMAGE_CHUNKS = [chunk for chunk in CHUNKS if chunk.modality == "image"]

    ui.table(
        [{"modality": chunk.modality, "id": chunk.id, "content": chunk.content[:90] + "…"} for chunk in CHUNKS],
        title=f"{len(CHUNKS)} chunks",
    )
    return CHUNKS, Chunk, IMAGE_CHUNKS, TEXT_CHUNKS


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 3 — Strategy A: describe once, index as text

    Images are already captions, so this is ordinary text retrieval: one text
    embedding model, one collection, every chunk in it. The metadata on each
    point — `modality`, `source_path` — is what lets you tell a chart from a
    memo *after* retrieval and go back for the pixels.

    Two things are built here that the other strategies reuse. A **text
    embedder** that calls your configured embedding endpoint and falls back to
    a small local model when there is none, and a **Qdrant collection** that
    runs inside this process. `":memory:"` is a real Qdrant engine with the
    same API as a production cluster; in production the one-line change is
    `url="https://your-qdrant-host:6333"`.

    **Which backend you get, and whether a token count appears.** Your chat
    provider does not decide this — embeddings are a separate endpoint, and
    Anthropic does not serve one. The embedder reads `.env` and picks:

    | Your `.env` | Backend | "Embedding cost" line |
    | --- | --- | --- |
    | `OPENAI_API_KEY` set (with `EMBED_MODEL=text-embedding-3-small`) | OpenAI, hosted | real count from `usage.total_tokens` |
    | `EMBED_MODEL=voyage/voyage-3.5` + `VOYAGE_API_KEY` | Voyage, hosted | real count |
    | `EMBED_API_BASE` pointing at a gateway, vLLM or Ollama | that server, hosted | whatever the server reports — many report 0 |
    | Anthropic key only, no embedding key | local ONNX `bge-small-en-v1.5` | **0** — it never left your machine |
    | a hosted key that fails on the first call (no credit, bad model) | ⚠️ then local | **0**, with the provider's error printed in Setup |

    The Setup cell prints which one you landed on (`… via api` or
    `… via local`), and 0 on the local path is correct, not a bug: there is
    no bill to measure. The count is cumulative across the notebook — every
    query Strategies A and C embed, and the gold-set scoring later, add to
    it — so the number here is the figure *as of this cell*; re-run the cell
    at the end to see the whole session's spend.
    """)
    return


@app.cell
def _(CFG, Path, mo):
    import os

    import numpy as np
    from litellm import embedding

    FASTEMBED_CACHE = Path.home() / ".cache" / "fastembed"

    def l2_normalise(vectors) -> "np.ndarray":
        """Unit length, so a dot product is a cosine and scores are comparable."""
        matrix = np.asarray(vectors, dtype="float32")
        return matrix / (np.linalg.norm(matrix, axis=-1, keepdims=True) + 1e-9)

    class TextEmbedder:
        """Text in, unit vectors out. The API when one is configured, a local ONNX model when not."""

        def __init__(self, cfg):
            self.cfg = cfg
            # Hosted when there is anywhere to send the request: an endpoint, an
            # embedding-specific key, a provider-prefixed model (voyage/..., cohere/...)
            # or the ambient OpenAI key. Anthropic has no embedding endpoint, so an
            # Anthropic-only .env lands on the local model.
            hosted = (
                cfg.embed_api_base
                or os.getenv("EMBED_API_KEY")
                or "/" in cfg.embed_model
                or os.getenv("OPENAI_API_KEY")
            )
            self.backend = "api" if hosted else "local"
            self.model_id = cfg.embed_model if self.backend == "api" else "BAAI/bge-small-en-v1.5"
            self.local_model = None
            self.tokens = 0  # what the API run cost, measured -- the number the challenge asks for

        def embed(self, texts: list[str]):
            if self.backend == "api":
                response = embedding(**self.cfg.embed_kwargs(), input=list(texts), timeout=600)
                usage = getattr(response, "usage", None)
                self.tokens += int(getattr(usage, "total_tokens", 0) or 0)
                rows = sorted(response.data, key=lambda item: item.get("index", 0))
                return l2_normalise([row["embedding"] for row in rows])
            if self.local_model is None:
                from fastembed import TextEmbedding

                self.local_model = TextEmbedding(self.model_id, cache_dir=str(FASTEMBED_CACHE))
            return l2_normalise(list(self.local_model.embed(list(texts))))

    with mo.status.spinner(title="Loading the text embedder…"):
        TEXT_EMBEDDER = TextEmbedder(CFG)
        try:
            probe = TEXT_EMBEDDER.embed(["probe"])
        except Exception as error:
            # A key that exists but cannot pay, a gateway that is down, a model the
            # host does not serve: all surface here, on the first call. Fall back to
            # the local model and say so, rather than taking the notebook down.
            if TEXT_EMBEDDER.backend != "api":
                raise
            print(f"⚠️ hosted embedding failed ({type(error).__name__}: {str(error)[:160]}…) — falling back to the local model")
            TEXT_EMBEDDER.backend = "local"
            TEXT_EMBEDDER.model_id = "BAAI/bge-small-en-v1.5"
            probe = TEXT_EMBEDDER.embed(["probe"])

    print(f"✅ text embedder: {TEXT_EMBEDDER.model_id} via {TEXT_EMBEDDER.backend}, {probe.shape[1]} dimensions")
    return FASTEMBED_CACHE, TEXT_EMBEDDER, l2_normalise


@app.cell
def _(CHUNKS, TEXT_EMBEDDER):
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

    QDRANT = QdrantClient(":memory:")  # one engine, several collections — one per strategy

    def build_collection(name: str, vectors, chunks) -> str:
        """Create a collection from precomputed vectors. The payload is what comes back with a hit."""
        if QDRANT.collection_exists(name):
            QDRANT.delete_collection(name)
        QDRANT.create_collection(name, vectors_config=VectorParams(size=len(vectors[0]), distance=Distance.COSINE))
        QDRANT.upsert(
            name,
            points=[
                PointStruct(
                    id=index,
                    vector=[float(value) for value in vector],
                    payload={"id": chunk.id, "modality": chunk.modality, "source_path": chunk.source_path, "content": chunk.content, **chunk.meta},
                )
                for index, (vector, chunk) in enumerate(zip(vectors, chunks))
            ],
        )
        return name

    def search_collection(name: str, query_vector, k: int = 3, modality: str | None = None) -> list[dict]:
        """Nearest neighbours, optionally restricted to one modality via a payload filter."""
        condition = Filter(must=[FieldCondition(key="modality", match=MatchValue(value=modality))]) if modality else None
        hits = QDRANT.query_points(name, query=[float(value) for value in query_vector], limit=k, query_filter=condition, with_payload=True).points
        return [{**hit.payload, "score": round(hit.score, 3)} for hit in hits]

    A_VECTORS = TEXT_EMBEDDER.embed([chunk.content for chunk in CHUNKS])
    build_collection("strategy_a", A_VECTORS, CHUNKS)

    def retrieve_A(query: str, k: int = 3) -> list[dict]:
        return search_collection("strategy_a", TEXT_EMBEDDER.embed([query])[0], k)

    return build_collection, retrieve_A, search_collection


@app.cell
def _(TEXT_EMBEDDER, mo, retrieve_A, ui):
    mo.vstack(
        [
            ui.table(
                [{"rank": rank + 1, "modality": hit["modality"], "id": hit["id"], "score": hit["score"]} for rank, hit in enumerate(retrieve_A("Which quarter had the most support tickets?"))],
                title="Strategy A · 'Which quarter had the most support tickets?'",
            ),
            mo.md(
                f"<sub>Embedding cost so far: **{TEXT_EMBEDDER.tokens:,} tokens**, measured from the API's usage field"
                + (" — the number to write next to your own corpus, because you pay it again every time the chunking changes.</sub>" if TEXT_EMBEDDER.backend == "api" else " (0: the local model reports none).</sub>")
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The chart comes back because its *caption* mentions quarters and tickets.
    That is the whole strength and the whole weakness of Strategy A: it finds
    exactly what the parser bothered to write down, and nothing else. For
    Nadia, nine hundred screenshots and zero descriptions of them means
    Strategy A costs nine hundred vision-model calls before the first search.

    ---
    ## Task 4 — Strategy B: one shared space for pixels and words

    CLIP was trained on hundreds of millions of (image, caption) pairs with one
    objective: the vector for a picture and the vector for its caption should
    land close together. The result is two encoders — a text tower and an
    image tower — that write into the *same* space, so a plain-English
    question can be compared directly against pixels, **with no caption on the
    image side at all.**

    The towers here are ONNX exports served by FastEmbed, Qdrant's own
    embedding library: about 600 MB on first use, cached under
    `~/.cache/fastembed`, no PyTorch. Press the button once.
    """)
    return


@app.cell
def _(mo):
    clip_button = mo.ui.run_button(label="🧲  Load CLIP (downloads ~600 MB once, then cached)")
    mo.vstack([clip_button, mo.md("<sub>Strategies B and C, and the video keyframes, need it. Everything else runs without it.</sub>")])
    return (clip_button,)


@app.cell
def _(FASTEMBED_CACHE, clip_button, l2_normalise, mo):
    class ClipEmbedder:
        """Text and images into one shared space. Two ONNX towers, one vector size."""

        def __init__(self, cache_dir):
            from fastembed import ImageEmbedding, TextEmbedding

            self.text_tower = TextEmbedding("Qdrant/clip-ViT-B-32-text", cache_dir=str(cache_dir))
            self.image_tower = ImageEmbedding("Qdrant/clip-ViT-B-32-vision", cache_dir=str(cache_dir))

        def embed_text(self, texts: list[str]):
            return l2_normalise(list(self.text_tower.embed([text[:300] for text in texts])))  # CLIP reads 77 tokens, no more

        def embed_images(self, paths: list[str]):
            return l2_normalise(list(self.image_tower.embed(list(paths))))

    CLIP = None
    CLIP_ERROR = ""
    if clip_button.value:
        try:
            with mo.status.spinner(title="Loading CLIP…"):
                CLIP = ClipEmbedder(FASTEMBED_CACHE)
        except Exception as error:  # a blocked download is the common case, and it is a finding
            CLIP_ERROR = f"{type(error).__name__}: {str(error)[:200]}"

    CLIP_READY = CLIP is not None

    def clip_unavailable_panel(what: str):
        reason = CLIP_ERROR or "the button above has not been pressed"
        return mo.callout(
            mo.md(
                f"**{what} needs CLIP, and it is not loaded** — {reason}.\n\n"
                "If the download is blocked on your network, that is a finding, not a blocker: write it in "
                "`use_case/ecosystem.md`. The alternatives are in the Conclusion — a hosted multimodal embedding "
                "endpoint, or the same ONNX files mirrored onto your firm's internal artifact store."
            ),
            kind="warn",
        )

    if CLIP_READY:
        print("✅ CLIP loaded: text tower + image tower, 512 dimensions")
    elif CLIP_ERROR:
        print(f"⚠️ CLIP not available: {CLIP_ERROR}")
    return CLIP, CLIP_READY, clip_unavailable_panel


@app.cell
def _(
    CLIP,
    CLIP_READY,
    IMAGE_CHUNKS,
    TEXT_CHUNKS,
    build_collection,
    clip_unavailable_panel,
    mo,
    search_collection,
    ui,
):
    if CLIP_READY:
        IMAGE_VECTORS = CLIP.embed_images([chunk.source_path for chunk in IMAGE_CHUNKS])  # from PIXELS
        TEXT_VECTORS_CLIP = CLIP.embed_text([chunk.content for chunk in TEXT_CHUNKS])  # from words
        build_collection("strategy_b", list(IMAGE_VECTORS) + list(TEXT_VECTORS_CLIP), IMAGE_CHUNKS + TEXT_CHUNKS)

        def retrieve_B(query: str, k: int = 3, modality: str | None = None) -> list[dict]:
            return search_collection("strategy_b", CLIP.embed_text([query])[0], k, modality)

        B_QUERY = "a bar chart comparing line latency across regions"
        B_PANEL = mo.vstack(
            [
                ui.table(
                    [{"rank": rank + 1, "modality": hit["modality"], "id": hit["id"], "score": hit["score"]} for rank, hit in enumerate(retrieve_B(B_QUERY))],
                    title=f"Unified search · '{B_QUERY}' — text and images compete in one ranking",
                ),
                ui.table(
                    [{"rank": rank + 1, "modality": hit["modality"], "id": hit["id"], "score": hit["score"]} for rank, hit in enumerate(retrieve_B(B_QUERY, modality="image"))],
                    title="Images only — pixels matched directly against the question",
                ),
            ]
        )
    else:
        IMAGE_VECTORS, TEXT_VECTORS_CLIP, B_QUERY = None, None, ""
        retrieve_B = None
        B_PANEL = clip_unavailable_panel("Strategy B")

    B_PANEL
    return IMAGE_VECTORS, retrieve_B


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **What just happened — the modality gap.** In the unified search the
    > memos usually outrank every chart, even though the query literally
    > describes a chart. Text vectors cluster in one region of CLIP's space and
    > image vectors in another, so a text query lands closer to *any* text than
    > to the best-matching image. The images-only search tells the real story:
    > among the pixels, the latency chart ranks first, matched with no caption
    > involved. That is the superpower of a shared space, and also why a single
    > mixed collection is fragile. Two standard fixes: filter per modality, as
    > above, or keep separate stores and fuse by rank — Strategy C.
    >
    > And CLIP still cannot read `240 ms` off the chart. It knows what a
    > latency chart looks like; it does not know what the bars say. That is why
    > the pixels go to the vision model at answer time in Task 6.

    ---
    ## Task 5 — Strategy C: separate stores, fused by rank

    Each modality gets its best embedder: the text model for memos, CLIP for
    the charts. Their similarity scores live on different scales, so the two
    result lists cannot be merged by score. They are merged by **rank**:
    Reciprocal Rank Fusion gives an item `1 / (k + rank)` from every list it
    appears in and sorts by the sum. Twelve lines, no tuning, and it is what
    most production hybrid search ends up doing.
    """)
    return


@app.cell
def _(
    CLIP,
    CLIP_READY,
    IMAGE_CHUNKS,
    IMAGE_VECTORS,
    TEXT_CHUNKS,
    TEXT_EMBEDDER,
    build_collection,
    clip_unavailable_panel,
    search_collection,
    ui,
):
    C_TEXT_VECTORS = TEXT_EMBEDDER.embed([chunk.content for chunk in TEXT_CHUNKS])
    build_collection("strategy_c_text", C_TEXT_VECTORS, TEXT_CHUNKS)

    def reciprocal_rank_fusion(result_lists: list[list[dict]], k: int = 60) -> list[dict]:
        """Merge ranked lists by rank, not by score. Scores from different embedders do not compare."""
        fused, keep = {}, {}
        for results in result_lists:
            for rank, hit in enumerate(results):
                key = (hit["modality"], hit["id"])
                fused[key] = fused.get(key, 0.0) + 1.0 / (k + rank + 1)
                keep[key] = {**hit, "score": round(fused[key], 4)}
        return [keep[key] for key in sorted(fused, key=fused.get, reverse=True)]

    if CLIP_READY:
        build_collection("strategy_c_images", IMAGE_VECTORS, IMAGE_CHUNKS)

        def retrieve_C(query: str, k: int = 3) -> list[dict]:
            text_hits = search_collection("strategy_c_text", TEXT_EMBEDDER.embed([query])[0], k)
            image_hits = search_collection("strategy_c_images", CLIP.embed_text([query])[0], k)
            return reciprocal_rank_fusion([text_hits, image_hits])[:k]

        C_QUERY = "why did the on-call engineer get paged about the Coast region?"
        C_PANEL = ui.table(
            [{"rank": rank + 1, "modality": hit["modality"], "id": hit["id"], "fused score": hit["score"]} for rank, hit in enumerate(retrieve_C(C_QUERY))],
            title=f"Strategy C · '{C_QUERY}'",
        )
    else:
        retrieve_C, C_QUERY = None, ""
        C_PANEL = clip_unavailable_panel("Strategy C")

    C_PANEL
    return reciprocal_rank_fusion, retrieve_C


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Trade-offs at a glance

    | | **A. Caption → text** | **B. One shared space** | **C. Separate + fuse** |
    | --- | --- | --- | --- |
    | Cross-modal search | via captions only | **native (pixels)** | native (image store) |
    | Ingestion cost | **high** — a vision call per image | low — one embedding per image | medium |
    | Fine-grained numbers | as good as the caption | weak — CLIP cannot read values | text strong, image weak |
    | Query latency | low | low | higher — two searches and a fuse |
    | Moving parts | **fewest** | few | most |
    | Best when | text-heavy, few figures | image-dominant corpora | each modality deserves its own embedder |
    | Main failure | the caption missed the ask | modality gap; cannot read values | rank calibration across stores |

    **The practical default is C for breadth, always paired with a vision
    model at answer time so exact figures are read from pixels.** A is the
    right start when the corpus is mostly text; B shines when it is mostly
    pictures. For Nadia's screenshots — nine hundred of them, every one with
    an error code that matters — A is the only strategy whose *captions* can
    carry the code, and C is how she keeps that without paying a vision call
    for every cabinet photograph too.

    > **🔀 If your non-text content is scanned documents rather than charts:**
    > the three strategies are the same, but the parser in Task 2 is OCR, not a
    > vision model — cheaper by a factor of a hundred, already through
    > procurement at most firms, and it gives you page numbers for free. Reach
    > for a vision model only where OCR cannot: diagrams, photographs,
    > handwriting, and charts whose meaning is in the shape rather than the
    > labels.

    ### ❓ Question #5

    A text embedding model cannot see, and a vision model's output cannot be
    indexed. Name the three ways this notebook gets a text question to return
    a chart, and say which one you would start with for the non-text content
    in your own corpus — and what about that content decides it.

    **Answer:**

    ### ❓ Question #6

    Strategy B found the latency chart from pixels alone, yet in the unified
    ranking a memo outranked it, and on its own Strategy B could not answer
    *"what is the P95 latency in the Coast region?"* Those are two different
    weaknesses. Name both, and the part of the full pipeline that compensates
    for each — which is also the answer to *which model never sees the whole
    corpus, and what narrows it first*.

    **Answer:**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Task 6 — Narrow, then read: answering from the pixels

    Second job of the vision model: **read the retrieved charts to answer.**
    The prompt carries the retrieved memos as text and the retrieved charts as
    the *actual pixels*, re-loaded from `source_path`. Now the model can read
    the exact number off the bar — the thing CLIP could not do — and it is
    asked to cite the chunk ids it used.

    The shape matters more than the prompt. The vision model reads **three
    candidates**, never the corpus. At nine hundred screenshots that is the
    difference between a query that costs three image reads and one that costs
    nine hundred; it is the only shape that fits a page with a cost line on it.
    """)
    return


@app.cell
def _(
    CFG,
    completion,
    image_part,
    retrieve_A,
    retrieve_B,
    retrieve_C,
    vlm_text,
):
    ANSWER_SYSTEM = (
        "You are a grounded assistant. Answer ONLY from the provided context (text and images). "
        "Read any figures carefully for exact values. Cite the chunk ids you used like [id]. "
        "If the answer isn't in the context, say so."
    )

    def retrieve(query: str, strategy: str = "C", k: int = 3) -> list[dict]:
        """One door for all three strategies. Falls back to A when a strategy needs CLIP and it is not loaded."""
        available = {"A": retrieve_A, "B": retrieve_B, "C": retrieve_C}
        chosen = available.get(strategy) or retrieve_A
        return chosen(query, k=k)

    def build_answer_message(query: str, retrieved: list[dict]) -> dict:
        parts = [{"type": "text", "text": f"Question: {query}\n\n--- CONTEXT ---"}]
        for hit in retrieved:
            if hit["modality"] == "text":
                parts.append({"type": "text", "text": f"\n[{hit['id']}] (text): {hit['content']}"})
            else:
                parts.append({"type": "text", "text": f"\n[{hit['id']}] (image below):"})
                parts.append(image_part(hit["source_path"]))  # the ACTUAL pixels go to the model
        parts.append({"type": "text", "text": "\n--- END CONTEXT ---\nAnswer with citations."})
        return {"role": "user", "content": parts}

    def answer(query: str, strategy: str = "C", k: int = 3) -> tuple[str, list[dict]]:
        retrieved = retrieve(query, strategy, k)
        response = completion(
            timeout=600,
            messages=[{"role": "system", "content": ANSWER_SYSTEM}, build_answer_message(query, retrieved)],
            max_tokens=400,
            **CFG.vlm_kwargs(),
        )
        return vlm_text(response), retrieved

    return ANSWER_SYSTEM, answer, retrieve


@app.cell
def _(CFG, mo):
    answer_button = mo.ui.run_button(
        label=f"👁️  Answer 4 questions with {CFG.vlm_model or 'VLM_MODEL (unset)'}",
        disabled=not CFG.has_vlm,
    )
    mo.vstack([answer_button, mo.md("<sub>Four model calls, each carrying up to three images. The first answer lives only in a chart.</sub>")])
    return (answer_button,)


@app.cell
def _(CFG, answer, answer_button, mo):
    DEMO_QUESTIONS = [
        "Which quarter had the most support tickets, and how many?",  # answer lives in an IMAGE
        "In which month was churn highest, and what caused it?",  # image + memo together
        "What share of tickets are caused by the customer's own equipment?",  # pie-chart IMAGE
        "How did NPS change over the year, and when did it dip?",  # image + memo
    ]

    if answer_button.value and CFG.has_vlm:
        with mo.status.spinner(title="Answering…"):
            ANSWERS = [(question, *answer(question, strategy="C")) for question in DEMO_QUESTIONS]
        ANSWER_PANEL = mo.vstack(
            [
                mo.md(
                    f"**Q: {question}**\n\n{text}\n\n<sub>retrieved: "
                    + ", ".join(f"{hit['modality']}:{hit['id']}" for hit in retrieved)
                    + "</sub>\n\n---"
                )
                for question, text, retrieved in ANSWERS
            ]
        )
    else:
        ANSWERS = []
        ANSWER_PANEL = mo.callout(
            mo.md(
                "No vision model configured, or the button has not been pressed. The retrieval half still runs — "
                "Task 7 measures it — but reading `27k` off the bar needs a model that can see. "
                "Set `VLM_MODEL` in `.env` to run this cell."
            ),
            kind="info",
        )

    ANSWER_PANEL
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice the division of labour: **retrieval** finds the tickets chart, and
    **reading** gets `27 thousand` off the bar. That number is in no memo.
    *Retrieve to find the chart, look at the chart to answer* is the core
    pattern of production multimodal retrieval — and for Nadia it is the
    attachments line on the page: a batch parser inside the network for the
    screenshots, three reads per query, never the corpus.

    > **🏢 In the enterprise:** every image in the prompt costs tokens — a
    > chart at this resolution is roughly a thousand, a full-page scan several
    > times that. Cap the number of image chunks per answer, downscale before
    > sending, and record per answer which images went in and what they cost.
    > The retrieval choice (`k=3`) is a cost control as much as a quality
    > control, and the page her manager signs is where that number goes.

    ### ❓ Question #7

    At answer time every retrieved chart is re-loaded from `source_path` and
    sent to the model as pixels — even though a caption for it already exists
    from Task 2. Why not send the caption? Connect your answer to the parse
    check in Task 2, and to *which identifiers your users search by, and what
    would verify a model's reading of them*.

    **Answer:**

    ---
    ## Task 7 — Measure it, and probe it with your own queries

    Two things get measured separately: **retrieval** — did the right chunk
    come back? that is recall@k — and **answer quality**, which needs a person
    or a judge model. The gold set below maps questions to the chunk ids that
    should come back.

    **Two phrasings, on purpose.** The first eight questions are *factual*:
    they ask for what a chart says, in the words a caption uses — "churn",
    "Coast region", "retention programme". On those, Strategy A cannot lose,
    because a caption is a text version of the chart and the question is a
    text version of the caption. The next three are *visual*: they ask for a
    chart by what it looks like — a pie, a line that dips — which no caption
    mentions, because the parser was asked for content, not form. That is the
    caption bottleneck, and it is the only place the pixels can win.
    """)
    return


@app.cell
def _(retrieve, retrieve_B, retrieve_C, ui):
    GOLD = {
        "Which quarter had the most support tickets?": {"fig_tickets_quarterly.png"},
        "In which month was churn highest?": {"fig_churn_monthly.png"},
        "What is the P95 latency in the Coast region?": {"fig_latency_region.png"},
        "Which support team has the most people?": {"fig_headcount_team.png"},
        "When did NPS dip during the year?": {"fig_nps_quarterly.png", "doc_customer_sentiment.md"},
        "What share of tickets are caused by customer equipment?": {"fig_root_cause.png"},
        "What did the retention programme focus on?": {"doc_retention_programme.md"},
        "What caused the March churn spike?": {"doc_ops_review_notes.md", "fig_churn_monthly.png"},
    }

    GOLD_VISUAL = {
        "a pie chart": {"fig_root_cause.png"},
        "a line chart that goes up, dips, then rises again": {"fig_nps_quarterly.png"},
        "a chart made of coloured wedges": {"fig_root_cause.png"},
    }

    def recall_at_k(strategy: str, gold: dict, k: int = 3) -> float:
        hits = 0
        for question, wanted in gold.items():
            got = {hit["id"] for hit in retrieve(question, strategy, k)}
            hits += bool(wanted & got)
        return hits / len(gold)

    STRATEGIES_AVAILABLE = ["A"] + (["B"] if retrieve_B else []) + (["C"] if retrieve_C else [])
    RECALL = {strategy: recall_at_k(strategy, GOLD) for strategy in STRATEGIES_AVAILABLE}
    RECALL_VISUAL = {strategy: recall_at_k(strategy, GOLD_VISUAL) for strategy in STRATEGIES_AVAILABLE}

    ui.table(
        [
            {
                "strategy": strategy,
                f"recall@3 · factual ({len(GOLD)} q)": f"{RECALL[strategy]:.2f}",
                f"recall@3 · visual ({len(GOLD_VISUAL)} q)": f"{RECALL_VISUAL[strategy]:.2f}",
            }
            for strategy in STRATEGIES_AVAILABLE
        ],
        title="recall@3 by phrasing" + ("" if len(STRATEGIES_AVAILABLE) == 3 else " — B and C need CLIP"),
    )
    return GOLD, STRATEGIES_AVAILABLE, recall_at_k


@app.cell
def _(mo):
    probe_query = mo.ui.text(
        value="a pie chart of where the support tickets come from",
        label="Your query",
        full_width=True,
    )
    mo.vstack([probe_query, mo.md("<sub>Try one *visual* phrasing (\"a pie chart of…\") and one *factual* one (\"what share of tickets…\"). The rankings will not agree.</sub>")])
    return (probe_query,)


@app.cell
def _(STRATEGIES_AVAILABLE, probe_query, retrieve, ui):
    ui.table(
        [
            {"strategy": strategy, "top 3": "  →  ".join(f"{hit['modality']}:{hit['id']}" for hit in retrieve(probe_query.value, strategy))}
            for strategy in STRATEGIES_AVAILABLE
        ],
        title=f"'{probe_query.value}'",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Read the two columns against each other.** On factual phrasing A and
    C should tie near the top — the caption carries the words — and B should
    trail, because memos and charts compete in one ranking and text sits
    closer to text (the modality gap). On visual phrasing the order should
    flip: A has no caption that says "pie" or "line", so it is guessing; C
    finds the chart from the pixels through its image store; B finds it too
    once the question is about appearance rather than content. That flip is
    the whole case for keeping an image store next to the caption index — and
    for Nadia it is also the cost case: nine hundred screenshots is nine
    hundred vision calls before A's first search, or nine hundred cheap
    embeddings for C with the vision model reading only the three candidates.

    **The failures that bite, and what each one is called.**

    | What happens | Which strategy | The fix |
    | --- | --- | --- |
    | The parser never mentioned it, so retrieval cannot find it | A | a richer parse prompt, or add B/C |
    | "Find the latency chart" works; "what was the Coast value" does not | B | keep the pixels and read them at answer time |
    | A text query sits closer to any memo than to the right chart | B | filter per modality, or fuse separate stores |
    | Two embedders' scores get compared directly | C | rank fusion, never raw-score thresholds |
    | No `source_path` on the chunk | all | carry provenance from the first parse; without it there are no pixels and no citation |
    | A chart changed and its caption did not | all | re-parse and re-embed together, then rebuild the collection |

    ---
    ## Task 8 — Video: two aligned streams and a timestamp

    A video is two aligned streams: an audio track that becomes a timestamped
    transcript, and a sequence of frames that are images. Video retrieval
    builds **time-windowed chunks** pairing *what was said* with *what was on
    screen*, then reuses everything above. The payoff is an answer that cites a
    timestamp.

    For Nadia's recorded calls this is the honest test, and the transcript
    usually wins: the frames of a support call are a static screen, and
    everything that matters was said. The slide video below has both, which is
    why it can show the fusion working.
    """)
    return


@app.cell
def _(DATA, json, ui):
    TRANSCRIPT = json.loads((DATA / "video" / "review_transcript.json").read_text(encoding="utf-8"))
    TRANSCRIPT_SEGMENTS = [(segment["start"], segment["end"], segment["text"]) for segment in TRANSCRIPT["segments"]]
    VIDEO_PATH = DATA / "video" / TRANSCRIPT["video"]

    ui.table(
        [{"window": f"{start:5.1f}–{end:5.1f} s", "said": text[:80] + "…"} for start, end, text in TRANSCRIPT_SEGMENTS],
        title=f"{VIDEO_PATH.name}: {len(TRANSCRIPT_SEGMENTS)} transcript segments (a speech-to-text model would produce these from the audio)",
    )
    return TRANSCRIPT_SEGMENTS, VIDEO_PATH


@app.cell
def _(DATA, Path, VIDEO_PATH, mo):
    import tempfile

    KEYFRAME_DIR = Path(tempfile.gettempdir()) / "fde_multimodal_keyframes"

    def sample_keyframes(video_path: Path, every_sec: float = 5.0, out_dir: Path = KEYFRAME_DIR) -> list[tuple[float, str]]:
        """One frame every `every_sec` seconds — interval sampling, which is enough for slides."""
        import cv2

        out_dir.mkdir(parents=True, exist_ok=True)
        capture = cv2.VideoCapture(str(video_path))
        fps = capture.get(cv2.CAP_PROP_FPS) or 8.0
        frames, index = [], 0
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if index % max(1, int(fps * every_sec)) == 0:
                stamp = index / fps
                frame_path = out_dir / f"kf_{int(stamp):04d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frames.append((stamp, str(frame_path)))
            index += 1
        capture.release()
        return frames

    try:
        KEYFRAMES = sample_keyframes(VIDEO_PATH)
        KEYFRAME_SOURCE = f"sampled with OpenCV into {KEYFRAME_DIR}"
    except Exception as error:  # no codec, no OpenCV: use the reference frames that ship with the corpus
        KEYFRAMES = [
            (float(frame.stem.split("_")[1]), str(frame))
            for frame in sorted((DATA / "video" / "keyframes").glob("frame_*.jpg"))
        ]
        KEYFRAME_SOURCE = f"reference frames shipped with the corpus ({type(error).__name__})"

    mo.vstack(
        [
            mo.md(f"**{len(KEYFRAMES)} keyframes** — {KEYFRAME_SOURCE}"),
            mo.hstack([mo.image(path, width=150) for stamp, path in KEYFRAMES[:5]], justify="start", wrap=True),
        ]
    )
    return (KEYFRAMES,)


@app.cell
def _(KEYFRAMES, TRANSCRIPT_SEGMENTS, ui):
    def build_video_chunks(segments, frames) -> list[dict]:
        """For each transcript window, attach the keyframe(s) inside it — or the nearest one."""
        out = []
        for index, (start, end, text) in enumerate(segments):
            inside = [path for stamp, path in frames if start <= stamp < end]
            nearest = [min(frames, key=lambda pair: abs(pair[0] - (start + end) / 2))[1]]
            out.append({"id": f"seg_{index:03d}", "t_start": start, "t_end": end, "transcript": text, "keyframes": inside or nearest})
        return out

    VIDEO_CHUNKS = build_video_chunks(TRANSCRIPT_SEGMENTS, KEYFRAMES)

    ui.table(
        [{"chunk": chunk["id"], "window": f"{chunk['t_start']:.0f}–{chunk['t_end']:.0f} s", "frames": len(chunk["keyframes"]), "said": chunk["transcript"][:60] + "…"} for chunk in VIDEO_CHUNKS],
        title="Time-windowed chunks: what was said, and what was on screen",
    )
    return (VIDEO_CHUNKS,)


@app.cell
def _(
    CLIP,
    CLIP_READY,
    Chunk,
    TEXT_EMBEDDER,
    VIDEO_CHUNKS,
    build_collection,
    mo,
    reciprocal_rank_fusion,
    search_collection,
    ui,
):
    TRANSCRIPT_CHUNKS = [
        Chunk(chunk["id"], "video_text", chunk["transcript"], chunk["keyframes"][0], meta={"t_start": chunk["t_start"], "t_end": chunk["t_end"]})
        for chunk in VIDEO_CHUNKS
    ]
    build_collection("video_transcript", TEXT_EMBEDDER.embed([chunk.content for chunk in TRANSCRIPT_CHUNKS]), TRANSCRIPT_CHUNKS)

    if CLIP_READY:
        FRAME_CHUNKS = [
            Chunk(chunk["id"], "video_frame", f"keyframe of {chunk['id']}", frame_path, meta={"t_start": chunk["t_start"], "t_end": chunk["t_end"]})
            for chunk in VIDEO_CHUNKS
            for frame_path in chunk["keyframes"]
        ]
        build_collection("video_keyframes", CLIP.embed_images([chunk.source_path for chunk in FRAME_CHUNKS]), FRAME_CHUNKS)
    else:
        FRAME_CHUNKS = []

    def retrieve_video(query: str, k: int = 3) -> list[dict]:
        """Transcript store plus keyframe store, fused by rank — Strategy C on a video."""
        lists = [search_collection("video_transcript", TEXT_EMBEDDER.embed([query])[0], k)]
        if CLIP_READY:
            lists.append(search_collection("video_keyframes", CLIP.embed_text([query])[0], k))
        return reciprocal_rank_fusion(lists)[:k]

    VIDEO_QUERY = "when did the latency alert come up in the review?"
    mo.vstack(
        [
            ui.table(
                [{"rank": rank + 1, "modality": hit["modality"], "chunk": hit["id"], "window": f"{hit['t_start']:.0f}–{hit['t_end']:.0f} s"} for rank, hit in enumerate(retrieve_video(VIDEO_QUERY))],
                title=f"'{VIDEO_QUERY}'" + ("" if CLIP_READY else " — transcript only; keyframe search needs CLIP"),
            )
        ]
    )
    return (retrieve_video,)


@app.cell
def _(ANSWER_SYSTEM, CFG, completion, image_part, retrieve_video, vlm_text):
    def format_timestamp(seconds: float) -> str:
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    def answer_video(query: str, k: int = 3) -> tuple[str, list[dict]]:
        """Same pattern as Task 6, with every piece of context tagged by its time window."""
        hits = retrieve_video(query, k=k)
        parts = [{"type": "text", "text": f"Question: {query}\nAnswer using the video context; cite timestamps."}]
        for hit in hits:
            stamp = f"[{format_timestamp(hit['t_start'])}-{format_timestamp(hit['t_end'])}]"
            if hit["modality"] == "video_frame":
                parts += [{"type": "text", "text": f"{stamp} keyframe:"}, image_part(hit["source_path"])]
            else:
                parts.append({"type": "text", "text": f"{stamp} transcript: {hit['content']}"})
        response = completion(
            timeout=600,
            messages=[{"role": "system", "content": ANSWER_SYSTEM}, {"role": "user", "content": parts}],
            max_tokens=300,
            **CFG.vlm_kwargs(),
        )
        return vlm_text(response), hits

    return (answer_video,)


@app.cell
def _(CFG, mo):
    video_button = mo.ui.run_button(
        label=f"🎬  Answer from the video with {CFG.vlm_model or 'VLM_MODEL (unset)'}",
        disabled=not CFG.has_vlm,
    )
    mo.vstack([video_button, mo.md("<sub>One model call: the transcript windows as text, the keyframes as pixels, the answer with a timestamp.</sub>")])
    return (video_button,)


@app.cell
def _(CFG, answer_video, mo, video_button):
    VIDEO_QUESTION = "When did the Coast latency problem come up, and what fixed it?"

    if video_button.value and CFG.has_vlm:
        with mo.status.spinner(title="Reading the video…"):
            VIDEO_ANSWER, VIDEO_HITS = answer_video(VIDEO_QUESTION)
        VIDEO_PANEL = mo.md(
            f"**Q: {VIDEO_QUESTION}**\n\n{VIDEO_ANSWER}\n\n<sub>context: "
            + ", ".join(f"{hit['modality']} {hit['id']} @ {hit['t_start']:.0f}s" for hit in VIDEO_HITS)
            + "</sub>"
        )
    else:
        VIDEO_ANSWER, VIDEO_HITS = "", []
        VIDEO_PANEL = mo.callout(mo.md("Set `VLM_MODEL` in `.env` and press the button to get an answer with a timestamp citation."), kind="info")

    VIDEO_PANEL
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    > **🏢 In the enterprise:** frame explosion is the enemy. Thirty minutes at
    > thirty frames a second is fifty-four thousand frames; nobody indexes
    > them all. Sample on an interval or on scene change, drop near-duplicates
    > with a perceptual hash, and **chunk on speech, attach vision** — segment
    > by transcript window and attach the representative frame. Carry
    > `t_start` and `t_end` on every chunk so an answer can deep-link
    > (`call.mp4?t=192`). For a corpus of support calls, measure the transcript
    > alone first; if it scores the same, the keyframe store is a cost with no
    > return and the page should say so.

    ### ❓ Question #8

    Strategy C — and the video index above — merge a text-store list and an
    image-store list with Reciprocal Rank Fusion rather than keeping whichever
    items have the highest raw similarity. Why are raw scores the wrong tool
    for that merge? Then look at your own ten real queries: for the ones that
    contain a number, a code or a name, which of the two lists is likely to be
    right — and what does that say about adding a lexical index alongside?

    **Answer:**

    ---
    # Conclusion

    You used one vision model two ways — as a parser at ingestion and as a
    reader at answer time — and built three retrieval strategies on one vector
    database, measured against the same questions. Then the same pipeline on a
    video, with a timestamp in the answer. The decision that came out of it is
    operational rather than clever: *describe once, index as text, verify
    anything numeric before it is indexed, narrow with retrieval, read with
    the model, and fuse by rank when two embedders disagree.*

    The attachments line on Nadia's page, filled in: OCR for the runbooks,
    through the scanner the firm already pays for, with page numbers; a
    parsing batch job inside the network for the screenshots, with every
    extracted code checked against the answer key before it is indexed; the
    transcript for the calls, with the keyframe store measured and probably
    dropped. Three attachment types, two tools, one new approval — and the
    number that justifies it is the "invented" column from Task 2, which is
    the difference between a diagnosis that cites `LOS 0x21` and one that
    cites a guess.

    | Component | What We Built | What Production Looks Like |
    | --- | --- | --- |
    | Vector store | Qdrant `:memory:`, rebuilt on every run | A managed or self-hosted Qdrant cluster: persistent collections, replication, snapshots, incremental upserts |
    | Corpus | 6 charts, 6 memos, one 45 s video | Millions of pages, slides and screenshots, rasterised page by page with provenance on every chunk |
    | Image parsing | A loop of six vision calls, a numbers check against an answer key | Parallel ingestion workers with retries, JSON-schema validation, a dead-letter queue, and a prompt-and-model record per caption |
    | Embeddings | CLIP ViT-B/32 as ONNX, downloaded from a public hub | A served embedding endpoint or a model mirrored onto the internal artifact store, version-pinned so index and queries never drift |
    | Retrieval | Top-3 cosine plus RRF | Hybrid (lexical + dense), metadata filters, a cross-encoder reranker, per-modality tuning |
    | Generation | One prompt with every retrieved image attached | Token budgets, image downscaling, prompt caching, citation post-checks, a fallback when no image was retrieved |
    | Evaluation | recall@3 over eight gold questions | A labelled set per release, retrieval and answer quality tracked separately, a judge for the second |
    | Video | Interval keyframes on one short clip | Scene-change detection, perceptual-hash dedupe, chapter summaries, deep links |

    **If the CLIP download is blocked where you work**, which it will be on
    many managed networks, there are two production answers and both are
    better than "it worked on my laptop". A **hosted multimodal embedding
    endpoint** — Voyage's `voyage-multimodal-3`, Cohere's `embed-v4.0`, Jina's
    `jina-clip-v2`, Amazon Titan Multimodal on Bedrock, or Google's
    `multimodalembedding` on Vertex — gives you the same shared space as an API
    call, with the caveat that Nadia's screenshots may not leave the network,
    so for her it is only an option through an approved gateway. Or **mirror
    the ONNX files** onto the firm's internal artifact store and point
    FastEmbed at them with `specific_model_path`; that is the shape that passes
    a security review, because the model becomes a versioned artifact like any
    other dependency. Either way, write which one in `use_case/ecosystem.md`:
    a blocked download is a finding, not a blocker.

    ---
    # Additional Context

    - [Learning Transferable Visual Models From Natural Language Supervision (CLIP)](https://arxiv.org/abs/2103.00020) — Radford et al., 2021. Two towers, one space, trained on pairs; §2 and Figure 1 are the whole idea
    - [Mind the Gap: Understanding the Modality Gap in Multi-modal Contrastive Representation Learning](https://arxiv.org/abs/2203.02053) — Liang et al., 2022. Why text and image vectors sit in different regions of the same space, which is Task 4's unified-search result explained
    - [Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods](https://dl.acm.org/doi/10.1145/1571941.1572114) — Cormack, Clarke & Büttcher, 2009. The twelve lines in Task 5, and why `k=60`
    - [FastEmbed — supported models](https://qdrant.github.io/fastembed/examples/Supported_Models/) — the CLIP, SigLIP and Nomic vision towers available as ONNX, with sizes; and [loading a model from a local path](https://qdrant.github.io/fastembed/) for the internal-mirror case
    - [Qdrant — payload filtering](https://qdrant.tech/documentation/concepts/filtering/) and [hybrid queries](https://qdrant.tech/documentation/concepts/hybrid-queries/) — the modality filter in Task 4, and the server-side version of Task 5's fusion
    - [ColPali: Efficient Document Retrieval with Vision Language Models](https://arxiv.org/abs/2407.01449) — retrieving over document *images* rather than their extracted text; the most direct answer to "should I OCR this or not"
    - [Anthropic — Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) — applies to captions too, and is the cheaper intervention most teams should make first
    - [An Easy Introduction to Multimodal Retrieval-Augmented Generation](https://developer.nvidia.com/blog/an-easy-introduction-to-multimodal-retrieval-augmented-generation/) — NVIDIA. A *pre-read for this session*: the strategies here laid out with their costs before you have built any
    - Hosted multimodal embeddings, for when the download is blocked: [Voyage multimodal](https://docs.voyageai.com/docs/multimodal-embeddings), [Cohere Embed v4](https://docs.cohere.com/docs/multimodal-embeddings), [Jina CLIP v2](https://jina.ai/embeddings/), [Amazon Titan Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/titan-multiemb-models.html), [Vertex AI multimodal embeddings](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-multimodal-embeddings)
    - **Keep building:** take the numbers check from Task 2 and turn it into the verification pass a real pipeline needs — a function that takes a parsed caption and a format rule or a lookup, returns *verified / unverified / invalid*, and writes the unverified ones to a file a person reviews. Then re-run Strategy A on only the verified captions and see whether recall@3 moves.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Bonus Tasks

    Optional. The first two are worth doing tonight; the third is a reading
    task with a decision at the end of it; the rest are meaningfully harder.

    ## Decide what your own non-text content needs

    Answer four questions about your use case, and write them into
    `use_case/decisions.md` — one line each, even if the honest answer is
    "there is none yet, and here is what would arrive first".

    1. **Is the information actually visual, or text rendered as pixels?** If
       it is text on a page, you want OCR plus the retrieval you already have,
       and a vision model is a detour.
    2. **Does the number you need live only in the pixels?** If so, which
       strategy can *find* the image, and what *reads* it — and what checks the
       reading before it is indexed?
    3. **Do you have descriptions?** Strategy A costs one parse per image before
       the first search. If nobody has described your images, that batch job —
       and where it runs — is the project.
    4. **For video or audio: does the transcript alone answer it?** Measure
       that first. If it does, the keyframe store is a cost with no return.

    *"We considered multimodal retrieval and OCR was the right tool"* is a good
    decision, well recorded. It is Nadia's, for the runbooks; the screenshots
    got the parsing batch job, inside the network, with the codes checked.

    ## Extend the evaluation set

    Add two gold questions to Task 7's set — one whose answer lives in a
    **memo**, one whose answer lives in a **chart** — using the data
    dictionary from Task 1 as the menu. Then say whether any strategy's
    recall@3 moved, and why that is plausible given the trade-offs table.
    """)
    return


@app.cell
def _(GOLD, STRATEGIES_AVAILABLE, recall_at_k, ui):
    MY_GOLD = {
        # "your question here": {"the_chunk_id_that_should_come_back"},
    }

    EXTENDED_GOLD = {**GOLD, **MY_GOLD}

    ui.table(
        [{"strategy": strategy, "recall@3": f"{recall_at_k(strategy, EXTENDED_GOLD):.2f}", "n": len(EXTENDED_GOLD)} for strategy in STRATEGIES_AVAILABLE],
        title="recall@3 with your questions added" if MY_GOLD else "recall@3 — add two questions to MY_GOLD above",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## When would you reach for LangChain — and when would you not?

    This notebook makes every model call with `litellm.completion()` and
    `litellm.embedding()`, talks to Qdrant with its own client, and keeps a
    chunk as a dataclass. Nothing in it needs a framework, and that was a
    choice: every line between the question and the answer is one you can
    read. The same pipeline is often written with **LangChain**, and knowing
    *when* that trade is worth making is a decision you will have to defend.

    **What LangChain would add here.** A single message format
    (`HumanMessage` with text and image content blocks) that every provider
    integration accepts; `init_chat_model("provider:model")` so the vendor is
    a string; a `Document` type with `page_content` and `metadata` that every
    vector-store integration understands, so `QdrantVectorStore.from_documents`
    replaces `build_collection`; a `Runnable` interface so retriever, prompt
    and model compose with `|`; and, through LangSmith or any OpenTelemetry
    exporter, a trace of each call with no code of your own. Multimodal
    *inputs* are well supported; LangChain's embedding interface is **text
    only**, which is why its image side still needs a wrapper exactly like
    `ClipEmbedder` — the framework does not remove Task 4, it moves it.

    **Reach for it when:** your firm has standardised on it and the platform
    team ships tracing, auth and rate limiting as LangChain callbacks — then
    *not* using it means re-implementing what they already run; when you need
    many integrations fast (five document loaders, three vector stores, two
    providers) and the glue code would otherwise be most of your repository;
    or when the orchestration becomes a graph with retries, branches and
    human-in-the-loop steps, which is LangGraph's job and tedious by hand.

    **Do not reach for it when:** the pipeline is this short — three strategies,
    one database, two model calls — and the framework's abstractions would hide
    the thing you are trying to measure; when the gateway you are allowed to
    use speaks a plain OpenAI-compatible protocol, which LiteLLM already
    handles with one config line; when a version bump in a fast-moving
    framework would be a change-control event at your firm; or when the person
    reviewing your code at work does not know it, because a dependency the
    reviewer cannot read is a dependency that does not pass review.

    The shape, if you do:

    ```python
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage
    from langchain_qdrant import QdrantVectorStore

    vlm = init_chat_model("anthropic:claude-sonnet-5", temperature=0)
    message = HumanMessage(content=[
        {"type": "text", "text": PARSE_PROMPT},
        {"type": "image", "source_type": "base64", "data": encoded, "mime_type": "image/png"},
    ])
    parsed = vlm.invoke([message]).content

    store = QdrantVectorStore.from_documents(documents, text_embedder, location=":memory:", collection_name="strategy_a")
    hits = store.similarity_search(query, k=3)
    ```

    Three things are the same under the hood: the base64 content block, the
    Qdrant collection, and the top-k cosine search. What changed is who owns
    the glue — and that is the decision to write down.

    **Reading:** [LangChain — multimodal inputs](https://docs.langchain.com/oss/python/langchain/models#multimodal) ·
    [`init_chat_model`](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html) ·
    [LangChain Qdrant integration](https://python.langchain.com/docs/integrations/vectorstores/qdrant/) ·
    [LangChain callbacks and tracing](https://docs.langchain.com/oss/python/langchain/observability) ·
    [LiteLLM — supported providers](https://docs.litellm.ai/docs/providers), the thing it would replace.

    ## Harder

    - **Hybrid on the text side.** Add a BM25 index over the memos and
      transcript, and fuse three lists with RRF instead of two. Then search for
      `240` and for `Coast` and see which list found it.
    - **Make Strategy A read tables.** Change `PARSE_PROMPT` to ask for a
      Markdown table of every data point, re-parse, and re-run recall@3 on the
      numeric questions.
    - **Rerank after the fuse.** Retrieve ten with Strategy C, then have the
      vision model score each against the query directly. Measure whether the
      top-1 improves enough to justify ten slow calls.
    - **Scene change instead of the clock.** Replace interval sampling with a
      frame-difference threshold and a perceptual-hash dedupe, and count how
      many keyframes the slide video needs. The answer is five.
    - **Ask something the corpus cannot answer** — *what was 2023 ticket
      volume?* — and confirm the model declines rather than inventing a bar.
    """)
    return


if __name__ == "__main__":
    app.run()
