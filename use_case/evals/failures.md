18 of 66 runs had at least one failure; 1 of those was caught by an assembly check.

# Failures in the utility extraction spike

**Traces:** 66 recorded runs on `gemini-3.5-flash`: 17 utility bills × strategies A (one request for the whole file), B (one request per page, merged) and C (page classifier, per-page reads, assembly with cross-checks), plus a second run of the 5 statement bills × A, B, C. All 66 read. The runs and their labels stay in the client repo; this file carries counts and sentences only.

**Method:** each run re-scored against its hand-checked label with the spike's current scorer (one run's stored score predated rate-tier summing and was stale). Where the score showed a problem, the extraction was compared with the label until the cause was clear. "Flagged" means the run's `checks` list has an entry with `ok: false`, i.e. the pipeline itself noticed (FR-11.2's flagged vs silently wrong split).

**By strategy:** A 8 of 22 runs failed, B 10 of 22, C 0 of 22.

| # | Failure | Count | Strategies | Flagged by a check? | Scorer |
|---|---|---|---|---|---|
| 1 | On a file of several complete statements merged with no roll-up page, got the bill totals wrong: B took the first statement's header as the whole file's, A left the totals blank. Every account line was right. | 8 | A (4), B (4) | 0 of 8 | `header_ok` |
| 2 | Dropped the first rate tier of an account's usage and reported only the remainder as billed kWh. | 3 | A | 0 of 3 | `usage_match` |
| 3 | Misread one digit of an account number on the summary page while the detail page had it right; the merge kept both and counted that account's charges twice. | 2 | B | 0 of 2 | `accounts_exact` |
| 4 | Read a non-account number on the page as a second account with the bill's amount, doubling the account total. | 1 | B | 0 of 1 | `accounts_exact` |
| 5 | Dropped a digit from an account number; amounts still added up, so nothing looked wrong. | 1 | A | 0 of 1 | `accounts_exact` |
| 6 | Lost two accounts when page requests hit the provider's rate limit. | 1 | B | 0 of 1 (the run logged the errors; no check failed) | `accounts_exact` |
| 7 | Returned one account twice, once per service section; the merge kept one section's charges and lost the rest. | 1 | A | 1 of 1 | `amounts_exact` |
| 8 | Filled the carried balance from page 1 when the bill carried nothing; the difference between current charges and total due was a late fee itemized on page 2. | 1 | B | 0 of 1 | `header_ok` |
| 9 | Reported an account's billed kWh as a figure not printed on its page: its kW demand with the decimal point dropped, which is also another account's billed kWh. | 1 | A | 0 of 1 | `usage_match` |

19 failures in 18 runs (one run had both #2 and #9).

**Not seen in these runs:** a misread dollar amount on an account that was otherwise found, a hallucinated amount, truncated output. `amounts_exact` therefore traces to #7 only; the digit-flip and 10%-off amount cases are covered by the generated failures in `synthetic.jsonl`.

**What the split says:** 17 of 18 failing runs were silently wrong. A's only check is for a repeated account and B has none, so a wrong bill came out looking like a right one. C ran the same checks on every bill and was never wrong, so these runs cannot show how often C's checks would catch a C failure. That is the reason the headline is `no_silent_error` and the reason its interval matters.
