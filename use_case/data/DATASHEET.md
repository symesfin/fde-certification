# Datasheet

<!-- Written in TC2, alongside your synthetic data. This file is committed; the
     data itself is not. -->

## What this data is

**Generated on:** <!-- date -->
**Generated from:** <!-- the schema + a written description, NOT real records -->
**Rows:** <!-- n -->

## Variation axes

<!-- What you varied to get coverage: persona, format, difficulty, edge cases. -->

| Axis | Values |
| --- | --- |
| <!-- --> | <!-- --> |

## What it can validate

<!-- Which claims this data supports. Be narrow. -->

## What it cannot validate

<!-- The important half. Synthetic data cannot tell you about real distribution,
     real frequency, or failure modes you did not think to generate. Say so. -->

## What it must never be compared against

<!-- If you have real ground truth somewhere, say where, and say explicitly that
     these rows are not it. -->

## Leakage check — outward (what left)

- [ ] No real record was used as a seed.
- [ ] No real entity names, IDs, or identifiers appear.
- [ ] No distinctive internal formats that would identify the firm.
- [ ] Rare categories were generated, not copied.

## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
<!-- yes, disjoint | no — overlap: <which goldens, which source> | unknown — who would know: <role> -->

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** <!-- n rows at threshold t -->
