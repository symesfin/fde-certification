"""Regenerate the multimodal corpus for the Multimodal Retrieval session.

Writes `03_Retrieval/sessions/data/multimodal/`:

    images/                 six charts (PNG). Four of the six numbers live ONLY here.
    text/                   six short memos (Markdown)
    video/review.mp4        a ~45 s narrated-slide video (silent; visuals only)
    video/review_transcript.json   timestamped transcript, as speech-to-text would emit
    video/keyframes/        one reference frame per slide, for machines without OpenCV
    parses.jsonl            reference parse of each chart, written from the source values
    data_dictionary.json    what each file contains, and the question it answers
    README.md, LICENSE      provenance and CC0

Everything is fictional and machine-generated: "Northline Broadband", the figures,
the memos and the narration describe no real company, person or product. The
dataset is a re-skin of the CC0 "ACME Robotics FY2024" demo corpus from the AI
Makerspace AI Engineering certification, re-drawn here so the numbers belong to
the operator the retrieval sessions follow.

The design choice that matters: the numeric facts for tickets, churn, latency and
root causes appear in no text file, so a question about them can only be answered
by retrieving a chart and reading it. Headcount and NPS appear in both a chart and
a memo on purpose — Strategy A has to beat Strategy B somewhere.

Regenerate with:

    uv run --with matplotlib --with imageio --with imageio-ffmpeg \\
        python scripts/make_multimodal_corpus.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "03_Retrieval" / "sessions" / "data" / "multimodal"
IMG, TXT, VID, KF = OUT / "images", OUT / "text", OUT / "video", OUT / "video" / "keyframes"

COMPANY = "Northline Broadband"

# ----------------------------------------------------------------------- charts
# (file, kind, title, labels, values, ylabel/format, takeaway, data_points)
CHARTS = [
    dict(
        file="fig_tickets_quarterly.png", kind="bar",
        title="Support tickets per quarter, 2024 (thousands)",
        labels=["Q1", "Q2", "Q3", "Q4"], values=[12, 18, 15, 27], ylabel="Tickets (thousands)",
        takeaway="Ticket volume peaked in Q4 at 27 thousand, more than double Q1's 12 thousand.",
        data_points=["Q1: 12k tickets", "Q2: 18k tickets", "Q3: 15k tickets", "Q4: 27k tickets"],
        about="Support tickets per quarter",
        fact="Q4 highest at 27k; Q1 lowest at 12k",
        demo_question="Which quarter had the most support tickets, and how many?",
        pixels_only=True,
    ),
    dict(
        file="fig_churn_monthly.png", kind="bar",
        title="Monthly customer churn rate (%)",
        labels=["Jan", "Feb", "Mar", "Apr"], values=[5.1, 4.8, 6.2, 3.9], ylabel="Churn (%)",
        takeaway="Churn spiked to 6.2% in March and fell to 3.9% in April, the best month shown.",
        data_points=["Jan: 5.1%", "Feb: 4.8%", "Mar: 6.2%", "Apr: 3.9%"],
        about="Monthly churn rate",
        fact="March spiked to 6.2%; April best at 3.9%",
        demo_question="In which month was churn highest?",
        pixels_only=True,
    ),
    dict(
        file="fig_latency_region.png", kind="bar",
        title="P95 line latency by region (ms)",
        labels=["North", "Central", "Coast"], values=[120, 180, 240], ylabel="Latency (ms)",
        takeaway="The Coast region is the slowest at 240 ms P95, twice the North region's 120 ms.",
        data_points=["North: 120 ms", "Central: 180 ms", "Coast: 240 ms"],
        about="P95 line latency by region",
        fact="Coast worst at 240 ms; North best at 120 ms",
        demo_question="What is the P95 latency in the Coast region?",
        pixels_only=True,
    ),
    dict(
        file="fig_headcount_team.png", kind="bar",
        title="Support headcount by team (FY2024)",
        labels=["Field", "First-line", "Second-line", "NOC"], values=[45, 30, 18, 12], ylabel="People",
        takeaway="Field engineering is the largest team at 45 people; the NOC is the smallest at 12.",
        data_points=["Field: 45", "First-line: 30", "Second-line: 18", "NOC: 12"],
        about="Support headcount by team",
        fact="Field largest at 45; total 105",
        demo_question="Which support team has the most people?",
        pixels_only=False,
    ),
    dict(
        file="fig_nps_quarterly.png", kind="line",
        title="Net Promoter Score by quarter",
        labels=["Q1", "Q2", "Q3", "Q4"], values=[22, 31, 28, 41], ylabel="NPS",
        takeaway="NPS rose from 22 in Q1 to 41 in Q4, with a dip to 28 in Q3.",
        data_points=["Q1: 22", "Q2: 31", "Q3: 28", "Q4: 41"],
        about="NPS by quarter",
        fact="Rose to 41 in Q4; dipped to 28 in Q3",
        demo_question="How did NPS change over the year?",
        pixels_only=False,
    ),
    dict(
        file="fig_root_cause.png", kind="pie",
        title="Ticket root causes (FY2024)",
        labels=["Customer equipment", "Line faults", "Billing", "Other"], values=[55, 20, 15, 10], ylabel="",
        takeaway="Over half of all tickets trace back to equipment in the customer's home.",
        data_points=["Customer equipment: 55%", "Line faults: 20%", "Billing: 15%", "Other: 10%"],
        about="Ticket root-cause breakdown",
        fact="Customer equipment 55%, Line faults 20%, Billing 15%, Other 10%",
        demo_question="What share of tickets are caused by the customer's own equipment?",
        pixels_only=True,
    ),
]

# ------------------------------------------------------------------------ memos
# Numbers for tickets, churn, latency and root causes are deliberately absent.
MEMOS = {
    "doc_retention_programme.md": (
        "# FY2024 Retention Programme\n\n"
        f"{COMPANY} prioritised keeping existing households over winning new ones this year. "
        "We stood up a dedicated save desk, rewrote the onboarding journey for new installs, and "
        "introduced quarterly check-in calls for business accounts. The largest single factor in the "
        "fourth-quarter ticket surge was the regional pricing change, which generated a wave of "
        "billing queries that the save desk absorbed.\n"
    ),
    "doc_network_reliability.md": (
        "# Network Reliability Review\n\n"
        "The access network is monitored per region (North, Central, Coast). We track P95 line latency "
        "per region as a core service-level objective and page the on-call network engineer when a region "
        "exceeds target at peak. In 2024 the Coast region was persistently the slowest and generated the "
        "most alerts; a regional cache at the Coast aggregation point brought latency back under target "
        "in the autumn.\n"
    ),
    "doc_ops_review_notes.md": (
        "# Operations Review Notes — Q4 2024\n\n"
        "- Ticket volume was highest in the final quarter, driven by the pricing change and a run of storm damage.\n"
        "- Churn improved after the onboarding rewrite but spiked in March because a billing bug double-charged "
        "a cohort of customers on the legacy tariff.\n"
        "- The review board asked for a reliability report after the Coast latency alerts.\n"
    ),
    "doc_support_team.md": (
        "# Support Organisation — FY2024\n\n"
        "The support organisation grew to 105 people. Hiring was field-heavy (45 field engineers), then "
        "first-line (30), second-line (18), and the network operations centre (12). A structured onboarding "
        "programme for new hires launched in Q2 and is credited with cutting time-to-competence.\n"
    ),
    "doc_customer_sentiment.md": (
        "# Customer Sentiment & Roadmap\n\n"
        "NPS trended up from 22 in Q1 to 41 in Q4, with a dip in Q3 (to 28) attributable to a partial outage "
        "in the Coast region. Next year focuses on self-service diagnostics in the customer app and on "
        "regional performance work.\n"
    ),
    "doc_root_cause_review.md": (
        "# Ticket Root-Cause Review — FY2024\n\n"
        "Most tickets trace back to equipment in the customer's home rather than to the network. A review "
        "recommended a guided modem-reset flow in the app before a ticket can be raised, and a swap-by-post "
        "programme for routers out of warranty. Line-fault tickets should fall once the Coast cache work "
        "reduces congestion-related complaints.\n"
    ),
}

# ------------------------------------------------------------------------ video
# (slide title, chart file or None, on-slide caption, narration, duration s)
TIMELINE = [
    (f"{COMPANY} — 2024 Support Review", None, "Fiscal Year 2024 Service Desk Review",
     f"Welcome to the {COMPANY} 2024 support review. We will cover ticket volume, retention, "
     "network reliability, and how the team grew.", 6),
    ("Ticket volume", "fig_tickets_quarterly.png", "Record Q4: 27 thousand tickets",
     "Ticket volume reached a record twenty-seven thousand in the fourth quarter, driven by the regional "
     "pricing change and storm damage, up from twelve thousand in the first quarter.", 10),
    ("Retention", "fig_churn_monthly.png", "March churn spike from a billing bug",
     "Monthly churn spiked to six point two percent in March because of a billing bug that double-charged a "
     "cohort, then improved to three point nine percent in April after the onboarding rewrite.", 10),
    ("Reliability", "fig_latency_region.png", "Coast P95 latency was the worst region",
     "On reliability, Coast ninety-fifth percentile latency reached two hundred and forty milliseconds, the "
     "worst of any region, which repeatedly paged the on-call engineer. A regional cache brought it back to "
     "target.", 11),
    ("Team", "fig_headcount_team.png", "Grew to 105 people, field-heavy",
     "Finally, the support organisation grew to a hundred and five people, with field engineering the largest "
     "team at forty-five.", 8),
]


def draw_charts() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    IMG.mkdir(parents=True, exist_ok=True)
    for chart in CHARTS:
        path = IMG / chart["file"]
        fig, ax = plt.subplots(figsize=(5.4, 3.4))
        if chart["kind"] == "bar":
            bars = ax.bar(chart["labels"], chart["values"], color="#2f8f9d")
            for bar, value in zip(bars, chart["values"]):
                ax.text(bar.get_x() + bar.get_width() / 2, value, f"{value:g}", ha="center", va="bottom", fontsize=9)
            ax.set_ylabel(chart["ylabel"])
            ax.spines[["top", "right"]].set_visible(False)
        elif chart["kind"] == "line":
            ax.plot(chart["labels"], chart["values"], marker="o", linewidth=2, color="#2f8f9d")
            for label, value in zip(chart["labels"], chart["values"]):
                ax.text(label, value, str(value), ha="center", va="bottom", fontsize=9)
            ax.set_ylabel(chart["ylabel"])
            ax.spines[["top", "right"]].set_visible(False)
        else:
            ax.pie(
                chart["values"],
                labels=[f"{label} {value}%" for label, value in zip(chart["labels"], chart["values"])],
                startangle=90, counterclock=False,
                colors=["#2f8f9d", "#c9773a", "#8e6bbf", "#3f8f5b"],
            )
        ax.set_title(chart["title"], fontsize=11, fontweight="bold", wrap=True)
        fig.tight_layout()
        fig.savefig(path, dpi=130)
        plt.close(fig)


def write_memos() -> None:
    TXT.mkdir(parents=True, exist_ok=True)
    for name, body in MEMOS.items():
        (TXT / name).write_text(body, encoding="utf-8")


def write_parses() -> None:
    with (OUT / "parses.jsonl").open("w", encoding="utf-8") as handle:
        for chart in CHARTS:
            handle.write(json.dumps({
                "file": chart["file"],
                "kind": f"{chart['kind']} chart",
                "title": chart["title"],
                "takeaway": chart["takeaway"],
                "data_points": chart["data_points"],
            }) + "\n")


def write_dictionary() -> None:
    payload = {
        "company": f"{COMPANY} (fictional / synthetic)",
        "images": {
            chart["file"]: {
                "about": chart["about"],
                "fact": chart["fact"],
                "demo_question": chart["demo_question"],
                "pixels_only": chart["pixels_only"],
            }
            for chart in CHARTS
        },
        "text": {name: {"about": body.splitlines()[0].lstrip("# ")} for name, body in MEMOS.items()},
        "video": {
            "review.mp4": "a 45-second narrated-slide review of the year; the transcript is what a speech-to-text model would emit",
        },
    }
    (OUT / "data_dictionary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _font(size: int):
    from PIL import ImageFont

    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ):
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render_video() -> None:
    import numpy as np
    from PIL import Image, ImageDraw

    KF.mkdir(parents=True, exist_ok=True)
    width, height, fps = 1280, 720, 8

    def slide(title: str, chart: str | None, caption: str):
        image = Image.new("RGB", (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([0, 0, width, 96], fill=(28, 42, 74))
        draw.text((40, 28), title, font=_font(40), fill=(255, 255, 255))
        if chart:
            chart_image = Image.open(IMG / chart).convert("RGB")
            chart_image.thumbnail((900, 500))
            image.paste(chart_image, ((width - chart_image.width) // 2, 130))
        if caption:
            draw.text((40, height - 70), caption, font=_font(24), fill=(40, 40, 40))
        return image

    frames, segments, clock = [], [], 0.0
    for index, (title, chart, caption, narration, duration) in enumerate(TIMELINE):
        array = np.asarray(slide(title, chart, caption))
        frames += [array] * int(duration * fps)
        segments.append({
            "id": f"seg_{index:03d}",
            "start": round(clock, 2),
            "end": round(clock + duration, 2),
            "text": narration,
            "onscreen_asset": chart,
        })
        Image.fromarray(array).save(KF / f"frame_{int(clock + duration / 2):04d}.jpg", quality=85)
        clock += duration

    import imageio.v2 as imageio

    imageio.mimwrite(VID / "review.mp4", frames, fps=fps, codec="libx264", quality=7, macro_block_size=None)
    (VID / "review_transcript.json").write_text(
        json.dumps({"video": "review.mp4", "fps": fps, "segments": segments}, indent=2) + "\n",
        encoding="utf-8",
    )


README = f"""# The multimodal corpus

**Six charts, six memos, one 45-second video — one fictional regional broadband
operator, "{COMPANY}".**

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
"""

LICENSE = """Creative Commons Legal Code — CC0 1.0 Universal

The person who associated a work with this deed has dedicated the work to the public
domain by waiving all of his or her rights to the work worldwide under copyright law,
including all related and neighboring rights, to the extent allowed by law.

You can copy, modify, distribute and perform the work, even for commercial purposes,
all without asking permission.

Full text: https://creativecommons.org/publicdomain/zero/1.0/legalcode
"""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    draw_charts()
    write_memos()
    write_parses()
    write_dictionary()
    render_video()
    (OUT / "README.md").write_text(README, encoding="utf-8")
    (OUT / "LICENSE").write_text(LICENSE, encoding="utf-8")
    print(f"✅ wrote {OUT.relative_to(ROOT)}")
    for path in sorted(OUT.rglob("*")):
        if path.is_file():
            print(f"   {path.relative_to(OUT)}  {path.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
