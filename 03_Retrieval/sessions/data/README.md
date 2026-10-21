# The retrieval corpus

**Seven pages of a fictional regional broadband operator's knowledge base,
one wiki index, and seven reviewed questions.**

Everything here is fictional and machine-generated for teaching retrieval.
"Northline Broadband", its tariffs, codes, procedures and figures describe no
real company, person or product. The corpus is a re-skin of the ACME Analytics
corpus from AI Makerspace's Titanium Engineer programme (MIT-licensed), redrawn
so the pages belong to the operator the retrieval sessions follow and so that
each page has a *shape* a retrieval technique can be measured against.

## The files

| File | What is in it | What it is for |
| --- | --- | --- |
| `corpus/northline_field_guide.md` | company facts, regions, headcount, services, history | plain "what is X" facts |
| `corpus/northline_glossary.md` | acronyms, status codes (`LOS 0x21`), product codes, exact identifiers | exact-text questions |
| `corpus/northline_tariffs_and_slas.md` | tariff pricing, minimum terms, service levels, credits, termination | near-duplicate sections that differ by one figure |
| `corpus/northline_fault_runbook.md` | the fault stages, the line test, truck-roll approval, closure, line migration | long multi-step procedures |
| `corpus/northline_data_handling.md` | encryption, access, retention, legal hold, incident response | breadth across many facets |
| `corpus/northline_network_operations.md` | the NOC, regional latency objectives, the Coast cache, maintenance windows | mixes exact tokens and concepts |
| `corpus/northline_quarterly_metrics.csv` | tickets, latency, churn and NPS by quarter and region | structured rows |
| `wiki/index.md` | the navigation page: one line per page, and how to move between them | the LLM Wiki's entry point; page names are stable tool inputs |
| `eval_cases.jsonl` | seven questions, each with `expected_terms`, `expected_pages` and the approach it `favours`, labelled before any run | the answer key, and the prediction |

The pages are plain Markdown with `##` section headings, which is the only
structure the chunker relies on. The metrics CSV is one section.

## The seven questions

Each case carries a `favours` field — the approach it was written to reward —
and a `why`, both decided before any run, so the notebook's results table is
predicted against observed rather than a leaderboard.

| id | shape | favours | the mechanism |
| --- | --- | --- | --- |
| `exact` | an acronym (`FTR`) | either | exact text; one call each way |
| `vocabulary` | none of the page's words in the question (£45 asked as "forty-five pounds") | DCI | ranking has nothing to rank on; the index names the page |
| `deep_section` | the answer sits past character 1,000 of the truck-roll stage | DCI | the retriever's 1,000-character cap hides it; `read_page` does not |
| `which_pages` | "which pages mention the Coast cache" | DCI | top-k cannot answer that; one `grep` returns every line with provenance, and cheaply |
| `broad_churn` | split between the metrics CSV's notes column and the field guide's exit-survey section | RAG | ranking returns both at fixed cost; DCI reads whole pages |
| `broad_incident` | three pages, no single section | RAG | same shape |
| `decline` | ticket volume in 2023 — a year the corpus does not cover | either | `must_decline`: the pass mark is a refusal that invents no figure; retrieval cannot say "nothing matched", the loop has to |

The truck-roll stage of the fault runbook is deliberately longer than the
retriever's cap, with the contact-on-the-day requirement as its eighth item.
That is the trap `deep_section` tests, and it is the shape of every "the
answer was in the document" complaint a chunk retriever ever gets.

## To run on your own data

Drop your own `.md`, `.txt` or `.csv` files into `corpus/`, rewrite
`wiki/index.md` so it names every page and says what each is for, and label
your own `eval_cases.jsonl` — page and terms first, then run. Pages without
`##` headings become one chunk each, which is itself a finding.

## Licence

Released under **Creative Commons Zero v1.0 (CC0)** — public-domain dedication.
The ACME corpus it was redrawn from is MIT-licensed by AI Makerspace.
