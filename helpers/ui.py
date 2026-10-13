"""Small notebook affordances: progress, tables that don't need pandas, and a chart.

Tier 1: stdlib + marimo only. `table()` deliberately takes plain dicts rather than a
DataFrame, so a notebook can show results without pulling pandas into its sandbox.
`lines()` emits SVG by hand for the same reason -- neither altair nor matplotlib is
a dependency of this project, and adding one would land in the PEP 723 block of
every notebook that wanted a chart.

The tier-1 purity check walks the whole AST, so nothing here may import numpy even
inside a function body. Callers pass numpy arrays in; these functions treat them as
plain sequences and never say so.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Iterator, Mapping, Sequence
from contextlib import contextmanager
from typing import Any


@contextmanager
def spinner(label: str = "Working..."):
    """Show a spinner while a slow block runs.

        with spinner("Embedding 400 chunks..."):
            vectors = embed(chunks)
    """
    import marimo as mo

    with mo.status.spinner(title=label):
        yield


def track(items: Sequence[Any], label: str = "") -> Iterator[Any]:
    """Iterate with a progress bar. Needs a sequence, not a bare generator."""
    import marimo as mo

    with mo.status.progress_bar(total=len(items), title=label) as bar:
        for item in items:
            yield item
            bar.update()


def table(rows: Iterable[dict], *, title: str = "") -> Any:
    """Render a list of dicts as a markdown table.

    Column order follows first appearance across the rows, so the first dict's keys
    lead and any later additions get appended rather than silently dropped.
    """
    import marimo as mo

    rows = list(rows)
    if not rows:
        return mo.md(f"**{title}**\n\n_(no rows)_" if title else "_(no rows)_")

    columns: list[str] = []
    for row in rows:
        for key in row:
            if key not in columns:
                columns.append(key)

    def cell(value: Any) -> str:
        return "" if value is None else str(value).replace("|", r"\|")

    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    lines += [
        "| " + " | ".join(cell(row.get(col)) for col in columns) + " |" for row in rows
    ]

    body = "\n".join(lines)
    return mo.md(f"**{title}**\n\n{body}" if title else body)


# Mid-luminance and mid-saturation on purpose: these have to stay legible on a
# white notebook and on a dark one, and the viewer's theme is not ours to know.
_SERIES_COLOURS = ("#2f8f9d", "#c9773a", "#8e6bbf", "#3f8f5b", "#b4495f", "#8a8f2f")


def _nice_ticks(lo: float, hi: float, count: int = 5) -> list[float]:
    """Round tick values spanning [lo, hi]. Ugly axes make a chart look wrong."""
    if hi <= lo:
        return [lo]
    raw = (hi - lo) / max(count - 1, 1)
    magnitude = 10 ** math.floor(math.log10(raw))
    for multiple in (1, 2, 2.5, 5, 10):
        step = multiple * magnitude
        if raw <= step:
            break
    start = math.floor(lo / step) * step
    out, value = [], start
    while value < hi + step / 2:
        if value >= lo - step / 2:
            out.append(round(value, 10))
        value += step
    return out or [lo, hi]


def _fmt(value: float) -> str:
    """Tick labels without floating-point noise."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.6g}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def lines(
    series: Mapping[str, Sequence[float]],
    *,
    x: Sequence[float] | None = None,
    x_label: str = "",
    y_label: str = "",
    title: str = "",
    log_y: bool = False,
    height: int = 260,
) -> Any:
    """Plot one or more series as an SVG line chart.

    `series` maps a label to its y-values. `x` is shared across every series; when
    it is omitted the values are indexed 0, 1, 2, ... Pass `x` explicitly whenever
    the spacing is uneven -- a recall@k sweep over k = 1, 5, 20, 50 drawn on evenly
    spaced ticks tells a different story from the one the data tells.

    **All series share one y-axis**, which is what makes lines comparable and is
    the whole reason to draw them together. If your quantities are on different
    scales, normalise before calling -- dividing each by its own baseline turns
    "four unrelated units" into "what moved", which is usually the actual question.

    `log_y` needs strictly positive values; a loss curve that reaches zero should
    stay linear.
    """
    import marimo as mo

    data = {str(name): [float(value) for value in values] for name, values in series.items()}
    data = {name: values for name, values in data.items() if values}
    if not data:
        return mo.md(f"**{title}**\n\n_(no data)_" if title else "_(no data)_")

    width, pad_l, pad_r, pad_t, pad_b = 720, 58, 16, 12, 40
    span = max(len(values) for values in data.values())
    xs = [float(value) for value in x] if x is not None else [float(index) for index in range(span)]
    if len(xs) < span:
        raise ValueError(f"x has {len(xs)} points, but a series has {span}")

    flat = [value for values in data.values() for value in values]
    if log_y and min(flat) <= 0:
        raise ValueError("log_y needs strictly positive values")

    def project_y(value: float) -> float:
        return math.log10(value) if log_y else value

    y_lo, y_hi = min(map(project_y, flat)), max(map(project_y, flat))
    if y_hi == y_lo:  # a genuinely flat series still deserves a sensible band
        y_lo, y_hi = y_lo - 0.5, y_hi + 0.5
    x_lo, x_hi = min(xs), max(xs)
    if x_hi == x_lo:
        x_lo, x_hi = x_lo - 0.5, x_hi + 0.5

    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    to_px = lambda value, lo, hi, size: (value - lo) / (hi - lo) * size  # noqa: E731

    def px(index: int, value: float) -> tuple[float, float]:
        return (
            pad_l + to_px(xs[index], x_lo, x_hi, plot_w),
            pad_t + plot_h - to_px(project_y(value), y_lo, y_hi, plot_h),
        )

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" '
        f'style="width:100%;height:auto;overflow:visible;font-size:11px;'
        f'font-family:ui-sans-serif,system-ui,sans-serif;color:inherit;">'
    ]

    y_ticks = _nice_ticks(y_lo, y_hi)
    for tick in y_ticks:
        y = pad_t + plot_h - to_px(tick, y_lo, y_hi, plot_h)
        if not (pad_t - 1 <= y <= pad_t + plot_h + 1):
            continue
        parts.append(
            f'<line x1="{pad_l}" y1="{y:.1f}" x2="{pad_l + plot_w}" y2="{y:.1f}" '
            f'stroke="currentColor" stroke-opacity=".13"/>'
            f'<text x="{pad_l - 8}" y="{y + 3.5:.1f}" text-anchor="end" '
            f'fill="currentColor" fill-opacity=".6">'
            f"{_fmt(10**tick if log_y else tick)}</text>"
        )

    # With few points, label the actual x values rather than invented round ones --
    # k = 1, 5, 20, 50 must read as those, not as 0, 12.5, 25.
    x_ticks = sorted(set(xs)) if len(set(xs)) <= 8 else _nice_ticks(x_lo, x_hi, 6)
    for tick in x_ticks:
        x_px = pad_l + to_px(tick, x_lo, x_hi, plot_w)
        parts.append(
            f'<text x="{x_px:.1f}" y="{pad_t + plot_h + 15}" text-anchor="middle" '
            f'fill="currentColor" fill-opacity=".6">{_fmt(tick)}</text>'
        )

    parts.append(
        f'<line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{pad_l + plot_w}" '
        f'y2="{pad_t + plot_h}" stroke="currentColor" stroke-opacity=".35"/>'
    )

    for order, (name, values) in enumerate(data.items()):
        colour = _SERIES_COLOURS[order % len(_SERIES_COLOURS)]
        points = [px(index, value) for index, value in enumerate(values)]
        path = " ".join(
            f"{'M' if index == 0 else 'L'}{x:.1f},{y:.1f}" for index, (x, y) in enumerate(points)
        )
        parts.append(
            f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round"/>'
        )
        if len(points) <= 24:  # dense series turn into a smear of dots
            parts += [
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{colour}"/>'
                for x, y in points
            ]

    if y_label:
        parts.append(
            f'<text x="{pad_l}" y="{pad_t - 1}" text-anchor="start" '
            f'fill="currentColor" fill-opacity=".6">{y_label}</text>'
        )
    if x_label:
        parts.append(
            f'<text x="{pad_l + plot_w}" y="{height - 4}" text-anchor="end" '
            f'fill="currentColor" fill-opacity=".6">{x_label}</text>'
        )
    parts.append("</svg>")

    legend = " ".join(
        f'<span style="white-space:nowrap;margin-right:1em;">'
        f'<span style="display:inline-block;width:.7em;height:.7em;border-radius:50%;'
        f'background:{_SERIES_COLOURS[index % len(_SERIES_COLOURS)]};margin-right:.35em;">'
        f"</span>{name}</span>"
        for index, name in enumerate(data)
    )
    chart = mo.Html(
        f'<div style="margin:.5em 0;">{"".join(parts)}'
        f'<div style="font-size:.85em;opacity:.8;margin-top:.25em;">{legend}</div></div>'
    )
    return mo.vstack([mo.md(f"**{title}**"), chart]) if title else chart
