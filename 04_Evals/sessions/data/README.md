# The eval datasets

Two files sets live here. **`claims.json`** is a fictional claims system —
four policies, four open claims, the clauses an assistant may cite, and a
handler authority limit — that S8's tool-calling agent reads and writes.
Nothing in it is a real person, policy or insurer; edit it freely, and keep
one policy lapsed and one claim above authority, because the scenarios
depend on both.

The rest is **30 news articles and 480 machine-written summaries of them,
each rated by three human experts** on four dimensions. You cannot check a
judge for agreement without something to check against. This is that
something: real human judgement of real model output, which is otherwise the
hardest thing to get hold of when you are learning to build evals. S7 uses
it in the Bonus calibration task.

## Where it comes from

[**SummEval**](https://github.com/Yale-LILY/SummEval) (Fabbri et al., 2021), via
the `mteb/summeval` mirror. MIT licensed. Articles are from CNN/DailyMail; the
summaries were produced by a range of summarisation models.

Regenerate with:

```bash
uv run --with pyarrow python scripts/make_eval_dataset.py
```

## The files

| File | What is in it |
| --- | --- |
| `claims.json` | the fictional claims system S8's tools read and write: `policies`, `claims`, `handler_authority_gbp` |
| `articles.jsonl` | `id`, `text` — the source article |
| `judgments.jsonl` | `article_id`, `summary_id`, `summary`, and four scores from 1 to 5 |

Each score is the mean of three expert annotators.

| Dimension | The question it asks |
| --- | --- |
| **consistency** | Is everything in the summary actually supported by the article? Hallucination, measured |
| **relevance** | Does it capture what mattered? |
| **coherence** | Does it hold together as a piece of writing? |
| **fluency** | Are the sentences well formed? |

## Two things worth knowing before you use it

**The experts disagree with each other, and how much depends on the dimension.**
How much, exactly, is something this file *cannot* tell you — and that is the
first lesson in it.

Each score here is the **mean** of three annotators; the individual ratings were
never published. A mean destroys information. Some means give the triple away and
most do not:

| The mean | What the three annotators must have said |
| --- | --- |
| `1.0` | `{1,1,1}` — unanimous, provably |
| `5.0` | `{5,5,5}` — unanimous, provably |
| `1.333` | `{1,1,2}` — split, provably |
| `2.0` | `{2,2,2}` **or** `{1,2,3}` **or** `{1,1,4}` — unknowable |

So unanimity can only be **bracketed**:

| Dimension | Agreed at least | At most |
| --- | --- | --- |
| consistency | **80%** | 83% |
| fluency | **67%** | 72% |
| coherence | **6%** | 32% |
| relevance | **4%** | 35% |

**Read the left column.** The right one is every whole-number mean, and three
annotators answering **completely at random** would produce a whole mean
**33%** of the time — so an "at most" near that number carries no
information about agreement whatsoever.

The ordering survives anyway, and now it is proved rather than asserted:
consistency's *lower* bound sits above coherence's *upper* bound, so the two
intervals cannot overlap however the hidden ratings fell. **Consistency is close
to a fact. Coherence is closer to an opinion.** That is not a flaw in the dataset
— it is the thing being measured, and it should change what you ask a judge to do.
**Demanding that your judge agree with you about coherence is demanding more
agreement than three trained humans managed with each other.** A judge that
"disagrees with you" on a subjective dimension may be sitting comfortably inside
the range people occupy.

> Worth keeping when you leave: the first question about any metric is what its
> value would be if the thing it measures were absent. Here that is 33%,
> and two of these four dimensions land on it.

**The distribution is lopsided, as real data always is.** 32 of 480
summaries (6.7%) are rated 2 or below for consistency. Sample
twenty at random to test whether your judge catches hallucination and you would
expect **about one** bad example.

That is the whole argument for generating your own failures rather than waiting
for them. It is not that synthetic data is more convenient — it is that the
events you most want to detect are, by definition, the ones your natural data
barely contains, and a test set that is 94% the happy path cannot tell you
whether the detector works.

## Licence

MIT, from the SummEval repository. The underlying articles are CNN/DailyMail news
text, distributed for research use as part of that dataset.
